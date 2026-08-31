using Microsoft.EntityFrameworkCore;

namespace Avos.Previews;

/// <summary>Mirrors avos-vault's SessionRevocationMiddleware: an access token's "sid" (RefreshToken
/// row id, see TokenService.CreateAccessToken) is checked against the database on every request.
/// Without this, logging out or a refresh rotating the old token would only stop future refreshes
/// while the outstanding 15-minute access token kept working. One indexed primary-key lookup per
/// authenticated request; tokens minted before the "sid" claim existed carry none and pass through
/// untouched.</summary>
public sealed class SessionRevocationMiddleware(RequestDelegate next)
{
    public async Task InvokeAsync(HttpContext context, AppDb db)
    {
        var sid = context.User.FindFirst("sid")?.Value;
        if (sid is not null && Guid.TryParse(sid, out var sessionId))
        {
            var revoked = await db.RefreshTokens
                .Where(t => t.Id == sessionId)
                .Select(t => (bool?)(t.RevokedAt != null))
                .FirstOrDefaultAsync();
            // A missing row (null) means the session was purged outright — treat like revoked.
            // Revoked-because-ROTATED tokens are fine: rotation issues a NEW access token bound to
            // the NEW row before the old row is revoked, so an old access token still presenting a
            // rotated sid is by definition stale (its bearer already has the newer one).
            if (revoked is null or true)
            {
                context.Response.StatusCode = StatusCodes.Status401Unauthorized;
                await context.Response.WriteAsJsonAsync(new { message = "Diese Sitzung wurde abgemeldet." });
                return;
            }
        }

        await next(context);
    }
}

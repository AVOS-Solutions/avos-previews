using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;
using System.Threading.RateLimiting;
using Avos.Previews;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.DataProtection;
using Microsoft.AspNetCore.RateLimiting;
using Microsoft.AspNetCore.StaticFiles;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;

var builder = WebApplication.CreateBuilder(args);

var dataDir = builder.Configuration["App:DataDir"] ?? Path.Combine(builder.Environment.ContentRootPath, "data");
Directory.CreateDirectory(dataDir);
var previewsRoot = Path.GetFullPath(builder.Configuration["Previews:Root"]
    ?? Path.Combine(builder.Environment.ContentRootPath, "..", "..", "..", "previews"));

// Postgres in normal operation (ERP parity); SQLite fallback when no connection string is
// configured, so the API runs locally with zero infrastructure.
var connectionString = builder.Configuration.GetConnectionString("Default");
builder.Services.AddDbContext<AppDb>(o =>
{
    if (!string.IsNullOrWhiteSpace(connectionString))
        o.UseNpgsql(connectionString);
    else
        o.UseSqlite($"Data Source={Path.Combine(dataDir, "previews.db")}");
});

builder.Services.AddDataProtection()
    .SetApplicationName("avos-previews")
    .PersistKeysToFileSystem(new DirectoryInfo(Path.Combine(dataDir, "dp-keys")));
builder.Services.AddHttpClient<LicensingSso>(c => c.Timeout = TimeSpan.FromSeconds(15));
builder.Services.AddSingleton<TokenService>();

builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(o =>
    {
        o.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(builder.Configuration["Jwt:Key"] ?? "")),
            ClockSkew = TimeSpan.FromSeconds(30),
        };
    });
builder.Services.AddAuthorization(o =>
{
    o.AddPolicy("StaffOnly", p => p.RequireRole("Staff"));
    // Mirrors avos-vault: FallbackPolicy applies to any endpoint lacking [AllowAnonymous]/
    // .AllowAnonymous(), even ones with no explicit .RequireAuthorization() at all — so a new
    // endpoint is protected by default instead of accidentally public.
    o.DefaultPolicy = o.GetPolicy("StaffOnly")!;
    o.FallbackPolicy = o.GetPolicy("StaffOnly")!;
});

builder.Services.AddRateLimiter(o =>
{
    o.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
    o.AddPolicy("unlock", ctx => RateLimitPartition.GetFixedWindowLimiter(
        ctx.Connection.RemoteIpAddress?.ToString() ?? "unknown",
        _ => new FixedWindowRateLimiterOptions { PermitLimit = 10, Window = TimeSpan.FromMinutes(5) }));
    o.AddPolicy("login", ctx => RateLimitPartition.GetFixedWindowLimiter(
        ctx.Connection.RemoteIpAddress?.ToString() ?? "unknown",
        _ => new FixedWindowRateLimiterOptions { PermitLimit = 20, Window = TimeSpan.FromMinutes(5) }));
});

var app = builder.Build();

using (var scope = app.Services.CreateScope())
    scope.ServiceProvider.GetRequiredService<AppDb>().Database.EnsureCreated();

app.UseRateLimiter();
// Nothing this API serves should ever be indexed (share previews included).
app.Use(async (ctx, next) =>
{
    ctx.Response.Headers["X-Robots-Tag"] = "noindex, nofollow";
    await next();
});
app.UseAuthentication();
app.UseMiddleware<SessionRevocationMiddleware>();
app.UseAuthorization();
// Serves the theme CSS + favicon used by the share gate pages.
app.UseStaticFiles();

var contentTypes = new FileExtensionContentTypeProvider();
var devLoginEnabled = app.Environment.IsDevelopment()
    && !string.IsNullOrWhiteSpace(app.Configuration["Auth:DevPassword"]);

string ShareBaseUrl() => (app.Configuration["App:PublicUrl"] ?? "").TrimEnd('/');

app.MapGet("/health", () => Results.Ok(new { status = "ok" })).AllowAnonymous();

// ---------------------------------------------------------------------------
// Auth (called server-to-server by the Next.js frontend)
// ---------------------------------------------------------------------------

app.MapGet("/api/public/auth/sso/authorize-url", (LicensingSso sso, string redirectUri, string state) =>
{
    if (!sso.Configured)
        return Results.Problem(statusCode: 503, title: "AVOS Licensing ist nicht konfiguriert.");
    return Results.Ok(new { url = sso.AuthorizeUrl(redirectUri, state) });
}).AllowAnonymous();

app.MapPost("/api/public/auth/sso/exchange", async (AppDb db, LicensingSso sso, TokenService tokens,
    SsoExchangeRequest req, CancellationToken ct) =>
{
    if (!sso.Configured)
        return Results.Problem(statusCode: 503, title: "AVOS Licensing ist nicht konfiguriert.");
    SsoIdentity? identity;
    try
    {
        identity = await sso.ExchangeCodeAsync(req.Code, req.RedirectUri, ct);
    }
    catch (Exception ex)
    {
        app.Logger.LogWarning(ex, "SSO code exchange failed");
        identity = null;
    }
    if (identity == null)
        return Results.Json(new { message = "SSO-Anmeldung fehlgeschlagen. Bitte erneut versuchen." },
            statusCode: StatusCodes.Status401Unauthorized);
    if (!identity.IsAuthorized)
        return Results.Json(new { message = "Kein Zugriff: für dieses Konto ist keine aktive AVOS-Previews-Lizenz hinterlegt." },
            statusCode: StatusCodes.Status403Forbidden);
    return Results.Ok(await IssueAuthResponseAsync(db, tokens, identity.UserId, identity.Email,
        identity.FullName ?? identity.Email));
}).RequireRateLimiting("login").AllowAnonymous();

if (devLoginEnabled)
{
    app.MapPost("/api/public/auth/dev-login", async (AppDb db, TokenService tokens, DevLoginRequest req) =>
    {
        var expected = app.Configuration["Auth:DevPassword"]!;
        var ok = CryptographicOperations.FixedTimeEquals(
            Encoding.UTF8.GetBytes(req.Password ?? ""), Encoding.UTF8.GetBytes(expected));
        if (!ok)
            return Results.Json(new { message = "Falsches Passwort." }, statusCode: StatusCodes.Status401Unauthorized);
        return Results.Ok(await IssueAuthResponseAsync(db, tokens, "dev", "dev@avos-solutions.com", "Dev-Login"));
    }).RequireRateLimiting("login").AllowAnonymous();
}

app.MapPost("/api/public/auth/refresh", async (AppDb db, TokenService tokens, RefreshRequest req) =>
{
    var hash = TokenService.HashRefreshToken(req.RefreshToken ?? "");
    var stored = await db.RefreshTokens.FirstOrDefaultAsync(t => t.TokenHash == hash);
    if (stored == null || !stored.IsActive)
        return Results.Json(new { message = "Sitzung abgelaufen." }, statusCode: StatusCodes.Status401Unauthorized);
    stored.RevokedAt = DateTimeOffset.UtcNow;
    var response = await IssueAuthResponseAsync(db, tokens, stored.UserId, stored.Email, stored.FullName);
    return Results.Ok(response);
}).AllowAnonymous();

app.MapPost("/api/public/auth/logout", async (AppDb db, RefreshRequest req) =>
{
    var hash = TokenService.HashRefreshToken(req.RefreshToken ?? "");
    var stored = await db.RefreshTokens.FirstOrDefaultAsync(t => t.TokenHash == hash);
    if (stored is { RevokedAt: null })
    {
        stored.RevokedAt = DateTimeOffset.UtcNow;
        await db.SaveChangesAsync();
    }
    return Results.NoContent();
}).AllowAnonymous();

async Task<object> IssueAuthResponseAsync(AppDb db, TokenService tokens, string userId, string email, string fullName)
{
    // Generated up front so the same id both names the RefreshToken row and rides along as the
    // access token's "sid" claim — see SessionRevocationMiddleware.
    var sessionId = Guid.NewGuid();
    var refreshToken = TokenService.GenerateRefreshToken();
    db.RefreshTokens.Add(new RefreshToken
    {
        Id = sessionId,
        UserId = userId,
        Email = email,
        FullName = fullName,
        TokenHash = TokenService.HashRefreshToken(refreshToken),
        ExpiresAt = DateTimeOffset.UtcNow.Add(TokenService.RefreshTokenLifetime),
        CreatedAt = DateTimeOffset.UtcNow,
    });
    await db.SaveChangesAsync();
    var (accessToken, expiresAt) = tokens.CreateAccessToken(userId, email, fullName, sessionId);
    return new
    {
        accessToken,
        accessTokenExpiresAt = expiresAt,
        refreshToken,
        user = new { id = userId, email, fullName },
    };
}

// ---------------------------------------------------------------------------
// Staff API (JWT bearer, called by the Next.js server)
// ---------------------------------------------------------------------------

app.MapGet("/api/me", (ClaimsPrincipal user) => Results.Ok(new
{
    id = user.FindFirstValue(ClaimTypes.NameIdentifier) ?? user.FindFirstValue("sub"),
    email = user.FindFirstValue(ClaimTypes.Email),
    name = user.FindFirstValue(ClaimTypes.Name),
})).RequireAuthorization("StaffOnly");

app.MapGet("/api/businesses", async (AppDb db) =>
{
    var businesses = BusinessCatalog.Load(previewsRoot);
    var now = DateTimeOffset.UtcNow;
    var links = await db.ShareLinks.AsNoTracking().ToListAsync();
    var bySlug = links.GroupBy(l => l.Slug).ToDictionary(g => g.Key, g => g.ToList());
    return Results.Ok(businesses.Select(b => new
    {
        b.Num, b.Slug, b.Name, b.Category, b.Region, b.Location, b.Description, b.OldWebsite,
        activeLinks = bySlug.TryGetValue(b.Slug, out var ls) ? ls.Count(l => l.IsUsable(now)) : 0,
        totalViews = bySlug.TryGetValue(b.Slug, out var ls2) ? ls2.Sum(l => l.ViewCount) : 0,
    }));
}).RequireAuthorization("StaffOnly");

app.MapGet("/api/shares", async (AppDb db, string? slug) =>
{
    var now = DateTimeOffset.UtcNow;
    var query = db.ShareLinks.AsNoTracking();
    if (!string.IsNullOrEmpty(slug)) query = query.Where(l => l.Slug == slug);
    // Ordered in memory: SQLite (the dev fallback provider) can't ORDER BY DateTimeOffset.
    var links = (await query.ToListAsync()).OrderByDescending(l => l.CreatedAt).ToList();
    return Results.Ok(links.Select(l => ShareDto(l, ShareBaseUrl(), now)));
}).RequireAuthorization("StaffOnly");

app.MapPost("/api/shares", async (AppDb db, ClaimsPrincipal user, CreateShareRequest req) =>
{
    var businesses = BusinessCatalog.Load(previewsRoot);
    if (businesses.All(b => b.Slug != req.Slug))
        return Results.BadRequest(new { message = "Unbekannter Betrieb." });
    if (req.MaxViews is < 1)
        return Results.BadRequest(new { message = "View-Limit muss mindestens 1 sein." });
    DateTimeOffset? expiresAt = null;
    if (req.ExpiresInDays is > 0)
        expiresAt = DateTimeOffset.UtcNow.AddDays(req.ExpiresInDays.Value);
    else if (req.ExpiresAt != null)
    {
        if (req.ExpiresAt <= DateTimeOffset.UtcNow)
            return Results.BadRequest(new { message = "Ablaufdatum liegt in der Vergangenheit." });
        expiresAt = req.ExpiresAt;
    }

    var link = new ShareLink
    {
        Id = Guid.NewGuid(),
        Token = Tokens.NewToken(),
        Slug = req.Slug,
        Label = string.IsNullOrWhiteSpace(req.Label) ? null : req.Label.Trim(),
        PasswordHash = string.IsNullOrWhiteSpace(req.Password) ? null : Tokens.HashPassword(req.Password),
        MaxViews = req.MaxViews,
        ExpiresAt = expiresAt,
        CreatedAt = DateTimeOffset.UtcNow,
        CreatedBy = user.FindFirstValue(ClaimTypes.Email) ?? "unbekannt",
    };
    db.ShareLinks.Add(link);
    await db.SaveChangesAsync();
    return Results.Ok(ShareDto(link, ShareBaseUrl(), DateTimeOffset.UtcNow));
}).RequireAuthorization("StaffOnly");

app.MapPost("/api/shares/{id:guid}/revoke", async (AppDb db, Guid id) =>
{
    var link = await db.ShareLinks.FindAsync(id);
    if (link == null) return Results.NotFound();
    link.RevokedAt ??= DateTimeOffset.UtcNow;
    await db.SaveChangesAsync();
    return Results.NoContent();
}).RequireAuthorization("StaffOnly");

app.MapDelete("/api/shares/{id:guid}", async (AppDb db, Guid id) =>
{
    var link = await db.ShareLinks.FindAsync(id);
    if (link == null) return Results.NotFound();
    db.ShareLinks.Remove(link);
    await db.SaveChangesAsync();
    return Results.NoContent();
}).RequireAuthorization("StaffOnly");

app.MapGet("/api/previews/{slug}/{**rest}", (string slug, string? rest) =>
    ServePreviewFile(slug, rest)).RequireAuthorization("StaffOnly");

// ---------------------------------------------------------------------------
// Public share links (browser-facing; the shared edge routes /s/* to this API)
// ---------------------------------------------------------------------------

app.MapGet("/s/{token}", (string token) => Results.Redirect($"/s/{token}/index.html")).AllowAnonymous();

app.MapPost("/s/{token}/unlock", async (HttpContext ctx, AppDb db, IDataProtectionProvider dp, string token) =>
{
    var link = await db.ShareLinks.FirstOrDefaultAsync(l => l.Token == token);
    var check = CheckLink(link);
    if (check != null) return check;
    var form = await ctx.Request.ReadFormAsync();
    var password = form["password"].ToString();
    if (link!.PasswordHash == null || !Tokens.VerifyPassword(password, link.PasswordHash))
    {
        return Results.Content(Pages.SharePassword(token, BusinessName(link.Slug), "Falsches Passwort."),
            "text/html", statusCode: StatusCodes.Status401Unauthorized);
    }
    SetUnlockCookie(ctx, dp, link);
    return Results.Redirect($"/s/{token}/index.html");
}).RequireRateLimiting("unlock").AllowAnonymous();

app.MapGet("/s/{token}/{**rest}", async (HttpContext ctx, AppDb db, IDataProtectionProvider dp, string token, string? rest) =>
{
    var link = await db.ShareLinks.FirstOrDefaultAsync(l => l.Token == token);
    var check = CheckLink(link);
    if (check != null) return check;

    if (link!.PasswordHash != null && !HasValidUnlock(ctx, dp, link))
        return Results.Content(Pages.SharePassword(token, BusinessName(link.Slug), null), "text/html");

    // Count a view when the landing page is opened, debounced per browser for 30 minutes
    // so reloads and in-site navigation don't burn the view limit.
    var isLanding = string.IsNullOrEmpty(rest) || rest == "index.html";
    if (isLanding)
    {
        var seenCookie = "avos_sv_" + link.Id.ToString("N")[..8];
        if (!ctx.Request.Cookies.ContainsKey(seenCookie))
        {
            link.ViewCount++;
            link.LastViewedAt = DateTimeOffset.UtcNow;
            await db.SaveChangesAsync();
            ctx.Response.Cookies.Append(seenCookie, "1", new CookieOptions
            {
                HttpOnly = true, SameSite = SameSiteMode.Lax, MaxAge = TimeSpan.FromMinutes(30),
                Secure = ctx.Request.IsHttps, Path = $"/s/{token}",
            });
        }
    }

    return ServePreviewFile(link.Slug, rest);
}).AllowAnonymous();

app.Run();

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

IResult ServePreviewFile(string slug, string? rest)
{
    if (string.IsNullOrEmpty(rest)) rest = "index.html";
    var slugDir = Path.GetFullPath(Path.Combine(previewsRoot, slug));
    if (!slugDir.StartsWith(previewsRoot + Path.DirectorySeparatorChar) || !Directory.Exists(slugDir))
        return Results.NotFound();
    var file = Path.GetFullPath(Path.Combine(slugDir, rest));
    if (!file.StartsWith(slugDir + Path.DirectorySeparatorChar) || !File.Exists(file))
        return Results.NotFound();
    if (!contentTypes.TryGetContentType(file, out var contentType))
        contentType = "application/octet-stream";
    return Results.File(file, contentType);
}

IResult? CheckLink(ShareLink? link)
{
    if (link == null)
        return Results.Content(Pages.ShareGone("Dieser Link existiert nicht (mehr)."), "text/html",
            statusCode: StatusCodes.Status404NotFound);
    var status = link.Status(DateTimeOffset.UtcNow);
    return status switch
    {
        "aktiv" => null,
        "widerrufen" => Results.Content(Pages.ShareGone("Dieser Link wurde deaktiviert."), "text/html",
            statusCode: StatusCodes.Status410Gone),
        "abgelaufen" => Results.Content(Pages.ShareGone("Dieser Link ist abgelaufen."), "text/html",
            statusCode: StatusCodes.Status410Gone),
        _ => Results.Content(Pages.ShareGone("Dieser Link hat sein Ansichts-Limit erreicht."), "text/html",
            statusCode: StatusCodes.Status410Gone),
    };
}

string BusinessName(string slug) =>
    BusinessCatalog.Load(previewsRoot).FirstOrDefault(b => b.Slug == slug)?.Name ?? slug;

void SetUnlockCookie(HttpContext ctx, IDataProtectionProvider dp, ShareLink link)
{
    var protector = dp.CreateProtector("share-unlock");
    var ttl = TimeSpan.FromHours(24);
    if (link.ExpiresAt is { } exp)
    {
        var remaining = exp - DateTimeOffset.UtcNow;
        if (remaining < ttl) ttl = remaining;
    }
    var payload = protector.Protect($"{link.Id:N}|{DateTimeOffset.UtcNow.Add(ttl).ToUnixTimeSeconds()}");
    ctx.Response.Cookies.Append("avos_su_" + link.Id.ToString("N")[..8], payload, new CookieOptions
    {
        HttpOnly = true, SameSite = SameSiteMode.Lax, MaxAge = ttl,
        Secure = ctx.Request.IsHttps, Path = $"/s/{link.Token}",
    });
}

bool HasValidUnlock(HttpContext ctx, IDataProtectionProvider dp, ShareLink link)
{
    if (!ctx.Request.Cookies.TryGetValue("avos_su_" + link.Id.ToString("N")[..8], out var value))
        return false;
    try
    {
        var payload = dp.CreateProtector("share-unlock").Unprotect(value);
        var parts = payload.Split('|');
        return parts.Length == 2
            && parts[0] == link.Id.ToString("N")
            && long.TryParse(parts[1], out var untilUnix)
            && DateTimeOffset.FromUnixTimeSeconds(untilUnix) > DateTimeOffset.UtcNow;
    }
    catch
    {
        return false;
    }
}

static object ShareDto(ShareLink l, string baseUrl, DateTimeOffset now) => new
{
    id = l.Id,
    slug = l.Slug,
    label = l.Label,
    url = $"{baseUrl}/s/{l.Token}",
    hasPassword = l.PasswordHash != null,
    maxViews = l.MaxViews,
    viewCount = l.ViewCount,
    expiresAt = l.ExpiresAt,
    createdAt = l.CreatedAt,
    createdBy = l.CreatedBy,
    revokedAt = l.RevokedAt,
    lastViewedAt = l.LastViewedAt,
    status = l.Status(now),
};

public record CreateShareRequest(
    string Slug, string? Label, string? Password, int? MaxViews,
    int? ExpiresInDays, DateTimeOffset? ExpiresAt);
public record SsoExchangeRequest(string Code, string RedirectUri);
public record DevLoginRequest(string? Password);
public record RefreshRequest(string? RefreshToken);

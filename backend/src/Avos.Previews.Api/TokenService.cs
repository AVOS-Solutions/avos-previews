using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;
using Microsoft.IdentityModel.Tokens;

namespace Avos.Previews;

/// <summary>JWT issuing, mirroring avos-erp's TokenService: HS256 on Jwt:Key,
/// access 15 minutes, refresh 7 days (hashed at rest, rotated on refresh).</summary>
public class TokenService(IConfiguration config)
{
    private static readonly TimeSpan AccessTokenLifetime = TimeSpan.FromMinutes(15);
    public static readonly TimeSpan RefreshTokenLifetime = TimeSpan.FromDays(7);

    public (string Token, DateTimeOffset ExpiresAt) CreateAccessToken(string userId, string email, string fullName)
    {
        var key = config["Jwt:Key"] ?? throw new InvalidOperationException("Jwt:Key not configured.");
        var issuer = config["Jwt:Issuer"] ?? throw new InvalidOperationException("Jwt:Issuer not configured.");
        var audience = config["Jwt:Audience"] ?? throw new InvalidOperationException("Jwt:Audience not configured.");

        var expiresAt = DateTimeOffset.UtcNow.Add(AccessTokenLifetime);
        var claims = new List<Claim>
        {
            new(JwtRegisteredClaimNames.Sub, userId),
            new(JwtRegisteredClaimNames.Email, email),
            new(ClaimTypes.Name, fullName),
            new(ClaimTypes.Role, "Staff"),
        };

        var signingKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(key));
        var credentials = new SigningCredentials(signingKey, SecurityAlgorithms.HmacSha256);
        var token = new JwtSecurityToken(
            issuer: issuer, audience: audience, claims: claims,
            expires: expiresAt.UtcDateTime, signingCredentials: credentials);
        return (new JwtSecurityTokenHandler().WriteToken(token), expiresAt);
    }

    public static string GenerateRefreshToken() =>
        Convert.ToBase64String(RandomNumberGenerator.GetBytes(32));

    public static string HashRefreshToken(string token) =>
        Convert.ToBase64String(SHA256.HashData(Encoding.UTF8.GetBytes(token)));
}

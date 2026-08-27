using System.Security.Cryptography;
using System.Text;
using System.Text.Json;
using Microsoft.EntityFrameworkCore;

namespace Avos.Previews;

/// <summary>A share link for one business preview. The raw token appears in the share URL;
/// it is stored in plaintext so links can be re-copied from the admin UI later.
/// The optional password is stored as a PBKDF2 hash only.</summary>
public class ShareLink
{
    public Guid Id { get; set; }
    public string Token { get; set; } = "";
    public string Slug { get; set; } = "";
    public string? Label { get; set; }
    public string? PasswordHash { get; set; }
    public int? MaxViews { get; set; }
    public int ViewCount { get; set; }
    public DateTimeOffset? ExpiresAt { get; set; }
    public DateTimeOffset CreatedAt { get; set; }
    public string CreatedBy { get; set; } = "";
    public DateTimeOffset? RevokedAt { get; set; }
    public DateTimeOffset? LastViewedAt { get; set; }

    public string Status(DateTimeOffset now) =>
        RevokedAt != null ? "widerrufen"
        : ExpiresAt != null && ExpiresAt <= now ? "abgelaufen"
        : MaxViews != null && ViewCount >= MaxViews ? "aufgebraucht"
        : "aktiv";

    public bool IsUsable(DateTimeOffset now) => Status(now) == "aktiv";
}


/// <summary>One rotating refresh token per login session, stored hashed (ERP pattern).
/// Identity claims are denormalized onto the row so refresh can re-issue an access token
/// without a local user table — identity lives in avos-licensing.</summary>
public class RefreshToken
{
    public Guid Id { get; set; }
    public string UserId { get; set; } = "";
    public string Email { get; set; } = "";
    public string FullName { get; set; } = "";
    public string TokenHash { get; set; } = "";
    public DateTimeOffset ExpiresAt { get; set; }
    public DateTimeOffset CreatedAt { get; set; }
    public DateTimeOffset? RevokedAt { get; set; }

    public bool IsActive => RevokedAt == null && ExpiresAt > DateTimeOffset.UtcNow;
}

public class AppDb(DbContextOptions<AppDb> options) : DbContext(options)
{
    public DbSet<ShareLink> ShareLinks => Set<ShareLink>();
    public DbSet<RefreshToken> RefreshTokens => Set<RefreshToken>();

    protected override void OnModelCreating(ModelBuilder b)
    {
        b.Entity<ShareLink>(e =>
        {
            e.HasIndex(x => x.Token).IsUnique();
            e.HasIndex(x => x.Slug);
        });
        b.Entity<RefreshToken>(e => e.HasIndex(x => x.TokenHash).IsUnique());
    }
}

public record Business(
    int Num, string Slug, string Name, string Category,
    string Region, string Location, string Description, string? OldWebsite);

public static class BusinessCatalog
{
    private static List<Business>? _cache;

    public static List<Business> Load(string previewsRoot)
    {
        if (_cache != null) return _cache;
        var path = Path.Combine(previewsRoot, "..", "businesses.json");
        if (!File.Exists(path)) path = Path.Combine(previewsRoot, "businesses.json");
        var json = File.ReadAllText(path);
        _cache = JsonSerializer.Deserialize<List<Business>>(json,
            new JsonSerializerOptions { PropertyNameCaseInsensitive = true }) ?? [];
        return _cache;
    }
}

public static class Tokens
{
    /// <summary>URL-safe random token, 160 bits.</summary>
    public static string NewToken()
    {
        var bytes = RandomNumberGenerator.GetBytes(20);
        return Convert.ToBase64String(bytes).Replace("+", "-").Replace("/", "_").TrimEnd('=');
    }

    public static string HashPassword(string password)
    {
        var salt = RandomNumberGenerator.GetBytes(16);
        var hash = Rfc2898DeriveBytes.Pbkdf2(password, salt, 100_000, HashAlgorithmName.SHA256, 32);
        return $"{Convert.ToBase64String(salt)}.{Convert.ToBase64String(hash)}";
    }

    public static bool VerifyPassword(string password, string stored)
    {
        var parts = stored.Split('.');
        if (parts.Length != 2) return false;
        var salt = Convert.FromBase64String(parts[0]);
        var expected = Convert.FromBase64String(parts[1]);
        var actual = Rfc2898DeriveBytes.Pbkdf2(password, salt, 100_000, HashAlgorithmName.SHA256, 32);
        return CryptographicOperations.FixedTimeEquals(actual, expected);
    }

    public static string Sha256(string value) =>
        Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(value))).ToLowerInvariant();
}

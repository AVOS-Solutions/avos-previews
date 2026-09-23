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

/// <summary>One preview site. <paramref name="AddedOn"/> is the ISO date (yyyy-MM-dd) on which
/// the preview folder was first committed, baked into the catalog by scripts/set-added-dates.py.
/// The runtime image carries no .git and every file shares the image build time, so the date
/// cannot be recovered here — a preview the catalog does not list therefore has none.</summary>
public record Business(
    int Num, string Slug, string Name, string Category,
    string Region, string Location, string Description, string? OldWebsite,
    string? Grade = null, double? Score = null, string? PitchHook = null,
    int? PriceLow = null, int? PriceHigh = null,
    string? Phone = null, string? Email = null, string? ContactPerson = null,
    List<string>? Pages = null, string Dataset = "relaunch", string? AddedOn = null);

/// <summary>One folder of preview sites (one subfolder per slug) plus the catalog file that
/// describes them. Dir is an absolute path without a trailing separator.</summary>
public sealed record PreviewRoot(string Dir, string CatalogPath, string Dataset);

public static class BusinessCatalog
{
    private static readonly JsonSerializerOptions JsonOptions = new() { PropertyNameCaseInsensitive = true };
    private static List<Business>? _cache;

    public static List<Business> Load(IReadOnlyList<PreviewRoot> roots)
    {
        if (_cache != null) return _cache;
        var all = new List<Business>();
        var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
        foreach (var root in roots)
        {
            foreach (var b in ReadCatalog(root))
                if (seen.Add(b.Slug)) all.Add(b with { Dataset = root.Dataset });
            // A preview folder no catalog lists is still a preview. Surfacing it with a
            // slug-derived name beats letting it sit on disk invisible to the dashboard.
            foreach (var slug in PreviewFolders(root.Dir))
                if (seen.Add(slug)) all.Add(FromFolder(slug, root.Dataset));
        }
        _cache = all;
        return _cache;
    }

    /// <summary>Absolute path of the folder holding <paramref name="slug"/>'s files, or null
    /// when no root has it. Rejects slugs that would escape a root.</summary>
    public static string? ResolveFolder(IReadOnlyList<PreviewRoot> roots, string slug)
    {
        foreach (var root in roots)
        {
            var dir = Path.GetFullPath(Path.Combine(root.Dir, slug));
            if (dir.StartsWith(root.Dir + Path.DirectorySeparatorChar, StringComparison.Ordinal)
                && Directory.Exists(dir))
                return dir;
        }
        return null;
    }

    private static List<Business> ReadCatalog(PreviewRoot root)
    {
        if (!File.Exists(root.CatalogPath)) return [];
        return JsonSerializer.Deserialize<List<Business>>(File.ReadAllText(root.CatalogPath), JsonOptions) ?? [];
    }

    private static IEnumerable<string> PreviewFolders(string dir)
    {
        if (!Directory.Exists(dir)) return [];
        return new DirectoryInfo(dir).EnumerateDirectories()
            .Where(d => File.Exists(Path.Combine(d.FullName, "index.html")))
            .Select(d => d.Name)
            .Order(StringComparer.Ordinal);
    }

    private static Business FromFolder(string slug, string dataset)
    {
        var rest = slug;
        var dash = rest.IndexOf('-');
        var num = 0;
        if (dash > 0 && int.TryParse(rest[..dash], out var parsed))
        {
            num = parsed;
            rest = rest[(dash + 1)..];
        }
        var name = string.Join(' ', rest.Split('-', StringSplitOptions.RemoveEmptyEntries)
            .Select(w => char.ToUpperInvariant(w[0]) + w[1..]));
        return new Business(num, slug, name.Length > 0 ? name : slug, "", "", "", "", null, Dataset: dataset);
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

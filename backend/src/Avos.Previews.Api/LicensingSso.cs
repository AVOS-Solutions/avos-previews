using System.Net.Http.Json;
using System.Text.Json.Serialization;

namespace Avos.Previews;

/// <summary>SSO client for avos-licensing, mirroring the flow documented in
/// avos-licensing SsoController: browser redirect to /api/sso/authorize, then a
/// server-to-server code exchange at /api/sso/token. The exchange returns an identity
/// assertion (no licensing token); this app mints its own session from it.
/// Contract (house rule): if Licensing:BaseUrl is blank the client is silently unusable —
/// never a startup failure.</summary>
public class LicensingSso(HttpClient http, IConfiguration config)
{
    public string? BaseUrl => Trimmed(config["Licensing:BaseUrl"]);
    public string? ClientId => Trimmed(config["Licensing:ClientId"]);
    private string? ClientSecret => Trimmed(config["Licensing:ClientSecret"]);

    public bool Configured =>
        !string.IsNullOrWhiteSpace(BaseUrl) &&
        !string.IsNullOrWhiteSpace(ClientId) &&
        !string.IsNullOrWhiteSpace(ClientSecret);

    private static string? Trimmed(string? v) => string.IsNullOrWhiteSpace(v) ? null : v.TrimEnd('/');

    public string AuthorizeUrl(string redirectUri, string state) =>
        $"{BaseUrl}/api/sso/authorize?client_id={Uri.EscapeDataString(ClientId!)}" +
        $"&redirect_uri={Uri.EscapeDataString(redirectUri)}&state={Uri.EscapeDataString(state)}";

    public async Task<SsoIdentity?> ExchangeCodeAsync(string code, string redirectUri, CancellationToken ct)
    {
        var resp = await http.PostAsJsonAsync($"{BaseUrl}/api/sso/token", new
        {
            clientId = ClientId,
            clientSecret = ClientSecret,
            code,
            redirectUri,
        }, ct);
        if (!resp.IsSuccessStatusCode) return null;
        return await resp.Content.ReadFromJsonAsync<SsoIdentity>(ct);
    }
}

public record SsoIdentity(
    [property: JsonPropertyName("userId")] string UserId,
    [property: JsonPropertyName("email")] string Email,
    [property: JsonPropertyName("fullName")] string? FullName,
    [property: JsonPropertyName("hasActiveLicense")] bool HasActiveLicense,
    [property: JsonPropertyName("roles")] string[]? Roles)
{
    public bool IsAuthorized => (Roles?.Contains("Admin") ?? false) || HasActiveLicense;
}

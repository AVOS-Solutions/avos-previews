using System.Text.Encodings.Web;

namespace Avos.Previews;

/// <summary>Server-rendered gate pages (login, share password, share errors) in the AVOS theme.
/// The admin UI itself lives in wwwroot/app/.</summary>
public static class Pages
{
    private static string E(string? s) => HtmlEncoder.Default.Encode(s ?? "");

    public const string BrandSvg =
        "<svg width=\"26\" height=\"26\" viewBox=\"0 0 24 24\" aria-hidden=\"true\">" +
        "<rect x=\"3.5\" y=\"3.5\" width=\"17\" height=\"17\" rx=\"2.5\" fill=\"#161225\" />" +
        "<path d=\"M4.23 4.23A2.5 2.5 0 0 1 6 3.5H18A2.5 2.5 0 0 1 20.5 6V18A2.5 2.5 0 0 1 19.77 19.77Z\" fill=\"#e0a437\" opacity=\"0.22\" />" +
        "<g fill=\"none\" stroke=\"#e0a437\" stroke-width=\"1.25\" stroke-linecap=\"round\" stroke-linejoin=\"round\">" +
        "<rect x=\"7.1\" y=\"10.1\" width=\"9.8\" height=\"6.2\" rx=\"1.2\" />" +
        "<path d=\"M10.2 10.1v-0.8a1.4 1.4 0 0 1 1.4-1.4h0.8a1.4 1.4 0 0 1 1.4 1.4v0.8\" />" +
        "<path d=\"M11.2 12.9h1.6\" stroke=\"#f4c04d\" stroke-width=\"0.75\" />" +
        "</g></svg>";

    private static string BrandRow =>
        "<div style=\"display:flex;align-items:center;gap:10px;margin-bottom:18px\">" + BrandSvg +
        "<span class=\"brand-word mono\">AVOS <span class=\"muted\">PREVIEWS</span></span></div>";

    private static string Shell(string title, string body) =>
        "<!DOCTYPE html>\n<html lang=\"de\">\n<head>\n" +
        "<meta charset=\"UTF-8\">\n" +
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n" +
        "<meta name=\"robots\" content=\"noindex, nofollow\">\n" +
        $"<title>{E(title)} · AVOS Previews</title>\n" +
        "<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">\n" +
        "<link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>\n" +
        "<link href=\"https://fonts.googleapis.com/css2?family=Fragment+Mono:ital@0;1&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap\" rel=\"stylesheet\">\n" +
        "<link rel=\"stylesheet\" href=\"/assets/avos.css\">\n" +
        "<link rel=\"icon\" href=\"/favicon.ico\">\n" +
        "</head>\n<body>\n" + body +
        "\n<footer class=\"footer\"><div class=\"wrap\">AVOS Previews · AVOS Solutions</div></footer>\n" +
        "</body>\n</html>";

    private static string ErrorBox(string? error) =>
        error == null ? "" : $"<div class=\"form-error\">{E(error)}</div>";

    public static string Login(bool ssoConfigured, bool devLogin, string? error)
    {
        var ssoBlock = ssoConfigured
            ? "<a class=\"btn btn-primary\" style=\"width:100%\" href=\"/auth/sso/start\">Mit AVOS Licensing anmelden</a>"
            : "<div class=\"form-error\">AVOS Licensing ist nicht konfiguriert (Licensing__BaseUrl / ClientId / ClientSecret setzen).</div>";
        var devBlock = !devLogin ? "" :
            "<form method=\"post\" action=\"/auth/dev-login\" style=\"margin-top:18px;border-top:1px solid var(--line);padding-top:18px\">" +
            "<label class=\"label eyebrow\" for=\"pw\">Dev-Login (nur Entwicklung)</label>" +
            "<div class=\"form-row\"><input class=\"input\" id=\"pw\" name=\"password\" type=\"password\" placeholder=\"Dev-Passwort\" required></div>" +
            "<button class=\"btn btn-secondary\" style=\"width:100%\" type=\"submit\">Anmelden</button></form>";
        return Shell("Anmeldung",
            "<main class=\"gate\"><div class=\"card\">" + BrandRow +
            "<h1>Anmeldung</h1>" +
            "<p class=\"sub\">Zugang für das AVOS-Team über AVOS Licensing.</p>" +
            ErrorBox(error) + ssoBlock + devBlock +
            "</div></main>");
    }

    public static string SharePassword(string token, string businessName, string? error) =>
        Shell("Geschützte Vorschau",
            "<main class=\"gate\"><div class=\"card\">" + BrandRow +
            "<h1>Geschützte Vorschau</h1>" +
            $"<p class=\"sub\">Die Design-Vorschau für <strong>{E(businessName)}</strong> ist passwortgeschützt.</p>" +
            ErrorBox(error) +
            $"<form method=\"post\" action=\"/s/{Uri.EscapeDataString(token)}/unlock\">" +
            "<div class=\"form-row\"><input class=\"input\" name=\"password\" type=\"password\" placeholder=\"Passwort\" autofocus required></div>" +
            "<button class=\"btn btn-primary\" style=\"width:100%\" type=\"submit\">Vorschau öffnen</button>" +
            "</form></div></main>");

    public static string ShareGone(string reason) =>
        Shell("Link nicht verfügbar",
            "<main class=\"gate\"><div class=\"card\">" + BrandRow +
            "<h1>Link nicht verfügbar</h1>" +
            $"<p class=\"sub\">{E(reason)}</p>" +
            "<p class=\"small muted\">Bitte wenden Sie sich an Ihren Ansprechpartner bei AVOS Solutions, um einen neuen Link zu erhalten.</p>" +
            "</div></main>");
}

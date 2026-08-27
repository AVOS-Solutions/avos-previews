# AVOS Previews — Deployment

Gleiche Topologie wie avos-erp: `.NET 10 API + Next.js 16 Frontend + PostgreSQL 17`,
pro Container ein interner Caddy-TLS-Sidecar, angebunden an das geteilte Docker-Netz
`avos-edge`, vor dem eine gemeinsame Edge-Caddy-Instanz `:80/:443` besitzt.

## 1. Voraussetzungen

- Server mit Docker (wie beim ERP: Ubuntu 24.04, Docker via get.docker.com)
- Geteiltes Edge-Netz existiert: `docker network create avos-edge` (einmal pro Host)
- DNS-A-Record für die gewünschte Domain (z. B. `previews.avos-solutions.com`) auf den Server

## 2. App in avos-licensing registrieren (einmalig, als Admin)

1. `POST /api/applications` mit
   `{"name":"AVOS Previews","slug":"avos-previews","description":"Design-Vorschauen & Share-Links","platform":"Web"}`
   → die zurückgegebene `id` ist die **Client-ID**.
2. `PUT /api/applications/{id}/sso/redirect-uris` mit
   `{"redirectUris":["https://<DOMAIN>/auth/callback"]}` (exakte Strings, keine Wildcards).
3. `POST /api/applications/{id}/sso/generate-secret` → **Client-Secret** (wird nur einmal angezeigt).
4. Zugriff: Licensing-`Admin`-Konten kommen immer hinein; alle anderen brauchen eine **aktive
   Lizenz** für diese Application (`hasActiveLicense` aus dem SSO-Token-Exchange).

## 3. Konfiguration

`.env` auf dem Server (chmod 600, nie ins Git):

```
DOMAIN=previews.avos-solutions.com
POSTGRES_PASSWORD=<openssl rand -base64 24>
JWT_KEY=<openssl rand -base64 48>
LICENSING_BASE_URL=https://<licensing-domain>       # öffentliche Licensing-Origin; /api/sso/* ist dort edge-geroutet
LICENSING_CLIENT_ID=<id aus Schritt 2.1>
LICENSING_CLIENT_SECRET=<secret aus Schritt 2.3>
```

## 4. Deploy / Update

```
docker compose -f docker-compose.prod.yml --env-file .env up -d --build
```

Migrations/Schema entstehen automatisch beim ersten API-Start (`EnsureCreated`).
Die statischen Preview-Sites und `businesses.json` werden ins API-Image gebacken —
nach Änderungen an `previews/` einfach neu deployen.

## 5. Edge-Routing

Die Blöcke aus `Caddyfile` (Repo-Root, Referenz — wird nicht vom Compose gelesen) in die
gemeinsame Edge-Caddy-Konfiguration übernehmen:

- `/s/*`, `/api/public/*`, `/assets/*` → `https://previews-api:8443`
- alles andere → `https://previews-frontend:3443`
  (mit `header_up X-Forwarded-Host …`, sonst blockt Next.js Server Actions — im Sidecar bereits gesetzt)

Alle übrigen `/api/*`-Routen sind von außen bewusst nicht erreichbar; nur der
Next.js-Server spricht mit der API (`API_INTERNAL_URL=https://previews-api:8443`).

## 6. Backups

Zustand liegt in zwei Volumes: `pgdata` (Share-Links, Refresh-Tokens) und `apidata`
(Data-Protection-Keys für Unlock-Cookies). `pg_dump` wie beim ERP; `apidata` ist
verschmerzbar (Verlust heißt nur: Besucher passwortgeschützter Links müssen das
Passwort erneut eingeben).

## 7. Lokale Entwicklung

Ohne Docker (SQLite-Fallback, Dev-Login):

```
# API
cd backend/src/Avos.Previews.Api
ASPNETCORE_ENVIRONMENT=Development Auth__DevPassword=dev \
  Jwt__Key=dev-only-jwt-key-0123456789-0123456789-01 \
  App__PublicUrl=http://localhost:5085 \
  dotnet run --urls http://localhost:5085

# Frontend
cd frontend
DEV_LOGIN_ENABLED=1 API_INTERNAL_URL=http://localhost:5085 npm run dev
```

Oder mit Docker: `docker compose up --build` (Frontend auf :3005, API auf :5085,
Dev-Login-Passwort `dev`). Der Dev-Login existiert nur bei
`ASPNETCORE_ENVIRONMENT=Development` — in Produktion gibt es ausschließlich den
Licensing-SSO-Weg.

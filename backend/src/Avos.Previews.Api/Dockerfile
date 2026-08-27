# Build context is the repository root (see docker-compose*.yml) so the image can bundle the
# static preview sites and businesses.json alongside the API.
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

COPY backend/src/Avos.Previews.Api/Avos.Previews.Api.csproj backend/src/Avos.Previews.Api/
RUN dotnet restore backend/src/Avos.Previews.Api/Avos.Previews.Api.csproj

COPY backend/src/ backend/src/
RUN dotnet publish backend/src/Avos.Previews.Api/Avos.Previews.Api.csproj -c Release -o /app --no-restore

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS runtime
WORKDIR /app
RUN useradd --create-home appuser
COPY --from=build /app .
COPY --chown=appuser:appuser previews/ /app/previews/
COPY --chown=appuser:appuser businesses.json /app/businesses.json
# Internal-TLS sidecar (see docker/Caddyfile) — terminates HTTPS on 8443 for container-to-container
# traffic within the Docker network, in front of the plain-HTTP Kestrel process on 8080.
COPY --from=caddy:2-alpine /usr/bin/caddy /usr/local/bin/caddy
COPY --chown=appuser:appuser backend/src/Avos.Previews.Api/docker/Caddyfile backend/src/Avos.Previews.Api/docker/entrypoint.sh docker/
RUN chmod +x docker/entrypoint.sh && mkdir -p /app/data && chown appuser:appuser /app/data
ENV HOME=/home/appuser
USER appuser

# businesses.json sits next to /app/previews, matching BusinessCatalog's lookup.
ENV Previews__Root=/app/previews
ENV App__DataDir=/app/data

EXPOSE 8080
EXPOSE 8443
# All-interfaces HTTP bind by default so the dev compose works without the sidecar;
# docker-compose.prod.yml overrides this to loopback-only behind the 8443 sidecar.
ENV ASPNETCORE_URLS=http://+:8080
ENTRYPOINT ["/app/docker/entrypoint.sh"]

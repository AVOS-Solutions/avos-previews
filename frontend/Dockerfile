FROM node:22-slim AS build
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:22-slim AS runtime
WORKDIR /app
ENV NODE_ENV=production
RUN useradd --create-home appuser

COPY --from=build /app/public ./public
COPY --from=build --chown=appuser:appuser /app/.next/standalone ./
COPY --from=build --chown=appuser:appuser /app/.next/static ./.next/static
# Internal-TLS sidecar (see docker/Caddyfile) — terminates HTTPS on 3443 for container-to-container
# traffic within the Docker network, in front of the plain-HTTP Next.js process on 3000.
COPY --from=caddy:2-alpine /usr/bin/caddy /usr/local/bin/caddy
COPY --chown=appuser:appuser docker/Caddyfile docker/entrypoint.sh docker/
RUN chmod +x docker/entrypoint.sh
ENV HOME=/home/appuser

USER appuser
EXPOSE 3000
EXPOSE 3443
# Bound to all interfaces (HOSTNAME unset) by default for the dev compose;
# docker-compose.prod.yml overrides HOSTNAME to loopback-only behind the 3443 sidecar.
ENV PORT=3000
ENTRYPOINT ["/app/docker/entrypoint.sh"]

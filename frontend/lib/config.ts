import { Agent } from "undici";

export const API_URL = process.env.API_INTERNAL_URL ?? "http://localhost:5085";

// In production API_URL points at the api container's Caddy sidecar (see
// backend/src/Avos.Erp.Api/Dockerfile and docker-compose.prod.yml), which terminates TLS with a
// `tls internal` self-signed cert. That cert isn't in Node's trusted root store, and it doesn't
// need to be: trust for this hop comes from the Docker private network boundary, not a CA chain —
// the same way the plaintext HTTP link it replaces was never validated by a CA either. Every
// server-side fetch to the internal API (lib/api.ts, proxy.ts, the auth route handlers) passes
// this as its `dispatcher` so only calls to our own internal API skip verification — every other
// outbound fetch this server makes stays fully verified.
export const internalApiDispatcher = new Agent({ connect: { rejectUnauthorized: false } });

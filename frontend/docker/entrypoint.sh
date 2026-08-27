#!/bin/bash
# Runs the Next.js standalone server and its internal-TLS Caddy sidecar as siblings in the same
# container (standalone output can't be wrapped in a custom HTTPS server). If either process
# exits, the other is killed and the container exits with the failing process's status.
set -e

node server.js &
node_pid=$!

caddy run --config /app/docker/Caddyfile --adapter caddyfile &
caddy_pid=$!

wait -n "$node_pid" "$caddy_pid"
exit_code=$?

kill "$node_pid" "$caddy_pid" 2>/dev/null || true
exit "$exit_code"

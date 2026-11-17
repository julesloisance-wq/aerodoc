#!/usr/bin/env bash
# Start the Docker daemon if it is not running (needed in ephemeral cloud sandboxes,
# where the machine can restart). On a normal machine Docker is already running: no-op.
set -euo pipefail
if docker info >/dev/null 2>&1; then exit 0; fi
if [ "$(id -u)" -eq 0 ] && command -v dockerd >/dev/null 2>&1; then
  echo "Starting Docker daemon..."
  (setsid nohup dockerd >/var/log/dockerd.log 2>&1 </dev/null &)
  for _ in $(seq 1 30); do docker info >/dev/null 2>&1 && exit 0; sleep 1; done
fi
echo "Docker is not running. Start Docker Desktop (or the Docker service) and retry." >&2
exit 1

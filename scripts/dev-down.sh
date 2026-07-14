#!/usr/bin/env bash
# Stage 0A dev infra DOWN — kills ONLY the PIDs we recorded.
set -euo pipefail
BASE="$(cd "$(dirname "$0")/.." && pwd)"
shopt -s nullglob
for f in "$BASE"/.run/*.pid; do
  pid="$(cat "$f" 2>/dev/null || true)"
  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
    kill "$pid" && echo "killed $(basename "$f" .pid) (pid $pid)"
  else
    echo "$(basename "$f" .pid) not running"
  fi
  rm -f "$f"
done

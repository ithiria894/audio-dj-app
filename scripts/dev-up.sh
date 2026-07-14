#!/usr/bin/env bash
# Stage 0A dev infra UP — reproducible, PID-tracked. No systemd/docker.
# Trusted LAN only. Do NOT port-forward 7880-7882 / 8790.
set -euo pipefail
BASE="$(cd "$(dirname "$0")/.." && pwd)"
LKBIN="$HOME/.local/bin/livekit-server"
mkdir -p "$BASE/.run" "$BASE/logs"
LAN_IP="$(hostname -I | tr ' ' '\n' | grep -E '^(192|10|172)\.' | head -1)"

start() { # name pidfile logfile cmd...
  local name="$1" pidf="$2" logf="$3"; shift 3
  if [ -f "$pidf" ] && kill -0 "$(cat "$pidf" 2>/dev/null)" 2>/dev/null; then
    echo "$name already running (pid $(cat "$pidf"))"; return
  fi
  nohup "$@" > "$logf" 2>&1 &
  echo $! > "$pidf"
  echo "$name started pid $(cat "$pidf") -> $logf"
}

start livekit "$BASE/.run/livekit.pid" "$BASE/logs/livekit.log" "$LKBIN" --dev --bind 0.0.0.0
sleep 2
start token "$BASE/.run/token-api.pid" "$BASE/logs/token-api.log" \
  env LK_URL="ws://$LAN_IP:7880" node "$BASE/services/api/dev-token.mjs"
sleep 1
echo "----"
echo "LiveKit : ws://$LAN_IP:7880  (devkey/secret)"
echo "Token   : http://$LAN_IP:8790/dev/token?role=dj|listener"
echo "Listener page (Gate1): http://localhost:5173 (laptop) / http://$LAN_IP:5173 (phone)"

#!/usr/bin/env bash
# Stage 0A dev infra HEALTH — actually requests both endpoints.
BASE="$(cd "$(dirname "$0")/.." && pwd)"
LAN_IP="$(hostname -I | tr ' ' '\n' | grep -E '^(192|10|172)\.' | head -1)"
echo "== livekit :7880 =="
curl -s -o /dev/null -w "  http %{http_code}\n" "http://localhost:7880" || echo "  DOWN"
echo "== token :8790 =="
curl -s "http://localhost:8790/dev/token?role=listener&identity=healthcheck" | head -c 220; echo
echo "== pids =="
for f in "$BASE"/.run/*.pid; do [ -f "$f" ] && echo "  $(basename "$f" .pid): $(cat "$f") $(kill -0 "$(cat "$f")" 2>/dev/null && echo alive || echo DEAD)"; done
echo "LAN: ws://$LAN_IP:7880 | http://$LAN_IP:8790/dev/token"

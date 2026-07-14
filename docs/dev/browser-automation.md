# Dev note — Browser automation via Chrome CDP

Development-tooling knowledge (not product architecture). Used to verify the web listener headlessly (`scripts/cdp.py`).

## Setup
- Chrome DevTools Protocol endpoint: **`localhost:9223`** (dedicated agent Chrome, port file `~/.config/agent-chrome/DevToolsActivePort`).
- The Python `websocket-client` handshake **must pass `suppress_origin=True`**. Chrome rejects a CDP WebSocket that carries a default `Origin` header (`403 Rejected an incoming WebSocket connection ... Use --remote-allow-origins`). Sending no `Origin` is accepted.
- Objective PCM / AudioWorklet analysis must run over a **secure context**: use `http://localhost:5173` (localhost dev exemption). `http://<LAN-IP>:5173` is **not** a secure context, so AudioWorklet/getUserMedia are unavailable there — use the LAN URL only for subjective listening on a second phone.

## 🚨 Security red line
- **Port 9223 (Chrome remote debugging) must remain bound to `localhost` only. Never expose it to the LAN or the Internet.** Anyone who can reach it can drive the browser session (read cookies, act as the logged-in user).
- Same for the Stage 0A dev servers (`7880-7882` LiveKit, `8790` token): trusted LAN only, **no router port-forwarding**.

## Usage
```
uv run --with websocket-client python3 scripts/cdp.py "http://localhost:5173" "JSON.stringify(window.__gate1||{})" 8
```
Opens a fresh tab, waits, evaluates the expression, prints the JSON result, closes the tab.

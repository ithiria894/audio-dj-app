// Stage 0A dev token endpoint (control plane). DEVELOPMENT ONLY — trusted LAN, no port-forward.
// devkey/secret live ONLY here on the dev machine — never in the APK or web bundle.
// GET/POST /dev/token?identity=&role=dj|listener  -> { url, token, room, identity, role }
// Guardrails (per Nicole): fixed room, role allowlist, short TTL, sanitized identity.
import { AccessToken } from 'livekit-server-sdk'
import http from 'node:http'

const API_KEY = process.env.LK_API_KEY || 'devkey'
const API_SECRET = process.env.LK_API_SECRET || 'secret'
const LK_URL = process.env.LK_URL || 'ws://10.0.0.247:7880'
const PORT = process.env.PORT || 8790
const ROOM = 'stage0'                    // fixed — do not accept arbitrary rooms
const ROLES = new Set(['dj', 'listener']) // allowlist — no "admin" etc.
const TTL = '30m'

async function mint(identity, role) {
  const dj = role === 'dj'
  const at = new AccessToken(API_KEY, API_SECRET, { identity, ttl: TTL })
  at.addGrant({
    roomJoin: true,
    room: ROOM,
    canSubscribe: true,
    canPublish: dj,          // Stage 0A: DJ publishes, listener subscribe-only. (pass-DJ enforcement = Stage 1)
    canPublishData: true,
  })
  return await at.toJwt()
}

http.createServer(async (req, res) => {
  const u = new URL(req.url, 'http://x')
  res.setHeader('access-control-allow-origin', '*')
  res.setHeader('x-env', 'development-only')
  if (u.pathname !== '/dev/token') { res.statusCode = 404; return res.end('not found') }
  const role = u.searchParams.get('role') || 'listener'
  if (!ROLES.has(role)) { res.statusCode = 400; return res.end(JSON.stringify({ error: 'role must be dj|listener' })) }
  const raw = u.searchParams.get('identity') || ('u' + Math.floor(Math.random() * 1e6))
  const identity = raw.replace(/[^a-zA-Z0-9_-]/g, '').slice(0, 32) || 'anon'
  try {
    const token = await mint(identity, role)
    res.setHeader('content-type', 'application/json')
    res.end(JSON.stringify({ url: LK_URL, token, room: ROOM, identity, role }))
  } catch (e) {
    res.statusCode = 500; res.end(JSON.stringify({ error: String(e) }))
  }
}).listen(PORT, '0.0.0.0', () => console.log(`[DEV-ONLY] dev-token on :${PORT}  room=${ROOM}  LK_URL=${LK_URL}`))

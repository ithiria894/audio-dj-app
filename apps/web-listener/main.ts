// Stage 0A · Gate 1 — signaling / token / state-machine only. NO audio subscription yet.
// Verifies: fetch subscribe-only token -> connect room stage0 -> canPublish=false -> reconnect handling.
import { Room, RoomEvent } from 'livekit-client'

const TOKEN_API = (import.meta as any).env?.VITE_TOKEN_API || 'http://localhost:8790/dev/token'
const statusEl = document.getElementById('status')!
const detailEl = document.getElementById('detail')!
const room = new Room()

function report(extra: Record<string, unknown> = {}) {
  const lp = room.localParticipant
  const s = {
    state: room.state,
    canPublish: lp?.permissions?.canPublish ?? null,
    canSubscribe: lp?.permissions?.canSubscribe ?? null,
    identity: lp?.identity ?? null,
    remoteParticipants: room.remoteParticipants.size,
    identities: [...room.remoteParticipants.values()].map((p: any) => p.identity),
    remoteTracks: [...room.remoteParticipants.values()].reduce((n: number, p: any) => n + p.trackPublications.size, 0),
    ts: performance.now() | 0,
    ...extra,
  }
  ;(window as any).__gate1 = s
  statusEl.textContent = 'state: ' + s.state + (s.canPublish === false ? '  (canPublish=false ✓)' : '')
  statusEl.className = s.state === 'connected' ? 'ok' : ''
  detailEl.textContent = JSON.stringify(s, null, 2)
  console.log('[gate1]', JSON.stringify(s))
}

room
  .on(RoomEvent.ConnectionStateChanged, () => report())
  .on(RoomEvent.Disconnected, (r) => report({ note: 'disconnected', disconnectReason: r }))
  .on(RoomEvent.Reconnecting, () => report({ note: 'reconnecting' }))
  .on(RoomEvent.Reconnected, () => report({ note: 'reconnected' }))
  .on(RoomEvent.ParticipantConnected, (p) => report({ note: 'participant+ ' + p.identity }))
  .on(RoomEvent.ParticipantDisconnected, (p) => report({ note: 'participant- ' + p.identity }))

async function connect() {
  try {
    report({ note: 'fetching token' })
    const res = await fetch(`${TOKEN_API}?role=listener&identity=web-listener`)
    const { url, token } = await res.json()
    report({ note: 'connecting', url })
    await room.connect(url, token)
    report({ note: 'connected' })
  } catch (e) {
    report({ error: String(e) })
  }
}

document.getElementById('connectBtn')!.addEventListener('click', connect)
document.getElementById('disconnectBtn')!.addEventListener('click', () => room.disconnect())

// auto-connect so headless CDP verification can read window.__gate1
connect()

// Stage 0A · Gate 1 — signaling / token / state-machine only. NO audio subscription yet.
// Verifies: fetch subscribe-only token -> connect room stage0 -> canPublish=false -> reconnect handling.
import { Room, RoomEvent, Track } from 'livekit-client'

const TOKEN_API = (import.meta as any).env?.VITE_TOKEN_API || 'http://localhost:8790/dev/token'
const statusEl = document.getElementById('status')!
const detailEl = document.getElementById('detail')!
const room = new Room()

// Gate 3.0 instrumentation: remote audio RMS + track source/kind, exposed for CDP.
let remoteRmsDb = -120
let analyser: AnalyserNode | null = null
let audioCtx: AudioContext | null = null
const audioEls: HTMLAudioElement[] = []

function trackInfos() {
  const out: Array<Record<string, unknown>> = []
  for (const p of room.remoteParticipants.values())
    for (const pub of (p as any).trackPublications.values())
      out.push({ identity: (p as any).identity, source: pub.source, kind: pub.kind, muted: pub.isMuted })
  return out
}

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
    remoteTrackInfos: trackInfos(),
    remoteRmsDb: Math.round(remoteRmsDb),
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
  .on(RoomEvent.TrackSubscribed, (track: any, pub: any) => {
    if (track.kind === Track.Kind.Audio) {
      const el = track.attach() as HTMLAudioElement
      el.autoplay = true
      document.body.appendChild(el)
      audioEls.push(el)
      try {
        audioCtx = audioCtx || new AudioContext()
        const src = audioCtx.createMediaStreamSource(new MediaStream([track.mediaStreamTrack]))
        analyser = audioCtx.createAnalyser()
        analyser.fftSize = 2048
        src.connect(analyser)
      } catch (e) { console.error('analyser setup', e) }
    }
    report({ note: 'trackSubscribed source=' + pub.source + ' kind=' + track.kind })
  })
  .on(RoomEvent.TrackUnsubscribed, (track: any) => {
    try { track.detach().forEach((el: HTMLMediaElement) => el.remove()) } catch {}
    analyser = null
    remoteRmsDb = -120
    report({ note: 'trackUnsubscribed' })
  })

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
document.getElementById('startAudioBtn')?.addEventListener('click', () => {
  audioCtx?.resume()
  audioEls.forEach((el) => el.play().catch(() => {}))
  report({ note: 'start-audio clicked' })
})

// remote RMS sampler (for Gate 3.2 "non-silent >=60s") + periodic report
setInterval(() => {
  if (analyser) {
    const buf = new Float32Array(analyser.fftSize)
    analyser.getFloatTimeDomainData(buf)
    let s = 0
    for (const v of buf) s += v * v
    const rms = Math.sqrt(s / buf.length)
    remoteRmsDb = rms > 0 ? 20 * Math.log10(rms) : -120
  }
  report()
}, 500)

// auto-connect so headless CDP verification can read window.__gate1
connect()

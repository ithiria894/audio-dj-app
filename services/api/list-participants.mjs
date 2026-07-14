// Authoritative check: who does the LiveKit SFU see in room stage0.
// Dev-only. Run: node list-participants.mjs
import { RoomServiceClient } from 'livekit-server-sdk'

const http = (process.env.LK_URL || 'ws://127.0.0.1:7880').replace(/^ws/, 'http')
const svc = new RoomServiceClient(http, process.env.LK_API_KEY || 'devkey', process.env.LK_API_SECRET || 'secret')
try {
  const ps = await svc.listParticipants('stage0')
  console.log(JSON.stringify(ps.map(p => ({ identity: p.identity, tracks: p.tracks?.length || 0, state: p.state })), null, 0))
} catch (e) {
  console.log(JSON.stringify({ error: String(e) }))
}

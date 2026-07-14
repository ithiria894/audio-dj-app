# Stage 0A — Gate results (LAN)

Objective, evidence-backed. Infra: `livekit-server --dev` + dev token endpoint + Vite web listener, all on the dev machine LAN. Verified headlessly via `scripts/cdp.py` (agent Chrome, localhost) + `services/api/list-participants.mjs` (SFU authoritative) + Android UI log / logcat.

## Gate 1 — Web listener signaling ✅ PASS
Browser fetches a **subscribe-only** token → connects room `stage0`:
```json
{ "state": "connected", "canPublish": false, "canSubscribe": true, "identity": "web-listener", "remoteParticipants": 0 }
```
Token/CORS/signaling/state-machine verified. No audio track (by design).

## Gate 2 — Android signaling (connect-only, no publish) ✅ PASS
Android connects to LiveKit as **DJ** but publishes nothing. `NoAudioHandler`; no MediaProjection, no capture service, no tracks.

**Browser (listener) — objective join / leave / reconnect:**
| step | remoteParticipants | identities | remoteTracks |
|---|---|---|---|
| baseline | 0 | [] | 0 |
| Android connect | **1** | **["pixel-host"]** | **0** |
| Android disconnect | 0 | [] | 0 |
| Android reconnect | 1 | ["pixel-host"] | 0 |

**SFU authoritative (`listParticipants stage0`):** `[web-listener (tracks 0), pixel-host (tracks 0)]` — both ACTIVE, zero tracks.

**Android side (UI log):**
```
[audio:before-connect] mode=NORMAL musicActive=false commDevice=1
[lk] CONNECTED identity=pixel-host canPublish=true publishedTracks=0
[audio:after-connect]  mode=NORMAL musicActive=false commDevice=1
[lk] disconnect() -> event: disconnected reason=CLIENT_INITIATED
(reconnect) [lk] CONNECTED ... canPublish=true publishedTracks=0, mode=NORMAL
```

**Key finding (A2DP early signal):** `AudioManager.mode` stayed **NORMAL** before *and* after room connect (and `commDevice` unchanged). `NoAudioHandler` prevented LiveKit from grabbing audio focus / switching to `IN_COMMUNICATION` on connect. This is only an early signal — the real A2DP test (music playing + a published audio track on a Bluetooth host) is **Gate 5**.

## Not yet done
- **Gate 3** first audible publish (Path B: audio-only MediaProjection → ScreenAudioCapturer → LocalAudioTrack; experiments B1/B2). Before Gate 3: bump `targetSdk 36` + rerun capture/lock/permission tests; add `disableAudioPrewarming` (verify AudioOptions param), verify `setAudioRecordEnabled(false)` still fires the buffer callback.
- **Gate 4** deterministic L/R stereo isolation.
- **Gate 5** Bluetooth A2DP + true-lock non-silent (M0.6) + 15-min stability + lifecycle.

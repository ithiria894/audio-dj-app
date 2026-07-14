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

## Gate 2.6 — ScreenAudioCapturer preflight ✅ PASS (Pixel 8 Pro / Android 16)
A review flagged a possible blocker: LiveKit 2.27.0 `ScreenAudioCapturer` bytecode does
`ByteBuffer.allocateDirect(...)` then rejects the buffer if `hasArray()==false`
(`"ByteBuffer does not have backing array."`). On a standard JVM a direct buffer always has
`hasArray()==false`, which would make `initAudioRecord` always return false. **Verified on-device
instead of assuming:**
```
directBuffer.hasArray=true  isDirect=true          ← Android ART direct buffers DO have a backing array
screenAudioInit=true  audioRecord.state=1 (INITIALIZED)
```
**Verdict:** ScreenAudioCapturer initializes fine on this device — the guard passes because Android/ART
`allocateDirect()` reports `hasArray()==true` (unlike a standard JVM). **No SDK vendoring/patch needed.**
Reusable dev-note: on Android, `ByteBuffer.allocateDirect().hasArray()` is `true`; do not assume JVM semantics.
(Preflight path: `AudioCaptureService.ACTION_PREFLIGHT` → `runPreflight()`.)

## Not yet done
- **Gate 2.5** targetSdk 35→36 isolated regression (rerun capture / permission / M0.5 lock / capture stop-start×2 / Gate 2 / FGS cleanup; keep target-35 vs target-36 results separate). Then add `AudioOptions(disableAudioPrewarming=true)` + rerun Gate 2.
- **Gate 3** first audible publish (Path B: audio-only MediaProjection → ScreenAudioCapturer → LocalAudioTrack; experiments B1/B2). Before Gate 3: bump `targetSdk 36` + rerun capture/lock/permission tests; add `disableAudioPrewarming` (verify AudioOptions param), verify `setAudioRecordEnabled(false)` still fires the buffer callback.
- **Gate 4** deterministic L/R stereo isolation.
- **Gate 5** Bluetooth A2DP + true-lock non-silent (M0.6) + 15-min stability + lifecycle.

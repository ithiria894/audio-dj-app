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

## Gate 2.5 — targetSdk 35→36 regression ✅ PASS (isolated commit, only targetSdk changed)
Re-ran on `targetSdk 36` (Pixel 8 Pro / Android 16); **identical to target 35, zero regressions:**
| check | target 35 | target 36 |
|---|---|---|
| capture start (MediaProjection permission flow) | ✓ | ✓ |
| YouTube capture (AUDIO) | −16.4 dBFS | −16.2 / −20.6 dBFS ✓ |
| M0.5 lock survival (onStop=0) | ✓ | ✓ (keyguard=true, 14 level lines, onStop=0) |
| capture stop/start ×2 + FGS cleanup | ✓ | ✓ (fg services 1→0→1→0) |
| Gate 2 signaling (join/leave/reconnect) | ✓ | ✓ |

## Gate 2.5b — disableAudioPrewarming ✅ PASS
Added `AudioOptions(audioHandler=NoAudioHandler(), disableAudioPrewarming=true)`. Re-ran Gate 2:
listener sees pixel-host, `publishedTracks=0`, `AudioManager.mode=NORMAL` before + after connect.
(`AudioOptions` also exposes `disableCommunicationModeWorkaround` — may be relevant for the Gate 5 A2DP work.)

## Gate 3 — split into hard sub-gates (one commit + objective evidence each)
- **Gate 3.0** ✅ docs/evidence cleanup + instrumentation (no core audio change): fixed the contradictory `hasArray` log; recorded `recordingState`; docs → targetSdk 36; browser handles `TrackSubscribed/Unsubscribed` + explicit Start-Audio button + exposes remote track source/kind/**RMS**/count (verified still connects, `canPublish=false`); SFU script reports each track's source/kind/muted. **targetSdk-36 YouTube Music 9.26.55 re-check ✓** (captured, −18.8 dBFS, Pixel 8 Pro / Android 16 / target 36).
- **Gate 3.1** ✅ **PASS** — service-owned session, **zero tracks**. Room/LiveKit lifecycle moved into `AudioCaptureService` (mic-type FGS); Activity only sends connect/disconnect; `LOCAL_PROOF`/`LIVEKIT_PUBLISH` mutually exclusive. Evidence: browser saw `pixel-host` (rp=1, tracks=0) on service-connect → **pressed HOME to background the Activity → pixel-host STAYED (rp=1)** → disconnect → rp=0. Android: `service-owned LiveKit connect … publishing 0 tracks` / `canPublish=true publishedTracks=0` / `mode=NORMAL` before+after. The session now survives the host switching to a music app.
- **Gate 3.2** first audible transport: `FOREGROUND_SERVICE_MICROPHONE` + type `mediaProjection|microphone` (start while Activity visible); **configure stereo input now** (`javaAudioDeviceModuleCustomizer`: `setUseStereoInput(true)`, `setInputSampleRate(48000)`, HW AEC/NS off — verify via javap first); **`ReplacingScreenAudioCallback`** (compose stock ScreenAudioCapturer, zero outgoing buffer, **overwrite** system PCM in — NOT sum; zero unused tail; no alloc in 10ms callback; count callbackCalls/format/channels/sampleRate/bytesRead; gain=1.0); publish **one** track source=`SCREEN_SHARE_AUDIO`, ~160k, dtx off, no video/VirtualDisplay. Pass = browser hears it, remote RMS non-silent ≥60s, callbacks increasing, channels+rate logged, SFU sees 1 SCREEN_SHARE_AUDIO track / 0 video, pause+clap = remote stays silent, mode NORMAL, stop removes track, 2nd start works.
- **Gate 3.3** physical AudioRecord disabled: runtime `setAudioRecordEnabled(false)`, repeat 3.2, classify honestly — A callbacks continue (preferred product path) / B callbacks stop (3.2 = transport proof only; mic pipeline required, samples overwritten not sent; not a complete product path) / C unstable (ADR for custom ADM, don't build without approval).

## Not yet done
- **Gate 4** deterministic L/R stereo isolation.
- **Gate 5** Bluetooth A2DP + true-lock non-silent (M0.6) + 15-min stability + lifecycle.

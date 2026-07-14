# audio-dj-app (working name)

A private, small-group **"pass the aux, live"** app: the **host's Android phone plays any (capturable) audio** and 2–5 friends hear the **exact live stream** — cross-platform, phone-first, dead-simple onboarding, with a **rotating DJ**. Not "everyone press play on their own subscription" (synced-separate), but **true audio rebroadcast** of whatever the host is playing.

> **Single source of truth: [`SPEC.md`](./SPEC.md)** (living doc). This README is just an orientation.
> Detailed docs in `docs/` are written in Cantonese (the founder reads them); an AI reviewer can read them directly.

## Status (2026-07-13)

**On-device empirical results — Google Pixel 8 Pro / Android 16 (the strictest current OS):**
- ✅ `AudioPlaybackCapture` captures playing audio — **plain YouTube** (RMS −16.4 dBFS) and **YouTube Music** (−15.3 dBFS), **true stereo**. (Refuted an earlier over-pessimistic "YT Music blocks capture" conclusion.)
- 🟡 **Screen lock:** the audio-only capture *pipeline* survived a real keyguard lock (`onStop`=0, capture loop kept running) — but "non-silent audio still flowing after lock" is **not yet proven** (free YouTube pauses on lock). Tracked as milestone **M0.6**. Recorded as *tested-device behavior, not a cross-OEM platform guarantee*.
- ✅ Control/media planes stood up locally; **web listener Gate 1 passed** (subscribe-only token → connects → `canPublish=false`, verified headlessly).

**Milestones:** `M0 ✅ · M0.5 ✅ · M0.6 ⏳ · Stage 0A (LAN) ⏳ · Stage 0B (public) ⏳ · Stage 1 (MVP) —`. See SPEC §11.

## Architecture (two planes)

```
Android host (Kotlin/Compose)  --system audio, Opus, 1 upload-->  LiveKit SFU (media plane)  --> PWA listeners
Android host & PWA             --HTTPS control msgs, no audio-->   tiny token/room API (control plane)
```
- **Host must be native Android** (AudioPlaybackCapture has no web equivalent). **Listener = React PWA** (tap a link, hear it).
- **Media plane = LiveKit SFU** (always-on; Stage 0A local `--dev`, Alpha = self-hosted VPS; Cloud used only as a diagnostic).
- **Control plane** never touches audio: issues short-lived LiveKit JWTs, enforces the rotating-DJ token. No recording, no egress.

## Repo layout
```
SPEC.md                  # authoritative living spec
docs/                    # 00 requirements · 02 feasibility · 03 competitive · 05 recalibration · 06 capture matrix
android/                 # Stage-0 capture spike (→ apps/android-host)
apps/web-listener/       # Vite + livekit-client PWA listener (Gate 1)
services/api/            # dev token endpoint (control plane)
scripts/                 # dev-up.sh / dev-down.sh / dev-health.sh / cdp.py
research/                # demand + competitor research (reproducible scripts + raw results)
```

## Run Stage 0A locally (LAN)
```bash
scripts/dev-up.sh                      # starts LiveKit --dev + token endpoint (PID-tracked)
cd apps/web-listener && npm i && npm run dev   # listener on :5173
scripts/dev-health.sh                  # verify both endpoints
```
Requires: `livekit-server` (v1.13.3), Node 20+, Android SDK (for the host). Dev keys are LiveKit placeholders (`devkey`/`secret`) — **trusted LAN only, no port-forwarding**.

## Notes for a reviewer
- Distribution = **sideload APK, not Google Play** (removes Play-policy concerns for the capture app).
- Legal/licensing is a **flagged risk, not a blocker** for a private, no-recording, sideloaded, few-friends tool; see `docs/05`. Product must decide a source/rights model before any public/commercial launch.
- Hard rule for the LiveKit integration: **do NOT copy the official screenshare-audio example verbatim** (it publishes screen video + a mic track, which creates a VirtualDisplay and can break the audio-only lock-screen behavior and Bluetooth A2DP). Product path = build `ScreenAudioCapturer` directly from the existing audio-only `MediaProjection`, no video, no mic, gain=1.0.

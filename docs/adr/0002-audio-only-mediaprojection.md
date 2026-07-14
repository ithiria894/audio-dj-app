# ADR 0002 — Product capture path: audio-only MediaProjection, no VirtualDisplay

- **Status: Proposed**
- Date: 2026-07-13
- Related: `docs/compatibility/android-capture.md`, SPEC §5

## Context
The DJ host must capture the audio another app is playing and publish it via LiveKit. LiveKit's official `screenshare-audio` example enables a **screen-share video track** and an Android **microphone audio track**, then routes `ScreenAudioCapturer` into the mic track. That path can:
- create a `VirtualDisplay` (screen capture), which **re-enables the Android 15 QPR1+/16 keyguard auto-stop** — destroying the audio-only lock-survival behavior measured in M0.5;
- put the WebRTC audio device into communication mode, degrading the host's own Bluetooth from A2DP to SCO/HFP;
- mark the publish source as `microphone` instead of `screen_share_audio`.

## Decision
For the **product capture path**, do **not** create a `VirtualDisplay` or publish screen video. Build capture directly from an **audio-only** `MediaProjection`:

```
audio-only MediaProjection
  → ScreenAudioCapturer            (a MixerAudioBufferCallback, NOT a standalone track)
  → LocalAudioTrack                (used only as the WebRTC transport carrier)
  → physical microphone recording disabled / isolated
  → no screen video, no VirtualDisplay
  → publish source = SCREEN_SHARE_AUDIO (where supported by SDK 2.27.0)
```

Clarification on "no microphone": this means **no physical microphone samples are captured or transmitted**. It does **not** mean zero microphone infrastructure — a LiveKit `LocalAudioTrack`, `RECORD_AUDIO` permission, and a `microphone`-type foreground service may still be required as transport/runtime plumbing (LiveKit needs a microphone-type FGS for background capture to keep producing audio rather than silence).

The official example path (screen video + mic track) is retained only as **Path A (baseline transport proof)**, run explicitly for comparison — never as the shipped architecture.

## Acceptance (promote to **Accepted** only after Gate 5 proves all three)
- Non-silent locked streaming reaches a remote listener (M0.6) with the audio-only path.
- Host Bluetooth A2DP preserved (no SCO/HFP downgrade; physical mic isolated).
- LiveKit end-to-end transport works (Gate 3/4, true stereo to listener).

Until then this remains **Proposed** — the audio-only lock survival is tested-device evidence, not yet an end-to-end product guarantee.

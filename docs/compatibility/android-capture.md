# Android Capture — On-Device Compatibility Record

Empirical, on-device evidence for `AudioPlaybackCapture`. Not web reports. Reproducible via `android/` (AuxCapture spike) — see procedure below.

## Test device / build fingerprint

| Field | Value |
|---|---|
| Manufacturer / Model | Google / Pixel 8 Pro (husky) |
| OS | Android 16 |
| SDK / Build ID | 36 / CP1A.260505.005 |
| Build fingerprint | `google/husky/husky:16/CP1A.260505.005/15081906:user/release-keys` |
| Security patch | 2026-05-05 |
| App version | `com.audiodj.capture` 0.1-spike (compileSdk 36, minSdk 29, targetSdk 35) |
| Repo commit | `3236183bacd7b46fdd32e832d836b629aeb21834` |
| Test date | 2026-07-13 |

## 1. Source capture matrix

Method: play a source, read a live RMS meter from the captured 48 kHz stereo PCM, save a 10 s WAV, compute RMS + L/R correlation.

| Source | Result | RMS | Peak | Stereo | Evidence |
|---|---|---|---|---|---|
| Plain YouTube (app) | ✅ CAPTURED | −16.4 dBFS | −1.2 dBFS | TRUE STEREO (L−R = −20.8 dB) | `research/results/capture-test-youtube.wav` |
| YouTube Music | ✅ CAPTURED | −15.3 dBFS | 0.0 dBFS | TRUE STEREO (L−R = −23.7 dB) | `research/results/capture-test-ytmusic.wav` |
| Spotify | ⬜ not tested | — | — | — | founder has no account |
| Local player / VLC / podcast | ⬜ not tested | — | — | — | pending (needed for M0.6, see §2) |

Note: this **refutes** an earlier web-report-based claim that YouTube Music opts out of `AudioPlaybackCapture` and yields silence. On this device/OS it captures cleanly. Capture policy is source-app + OS-version + OEM dependent, so this is per-device evidence, not a universal guarantee — maintain this matrix.

## 2. Screen-lock experiment (the make-or-break)

Question: does an audio-only `MediaProjection` capture session survive a real keyguard lock on Android 16 (the OS whose docs say general MediaProjection auto-stops on lock since 15 QPR1)?

### Procedure
1. Start capture (foreground service, `foregroundServiceType=mediaProjection`, audio-only — never `createVirtualDisplay()`).
2. Play plain YouTube; confirm non-silent capture.
3. `adb logcat -c`; `adb shell input keyevent 26` (screen off → keyguard).
4. Wait 16 s locked; read logs; power screen back on.

### Observed
```
Keyguard:                 isKeyguardShowing=true
Device awake:             mAwake=false
MediaProjection onStop:   0 events
Capture loop (level log): continued, 16 lines over 16 s
Captured audio after lock: SILENCE (−120 dBFS) after ~3 s
Reason for silence:       free YouTube stopped playback on lock (source-side), NOT capture death
```
Logcat excerpt (during lock):
```
07-13 19:37:42.917 I AuxCapture: level=-36.3 dBFS peak=-24.8 (AUDIO)
07-13 19:37:44.961 I AuxCapture: level=-120.0 dBFS peak=-120.0 (silent)   <- YouTube paused
07-13 19:37:58.277 I AuxCapture: level=-120.0 dBFS peak=-120.0 (silent)
VERDICT: level-lines-during-lock=16  onStop-events=0
```

### Conclusion
- **M0.5 (PASS, tested-device):** the audio-only capture **pipeline survived** a true device lock — `AudioRecord` + capture loop kept running, `MediaProjection.onStop` did not fire. This is consistent with the AOSP `MediaProjectionStopController.isExempt()` `INVALID_DISPLAY` carve-out (audio-only sessions have no VirtualDisplay).
- **M0.6 (PENDING):** **non-silent** streaming after lock is **NOT proven** here, because the source app stopped playing. Must re-test with a source that keeps playing while locked (local WAV/FLAC player, VLC, YT Music Premium, or an ExoPlayer test source), lock ≥5 min, and confirm a **remote LiveKit listener** keeps receiving non-silent PCM.
- Record as **tested-device behavior on Pixel 8 Pro / Android 16, not a cross-OEM / cross-version platform guarantee.** OEM power management (Samsung/Xiaomi/OnePlus) and other kill paths (battery optimization killing the FGS) are untested.

## 3. Reproduce
```
cd android && JAVA_HOME=~/.gradle/jdks/eclipse_adoptium-21-amd64-linux.2 ./gradlew :app:assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb shell pm grant com.audiodj.capture android.permission.RECORD_AUDIO
# launch, tap 開始擷取, choose "Share entire screen", play a source, watch `adb logcat -s AuxCapture`
# adb shell am broadcast -a com.audiodj.capture.DO_SAVE  -> saves a 10s WAV to the app's files dir
```

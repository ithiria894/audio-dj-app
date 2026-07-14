# 技術可行性報告 (verify ChatGPT + screen-lock + RTC + iOS + legal)

> 來源:audio-dj-app-research workflow (15 agents, Opus, 7 dimensions × adversarial verify, 2026-07-13)。

# Music Rebroadcast App — Synthesis & Build Decision

**Prepared by:** Synthesis lead
**Inputs:** 7 research dimensions, each with a research pass + an independent adversarial-verify pass
**Founder rules honored:** own-it / self-host over SaaS, official SDKs over hand-rolled, spec-first, evidence over narrative
**Date:** 2026-07-13

---

## 1. Executive summary

**The named make-or-break question — does audio survive the screen locking during street use — resolves ACHIEVABLE.** A pure audio-only `AudioPlaybackCapture` session (one that never calls `createVirtualDisplay()`) is explicitly *exempt* from the Android 15 QPR1+/16 keyguard auto-stop. The AOSP stop logic only fires when `mVirtualDisplayId != INVALID_DISPLAY`, and an audio-only session keeps that field at `INVALID_DISPLAY` forever ([MediaProjectionManagerService.java, android15-qpr1-release](https://github.com/aosp-mirror/platform_frameworks_base/blob/master/services/core/java/com/android/server/media/projection/MediaProjectionManagerService.java)). The verify pass strengthened this: it read the *actual* QPR1 shipping code the research pass had skipped, and the conclusion held across three separate AOSP code states (QPR1 inline, master, android16-release). The keyguard stop targets **screen/video** projection only; ChatGPT's "therefore audio-only apps die on lock" is REFUTED.

**But viability of the product as literally worded is a different, harder answer: PARTIAL, trending BLOCKED for the headline feature.** "Host plays *any* music (Spotify / Apple Music / YouTube Music) and friends hear the *exact* audio" is defeated at the capture layer, not the transport layer: those apps opt out of `AudioPlaybackCapture` and the OS hands you **silence, not an error** ([developer.android.com/media/platform/av-capture](https://developer.android.com/media/platform/av-capture)), independently corroborated by an unrelated commercial SDK vendor and by the existence of a root/Xposed module built specifically to force those apps capturable ([XAudioCapture](https://github.com/wzhy90/XAudioCapture)). What **is** buildable and survives every test in this bundle: an **Android host rebroadcasting local files + non-DRM audio** (podcasts, games, browser/YouTube-in-Chrome, VLC) to **2–5 cross-platform listeners** with a **rotating DJ**, over a **self-hosted LiveKit SFU**, **through a locked screen**. Recommendation: **BUILD**, but make the scope pivot deliberate (drop or degrade the big-three streaming promise) and run three on-device de-risking tests before committing architecture.

---

## 2. Verified vs Refuted — the ChatGPT claims we tested

| # | ChatGPT / premise claim | Verdict | Decisive source | Note |
|---|---|---|---|---|
| 1 | `AudioPlaybackCapture` can grab Spotify / Apple Music / YouTube Music so friends hear the exact audio | **REFUTED** (YT Music, Apple Music) / **DISPUTED-UNKNOWN** (Spotify) | [av-capture doc](https://developer.android.com/media/platform/av-capture); [XAudioCapture](https://github.com/wzhy90/XAudioCapture) | Opt-out → silence. YT Music/Apple Music consistently reported opting out; Spotify genuinely disputed (AudioRelay lists it capturable, field reports say silent). **No primary manifest proof either way — must apktool + on-device test.** |
| 2 | Spotify Jam / SharePlay / Stationhead are "audio rebroadcast" | **REFUTED** | [billboard/Stationhead](https://www.billboard.com/pro/stationhead-social-audio-streams-listening-parties/); [9to5mac/Jam](https://9to5mac.com/2023/09/26/spotify-jam-new-feature-music/) | They are *synced-separate-playback*: only track+timestamp metadata travels; each phone streams from its own (Premium) account. Not cross-service, not exact-audio. |
| 3 | Capturing adds no latency to the source app | **CONFIRMED** (verbatim) | [av-capture doc](https://developer.android.com/media/platform/av-capture) | "does not affect the latency of the app whose audio is being captured." Promise is *only* about source-app latency, not the capturer's CPU/battery. |
| 4 | Android 15 QPR1+ auto-stops MediaProjection on screen lock | **CONFIRMED** | [media-projection doc](https://developer.android.com/media/grow/media-projection); [LiveKit #595](https://github.com/livekit/client-sdk-android/issues/595) | QPR1-specific (not base 15); unconditional on Android 16. Real logcat: "Stopped MediaProjection due to keyguard lock." |
| 5 | **Therefore pure-audio capture dies on lock** (the make-or-break) | **REFUTED** | AOSP [MediaProjectionStopController](https://github.com/aosp-mirror/platform_frameworks_base/blob/master/services/core/java/com/android/server/media/projection/MediaProjectionStopController.java) `isExempt()` INVALID_DISPLAY carve-out | Audio-only = no VirtualDisplay = exempt. Verified across 3 branches. **See §5.** |
| 6 | LiveKit Android can publish custom PCM from `AudioPlaybackCapture` | **CONFIRMED** | [ScreenAudioCapturer.kt](https://github.com/livekit/client-sdk-android/blob/main/livekit-android-sdk/src/main/java/io/livekit/android/audio/ScreenAudioCapturer.kt); official `examples/screenshare-audio` | First-class, example-backed. Not hand-rolled. |
| 7 | 48 kHz stereo is the "easy case" for LiveKit's Android buffer callback | **REFUTED** | 960-byte/10 ms buffer = mono (stereo = 1920 B); [WebRTC JavaAudioDeviceModule](https://chromium.googlesource.com/external/webrtc/+/HEAD/sdk/android/api/org/webrtc/audio/JavaAudioDeviceModule.java) defaults mono; [LiveKit #2101](https://github.com/livekit/livekit/issues/2101) closed *not planned* | Music-grade **stereo from an Android publisher is unproven and historically flaky.** Expect mono out of the box. |
| 8 | Rotating-DJ via `canPublish:false` → flip at runtime | **CONFIRMED mechanism / PARTIAL reliability** | [VideoGrant](https://docs.livekit.io/reference/server-sdk-js/interfaces/VideoGrant.html); [UpdateParticipant](https://docs.livekit.io/reference/server-sdk-js/types/UpdateParticipantOptions.html) | Revoking canPublish auto-unpublishes the old DJ (clean demotion), but runtime-promotion has a bug history ([swift #244](https://github.com/livekit/client-sdk-swift/issues/244), [js #1314](https://github.com/livekit/client-sdk-js/issues/1314)). Device-test across clients. |
| 9 | iOS host can capture other apps' audio via ReplayKit | **REFUTED** | [Twilio ReplayKitExample README](https://github.com/twilio/video-quickstart-ios/blob/master/ReplayKitExample/README.md); [Apple forum 91322](https://developer.apple.com/forums/thread/91322) | Only own-app audio + mic; AVPlayer/Safari/Music blocked; 50 MB RAM cap. iOS host is impossible, not just deferred. |
| 10 | iOS listener works backgrounded + screen-locked | **CONFIRMED** (but not "trivial") | [LiveKit Swift](https://github.com/livekit/client-sdk-swift); [Apple QA1626](https://developer.apple.com/library/ios/qa/qa1626/_index.html) | Feasible and low-*ish* risk. Downgraded from "trivial": receive-only WebRTC on iOS pulls in the voice-processing unit + a mic-permission prompt ([WebRTC 42222376](https://issues.webrtc.org/issues/42222376), [LiveKit #815](https://github.com/livekit/client-sdk-swift/issues/815)). |
| 11 | A web (Safari) listener equals a native iOS listener | **REFUTED** | [Apple forum 774239](https://developer.apple.com/forums/thread/774239); WebKit bugs 231105/175014 | Safari suspends WebRTC/Web Audio on lock/background; the silent-mp3 keep-alive hack is dead. Web = foreground-only tier. |
| 12 | A normal app can sync/route audio to Bluetooth + speaker or control BT latency | **REFUTED** | [AOSP Combined Audio Device Routing](https://source.android.com/docs/core/audio/routing); `BluetoothA2dp.setActiveDevice` is `@hide` | Multi-device routing + active-device selection are privileged/system APIs (Android 12+). BT latency is codec/hardware-bound, not app-controllable. **See §4 Bluetooth rule.** |
| 13 | Rebroadcasting music-service audio breaches ToS/copyright | **CONFIRMED** (low enforcement) | [Spotify legal terms](https://www.spotify.com/us/legal/end-user-agreement/plain/) | "personal, non-commercial use," "agree not to redistribute." Breach for any group size; enforcement is complaint/scale-driven, so tiny + private + non-recording ≈ dormant risk. |
| 14 | A sideloaded private tool escapes all Google policy | **PARTIAL / REFUTED going forward** | [Android Developer Verification](https://developer.android.com/developer-verification); Android 16 Advanced Protection Mode | Avoids Play *content* review, but from Sep 2026 (select regions) → 2027 global, installing on certified devices needs a *verified developer identity*; Advanced Protection Mode can block sideloading + auto-revoke accessibility at the OS level. |
| 15 | Accessibility can auto-dismiss the capture-consent dialog | **REFUTED** | [Play Accessibility policy](https://support.google.com/googleplay/android-developer/answer/10964491?hl=en) + OS Advanced Protection | Prohibited and now OS-blockable. Don't do it. (Nuance: the live policy *does* permit deterministic "If X then Y" macros, but auto-tapping a system privacy prompt is still circumvention.) |

### Contradictions the verify pass surfaced, and how they reconcile

1. **Screen-lock — research skipped the QPR1 code, conclusion survived anyway.** The research pass claimed it "verified on master and android16-release" and generalized to "QPR1+." It never opened the actual `android15-qpr1-release` code (`MediaProjectionStopController.java` returns 404 there; the logic lives inline in `MediaProjectionManagerService`). The verify pass read it and found audio-only is exempt *even more robustly* than argued. **Reconciled verdict: ACHIEVABLE at the source-code level, verified across three code states; on-device confirmation still mandatory.**

2. **Cross-dimension reconciliation of "audio dies on lock."** The `audioplaybackcapture` dimension asserted audio capture "dies silently on lock" as settled fact, and its own verify correctly flagged that the doc only literally says *screen* projection stops. The `screenlock-risk` dimension then *resolved* this at the AOSP source level: audio-only is exempt. **These two dimensions agree once reconciled — the assertion was an overstatement; the source-of-truth answer is "audio-only survives."**

3. **rtc-backend stereo — "easy case" was self-contradicting.** The research cited the 960-byte/48 kHz buffer as evidence stereo "matches," but that buffer size *proves mono*. **Reconciled: LiveKit stays #1, but music-grade stereo from an Android publisher is an UNSOLVED, must-prototype risk; plan a high-bitrate mono fallback.**

4. **Prior-art fork target was oversold.** `jofr/listentogether-app` was rated "BEST fork target, HIGH confidence," but it is a 3-star / 0-fork solo GitLab mirror whose rotating-DJ feature is *not implemented* (README lists it as a future plan). **Reconciled: treat it as a learn-from reference for the WebRTC/room shell, not a turnkey base; the rotating-DJ core is built fresh.**

5. **Legal "sideload escapes policy" is dated.** **Reconciled: sideloading avoids Play content review but is no longer beyond Google/OS reach (Developer Verification + Advanced Protection Mode).**

---

## 3. Prior art & fork-or-build decision

No single project does all of {cross-platform + over-internet + phone-first + true rebroadcast + rotating DJ}. That gap is real, and it exists mostly because of the DRM capture wall, not because it's hard to wire. **Do not fork one app; split by layer.**

**Ranked plan:**

1. **Transport / SFU / rooms / DJ gating → USE LiveKit as-is (self-hosted), do not fork.** Apache-2.0 server *and* every client SDK (Android/Swift/JS), embedded TURN, and a first-class `ScreenAudioCapturer` path that is literally the `AudioPlaybackCapture` use case ([livekit/livekit](https://github.com/livekit/livekit), [client-sdk-swift LICENSE](https://github.com/livekit/client-sdk-swift/blob/main/LICENSE)). This replaces both "fork a WebRTC PWA" and "learn transport from SonoBus."

2. **Android capture layer → BUILD FRESH**, using **`rom1v/sndcpy` (MIT — verified LICENSE, safe to copy)** and **`julioz/AudioCaptureSample`** (license still unverified — the verify pass got a 404 on its LICENSE file, so confirm before copying) as references for the foreground-service + `MediaProjection` + `AudioRecord(AudioPlaybackCaptureConfiguration)` wiring. LiveKit's own `examples/screenshare-audio` is the closest drop-in ([MainViewModel.kt](https://github.com/livekit/client-sdk-android/blob/main/examples/screenshare-audio/src/main/java/io/livekit/android/example/screenshareaudio/MainViewModel.kt)).

3. **Room/DJ shell → learn-from only.** `jofr/listentogether-app` (GPL-3.0) shows a clean WebRTC-P2P room model but is an immature solo repo with the DJ feature unbuilt; LiveKit already gives you rooms + gating, so you don't need it. `SonoBus` (GPLv3) and `Snapcast` (GPL-3.0) remain references for Opus/jitter-buffer and clock-sync *ideas*, not code you ship.

4. **NAT traversal → LiveKit embedded TURN first, `coturn` (BSD-3) as fallback.** TURN is mandatory for cellular CGNAT ([webrtchacks/symmetric-nat](https://webrtchacks.com/symmetric-nat/)).

**Avoid:** raw libwebrtc / Janus (GPL) / ion-sfu (low-maintenance) — all re-impose a custom AudioDeviceModule + all signaling, the exact work LiveKit already did. **Never ship on Agora/Daily/Twilio** — closed, metered, rug-pull risk (Twilio Video was EOL-announced in 2024 then reversed: [changelog](https://www.twilio.com/en-us/changelog/-twilio-video-will-remain-a-standalone-product)); fine only as a throwaway week-1 prototype.

**GPL note:** LiveKit + coturn are permissive (Apache-2.0 / BSD). The GPL-3.0 fork candidates you're now *not* forking would have forced your whole app open. Staying on LiveKit keeps your licensing options open.

### Fastest ZERO-CODE validation tonight (pick by what you're validating)

- **Validate the social feel (rotating DJ, cross-platform, over-internet):** **Spotify Jam remote** via share link/QR. Cross-platform iOS+Android, different networks, anyone can add/steal tracks. Caveat: it validates the *experience*, not the mechanic — it's synced-separate-playback and **every remote participant needs Premium** (verified stricter than stated: free users only get in-person jams) ([Spotify Jam](https://support.spotify.com/us/article/jam/)).
- **Feel true rebroadcast + see the DRM wall live:** **Discord** on a laptop — play a YouTube tab / local file with "Go Live + Share sound," friends join the voice channel on any phone. **Spotify/Netflix audio will be silent**, which demonstrates the exact wall you're up against.
- **Feel Android-to-Android true rebroadcast (LAN):** **AudioRelay** — proves the capture→stream mechanic and its DRM limits in 5 minutes ([docs](https://audiorelay.net/docs/android/stream-audio-from-a-phone-to-a-pc-or-to-another-phone)). Not forkable (closed), LAN-only.

---

## 4. Recommended architecture (v1, self-host first)

```
[Android HOST]                                   [LISTENERS x2-5]
 local file / non-DRM app plays audio             LiveKit client SDK (subscribe-only)
        │  USAGE_MEDIA, capturable                 ├─ Android (native)
        ▼                                          ├─ iOS (native, .playback + bg audio)
 AudioPlaybackCapture (FGS type=mediaProjection)   └─ Web (foreground-only tier)
        │  48kHz PCM (mono in practice)                     ▲
        ▼                                                   │ Opus fan-out
 LiveKit LocalAudioTrack.setAudioBufferCallback ──▶ LiveKit SFU (self-hosted, Apache-2.0)
   (setAudioRecordEnabled(false) to drop mic)        + embedded TURN/TLS:443
                                                     + token backend (mints canPublish grants)
```

**Capture (Android host):** `AudioPlaybackCapture` via a foreground service of `foregroundServiceType="mediaProjection"` + `FOREGROUND_SERVICE_MEDIA_PROJECTION`. Start the FGS **while the app is visible** (the while-in-use rule blocks *starting* from background, not *continuing*), get fresh consent every session (no token caching since Android 14 — reuse throws `SecurityException`, [behavior-changes-14](https://developer.android.com/about/versions/14/behavior-changes-14)), hold a `PARTIAL_WAKE_LOCK`, register `MediaProjection.Callback.onStop()`, and **never call `createVirtualDisplay()`** (that's what keeps you exempt from the lock-stop). Add a **runtime silence-detection probe** so a DRM/opted-out source (or a Google component update like the April-2026 WebView v147 breakage, [PRISM Live](https://guide.prismlive.com/mobile/announcement/service-disruption/android-internal-audio-capture-issue)) surfaces as "this app blocks capture," not a mystery bug.

**Transport / SFU:** **Self-hosted LiveKit.** Self-hosting does **not** impede custom-PCM publish — the publish path runs entirely client-side in the Android SDK, so you own the whole stack (server + TURN + clients) with zero paid dependency. Run `livekit-server` + a small Node/Go token backend.

**Rotating-DJ token model:** Backend mints every listener a token with `canPublish:false`. To hand over the DJ role, call the `UpdateParticipant` server API to promote exactly one participant to `canPublish:true` and demote the previous one (revoking canPublish auto-unpublishes their track — clean). Server-authoritative, no client trust. **Reliability caveat:** runtime permission-change has documented client bugs; device-test the promotion flow on iOS/Android/web before relying on it.

**Custom-PCM publish effort — the honest accounting:**
- **Mono publish = LOW effort.** Fork `examples/screenshare-audio`; `ScreenAudioCapturer` + `setAudioBufferCallback` + `setAudioRecordEnabled(false)` is a supported, example-backed path.
- **Stereo music publish = UNSOLVED / HIGH effort.** The WebRTC ADM defaults to mono and AEC downmixes; one independent dev tried `setUseStereoInput(true)` + disabling AEC/NS + SDP munging and *still* got mono ([report](https://dev.to/ko3ak81/android-webrtc-stream-always-downmixes-stereo-audio-to-mono-4gmd)). Budget a custom `JavaAudioDeviceModule` spike, and **plan a high-bitrate mono fallback** if it fails.
- **DRM-source handling = MEDIUM.** The silence probe + honest per-app UX.

**Sync buffer:** WebRTC/LiveKit is tuned for low-latency conversation, not sample-accurate multi-listener playout. Configure a **fixed/larger jitter (playout) buffer** on listeners so 2–5 devices stay roughly aligned; LiveKit exposes limited jitter-buffer control, so **confirm what's actually tunable** (open question). Realistic expectation: ~100–300 ms end-to-end with per-listener drift. That's fine for casual co-listening, not for a synchronized-speaker array. `Snapcast`'s clock-sync is the learn-from if you ever need tighter.

**Bluetooth rule (important, evidence-backed):** **Treat each listener's Bluetooth output as opaque and uncorrectable.** A normal app cannot pick the active BT sink (`setActiveDevice` is `@hide`), cannot route to BT+speaker simultaneously (privileged, Android 12+ only, [AOSP routing](https://source.android.com/docs/core/audio/routing)), and cannot measure or compensate A2DP latency (codec/hardware-bound; even Developer-Options codec switching often no-ops per SoundGuys/XDA). Consequence: if friend A wears AirPods (~150 ms) and friend B wears cheap earbuds (~250 ms), they drift ~100 ms and **the app can do nothing about it.** The rule: sync *only* at the network/jitter-buffer layer, never promise tight cross-listener sync when Bluetooth is in the path, and build no feature that assumes app-level BT control. (LE Audio / Auracast broadcast for third-party apps on Android 15/16 is an untested open question — do not design around it.)

**Opus config for music:** `usedtx=0` (do **not** let music get gated as silence), disable WebRTC voice DSP (AEC/NS/AGC mangle music), `red=false`, `maxplaybackrate=48000`. Target **~96–128 kbps mono** as the safe, shippable baseline. LiveKit's `AudioPresets.musicHighQualityStereo` (`channelCount:2`, `audioBitrate:510000`, [advanced media docs](https://docs.livekit.io/transport/media/advanced/)) works for **server/browser publishers** but is moot if the Android ADM feeds mono — mono in, mono Opus out regardless of preset.

---

## 5. The screen-lock problem (deepest treatment)

**What exactly breaks.** On Android 15 QPR1+ and all of Android 16, the framework auto-stops a `MediaProjection` grant the instant the keyguard shows. The trigger is `KeyguardManager` → `onKeyguardLockedStateChanged(isKeyguardLocked=true)` → `STOP_REASON_KEYGUARD`. On a **video/screen** projection this revokes the token, and any app built on a virtual display (every mainstream screen-share SDK, e.g. LiveKit's video path) gets killed — real logcat: `Content Recording: Stopped MediaProjection due to keyguard lock` ([LiveKit #595](https://github.com/livekit/client-sdk-android/issues/595)). Screen-off ≈ keyguard-shows on any device with a keyguard enabled, so "power button pressed" is enough.

**Why audio-only survives.** The AOSP stop logic guards the stop behind `mVirtualDisplayId != INVALID_DISPLAY`. `mVirtualDisplayId` is written in exactly **one** place, `notifyVirtualDisplayCreated()`, which only runs when `createVirtualDisplay()` is called. A pure `AudioPlaybackCapture` session (`AudioPlaybackCaptureConfiguration` → `AudioRecord`, no virtual display) keeps `mVirtualDisplayId == INVALID_DISPLAY`, so the keyguard-stop condition short-circuits and **the token is never revoked** ([MediaProjectionStopController](https://github.com/aosp-mirror/platform_frameworks_base/blob/master/services/core/java/com/android/server/media/projection/MediaProjectionStopController.java)). The verify pass confirmed this is a **deliberate, standing exemption** (original commit javadoc: "exempt... if the current projection does not have an active VirtualDisplay") gated by the aconfig flag `media_projection_keyguard_restrictions`, and that it holds whether the flag is on or off. Plain **microphone** foreground services (`RECORD_AUDIO`, FGS type `microphone`) never touch `MediaProjection` at all, so the rule can't apply to them.

**Which versions / OEMs.**
- Android ≤14: no keyguard auto-stop at all.
- Android 15 QPR1 (Dec 2024 Pixels onward): active, flag-gated, but **audio-only exempt** via the INVALID_DISPLAY term.
- Android 16: hardcoded-on (flag guard removed), **audio-only still exempt**.
- Verified identical on **three** AOSP code states. **Not** verified: aggressive OEM builds (Samsung One UI, Xiaomi HyperOS) — no source or dev report found confirming or refuting an OEM modification to the keyguard logic. This is a genuine, unresolved surface.

**Realistic mitigation.** For an audio-only product, **you need no mitigation** — the screen genuinely locks and audio keeps flowing because of the exemption. **Pocket Mode is unnecessary** (it only matters for a *video*/virtual-display projection, where you'd keep the screen on with `FLAG_KEEP_SCREEN_ON` / a black overlay / proximity wake lock to keep `isKeyguardLocked()==false`); it costs heavy battery/thermal, is fragile across OEM battery managers, and a hidden black overlay masking an active capture invites deceptive-behavior scrutiny. The real reliability threat for long screen-off street sessions is **OEM battery-manager kills** of the foreground service (Xiaomi/Samsung/OnePlus/Huawei), mitigated with a battery-optimization exemption prompt + per-brand dontkillmyapp guidance, plus a `PARTIAL_WAKE_LOCK`.

**Verdict on the street use case: ACHIEVABLE**, with one caveat that is code-proven but not yet hardware-proven. **Mandatory pre-ship test:** fork `julioz/AudioCaptureSample`, run the pure-audio path on (1) a real Android 15 QPR1 Pixel, (2) a real Android 16 device, and (3) at least one Samsung/Xiaomi build; lock the screen; confirm logcat prints `Continuing MediaProjection as current projection has no VirtualDisplay` (good) and **not** `Stopped MediaProjection due to keyguard lock` (bad). This is the single link proven only at source level. Also confirmed safe against the future: Android 17 "background audio hardening" restricts playback/focus/volume APIs only and explicitly does **not** touch `AudioPlaybackCapture` or mic capture ([Android 17 bg-audio](https://developer.android.com/about/versions/17/changes/bg-audio)).

---

## 6. Scope for v1 MVP

**Host platforms:** **Android only.** iOS host is impossible (no API delivers arbitrary other-app audio; ReplayKit yields only own-app audio + mic, 50 MB cap). Do not list it as "coming soon."

**Listener platforms:**
- **Android — native** (LiveKit, subscribe-only): full support, backgrounded + locked.
- **iOS — native** (LiveKit Swift, `.playback` + "Audio, AirPlay, PiP" background mode): supported, plays locked. **Effort = low-to-moderate, not "trivial"** — expect a mic-permission usage string, a voice-processing/`.playback` decision, and a device test of background-during-silence + App-Review justification for intermittent audio.
- **Web — foreground-only convenience tier.** Safari suspends WebRTC on lock/background; do not promise background listening on web.

**Room model:** One host owns a room; 2–5 listeners join by link/QR. Server-authoritative rotating DJ via `canPublish` token grants (one active publisher at a time, promote/demote through `UpdateParticipant`). Ephemeral — **stream only, never record or store** (this also keeps the copyright profile minimal).

**Capture sources — IN:** local files, podcasts, games, browser/YouTube-in-Chrome, VLC and other non-DRM players (`USAGE_MEDIA`, not opted out).
**Capture sources — OUT / silent-by-design:** Spotify, Apple Music, YouTube Music, Netflix, Disney+, and other DRM apps (opt-out → silence). Surface this as a clear per-app state, not a bug.

**Features OUT of v1:** iOS host; background web listening; Bluetooth sync guarantees; sample-accurate multi-listener sync; Play Store distribution (start sideloaded — see §7/§8); music-grade *stereo* (stretch goal pending the ADM spike).

---

## 7. Risk register

| Risk | Level | Evidence | Mitigation |
|---|---|---|---|
| **DRM capture wall** — big-three streaming apps produce silence, killing the headline promise | **HIGH** | [av-capture doc](https://developer.android.com/media/platform/av-capture), [XAudioCapture](https://github.com/wzhy90/XAudioCapture) | Reposition to local + non-DRM sources; apktool + on-device test to confirm each target app; silence-detection probe + honest UX. |
| **Music-grade stereo from Android publisher unproven** | **HIGH** | 960 B = mono; [LiveKit #2101](https://github.com/livekit/livekit/issues/2101) closed not-planned | Custom `JavaAudioDeviceModule` spike *before* committing; ship high-bitrate mono fallback. |
| **Screen-lock audio survival not yet hardware-confirmed** | **MED** (code-proven) | AOSP 3-branch verify; no on-device report either direction | Mandatory logcat test on QPR1 Pixel + Android 16 + one aggressive OEM. |
| **OEM battery-manager kills the capture FGS** on long screen-off sessions | **MED** | dontkillmyapp pattern; OEM behavior | Battery-optimization exemption prompt, `PARTIAL_WAKE_LOCK`, per-brand guidance. |
| **Rotating-DJ runtime promotion flakiness** across clients | **MED** | [swift #244](https://github.com/livekit/client-sdk-swift/issues/244), [js #1314](https://github.com/livekit/client-sdk-js/issues/1314) | Device-test promotion on all three client types; handle `ParticipantPermissionChanged`. |
| **Cellular CGNAT breaks connect** without TURN | **MED** | [symmetric-nat](https://webrtchacks.com/symmetric-nat/) | LiveKit embedded TURN/TLS:443 (needs own domain+cert; can't co-reside on 443 without an L4 LB); coturn fallback. |
| **Bluetooth per-listener drift** the app can't fix | **LOW-MED** | `setActiveDevice` `@hide`; A2DP codec-bound latency | Accept as limitation; document it; jitter-buffer sync only. |
| **iOS listener effort/App-Review nuance** (mic prompt, intermittent-audio justification) | **LOW-MED** | [WebRTC 42222376](https://issues.webrtc.org/issues/42222376), Apple audio-guidelines | Add mic usage string, set `isVoiceProcessingBypassed`, keep listener subscribe-only, device-test background-silence. |
| **Google Developer Verification** (2026 select regions → 2027 global) requires verified identity to install on certified devices | **MED (legal/policy)** | [developer-verification](https://developer.android.com/developer-verification) | Plan to register as a verified developer, or route friends through the ADB/advanced-flow power-user path. Canada is in the later global wave, so runway exists. |
| **Android 16 Advanced Protection Mode** can block sideloading + auto-revoke accessibility on a friend's phone | **LOW-MED (legal/policy)** | Android 16 APM teardown | Don't depend on any accessibility service; document that an APM-on friend may not be able to install. |
| **Music-service ToS breach** for rebroadcasting captured audio | **LOW** | [Spotify terms](https://www.spotify.com/us/legal/end-user-agreement/plain/) | Keep private/tiny/ephemeral/non-recording; and note the big three are silent anyway, so this mostly bites only the non-DRM audio you *can* capture. |
| **Accessibility-to-auto-tap-consent = instant removal / OS block** | **HIGH if attempted** | [Play policy](https://support.google.com/googleplay/android-developer/answer/10964491?hl=en) | Simply don't. Accept the per-session consent tap + status-bar chip. |
| **Fork base immaturity** (if you had forked listentogether) | **LOW** (avoided) | 3-star/0-fork solo repo, DJ unbuilt | Use LiveKit instead; treat listentogether/SonoBus/Snapcast as learn-from only. |

**Negative confirmation (what was checked and found clean):** the no-latency-to-source claim (holds), the Android-14 token-reuse rule (holds verbatim), the QPR1-vs-base-15 attribution (precise), LiveKit's Apache-2.0 across server+clients (holds), sndcpy MIT (holds). **Not checked / genuinely open:** on-device audio-lock survival on real QPR1/16/OEM hardware; big-three capturability via apktool manifest dump; stereo-from-Android on a custom ADM; `julioz/AudioCaptureSample` exact license; LiveKit jitter-buffer tunability; LE Audio/Auracast third-party APIs; Canadian private-copying doctrine (needs a lawyer, not a scan).

---

## 8. Open DECISIONS for the founder

Each is framed as a crisp choice with a recommended default.

**D1 — What does "host plays any music" mean now that the big three are silent?**
Options: (a) **Honest narrow scope** — rebroadcast local files + non-DRM sources only; (b) pivot to synced-separate-playback (Spotify Jam model — but that's single-service, everyone-Premium, and not your mechanic); (c) hybrid.
**Recommended default: (a).** It's the only lane that keeps your true-rebroadcast + cross-service + rotating-DJ premise intact and buildable. Market it as "share whatever's playing on your phone" and let the silence-probe gracefully explain the DRM apps. **This is the load-bearing decision — everything else follows from it.**

**D2 — Self-host LiveKit vs paid SaaS?**
**Recommended default: self-host LiveKit** (Apache-2.0 server + clients + embedded TURN). It satisfies own-it, has the custom-PCM path as a first-class feature, and removes the Twilio-style rug-pull risk. Use Agora/Daily only as a throwaway week-1 pipeline prototype, never as the shipping backend.

**D3 — Mono now, or block on stereo?**
**Recommended default: ship high-bitrate mono for v1**, run the custom-ADM stereo spike in parallel as a stretch goal. Stereo from an Android publisher is unproven; don't let it gate the MVP. Reassess after the spike.

**D4 — How to handle screen-lock?**
**Recommended default: rely on the audio-only exemption, no Pocket Mode.** Architecture rule: audio-only, never `createVirtualDisplay()`, never a video screen-share SDK. Gate the whole product on passing the on-device logcat test (§5) first. Add OEM battery-whitelisting UX.

**D5 — Fork AudioRelay's concept or build the capture layer fresh?**
**Recommended default: build fresh** on `sndcpy` (MIT) + `julioz/AudioCaptureSample` references, publishing through LiveKit's `ScreenAudioCapturer`. AudioRelay is closed/LAN-only/not forkable; it's your tonight-demo and UX benchmark, not a codebase.

**D6 — Distribution: sideload private vs Play Store?**
**Recommended default: sideload for v1** (avoids Play content review, prominent-disclosure, accessibility-review surface), but budget for **Android Developer Verification** (register a verified developer identity before the 2027 global rollout reaches Canada) and warn that an Advanced-Protection-Mode friend may be unable to install. If you ever want Play distribution, the full policy stack (mediaProjection FGS type, prominent disclosure, zero accessibility involvement) re-applies.

**D7 — Music-service ToS risk appetite.**
**Recommended default: low-exposure posture** — keep it private, ≤5 people, stream-only/never-record, don't publicize. Note this risk mostly applies to the non-DRM audio you *can* capture; the big three are silent, so they're moot. A real Canadian copyright opinion needs a lawyer if this ever goes commercial or public.

**D8 — Bluetooth sync expectations to set with users.**
**Recommended default: promise "roughly in sync," not "perfectly in sync."** State plainly that earbuds add latency the app can't control. Don't build BT-sync features; they require system-privileged APIs you can't access.

---

### Bottom line
Build it, Android-host + cross-platform-listener, on self-hosted LiveKit, audio-only so it survives the lock screen. The screen-lock make-or-break is **ACHIEVABLE** (verified across three AOSP code states, pending one on-device test). The real product-defining constraint is the **DRM capture wall**, which forces an honest scope pivot away from Spotify/Apple/YouTube Music toward local + non-DRM audio. Before writing architecture, run the three de-risking tests: **(1)** on-device screen-lock logcat, **(2)** apktool + live capture of the big three, **(3)** the custom-stereo-ADM spike. If (1) passes (expected) and you accept the (2) scope reality, the experience the founder wants — rotating DJ, friends hearing the host's actual audio, cross-platform, street, screen-locked — is shippable.
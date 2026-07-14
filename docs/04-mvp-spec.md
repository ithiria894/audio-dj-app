# MVP Spec — 先實錘技術核心,再堆功能

> Spec-first。範圍決定基於 `02-feasibility-report.md` + `03-competitive-report.md` + the founder 拍板。
> 原則:build feedback loop first;每個 milestone 證一件事先入下一個。唔 build 未 spec 嘅嘢。

## 範圍決定(the founder 拍板)
- **分發 = sideload APK,唔上 Google Play** → 冇 Play policy 顧慮,capture app 隨便裝。
- **Legal = 非問題**(私人、sideload、兩三個朋友、唔錄音;墳場啲 app 係死喺公開規模化經營 licensed catalog)。
- **Lane A(收窄版):rebroadcast「捕捉得到」嘅音源。** YouTube Music / Apple Music = opt-out 靜音(唔掂);本地檔 / podcast / VLC / 遊戲 / 瀏覽器播嘅 YouTube = 得;**Spotify = 未知,MVP 落機實測。**
- **Host = Android only**(iOS host 技術上冇可能)。Listener 之後做 Android + iOS native。
- **Transport = self-host LiveKit**(官方 `ScreenAudioCapturer` 直接 publish AudioPlaybackCapture PCM,唔手搓)。

## Milestone 0 — Capture Spike(而家做緊,證 #1 風險)
**證咩:**(a) Android `AudioPlaybackCapture` 喺 the founder 部機 capture 到播緊嘅聲;(b) 邊個音源 app 真係出到聲 vs 靜音(尤其 **Spotify**);(c) 音訊-only session 鎖屏後**唔停**(feasibility 話豁免,實機驗)。
**點證:**
- 一個 Activity:`開始擷取`(彈系統 MediaProjection 同意)/ `停止` 掣。
- Foreground service(`foregroundServiceType=mediaProjection`)行 `AudioRecord` + `AudioPlaybackCaptureConfiguration`(usage MEDIA/GAME/UNKNOWN,excludeUid 自己),48kHz stereo PCM16。
- 實時 **dB 音量錶**(RMS→dBFS,~10Hz 更新)—— 錶郁 = capture 到;平 = 靜音/被封。
- 錄頭 **~10 秒 WAV** 落 app 專屬目錄(`adb pull` 聽返做鐵證)。
- 通知常駐 + 狀態 log。
**通過準則:** the founder 播本地音樂,錶郁 + WAV 有聲;鎖屏後錶仍郁。逐個 app 播記低邊個出聲。

## Milestone 1 — 串流(證 transport)
Capture PCM → LiveKit `ScreenAudioCapturer` publish → self-host LiveKit SFU → 另一部機/browser listener 聽到。先 LAN,再過 internet(4G)。量延遲。

## Milestone 2 — 房間 + 跨平台 listener
開房 / 6-char code join / host 一個、listener 幾個;Android + iOS native listener,鎖屏 background 聽。

## Milestone 3 — 輪流 DJ + 打磨
`activeDJ` token(LiveKit canPublish flip,實測 runtime 升級可靠性);host mic 預設 OFF(避 A2DP→HFP);唔錄音、房自動過期。

## 已知 caveat(feasibility)
- LiveKit Android publisher 預設 **mono**;音樂 stereo 要落力(Milestone 1 處理)。
- 輪流 DJ runtime 升級有 bug 史 → 實測多 client。
- iOS listener 收音會拉起 voice-processing unit + mic 權限提示(非 trivial)。
- 鎖屏豁免只限**純音訊**(唔可以 createVirtualDisplay)。

## 工具鏈(實錘可 build)
JDK 21 Temurin(`~/.gradle/jdks/eclipse_adoptium-21-amd64-linux.2`)· Android SDK `~/android-sdk`(platform 36 / build-tools 36)· Gradle 8.11.1 · AGP 8.9.2 · Kotlin 2.0.21 · minSdk 29 / target 35 / compile 36。

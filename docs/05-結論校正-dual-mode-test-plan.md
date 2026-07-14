# 結論校正 + Dual-Mode 架構 + 落機測試計劃(權威版)

> 呢份 supersede `02-feasibility-report.md` 同 `03-competitive-report.md` 入面**過度肯定嘅結論**。
> 起因:the founder 帶咗一份高質 critique(附 12 條一手 source)。判斷:**研究方向 7/10,結論校準 4/10** —— 即係 workflow 捉到兩個真風險,但將「高風險、要實測/要律師」寫成咗「技術多數唔得、法律必死」。以下係校正後嘅立場。研究方法(raw JSON、query、scripts)全部喺 `research/`,本地可審。

## 校正對照表(採納 critique)

| 之前報告講法 | 校正後(準確版) | 依據 |
|---|---|---|
| Spotify/YTM 最可能封 capture → 靜音 | **誇張。現有實測反而顯示可 capture。** 準確講:Android 目前技術上相當有機會 capture 到,但係**第三方控制嘅不穩定依賴,唔係永久保證**(app 版本/OEM/Android 版本可變) | AudioRelay 相容表列 Spotify/YouTube/YTM/Deezer/VLC/Twitch/Pocket Casts 可擷取;Netflix/SoundCloud 有問題 |
| 鎖屏會令 capture 停(致命) | **真、係最大技術風險,要第一時間測。** 但有一個 nuance ↓ | Android 15 QPR1+ 鎖屏停 MediaProjection |
| (我哋 workflow 加嘅)純音訊 capture 豁免鎖屏停 | **AOSP 源碼有此 carve-out(`isExempt()` INVALID_DISPLAY),跨 3 分支核實 —— 但未落機驗,OEM 可能改咗,仲有省電殺 FGS 等其他 kill path。= 待實測嘅樂觀 hypothesis,唔可以當定論(唔好又反方向 over-calibrate)** | AOSP MediaProjectionStopController;spike 頭號任務就係驗呢個 |
| iOS 完全冇公開 API | **太絕。有 ReplayKit + Broadcast Upload Extension + `RPBroadcastSampleHandler`(有 `audioApp` buffer)。** 準確:iOS 冇一條似 Android AudioPlaybackCapture 咁清晰、可靠、可長背景、可擷取任意第三方 app 嘅路。iOS host 高風險、非 v1;iOS listener 標準 | Apple ReplayKit docs |
| 私房 rebroadcast 必然同時侵犯兩種版權 | **過度肯定。** 分三層:①平台 ToS/執法(最實在)②public performance 唔係見到 stream 就自動成立(睇固定小圈子 vs 公開、point-to-point 單次傳送 vs 規模重複)③reproduction:毫秒 jitter buffer、唔儲、唔 replay 是否「固定 copy」有司法細節。**風險高到影響商業模式,但唔係自動侵權** | 加最高院 point-to-point;US Aereo;US Cablevision/Cartoon Network buffer 案 |
| 墳場全部同一 licensing 死因 | **夾硬 narrative。** Groovy/Rythm=高度相關(平台 ToS 執法先例);Turntable=部分(licensing+economics,但「$7M 全花喺 royalty+律師」查唔到可靠 source=誇張演繹);plug.dj=財務/持續性;Rdio=完整 on-demand streaming,另一類生意,類比太遠 | Verge/Pitchfork/plugdj 官方/plug.dj |
| Stationhead patent 咗 synced-separate = 封死呢招 | **有專利但唔壟斷「同步播放」概念。** claims 係具體組合(music/voice channel、content ID、cataloging、account crediting、ad channel);是否落入要正式 freedom-to-operate 分析,後期 due diligence,唔係唔做 prototype 嘅理由 | US10761683B2 |
| Reddit demand「非常強」 | **證明有持續、跨 subreddit 嘅真實痛,但未證明願付費或市場夠大。** Jam 每月 ~1 億小時證「同步聽」係巨大行為,但未證「有人會為『一人 relay 任何平台聲畀朋友』畀錢」 | Spotify Jam 官方 |
| 「SharePlay +43% YoY」 | **抽走 —— 冇可靠 Apple 官方 source,似低質統計網站,唔應入報告** | (competitor workflow trend agent 引咗 sqmagazine,不可靠) |

## Dual-Mode 架構(採納 critique,取代我之前嘅 Lane A/B 二選一)

唔使一開始就犧牲核心體驗,又唔使賭 Spotify 永遠容許 capture:

**① Direct Relay(真「我聽乜你聽乜」)** — 用於:本地檔、自己擁有版權嘅音訊、podcast、網台、DJ set、容許 capture 嘅 app、**測試期嘅 Spotify/YTM(但唔公開承諾永久支援)**。

**② Sync Mode(fallback)** — 遇到禁止 capture 或正式商業音樂服務:host 傳歌曲 metadata/ISRC → listener 用自己可用嘅服務搵同一首 → 各自播但同步 playhead → 搵唔到就清楚顯示 unavailable。

App 自動偵測音源能否 capture,揀 mode。核心賣點(跨平台一齊聽)兩 mode 都保得住。

## 風險排序(校正版,由最易發生到最遠)
1. 平台 Terms of Service / 執法(封 API、律師信、下架)
2. App Store / Play 審核或投訴(但我哋 **sideload**,呢層大幅減)
3. 來源 app 改 capture policy(→ 靠 compatibility matrix + Sync Mode fallback 緩解)
4. 音樂版權 / 傳送 / 表演權責任
5. 規模大後權利人壓力

私人、邀請制、無錄音、無公開搜尋、無 content catalog → 事實形態比公共電台溫和,但**唔係法律豁免**。正式公開/收費前要畀熟 music licensing + platform terms + 加/美數碼傳送法嘅律師睇 architecture。**prototype 照做。**

## 落機測試矩陣(= critique 建議嘅「一星期做實驗,唔好再寫報告」;spike 已 build 好)

| 測試 | 必須記錄 |
|---|---|
| Spotify | 有冇聲、stereo/mono、切歌、廣告 |
| YouTube Music | app vs WebView、背景、切歌 |
| YouTube | 音樂片 vs 普通片、Premium vs 非 |
| 本地檔 | baseline |
| Pixel / Samsung | Android 14/15/16 |
| 螢幕暗(未鎖) | 可否持續 |
| 真正鎖屏(電源鍵) | 幾時被 stop(**驗音訊-only 豁免 hypothesis**) |
| Wi-Fi → 5G | reconnect 時間 |
| 藍牙耳機 | 有冇跌去 HFP 通話音質 |
| 3 個 listener | upload、延遲、電量、熱度 |

**成功門檻:** ①Spotify/YTM 至少兩款主流機穩定 capture 30 分鐘;②host 自己藍牙聽歌正常;③3 listener 延遲差 < ~0.5s;④Pocket Mode 避到誤鎖 + 耗電合理;⑤5G handover 自動恢復;⑥零 server-side 錄音/永久儲存。

## 最終判決(校正版)
- ✅ **綠燈:繼續做技術 spike + 上面測試矩陣。**(而家 Milestone 0 APK 已 build 好)
- 🟡 **未綠燈:用「Spotify retransmission」做公開商業承諾。** 要 compatibility matrix + dual-mode + 法律審查去降平台依賴先。
- ❌ 唔係「已被歷史證明必死」嘅 idea;係「值得實驗、要用工程 + 架構 + 法律去管風險」嘅 idea。

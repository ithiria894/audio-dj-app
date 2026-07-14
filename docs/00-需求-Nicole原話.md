# 需求 — Nicole 原話 (source of truth)

> 呢份係 Nicole 喺同 ChatGPT 對話入面**自己講嘅需求原話**，係成個 project 嘅真相源。
> ChatGPT 提出嘅技術方案係「claim」，要另外核實，唔可以當 evidence。
> 完整對話：`chatgpt-requirements-transcript.md`

## 一句話 north star

**一個 app，download 就用 → 開房 → 朋友撳條 link 就即刻聽到「你部手機而家播緊嘅任何歌」→ 可以輪流做 DJ → 兩三個朋友 → 喺街用手機 → 唔理大家用邊個音樂平台。**

## Nicole 逐點原話拆解

1. **核心體驗**：開咗個 app 就可以同時聽歌，好似有個 DJ 喺度播歌，其他人聽；或者輪流播歌。「即係可以逼人一齊聽歌噉樣。」
2. **音源 = 我部手機播緊嘅嘢**：啲歌係個人自己 playlist，或者「個人自己部手機播乜歌就係乜歌」。可能係 Apple Music 或其他 app，總之佢自己喺部手機度播嘅歌，就 stream 去平台畀人聽。
3. **規模好細**：唔係 broadcast 畀好多人睇，就兩三個 friend 同時開 app，一個人播或者輪流播。
4. **跨平台**：冇 Spotify。「我個 friend 喺 Spotify，我喺 YouTube Music 咁點啫？」→ 要跨音樂平台。
5. **關鍵定義（Nicole 自己講清楚咗）**：「總之手機播乜就 display 啲乜」「我隻/我個耳機聽乜，人哋就聽乜」→ 即係 **system audio streaming**，唔係「大家各自同步播同一首歌」。
6. **使用場景 = 喺街，手機主導**：「你冇理由坐喺電腦面前聽歌㗎嘛，通常都係喺街嘅時候用手機控制㗎啦。」→ 手機做 host 係首選；電腦做 host（好似 AI CLI host 喺電腦、手機做 client）係佢主動提出可以接受嘅退路。
7. **佢自己諗過嘅路**：問過「截取藍牙得唔得」（反正都要播去耳機，喺出街之前 intersect 一份）；問過 Android 會唔會容易啲、Accessibility 係唔係捷徑。
8. **Onboarding 要極簡（硬要求）**：「有冇得包裝成一個 app，人哋 download 就用得？定係要…呢個 onboarding setup 好撚多嘢煩㗎嘛係咪先？」→ 唔可以要用戶裝兩個 app / 登入 VPN / 揾 IP。

## ChatGPT 收斂到嘅方向（= 待核實嘅 hypothesis，唔係結論）

- 核心機制：Android `AudioPlaybackCapture` API（Android 10+），喺聲入藍牙耳機之前分叉一份 PCM；原聲照去耳機，官方話唔加 latency。
- 截藍牙 / Accessibility / root 都唔啱做上架 app（冇公開 API / 踩 Play policy）。
- 音源 app 有權封鎖 capture（capture policy）。Spotify 喺 Discord 被封；YouTube Music / VLC / Deezer 等可擷取。
- 網絡：WebRTC + **SFU**（唔用 P2P mesh，host 喺 4G 只 upload 一份）。選項：Agora（付費，`pushExternalAudioFrame` 最快原型）/ LiveKit 或自架 WebRTC SFU（可 self-host，較多底層整合）。
- 輪流 DJ = server 一個 token：`activeDJ`，只有佢可以 publish；接棒就交 token + 新 DJ 批准 MediaProjection。
- 同步：唔追最低 latency，畀每個 receiver 300–800ms 固定 playout buffer，用 host timestamp 校準。
- 藍牙：唔好長開咪，否則 A2DP 掉去 HFP 通話音質。v1 只傳 system audio、host mic 預設 OFF、文字 chat、要講嘢先 push-to-talk。
- **最大風險**：Android 15 QPR1+ 鎖屏會自動停 MediaProjection → 連 AudioPlaybackCapture 一齊停。對「喺街鎖屏聽」係致命。可能有 "Pocket Mode" workaround，但要實機測 Samsung/Pixel/Xiaomi/OnePlus。
- iOS host 好難（ReplayKit + Broadcast Upload Extension + DRM），v1 唔應該由 iPhone host 開始；iOS 做 listener 就冇問題。
- 落地次序：Step1 唔寫 code，用 AudioRelay + Tailscale 驗證體驗；Step2 Android-only MVP；Step3 iOS listener，最後先研究 iOS host。

## 我哋自己嘅立場（依 Nicole 原則）

- **Own it / 移除依賴**：傾向 **self-host SFU（LiveKit / mediasoup / raw libwebrtc）**，唔好綁死 Agora 付費 SaaS（可以隨時收費或消失）。研究要充分覆蓋 self-host 路。
- **用官方 SDK 唔好由零手寫**：Android capture 用官方 `AudioPlaybackCapture`；Opus 用官方 encoder；WebRTC 用 libwebrtc / 真 SFU，唔好手搓傳輸層。
- **Spec-first**：呢個 project non-trivial，先核實 + 寫 spec，再 code。
- **待核實**：上面每個 ChatGPT claim 都要對返 primary source（Android 官方文檔 / AOSP / GitHub issue / 官方 SDK doc），尤其鎖屏風險。

## 名（TBD）

Folder 用 working name `audio-dj-app`；正式名遲啲用 `/name-product` 或 Nicole 決定。
（概念關鍵字：pass the aux / 逼你一齊聽 / live DJ room。）

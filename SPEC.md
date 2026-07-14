# audio-dj-app — 項目 SPEC(living document)

> 單一真相源。一路做一路更新。任何 code 都要 trace 返呢份 spec 嘅某一行;唔喺 spec 嘅嘢 = 要 spec + benchmark 先加,唔好 code-first 塞。
> Working name `audio-dj-app`(未定名);概念關鍵字:pass the aux / 逼你一齊聽 / live DJ room。
> 相關文檔:`docs/00`需求原話 · `docs/02`技術可行性 · `docs/03`競品 · `docs/05`結論校正+dual-mode · `docs/06`capture 實測矩陣。

## 0. Changelog
- **2026-07-13** v0.1 初稿。已完成:需求、雙 workflow 研究(技術+競品)、結論校正、Android capture spike **落機實測(Pixel 8 Pro/Android 16)**。
- **2026-07-13** v0.2(Nicole 拍板):鎖屏結論 wording 修正(pipeline 存活 ≠ 鎖屏後仍有非靜音音流;拆出 M0.6);Stage 0 拆成 **0A LAN 驗證 / 0B 公網實測**;0A 用 `livekit-server --dev` 唔用 Docker-first、plain web listener 唔做 PWA、debug cleartext config;採納嚴格 0A acceptance(deterministic stereo 測試檔 + hash + BT + lock-through source + lifecycle);LiveKit Cloud 降為 **diagnostic 對照組**,own-it VPS 為正式目標。

---

## 1. 產品(咩 + 點解)

**North star:** 一個 app,download 就用 → 開房 → 朋友撳條 link 就即刻聽到「你部手機而家播緊嘅任何(可擷取)音源」→ 可輪流做 DJ → 跨平台 → 喺街手機用 → onboarding 極簡。「逼人一齊聽歌。」

**核心機制 = system audio streaming**(你聽乜、朋友聽乜),唔係「各自同步播同一首歌」。

**Target segment(beachhead):** 3-4 人 Gen-Z friend group,喺街「pass the aux」,跨 iPhone+Android + 跨音樂 service。LDR 情侶 = 高 intent 擴展(同一引擎、DJ 層 off)。避開 fandom broadcast(擠 + UMG/HYBE 資本)。

**雙 mode(避免 Lane A/B 二選一,見 `docs/05`):**
- **Direct Relay** — 真 rebroadcast:本地檔 / 自己擁權音訊 / podcast / 網台 / DJ set / 容許 capture 嘅 app(**實測 YouTube、YouTube Music 得**)。
- **Sync Mode(fallback,Stage 2+)** — 遇禁 capture 或正式商業服務:host 傳 metadata/ISRC,listener 各自播、同步 playhead,搵唔到就顯示 unavailable。

---

## 2. 已實錘嘅事實(de-risk 成果,Pixel 8 Pro / Android 16)
呢啲唔再係 hypothesis,係落機數據(`docs/06` + `research/results/*.wav`):
1. ✅ **Android `AudioPlaybackCapture` capture 到播緊嘅聲** —— 普通 YouTube(RMS -16.4dBFS)、YouTube Music(-15.3dBFS),**真立體聲**。
2. 🟡 **鎖屏:pipeline 存活已證,但「非靜音音流」未證**(M0.5 ✅ / M0.6 ⏳)。Pixel 8 Pro/Android 16 真鎖屏(`isKeyguardShowing=true`)期間:`AudioRecord`+level loop 繼續、`MediaProjection.onStop` 0 次 = **水管冇斷**。但因免費 YouTube 鎖屏自己暫停,capture 收到 -120dBFS = **未證「鎖屏後仲有水流」**。**要用鎖屏會繼續播嘅 source(本地/VLC/YTM Premium/ExoPlayer 測試源)+ 鎖屏 ≥5 分鐘 + 遠端 listener 持續收到非靜音,先算 PASS。** 記做**已測裝置行為,唔係跨 OEM/版本平台保證**(Android 官方文件仍寫 15 QPR1+ 一般 MediaProjection 鎖屏會停)。
3. ✅ capture 側係 true stereo(mono 隱憂只喺下游 LiveKit publish path,Stage 0A 驗)。

**推翻咗** feasibility 個「YTM opt-out 靜音」悲觀結論(Nicole 引 AudioRelay 相容表先啱)。教訓:落機實測係唯一裁決,唔好將「高風險」寫成「技術唔得」。

---

## 3. 架構 —— Two Planes(Nicole 定案,採納)

```
                          ┌──→ Friend A  (PWA listener)
 Android DJ/Host ────────→│
  system audio            │      LiveKit SFU        ← MEDIA PLANE(長開)
  → Opus/WebRTC           ├──→ Friend B  (PWA)         host 只 upload 一份,SFU 派畀所有人
  (1 份 upload)           │
                          └──→ Friend C  (PWA / native later)

 Android DJ  ──HTTPS──┐
 Friend PWA ──HTTPS──┤→  Token / Room API  ← CONTROL PLANE(細、serverless-able)
                      └   開房 / 派 token / 控制 activeDJ / 過期。**永不經手音樂。**
```

**兩個 backend 分清楚:**
- **Media plane = LiveKit SFU** — 真正轉送音樂。SFU = 低延遲 router,唔混音唔重編碼。**要長開**(Cloud 或自架 VPS)。手機喺街直連線上 LiveKit,**Nicole 唔使長開屋企電腦**。
- **Control plane = 自己個細 API** — 只開房 / 派短期 LiveKit JWT / 驗 invite / 控制 pass-DJ / 房過期。**唔 proxy / decode / record / buffer / store 任何音訊。** 幾乎冇流量,serverless 都得。

**Host 一定 native**(AudioPlaybackCapture 係 Android API,web/PWA/Capacitor 都做唔到 host capture)。**Listener 用 PWA**(撳 link 即聽,最啱)。

**唔用 P2P mesh**:host 要 upload N 份、NAT 穿透煩、仍要 signaling+STUN+TURN。SFU 一份 upload 解決,對 4G/5G host 關鍵。

---

## 4. 技術棧(定案)

| 層 | 選擇 | 理由 |
|---|---|---|
| Host | **Kotlin + Jetpack Compose + Coroutines/StateFlow**,minSdk 29 | AudioPlaybackCapture 要 API29;Compose 比 Capacitor+plugin 乾淨 |
| Host capture→RTC | **LiveKit Android SDK `ScreenAudioCapturer`**(底層 = AudioPlaybackCapture) | 官方有 `examples/screenshare-audio`,唔使手接 raw PCM 入 WebRTC(用官方 SDK 唔由零砌) |
| Listener | **React + TypeScript + Vite + `livekit-client` + `@livekit/components-react` + vite-plugin-pwa** | 撳 link 即入房;`StartAudio` component 處理 browser autoplay 限制 |
| Control API | **Node + TypeScript + Fastify + Zod + LiveKit Server SDK** | 細、AI 易維護;token 一定 server 出(secret 不可入 client) |
| DB | **無(Stage 0-1)**;需要時 Postgres + Drizzle | 單 node MVP 唔使;房 state 短暫 |
| Media transport | **LiveKit SFU** — Stage 0 Cloud,Alpha 自架 VPS | 換 endpoint 就得,client code 唔變 |
| Infra(own-it) | **1 VPS:Docker Compose = LiveKit + embedded TURN + Caddy(HTTPS/WSS) + API** | 唔使 Redis(單 node)、唔使 k8s |

---

## 5. 音訊 pipeline spec

```
來源 app → Android audio mixer ─┬─→ 藍牙耳機(host 自己聽,A2DP,原聲)
                                └─→ AudioPlaybackCapture(48kHz stereo PCM16)
                                      → LiveKit ScreenAudioCapturer → Opus → LiveKit track(1 份 upload)
                                        → SFU → listeners → 各自耳機
```

**Opus / audio 設定(音樂,唔係語音):**
- 48 kHz **stereo**;Opus **160 kbps 起步**(preset:Data Saver 96k / High Quality 160-192k)。唔用 510k(數據/發熱/丟包未測)。
- **DTX off、noise suppression off、echo cancellation off、AGC off** —— 開咗會將音樂當背景聲削走。
- **⚠️ 風險(我 adversarial 研究):LiveKit Android publisher 預設 mono,音樂級 stereo publish 未證(LiveKit #2101 closed not-planned)。** capture 側已實測 stereo;**Stage 0 必驗「stereo 真係去到 listener」,有 mono fallback。**
- 多 listener 同步:每 receiver 固定 playout buffer(唔追最低 latency);buffer 值 Stage 1 定。

**Capture path(Path B,產品目標)—— 見 `docs/adr/0002-audio-only-mediaprojection.md`:**
```
audio-only MediaProjection → ScreenAudioCapturer(= MixerAudioBufferCallback,唔係獨立 track)
  → LocalAudioTrack(只做 WebRTC transport carrier)→ 實體咪 recording 停用/隔離
  → 唔發 screen video、唔開 VirtualDisplay → publish source = SCREEN_SHARE_AUDIO
```
- **精準 wording**:「唔混 mic」= **唔擷取/唔傳送任何實體咪 sample**。**唔等於**冇 mic infrastructure —— LiveKit `LocalAudioTrack`、`RECORD_AUDIO` 權限、`microphone`-type foreground service **可能仍然需要**(ScreenAudioCapturer 背景輸出要 mic-type FGS,否則背景可能得靜音)。
- **Path A(baseline)**:官方 example(screen video + mic track)只做 transport proof 對照,**唔會**係 shipped 架構(會開 VirtualDisplay 破壞鎖屏 + 迫 A2DP→SCO)。

**藍牙 A2DP rule:**
- host mic 預設 off;gain=1.0f;NS/EC/AGC/high-pass/typing-detection/DTX 全 off(音樂)。
- **`AudioOptions(audioHandler=NoAudioHandler(), disableAudioPrewarming=true)`** —— NoAudioHandler 唔管 audio focus/routing,避免一 connect room 就搶 focus / 改 BT route。Gate 2 起就用。
- Gate 3 實驗 `JavaAudioDeviceModule.setAudioRecordEnabled(false)`(停實體咪,保留 custom system-audio callback)—— **必須實機驗 callback 仲行**,唔靠 setting 名判斷,要量 `AudioManager.mode` / BT profile / active device / listener PCM / mic 隔離。

---

## 6. 輪流 DJ(server 強制,唔靠 UI)

Token grants:
- **Listener:** `canSubscribe=true, canPublish=false`
- **Active DJ:** `canSubscribe=true, canPublish=true, canPublishSources=["screen_share_audio"]`

**Pass DJ(A→B):** ①API 鎖 room row ②A `canPublish=false`(LiveKit 自動 unpublish A 條 track)③B `canPublish=true` ④更新 `activeDjIdentity` ⑤通知全房 ⑥B 開始 Android capture。即使有人改 client code 都唔可以偷偷同時播。
- **⚠️ 風險:runtime 升 DJ(flip canPublish)有 bug 史(LiveKit swift #244 / js #1314)→ 跨 client 實測,唔當 clean。**

---

## 7. 部署階段

| 階段 | Media | Control | 其他 | 目的 |
|---|---|---|---|---|
| **Stage 0A(LAN 驗證)** | **`livekit-server --dev --bind 0.0.0.0`** 喺開發電腦(devkey/secret;`ws://<LAN-IP>:7880`)。**唔用 Docker-first**(Docker networking/UDP 唔好阻住第一次音訊驗證;通過後先固化 `infra/livekit/docker-compose.yml`) | 本地細 token endpoint(`POST /dev/token`),devkey/secret **只喺電腦、絕不入 APK/bundle** | **plain React web listener(唔做 PWA)**;debug-only network_security_config 容許 cleartext ws://(放 `src/debug/`,release 一定 TLS);無 DB/accounts/invite/pass-DJ | 最快驗 3 件最重要事:①LiveKit 端到端 stereo ②藍牙 A2DP ③接 RTC 後鎖屏 + latency/reconnect。**同 Wi-Fi 永遠驗唔到 5G/CGNAT/TURN/切網,所以 0A ≠ 完整 Stage 0** |
| **Stage 0B(公網實測)** | **一部短期 VPS 自架 LiveKit**(真 domain + 可信 TLS + embedded TURN + Caddy) | 同上(暫可 local/簡單) | — | 驗 5G↔Wi-Fi handover、CGNAT、TURN fallback、2-3 遠端 listener、30 分鐘、背景/鎖屏、uplink bitrate/loss/jitter |
| **Stage 1(private alpha)** | 同 VPS LiveKit | 加細 TS API(Fastify,serverless/細 container,**唔喺 media path**) | 私人房、invite、max 5、pass-DJ、房過期 | 真 MVP 功能 |

- **LiveKit Cloud = diagnostic 對照組**(VPS 卡住時判斷係 client code 定 self-host networking / benchmark / 災難恢復),**唔做產品依賴**。啱 own-it。
- Cloud↔self-host 只換 `LIVEKIT_URL`/keys env,client code 唔可以寫任何 Cloud 專屬邏輯。
- **PWA trap:** service worker/安裝需 HTTPS 安全環境;LAN IP ≠ localhost 例外。所以「可安裝 PWA / iOS Safari / 背景鎖屏播 / deep link」全部留 **Stage 0B(真 HTTPS)** 先驗,唔好喺 0A 整本地自簽 CA 浪費時間。
- **Android 17 note:** target SDK 37+ 連 LAN 要 `ACCESS_LOCAL_NETWORK` runtime permission。Pixel 8 Pro(Android 16)暫時唔受影響,但 compat checklist 要記,將來升 target SDK 唔好突然連唔到本地 LiveKit。
- E2EE(LiveKit media track 端對端加密)= Stage 1+(key 分發要自己 API 管)。

---

## 8. 私隱 / 法律 model
- **唔錄音、唔開 LiveKit Egress、唔寫音訊落磁碟。** 房完 = 音訊冇咗。
- **Sideload 分發,唔上 Google Play** → 冇 Play policy 顧慮。
- 私人、邀請制、無公開搜尋、無 content catalog、max 5 人 → 事實形態比公共電台溫和。
- 風險排序(見 `docs/05`):ToS 執法 > store 審核(sideload 已減) > 來源改 capture policy(→ compat matrix + Sync Mode) > 版權/表演權 > 規模壓力。
- **prototype/私人試 = 冇實務風險;正式公開/收費前先畀 music-licensing + platform-terms 律師睇 architecture。** 唔用 Accessibility/root/截藍牙硬繞。

---

## 9. 已知風險 & caveat(逐個 Stage 0 驗)
1. **Stereo publish 去唔去到 listener**(LiveKit Android 預設 mono)—— 有 mono fallback。
2. **藍牙 A2DP→HFP**(LiveKit audio session 一開可能迫 host 落通話音質)—— 可能要自訂 ADM。
3. **DJ 音源要支援鎖屏播**(capture 過到鎖屏,但免費 YouTube source 會停)。
4. **runtime 交 DJ 可靠性**(canPublish flip bug 史)。
5. iOS host = 冇可能(ReplayKit 只自己 app+mic);iOS listener = 得(拉起 voice-processing unit + mic 提示,非 trivial)。
6. 來源 app 隨時改 capture policy → 靠 compat matrix + Sync Mode。

---

## 10. Repo 結構(monorepo)
```
audio-dj-app/
├── apps/
│   ├── android-host/     (Kotlin/Compose;capture/rtc/rooms/diagnostics)
│   └── web-listener/     (React/TS/Vite PWA)
├── services/
│   └── api/              (Fastify token/room/DJ control)
├── packages/
│   └── protocol/         (版本化 JSON events,e.g. {version,type:"dj.changed",roomId,activeDjIdentity,effectiveAt})
├── infra/
│   ├── docker-compose.yml
│   └── livekit/          (self-host:LiveKit+TURN+Caddy)
├── docs/                 (00-06 + architecture/audio-capture-matrix/privacy/adr)
└── research/             (demand/competitor scripts + results,已有)
```
> 現有 `android/`(capture spike)= Stage 0 起點,之後併入 `apps/android-host/`。

---

## 11. Project board / milestones
```
M0       Local capture proof(capture + stereo,落機)        ✅
M0.5     Lock survival, pipeline only(onStop=0)             ✅ tested-device (Pixel 8 Pro/A16)
M0.6     Non-silent remote audio after lock                 ⏳
Stage 0A LiveKit over LAN                                    ⏳ ← 而家
  ├ Gate 1  Web listener signaling(token/CORS/state/canPublish=false)  ✅
  ├ Gate 2  Android signaling(connect DJ token, publishedTracks=0)     ⏳
  ├ Gate 3  First audible publish(Path B)                              ⏳
  ├ Gate 4  Objective stereo(L/R tone + listener PCM + SDP stats)      ⏳
  └ Gate 5  Bluetooth A2DP + true-lock non-silent + 15min + lifecycle  ⏳
Stage 0B LiveKit over public internet(VPS)                 ⏳
Stage 1  Private-room MVP                                    未開始
Stage 2  Native listeners / background / Sync Mode           未開始
```
> ⚠️ 唔可以寫成「三大風險全部破解 → 開始整完整產品」。目前最準確結論:**核心 Android capture 概念非常有希望;而家用最簡單本地 LiveKit 打通端到端音訊鏈,通過後即上公網 VPS 驗真網絡條件。**

**Stage 0A acceptance(嚴格,全部要證據唔係「聽到有聲就算」):**
1. **端到端音訊** source→AudioPlaybackCapture→LiveKit Android→本地 SFU→browser→出聲,**連續 ≥15 分鐘**。
2. **真端到端 stereo**:播 deterministic 測試檔(0-5s 左1kHz右靜 / 5-10s 右500Hz左靜 / 10-15s 左右不同頻)→ listener 端擷 PCM 驗:左段冇大量漏右、右段冇大量漏左、冇 downmix mono、SDP/WebRTC stats 見 Opus stereo negotiation、capture WAV + listener WAV 都有 SHA-256。
3. **藍牙 A2DP**:記錄 連 LiveKit 前/後 AudioManager mode + BT profile/route + 主觀音質 + host 自己聽到嘅聲。Pass = 唔跌 SCO/HFP、唔開咪、唔搶 audio focus 令來源停、host 仍正常聽。
4. **真鎖屏 + 非靜音 + 遠端收到**(= M0.6):用鎖屏續播 source → capture → listener 收到 → 真鎖屏 → 等 5 分鐘 → listener 持續非靜音 → onStop=0。
5. **Lifecycle cleanup**:停止後 MediaProjection/AudioRecord released、track unpublished、通知消失、第二次 session 成功、冇殘留 route/重複 publishing。
6. **唔做**:accounts、chat、playlist、public room、pass-DJ、payment;**LAN 通過唔可以宣稱 Stage 0 完成**。

**Stage 0B(0A 一通過即做):** 公網 VPS 自架 LiveKit(domain+可信TLS+embedded TURN+Caddy)→ host 5G、listener 另一網絡 → Wi-Fi↔5G handover、CGNAT、TURN fallback、2-3 listener、30 分鐘、背景/鎖屏、uplink bitrate/loss/jitter。
**Stage 1:** 私人房、invite link、max 5、pass DJ、request DJ、連線質素、音量 meter、「source 不支援」提示、text chat、reaction、房過期;加細 API(serverless,唔喺 media path)。
**Stage 2:** native iOS/Android listener、可靠背景/鎖屏播、lock-screen controls、deep-link、Sync Mode。iOS host 排最後。

---

## 12. Compat / test matrix
見 `docs/06-capture-compat-matrix.md`(已有實測:YouTube ✓、YT Music ✓、鎖屏 ✓ @Pixel8Pro/Android16)。待補:本地檔、podcast、藍牙(接 LiveKit 後)、5G handover、其他機/OEM。

---

## 13. Open decisions
- 正式產品名(遲啲 `/name-product`)。
- Playout buffer 值 / stereo-vs-mono fallback 門檻(Stage 0 數據定)。
- self-host VPS provider + region(Alpha 前)。

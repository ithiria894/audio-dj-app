# Audio Capture Compatibility Matrix(落機實測)

> 架構 spec 要求嘅 `audio-capture-matrix.md`。呢啲係**第一手落機數據**,唔係 web report。
> 工具:`android/` 嘅 AuxCapture spike(AudioPlaybackCapture 48kHz stereo)。方法:播歌 → 量 RMS dBFS + 存 10 秒 WAV。
> WAV 證物:`research/results/capture-test-*.wav`。可重跑。

## 測試機
- **Google Pixel 8 Pro**
- **Android 16(SDK 36)** ← 最新、MediaProjection/鎖屏規則最嚴嘅版本

## 結果

| 音源 | 結果 | RMS | Stereo | 備註 |
|---|---|---|---|---|
| 普通 YouTube(app) | ✅ **CAPTURED** | -16.4 dBFS | TRUE STEREO | dB 直接跟音樂郁;`capture-test-youtube.wav` |
| **YouTube Music** | ✅ **CAPTURED** | -15.3 dBFS | TRUE STEREO | 撳 play @15s 即捉到;`capture-test-ytmusic.wav` |
| Spotify | ⬜ 未測 | — | — | Nicole 冇裝(冇 account) |
| 本地檔 player | ⬜ 未測 | — | — | 待測 baseline |
| Podcast app | ⬜ 未測 | — | — | 待測 |

### 🔒 鎖屏測試(Android 16,最大風險)—— ✅ CAPTURE SURVIVED
- 部機真正鎖咗(`isKeyguardShowing=true, mAwake=false`)。
- 鎖屏 16 秒期間:level 行程照每秒 log(16 條)、`MediaProjection.onStop()` **0 次** → **capture pipeline 冇被殺**。
- **裁決:純音訊 AudioPlaybackCapture 豁免 Android 15 QPR1+/16 嘅鎖屏停,喺 Pixel 8 Pro/Android 16 實錘成立。** feasibility 個 AOSP hypothesis 得到落機確認。
- ⚠️ caveat:鎖屏後 level→靜音,因為**免費 YouTube 自己暫停**(source 層)。capture 冇死。產品上 DJ 音源要本身支援鎖屏播(本地/Premium/VLC)。

## 關鍵結論
1. **Nicole 兩個真實音源(普通 YouTube + YouTube Music)喺 Pixel 8 Pro / Android 16 都 capture 到,而且真立體聲。** 核心「你聽乜、朋友聽乜」機制實錘成立。
2. **推翻咗 feasibility workflow 個「YTM opt-out 靜音」結論** —— 嗰個係 web report 過度悲觀;Nicole 引 AudioRelay 相容表(列 YTM 可 capture)先啱。**落機實測 = 唯一裁決,結果係 optimistic 嗰邊。** 呢個正好印證咗 critique:唔好將「高風險」寫成「技術唔得」。
3. capture 側係 **true stereo**(L-R 有真差異),即係 mono 隱憂唔喺 capture,而係下游 LiveKit publish path(待 Stage 1 驗)。

## 仲要測(按重要性)
| # | 測試 | 點解重要 |
|---|---|---|
| 1 | **真正鎖屏(電源鍵)喺 Android 16** | 成個 project 最大 UX 風險。feasibility 讀 AOSP 揾到「純音訊豁免鎖屏停」,但 Android 16 正正係規則最硬嗰版 → 呢部機實測係最權威嘅裁決 |
| 2 | 螢幕熄但未鎖 | Pocket Mode 可行性 |
| 3 | 藍牙耳機 | host 自己聽歌會唔會跌 A2DP→HFP(尤其接 LiveKit 之後) |
| 4 | 本地檔 / podcast | baseline + 覆蓋率 |
| 5 | Wi-Fi → 5G | reconnect(接 LiveKit 之後) |

**下一步大 de-risk = #1 鎖屏測試**(即刻做得),然後接 LiveKit 令 listener 真係聽到。

# Reddit Demand 驗證 findings

> 方法:經 agent Chrome logged-in browser session(唔用 raw curl,繞 403)跑 22 個 keyword×subreddit search,
> 232 條 relevant thread → 180 條有正 demand-intent → 抽 top 14 comment tree。
> 可重跑:`research/reddit_demand_scan.py` → `rank_demand.py` → `pull_top_threads.py`;raw 存 `research/results/`。
> 日期:2026-07-13。

## 判決:**有真實、重複、跨社群嘅需求。** ✅

唔係一兩個人心血來潮。同一個痛喺 r/spotify、r/androidapps、r/LongDistance、r/discordapp、r/AppIdeas、r/YoutubeMusic 反覆出現,
而且**一批又一批 indie dev 各自造過**(spotifybuddy、Play2Gether、Spotify Together、spicetify Listen Together、Rave…)——
呢個「反覆有人自己動手整」係最強嘅 demand 訊號:痕到有人肯無償寫 app。

## 5 個核心 demand pattern(附原話 + link)

### 1. 平台鎖死 = universal 痛點(正正你個 thesis)
現有方案幾乎全部要**大家都 Spotify Premium**。唔係 Spotify / 免費 / 本地檔嘅人被鎖死。
- r/spotify「Social extension…」:*"the limit of 5 friends, and the fact that people who I don't share the link with can't join is a bummer. Moreover, when I share music with a friend they need to have Spotify too."* — https://reddit.com (score 129)
- r/androidapps:*"I just really want to listen to music together with my girlfriend, but we will have to pay for Spotify premium?"* (score 67 thread)
- r/spotify:*"Is there any way to listen to music together, neither of us have premium accounts."*

### 2. YouTube Music / 非-Spotify 用戶明確被遺棄(= 你嘅 cross-platform 缺口)
- r/YoutubeMusic「Listen to YTM together, in sync」:*"I've always been looking for a way to listen to YTM with friends, since the down of Plug.dj back in the days, but couldn't find any good apps. Spotify has Spotify Jam and Apple has Apple SharePlay, but nothing for YouTube Music :("*
  - 回覆狂求 mobile + 跨 OS:*"A mobile app would be awesome"* / *"any possibility of mobile support?"* / *"share between MacOS and Windows also"* — https://reddit.com (score 26)

### 3. 人哋而家用「倒數一齊撳 play」/ Discord 頂住 —— workaround 全部有硬傷
- r/LongDistance「Ways to listen to music together?」workaround 一覽:
  - *"I use discord to play youtube playlists while my boyfriend and I are in a call"*(desktop only)
  - *"There is watch2gether.com and it works for YT videos"*(淨係 YouTube)
  - *"if nothing works you both can access it however you can and just do a **countdown before you press play**"* ← **赤裸裸嘅痛**
- 通用 workaround = Discord screen+audio share:desktop-only、封 Spotify、手機版廢 —— 同 ChatGPT 講嘅一致。

### 4. 輪流做 DJ 係人哋**未經提示**就想要嘅玩法
- r/AppIdeas「I'm the DJ now」:*"An app where you can go online and be in some sort of party. You and your Friends can switch turns on being the DJ (playing songs)."* — 完全就係你講嘅 rotating DJ。
- r/androidapps「passing the aux cord」frustration(16 歲仔造咗 Juke Pro,score 160)—— "pass the aux" 呢個 frame 有真實文化共鳴。

### 5. 極簡 onboarding 係贏家賣點(你嘅硬要求 = 對嘅)
- spicetify「Listen Together」賣點:*"no accounts, no setup, just a **6-character code**"* —— 正正你要嘅 download-就用。
- spotifybuddy 賣點:*"easy link sharing / **no need to download an app**"*。

## 最強 target segment:LDR 情侶
r/LongDistance + r/LDR demand 密度最高、最有感情(「music date」「同 partner 背景一齊聽仲可以傾偈」)。
呢個 segment:①痛到肯試新 app ②有付費意欲(情侶願意畀錢維繫)③口碑傳播強。**建議第一個 beach-head 就打 LDR。**

## 藍牙痛點都自然浮面(驗證咗技術隱憂)
- r/discordapp:*"it kept stopping playback when I got in calls"*(Spotify listen-along + call 撞)
- 另一條 r/discordapp Bluetooth headphones + game/voice 出事 —— 即係 ChatGPT 講嘅 A2DP↔HFP 通話音質跌 + audio focus 搶播 係真用戶痛,唔係理論。

## Demand 對你需求嘅對應
| 你嘅需求 | Reddit 有冇人想要 | 證據強度 |
|---|---|---|
| 跨平台(唔限同一 music service) | **狂想**,universal 第一痛 | 🔥🔥🔥 |
| 手機用(喺街) | 明確求 mobile,現有多數 desktop/web | 🔥🔥🔥 |
| 兩三個朋友私人房 | LDR/friend group 主流用例 | 🔥🔥🔥 |
| 輪流做 DJ | 未提示都有人講 | 🔥🔥 |
| 極簡 onboarding(download 就用) | 贏家都主打「no account / code」 | 🔥🔥🔥 |
| 真 rebroadcast(播乜聽乜) | 需求在,但無人 cross-platform 做到(見競品 report) | 🔥🔥 |

## 未做 / 下一步(唔好過度自信)
- Demand 係「想要一齊聽 + 跨平台」= 強;但「肯裝一個要開 system-audio 權限嘅 app」嘅意願未直接驗證 → beta 先測。
- 未量化市場大細(只係質性訊號);未睇 App Store review 規模 → 交畀競品 workflow。
- Reddit 個 agent Chrome 未 login 落 account(`/api/me.json` 403),但公開 read 足夠;要更深 comment tree 先需要 login。

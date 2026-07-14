# 競品市場分析報告 (competitor + graveyard + trend)

> 來源:audio-dj-competitor-research workflow (6 agents, Opus, 2026-07-13)。原始 per-agent findings 見 workflow journal。

# Competitive Analysis: Phone-Hosted Live Audio Rebroadcast for 2-3 Friends (Rotating DJ, Cross-Platform)

*Synthesis of 5 research lenses. Product under test: "my phone plays any source (YT Music / Apple / Spotify / local), 2-3 friends hear the EXACT live audio in real time, rotating DJ, cross-platform, phone-first on-the-go, one-app dead-simple onboarding."*

---

## 1. Competitor comparison table

Sorted so **true-rebroadcast** products (the ones that actually do what our idea does) sit at the top, then screen-share, then the synced-separate camp that dominates by volume.

| Product | Mechanism | Platforms | Price | Status | Key complaint |
|---|---|---|---|---|---|
| **Pulse 2.0** | True-rebroadcast (WebRTC/LiveKit capture) | Web, **desktop host only** | Free | Alive | Host must install BlackHole/VB-Cable virtual driver; no mobile host; only demos non-label audio (radio/DJ sets) to dodge licensing ([HN 46081443](https://news.ycombinator.com/item?id=46081443)) |
| **AudioRelay** | True-rebroadcast (real app/system audio) | Android, Win, Linux — **no iOS host** | Free + Pro | Alive | LAN/power-user server-client tool; no social or DJ layer; no iOS sender ([audiorelay.net](https://audiorelay.net/)) |
| **Airfoil** (Rogue Amoeba) | True-rebroadcast | **Mac/PC host**; iOS/Android receivers | ~$35 | Alive | Host tethered to a Mac/PC — cannot host from a phone on the go; no DJ layer ([rogueamoeba.com](https://www.rogueamoeba.com/airfoil/mac/)) |
| **SonoBus** | True-rebroadcast (P2P Opus/PCM) | iOS, Android, Mac, Win, Linux | Free (OSS) | Alive | Built for musicians; no music-source integration, no rooms/DJ, not consumer-simple ([sonobus.net](https://sonobus.net/)) |
| **Discord bots (Groovy, Rythm)** | True-rebroadcast (YouTube → voice) | Discord | Free | **DEAD** | C&D'd offline by Google/YouTube in 2021 — the canonical "unlicensed rebroadcast at scale gets killed" case ([HN 28317084](https://news.ycombinator.com/item?id=28317084)) |
| **Discord Go Live / screen-share** | Screen/system-share | Desktop, browser, mobile | Free + Nitro | Alive | Desktop/Chrome-centric; **mobile audio capture is flaky/limited**; no music UX, no rotating DJ ([support.discord.com](https://support.discord.com/hc/en-us/articles/360040816151-Go-Live-and-Screen-Share)) |
| **Kosmi** | Screen/system-share (virtual browser) | Browser, iOS, Android | Free + premium | Alive | Watch-party tool; music is a side use; not phone-audio rebroadcast ([kosmi.io](https://kosmi.io/)) |
| **Spotify Jam** | Synced-separate | iOS, Android, Desktop, Auto | Host Premium; **every remote guest also Premium** | Alive | #1 category complaint: everyone needs their own Premium; sync drift; Spotify-only ([jukeboxduo.com](https://jukeboxduo.com/spotify-jam-without-premium)) |
| **Apple Music SharePlay** | Synced-separate | Apple ecosystem + web | Apple Music sub | Alive | Apple-locked, **Android excluded**; per-listener subscription ([apple.com](https://support.apple.com/en-us/108767)) |
| **Stationhead** | Synced-separate *(see reconciliation note)* | iOS, Android, web | Every listener needs own Premium/Apple | Alive | **2.46★ / ~22k on Play** despite ~2.4M installs; no Android hosting; glitchy; fandom-skewed ([justuseapp](https://justuseapp.com/en/app/1076117681/stationhead/reviews)) |
| **Hangout.fm** (Turntable revival) | Synced-separate (own licensed catalog) | Web, iOS, Android | Free ($8.2M VC) | Alive/Zombie | Locked to its **own** catalog — you can't bring Spotify/YT/local/DJ mix; publicly still needs funding "to be legal" ([hypebot](https://www.hypebot.com/hypebot/2024/08/turntable-returns-as-hangout.html)) |
| **Vertigo Music** | Synced-separate | iOS, Android | Spotify Premium OR Apple Music | Zombie | Must link own paid account; little recent activity ([macworld](https://www.macworld.com/article/229599/vertigo-now-lets-apple-music-members-share-music-with-friends-on-spotify.html)) |
| **JQBX** | Synced-separate | iOS, Android, desktop | Spotify Premium (all) | Zombie | Abandoned its DJ-room core; absorbed into Turntable 2023 ([musically](https://musically.com/2023/04/14/turntable-live-acquires-fellow-social-music-startup-jqbx/)) |
| **AmpMe** | Synced-separate (co-located speaker array) | iOS, Android | Freemium (predatory subs) | Alive | Same-room "louder together" toy, **not remote rebroadcast**; ~$13M fake-review/scam-pricing scandal; sync drift ([TechCrunch](https://techcrunch.com/2022/01/12/music-app-ampme-lowers-pricing-after-accused-of-being-an-app-store-scammer/)) |
| **Groic** | Synced-separate | Android, iOS, web | Free (India) / Pro | Alive | "No Premium" only by using a non-licensed catalog; iOS paywall trap; sync drift ([Play Store](https://play.google.com/store/apps/details?id=com.pscube.groic)) |
| **plug.dj** | Synced-separate (YT/SC embeds) | Web | Free/donation | Dead/Zombie | Went broke repeatedly (2015, 2021); browser-only; video-sync not audio ([Wikipedia](https://en.wikipedia.org/wiki/Plug.dj)) |
| **Rave** | Synced-separate | Android, desktop, TV (**iOS pulled Aug 2025**) | Freemium | Zombie | Lost iOS availability; video-first ([kosmi blog](https://blog.kosmi.io/p/how-to-install-rave-on-ios-and-iphone)) |

*Not true competitors (name/category collisions), excluded from analysis: OutLoud (single-speaker jukebox voting, not remote), SoundShare (Mac Bluetooth multi-headphone utility), ListenTogether/jofr (hobby OSS PWA, free catalog only), Frisson (music logging), Sesh.fm (collaborative DAW).*

**Two contradictions in the source lenses, reconciled** (4-vs-1 and original-vs-revival):
- **Stationhead mechanism.** Four lenses classify it as synced-separate; one (trend-mainstreaming) labeled it true-rebroadcast. The documented, *patented* mechanism is synced-separate: each listener connects their **own** Spotify Premium/Apple Music account and their device streams the track, so "every listener counts as one stream" ([graveyard lens; DMN Series A](https://www.digitalmusicnews.com/2022/07/14/stationhead-series-a/)). **Verdict: synced-separate.** The single outlier label is wrong.
- **Turntable.fm vs Hangout.fm.** The *original* (2011-13) was server-side broadcast of a licensed catalog — one stream, everyone hears it — which is why it hit the licensing wall. The *2024 Hangout revival* deliberately switched to synced-separate to stay legal. Both states shown above.

---

## 2. The gap — and are we "just Discord/AmpMe"?

**The precise combination NO product satisfies at once:**

> true-rebroadcast of the host's **actual audio from ANY source** (incl. Spotify/Apple/YT/local/DJ mix) **+ hosted live from a phone on the go + genuinely cross-platform iOS↔Android in one room + rotating-DJ social layer + dead-simple one-app onboarding with NO per-guest subscription and NO virtual-audio-cable install.**

Every product fails on at least one axis, and the failures cluster cleanly:

- **Everything that does true rebroadcast fails "phone-host + simple + social."** Airfoil needs a Mac/PC host. AudioRelay/SonoBus are LAN/power-user server-client tools with no iOS host and no DJ layer. Pulse 2.0 is desktop-only and needs BlackHole/VB-Cable. None have a rotating-DJ room.
- **Everything social/consumer fails "true rebroadcast + no per-guest sub + cross-service."** The entire synced-separate camp (Jam, SharePlay, Stationhead, Vertigo, JQBX, Hangout) structurally requires every participant to hold a paid sub on the **same** service and locks the room to that catalog. A Spotify host literally cannot co-listen with an Apple Music friend, and a friend who pays for nothing hears nothing.

So on paper, **yes — the full five-way intersection is genuinely empty.** But "brutally honest" requires naming *why* it's empty and how close the two obvious substitutes get:

**vs AmpMe → not the same product.** AmpMe is co-located speaker-sync: it makes several phones in the *same room* louder together, each playing from *its own* source. It is synced-separate, not remote, not one-source rebroadcast. Different category. We are not AmpMe.

**vs Discord → this is the real substitute, and the honest answer is uncomfortable.** Discord's screen/system-share *does* true-rebroadcast host audio to friends who pay for nothing — MakeUseOf calls it "the most reliable tool" for listening together for free ([makeuseof](https://www.makeuseof.com/tag/listen-music-friends-far-away/)). Our differentiation over Discord is **packaging, not a new capability**: phone-native hosting (Discord's mobile audio capture is flaky/desktop-bound), a purpose-built music/rotating-DJ UX, and dead-simple onboarding. That is a real wedge, but it is a **UX/form-factor wedge over an existing capability**, not a defensible technical secret. And Discord already demonstrates the landmine underneath it: its rebroadcast music bots were C&D'd out of existence.

**Bottom line:** The idea is differentiated on the *full* combination, and the on-the-go + cross-platform + one-source angle is a genuine hole the incumbents refuse to cross (they have no incentive to bridge services they compete on). But the intersection is empty **for reasons, not by oversight** — it sits on top of two unsolved walls (licensing + phone audio-capture) that have killed or crippled everyone who attempted true rebroadcast. We are "Discord's rebroadcast, rebuilt phone-native and music-shaped," which is a positioning wedge, not a moat.

---

## 3. The graveyard lesson — does our private / no-recording / capture model dodge the licensing death?

**Did licensing/cost kill the predecessors? Overwhelmingly yes, and the pattern is monotonous.**

- **Turntable.fm** spent "more than a quarter of our cash on lawyers, royalties and services," couldn't afford international licenses (geo-blocked to US, usage fell two-thirds), and died Dec 2013 because per-stream content cost outran monetization ([failory](https://www.failory.com/cemetery/turntable-fm), [hypebot](https://www.hypebot.com/hypebot/2013/11/turntablefm-to-shut-down.html)).
- **Rdio** — a *fully licensed* service — still bled ~$2M/month on royalties into 2015 bankruptcy; Sony later sued over unpaid royalties ([Billboard](https://www.billboard.com/music/music-news/rdio-bankruptcy-story-how-it-happened-failing-streaming-service-7519014/)).
- **Groovy/Rythm** were C&D'd by Google/YouTube in 2021 for rebroadcasting to groups with no license ([HN](https://news.ycombinator.com/item?id=28317084)).
- **plug.dj** used YT/SoundCloud embeds to *avoid* licensing bills and still went broke on ops ([Wikipedia](https://en.wikipedia.org/wiki/Plug.dj)).

**The survival pattern is singular:** every durable player (Stationhead $12M Series A + UMG stake, Vertigo, Jam, SharePlay) uses **synced-separate-playback**, where the app sends only "play track X at time T" and each device plays from its *own already-licensed* account — so no new license is ever needed. That is the entire trick, and Stationhead patented it.

**Does our model dodge the death? Clear verdict: PARTIALLY, and not the part that matters most.**

Our capture-and-retransmit model is on the **same side of the wall as Turntable**, not the safe side. Whether you server-broadcast a catalog (Turntable) or capture the host's device audio and retransmit it (us), you are performing and reproducing the sound recording to a group. The synced-separate camp is safe precisely because it *never* moves audio between people.

What the "private / 2-3 close friends / ephemeral / no-recording" framing genuinely buys us:
- **It dodges the SCALE death** (the per-stream royalty burn that bankrupted Turntable and Rdio), because we are not operating a licensed catalog service.
- **It is the strongest available legal argument among rebroadcast models.** The public-performance right explicitly covers "a group outside a normal circle of family and social acquaintances." A genuinely tiny, invite-only room of 2-3 *real* friends is far more defensible as inside that "normal circle" than a public DJ room of strangers ([graveyard lens legal analysis](https://uslawexplained.com/public_performance_right)).

What it does **NOT** dodge, and this is the make-or-break:
1. **The sound-recording reproduction right.** Even if the private-performance exception held, the act of capturing and retransmitting the master may itself be an unauthorized reproduction. Untested.
2. **Source-platform ToS — the faster kill switch.** Spotify/Apple/YouTube ToS independently prohibit capturing and retransmitting their streams. They don't need to win a copyright argument; they enforce a contract (cut API access, ban accounts, C&D). This is exactly how YouTube killed Groovy/Rythm — a ToS/rights action, not a courtroom.
3. **It cannot scale.** The moment rooms stop being provably small/private/ephemeral, we hit the identical wall that killed everyone.

**And a wall the source lenses under-weighted — the phone audio-capture wall** `[CHECKED — platform API behavior, not runtime-verified this session; recommend a technical spike before any build commit]`:
- **iOS gives an app no public API to tap another app's audio output.** You cannot capture "whatever Spotify/Apple Music is playing" system-wide and rebroadcast it.
- **Android's AudioPlaybackCapture (API 29+) exists but the playing app can opt out**, and DRM/protected content is not capturable. Spotify, YT Music, and Apple Music are the exact apps most likely to block capture.
- The provided research corroborates the root cause: even on **desktop**, Pulse 2.0 requires a BlackHole/VB-Cable virtual driver because the OS won't let an app freely tap another app's output ([HN 46081443](https://news.ycombinator.com/item?id=46081443)). Phones are *more* locked down, not less.

**Strategic verdict:** The "capture the EXACT audio of Spotify/Apple from a phone and rebroadcast it" promise is the load-bearing risk of the entire concept, and it is doubly exposed — legally grey **and** likely technically blocked for the marquee sources. The realistic buildable v1 is Pulse's constrained lane made phone-native: **rebroadcast only what the host is allowed to and technically able to capture** — local files, user uploads, internet radio, podcasts, DJ/live sets, YouTube via the host's own playback — not DRM'd Spotify/Apple streams. **Decide the source model and run the capture technical spike BEFORE writing product code. The whole graveyard is products that shipped the experience before solving the rights.**

---

## 4. Tailwind or headwind — and who to target first

**STRONG TAILWIND.** The behavior has moved from gimmick to first-class feature, and every curve points up:
- Spotify Jam hit **100M monthly listening hours** by Aug 2025, expanded to 42 participants + Desktop + Android Auto, and wired real-time co-listening into Messages in Jan 2026 ([Spotify newsroom](https://newsroom.spotify.com/2025-08-25/jam-reaches-100-million-monthly-listening-hours/)).
- Apple Music SharePlay usage **+43% YoY** ([sqmagazine](https://sqmagazine.co.uk/apple-music-statistics/)).
- **Gen-Z behavior:** nearly half attended an in-person listening party; collaborative playlists +41% among under-30 ([Spotify Culture Next](https://newsroom.spotify.com/2024-11-04/culture-next-2024-the-major-gen-z-trends-that-are-shaping-audio-streaming/), [onestowatch](https://resources.onestowatch.com/genz-discovers-new-music-2026/)).
- Fandom/broadcast layer at industrial scale (Weverse 52k+ listening parties, 12M MAU; TikTok+Apple Music listening parties Feb 2026) ([MBW](https://www.musicbusinessworldwide.com/hybe-says-weverse-hit-12m-monthly-users-last-year-and-that-its-turning-casual-fans-into-superfans/)).
- The one "death," TikTok Music, was a **pivot into** listen-together (partnering with Apple Music), not away from it ([musically](https://musically.com/2026/02/16/tiktok-teams-up-with-apple-music-to-play-full-songs-in-its-app/)).

**Segment to target first: tight Gen-Z friend groups (3-4 people) doing "pass the aux on the go."** Name it plainly — *the commute / walk / park / pregame moment where three friends want one shared live soundtrack across mixed iPhone+Android and mixed music services.* Rationale:
- It is the exact seam the incumbents serve *worst*: Jam is proximity/Premium-gated, SharePlay is Apple-locked. Cross-platform + one-source + on-the-go is their blind spot.
- The rotating-DJ mechanic **needs 3+ people** to be fun (turn-taking), so this segment fits the product spec natively.

**Note on the couples signal:** the trend lens flags LDR couples as the *highest-intent* unmet segment (a whole cottage industry of sync apps serves them badly). That is real, but a 2-person couple doesn't "rotate DJ." Treat couples as the **high-intent expansion** the same rebroadcast engine serves with the DJ layer off ("we both hear the exact same live audio"), not the beachhead. **Avoid fandom broadcast head-on** — it's crowded and capital-backed (UMG/HYBE).

---

## 5. Positioning

**One-sentence differentiation:**
> The only phone-hosted, cross-platform app where 2-3 friends hear the **exact same live audio streaming from one person's phone** — whatever's playing, whoever they subscribe to — and take turns as DJ, with no per-guest subscription and no PC or virtual-audio-cable setup.

**Target user:** tight-knit Gen-Z friend groups of 3-4 who already "pass the aux," on the go, across mixed iPhone/Android devices and mixed (or no) music subscriptions.

**Top 3 features that would let us win vs the incumbents** (each maps to a documented, unsolved complaint):

1. **Zero-friction phone hosting.** Host and rebroadcast straight from the phone — no Mac/PC, no BlackHole/VB-Cable, no per-guest subscription. This beats Airfoil (Mac host), AudioRelay/SonoBus (LAN), Pulse (desktop + virtual driver), and the entire synced-separate camp's per-guest-Premium wall in one move. **Hard caveat:** gated by the capture wall in §3 — v1 source model must be local files / uploads / radio / podcasts / DJ sets / host-played YouTube, **not** DRM'd Spotify/Apple. Validate with a spike first.
2. **True cross-service + cross-platform in one room.** iPhone host, Android guest hears it, nobody else needs a subscription — the host is the single source, guests just listen. This attacks the category's #1 universal complaint ("everyone needs Premium / same service"), which no purpose-built app solves ([jukeboxduo](https://jukeboxduo.com/spotify-jam-alternative)).
3. **Sub-second sync + a rotating-DJ social layer built for small groups.** Sync drift is the other universal complaint ("I hear the chorus, my friend's on the verse"); nail it, and pair it with lightweight turn-taking DJ / shared-queue rooms designed for 3-4 friends on the go — the casual small-group experience the fandom-broadcast incumbents (Stationhead, Weverse) structurally ignore.

**Governing constraint on all three:** decide the licensing + source-capture model *before* building. The differentiation is genuine, the tailwind is strong, but the wedge lives in a legally-grey, technically-constrained lane. Ship the source-and-rights decision first, the experience second.
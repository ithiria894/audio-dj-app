#!/usr/bin/env python3
"""
Re-rank the raw Reddit demand pool by DEMAND INTENT, not raw engagement.
Reads results/reddit_demand_raw.json (no browser needed), scores each thread by how
much it reads like a real person WANTING this product, writes results/reddit_demand_ranked.json.
Run: python3 rank_demand.py
"""
import json, os

D = os.path.join(os.path.dirname(__file__), "results")
rows = json.load(open(os.path.join(D, "reddit_demand_raw.json")))["rows"]

STRONG = ["is there an app", "any app", "looking for an app", "app that lets", "app that would",
          "wish there was", "wish there were", "somebody make", "someone make", "does anyone know an app",
          "need an app", "recommend an app", "recommend me an app", "how can i listen", "how do we listen",
          "way to listen together", "app to listen", "app where", "an app to", "is there a way",
          "any way to", "app for listening", "app to stream", "app that streams", "app idea"]
MEDIUM = ["long distance", "long-distance", "different app", "different platform", "cross platform",
          "cross-platform", "she uses spotify", "he uses spotify", "i use youtube music", "i use apple music",
          "at the same time", "in sync", "real time", "real-time", "same song at the same",
          "listen together", "listen to music together", "listen along", "with my partner",
          "with my girlfriend", "with my boyfriend", "with friends", "pass the aux", "be a dj"]
NAMED = ["ampme", "jqbx", "stationhead", "spotify jam", "group session", "shareplay", "share play",
         "watch2gether", "airfoil", "sonobus", "audiorelay", "vertigo", "plug.dj", "turntable",
         "discord", "rave app", "kosmi", "syncplay", "soundshare", "outloud"]
GOOD_SUBS = {"somebodymakethis", "appideas", "androidapps", "apphookup", "longdistance", "ldr",
             "spotify", "discordapp", "youtubemusic", "software", "sideproject"}
NOISE_SUBS = {"aitah", "amitheasshole", "relationship_advice", "bestofredditorupdates", "tifu",
              "mildlyinfuriating", "popculturechat", "gratefuldead", "goosetheband", "eurovision",
              "destinythegame", "brit", "hyperx"}
NOISE_TITLE = ["aita", "tifu", "setlist", "megathread", "live thread", "update:", "[live"]


def score(r):
    t = (r["title"] + " " + r.get("self", "")).lower()
    s = 0
    s += 4 * sum(k in t for k in STRONG)
    s += 2 * sum(k in t for k in MEDIUM)
    s += 1 * sum(k in t for k in NAMED)
    if r["sub"].lower() in GOOD_SUBS:
        s += 4
    if r["sub"].lower() in NOISE_SUBS:
        s -= 8
    if any(k in r["title"].lower() for k in NOISE_TITLE):
        s -= 6
    # a title that is a question is usually a real ask
    if "?" in r["title"]:
        s += 1
    return s


for r in rows:
    r["intent"] = score(r)

ranked = sorted(rows, key=lambda x: (x["intent"], x["comments"]), reverse=True)
ranked = [r for r in ranked if r["intent"] > 0]
json.dump(ranked, open(os.path.join(D, "reddit_demand_ranked.json"), "w"), ensure_ascii=True, indent=1)

print(f"{len(ranked)} threads with positive demand-intent (of {len(rows)} relevant)\n")
print("--- TOP 30 BY DEMAND INTENT ---")
for r in ranked[:30]:
    snip = " ".join(r.get("self", "").split())[:150]
    print(f"[{r['intent']:>2}] r/{r['sub'][:16]:16} s={r['score']:>5} c={r['comments']:>4} | "
          f"{r['title'][:72].encode('ascii','replace').decode()}")
    if snip:
        print(f"       ↳ {snip.encode('ascii','replace').decode()}")

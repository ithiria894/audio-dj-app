#!/usr/bin/env python3
"""
Demand scan for the "phone plays -> friends hear it live, rotating DJ, cross-platform"
app idea. Reads Reddit through the logged-in agent-Chrome session (CDP), one browser
connection, many searches -> dedup -> relevance filter -> rank -> pull comment trees.

Run:  uv run --with websocket-client python3 reddit_demand_scan.py
Out:  results/reddit_demand_raw.json (all hits) + results/reddit_demand_top.json (shortlist + comments)
"""
import json, time, os, sys
from reddit_cdp import CDP

OUTDIR = os.path.join(os.path.dirname(__file__), "results")
os.makedirs(OUTDIR, exist_ok=True)

# (query, subreddit or "" for global). Short keyword queries — Reddit relevance is bad on long ones.
SEARCHES = [
    ("listen to music together long distance", ""),
    ("listen to music together app", ""),
    ("share what I'm listening to", ""),
    ("listen along with friends", ""),
    ("stream my music to friends", ""),
    ("pass the aux app", ""),
    ("listen to same song at same time friends", ""),
    ("broadcast my music to friends app", ""),
    ("listen to music together different apps", ""),
    ("app to DJ for friends online", ""),
    ("listen to music", "longdistance"),
    ("listen together", "longdistance"),
    ("music together", "longdistance"),
    ("listen to music together", "SomebodyMakeThis"),
    ("listen music friends", "AppIdeas"),
    ("listen together", "androidapps"),
    ("listen together", "apphookup"),
    ("listen together friend", "spotify"),
    ("listen to music together", "discordapp"),
    ("listen party audio", "spotify"),
    ("share music real time", "Music"),
    ("listen to music with partner", "LDR"),
]

MUSIC = ("music", "song", "audio", "aux", "spotify", "playlist", "dj", "listen", "sound", "tune")
SOCIAL = ("together", "friend", "distance", "partner", "share", "broadcast", "along",
          "sync", "same time", "remote", "with my", "with your", "each other", "group")


def _san(o):
    """Drop lone UTF-16 surrogates (broken emoji halves from CDP) so UTF-8 dump/print won't crash."""
    if isinstance(o, str):
        return o.encode("utf-8", "ignore").decode("utf-8")
    if isinstance(o, list):
        return [_san(x) for x in o]
    if isinstance(o, dict):
        return {k: _san(v) for k, v in o.items()}
    return o


def relevant(title, self_text):
    t = (title + " " + self_text).lower()
    return any(m in t for m in MUSIC) and any(s in t for s in SOCIAL)


def search(c, query, sub, limit=25):
    base = ("/r/%s/search.json?restrict_sr=on&" % sub) if sub else "/search.json?"
    js = ("const u=%r + 'q=' + encodeURIComponent(%r) + '&limit=%d&sort=relevance&t=all';"
          "const r=await fetch(u,{credentials:'include'});"
          "if(r.status!==200) return JSON.stringify({status:r.status,results:[]});"
          "const j=await r.json();"
          "return JSON.stringify({status:r.status,results:(j.data&&j.data.children||[])"
          ".map(x=>({sub:x.data.subreddit,title:x.data.title,score:x.data.score,"
          "comments:x.data.num_comments,created:x.data.created_utc,"
          "self:(x.data.selftext||'').slice(0,800),url:'https://reddit.com'+x.data.permalink}))});"
          ) % (base, query, limit)
    try:
        return json.loads(c.evalfetch(js))
    except Exception as e:
        return {"status": "err", "err": str(e)[:200], "results": []}


def thread(c, perma, limit=40):
    p = perma.replace("https://reddit.com", "").replace("https://www.reddit.com", "").rstrip("/")
    js = ("const u=%r+'.json?limit=%d&sort=top';"
          "const r=await fetch(u,{credentials:'include'});"
          "if(r.status!==200) return JSON.stringify({status:r.status});"
          "const j=await r.json();const post=j[0].data.children[0].data;"
          "const cmts=(j[1].data.children||[]).filter(x=>x.kind==='t1')"
          ".map(x=>({author:x.data.author,score:x.data.score,body:(x.data.body||'').slice(0,600)}));"
          "return JSON.stringify({title:post.title,self:(post.selftext||'').slice(0,1500),"
          "score:post.score,sub:post.subreddit,num_comments:post.num_comments,"
          "comments:cmts.slice(0,15)});") % (p, limit)
    try:
        return json.loads(c.evalfetch(js))
    except Exception as e:
        return {"status": "err", "err": str(e)[:200]}


def main():
    c = CDP()
    c.open_reddit()
    seen, hits, errs = {}, [], []
    try:
        for q, sub in SEARCHES:
            r = search(c, q, sub)
            if r.get("status") != 200:
                errs.append({"q": q, "sub": sub, "status": r.get("status"), "err": r.get("err")})
                continue
            kept = 0
            for row in r["results"]:
                if not relevant(row["title"], row.get("self", "")):
                    continue
                u = row["url"]
                if u not in seen or row["score"] > seen[u]["score"]:
                    row["found_via"] = f"{sub or 'all'}:{q}"
                    seen[u] = _san(row)
                    kept += 1
            hits.append({"q": q, "sub": sub or "all", "total": len(r["results"]), "relevant_kept": kept})
            print(f"[{sub or 'all':16}] {q[:40]:40} -> {len(r['results'])} hits, {kept} relevant")
            time.sleep(0.4)

        allrows = sorted(seen.values(), key=lambda x: (x["comments"], x["score"]), reverse=True)
        json.dump({"query_log": hits, "errors": errs, "rows": allrows},
                  open(os.path.join(OUTDIR, "reddit_demand_raw.json"), "w"), ensure_ascii=True, indent=1)
        print(f"\n=== {len(allrows)} unique relevant threads; {len(errs)} query errors ===")

        top = allrows[:18]
        for t in top:
            t["thread"] = _san(thread(c, t["url"]))
            time.sleep(0.5)
        json.dump(top, open(os.path.join(OUTDIR, "reddit_demand_top.json"), "w"),
                  ensure_ascii=True, indent=1)
        print(f"pulled comment trees for top {len(top)}")
        print("\n--- TOP THREADS ---")
        for t in top:
            print(f"  r/{t['sub']:18} score={t['score']:>6} cmts={t['comments']:>5} | {t['title'][:75].encode('ascii','replace').decode()}")
    finally:
        c.close()


if __name__ == "__main__":
    main()

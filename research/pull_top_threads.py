#!/usr/bin/env python3
"""
Pull comment trees for the top demand-intent threads (one browser session).
Reads results/reddit_demand_ranked.json, pulls the top N genuine-ask threads,
saves results/reddit_demand_threads.json.
Run: uv run --with websocket-client python3 pull_top_threads.py [N]
"""
import json, os, sys, time
from reddit_cdp import CDP

D = os.path.join(os.path.dirname(__file__), "results")
N = int(sys.argv[1]) if len(sys.argv) > 1 else 14
ranked = json.load(open(os.path.join(D, "reddit_demand_ranked.json")))


def _san(o):
    if isinstance(o, str):
        return o.encode("utf-8", "ignore").decode("utf-8")
    if isinstance(o, list):
        return [_san(x) for x in o]
    if isinstance(o, dict):
        return {k: _san(v) for k, v in o.items()}
    return o


def thread(c, perma, limit=40):
    p = perma.replace("https://reddit.com", "").replace("https://www.reddit.com", "").rstrip("/")
    js = ("const u=%r+'.json?limit=%d&sort=top';"
          "const r=await fetch(u,{credentials:'include'});"
          "if(r.status!==200) return JSON.stringify({status:r.status});"
          "const j=await r.json();const post=j[0].data.children[0].data;"
          "const cmts=(j[1].data.children||[]).filter(x=>x.kind==='t1')"
          ".map(x=>({author:x.data.author,score:x.data.score,body:(x.data.body||'').slice(0,700)}));"
          "return JSON.stringify({num_comments:post.num_comments,comments:cmts.slice(0,15)});") % (p, limit)
    try:
        return json.loads(c.evalfetch(js))
    except Exception as e:
        return {"status": "err", "err": str(e)[:150]}


c = CDP()
c.open_reddit()
out = []
try:
    for r in ranked[:N]:
        tr = _san(thread(c, r["url"]))
        out.append({"title": r["title"], "sub": r["sub"], "score": r["score"],
                    "comments": r["comments"], "intent": r["intent"], "url": r["url"],
                    "self": r.get("self", ""), "thread": tr})
        cc = len(tr.get("comments", [])) if isinstance(tr, dict) else 0
        print(f"[{r['intent']:>2}] r/{r['sub'][:16]:16} ({cc} cmts) {r['title'][:60].encode('ascii','replace').decode()}")
        time.sleep(0.5)
    json.dump(out, open(os.path.join(D, "reddit_demand_threads.json"), "w"), ensure_ascii=True, indent=1)
    print(f"\nsaved {len(out)} threads -> results/reddit_demand_threads.json")
finally:
    c.close()

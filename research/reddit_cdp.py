#!/usr/bin/env python3
"""
Reddit research via the logged-in agent-Chrome session (CDP), NOT raw curl.

Why: raw `curl reddit.com/*.json` returns 403 / surface-only + rate-limited.
Fetching from inside the logged-in browser session (same-origin, real cookies)
returns full data with no throttling. This is the deep-research skill HARD RULE.

Talks to agent Chrome on port 9223 (CDP_PORT_FILE=~/.config/agent-chrome/DevToolsActivePort).
Run with:  uv run --with websocket-client python3 reddit_cdp.py <mode> ...

Modes:
  login                         -> print logged-in reddit username (or null)
  search "<query>" [limit] [sub]-> global or subreddit search.json
  thread "<permalink>"          -> full post + comment tree (self text + top comments)
"""
import json, sys, time, urllib.request

PORT = 9223


def http_json(path):
    return json.load(urllib.request.urlopen(f"http://localhost:{PORT}{path}", timeout=8))


class CDP:
    def __init__(self):
        import websocket  # from websocket-client
        ver = http_json("/json/version")
        # Chrome rejects CDP WS handshakes that carry an Origin header unless it
        # matches --remote-allow-origins. suppress_origin=True sends no Origin -> accepted.
        self.ws = websocket.create_connection(ver["webSocketDebuggerUrl"], max_size=None,
                                              timeout=40, suppress_origin=True)
        self._id = 0

    def send(self, method, params=None, sessionId=None):
        self._id += 1
        msg = {"id": self._id, "method": method, "params": params or {}}
        if sessionId:
            msg["sessionId"] = sessionId
        self.ws.send(json.dumps(msg))
        while True:  # skip events (no "id"), return the matching response
            resp = json.loads(self.ws.recv())
            if resp.get("id") == self._id:
                if "error" in resp:
                    raise RuntimeError(resp["error"])
                return resp.get("result", {})

    def open_reddit(self):
        t = self.send("Target.createTarget", {"url": "about:blank"})
        tid = t["targetId"]
        sid = self.send("Target.attachToTarget", {"targetId": tid, "flatten": True})["sessionId"]
        self.send("Page.enable", sessionId=sid)
        self.send("Runtime.enable", sessionId=sid)
        self.send("Page.navigate", {"url": "https://www.reddit.com/"}, sessionId=sid)
        time.sleep(4.5)  # let origin + cookies settle
        self._sid, self._tid = sid, tid
        return sid

    def evalfetch(self, js_body):
        expr = "(async () => { %s })()" % js_body
        r = self.send("Runtime.evaluate",
                      {"expression": expr, "awaitPromise": True, "returnByValue": True},
                      sessionId=self._sid)
        if r.get("exceptionDetails"):
            raise RuntimeError(json.dumps(r["exceptionDetails"])[:500])
        return r["result"].get("value")

    def close(self):
        try:
            self.send("Target.closeTarget", {"targetId": self._tid})
        except Exception:
            pass
        self.ws.close()


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "login"
    c = CDP()
    c.open_reddit()
    try:
        if mode == "login":
            js = ("const r=await fetch('/api/me.json',{credentials:'include'});"
                  "let d=null;try{d=await r.json();}catch(e){}"
                  "return JSON.stringify({status:r.status, user:(d&&d.data)?d.data.name:null});")
            print(c.evalfetch(js))

        elif mode == "search":
            q = sys.argv[2]
            limit = sys.argv[3] if len(sys.argv) > 3 else "25"
            sub = sys.argv[4] if len(sys.argv) > 4 else ""
            base = ("/r/%s/search.json?restrict_sr=on&" % sub) if sub else "/search.json?"
            js = ("const u=%r + 'q=' + encodeURIComponent(%r) + '&limit=%s&sort=relevance&t=all';"
                  "const r=await fetch(u,{credentials:'include'});const j=await r.json();"
                  "return JSON.stringify({status:r.status, count:(j.data&&j.data.children||[]).length,"
                  "results:(j.data&&j.data.children||[]).map(x=>({sub:x.data.subreddit,title:x.data.title,"
                  "score:x.data.score,comments:x.data.num_comments,created:x.data.created_utc,"
                  "self:(x.data.selftext||'').slice(0,600),url:'https://reddit.com'+x.data.permalink})) });"
                  ) % (base, q, limit)
            print(c.evalfetch(js))

        elif mode == "thread":
            perma = sys.argv[2]
            if perma.startswith("https://reddit.com"):
                perma = perma[len("https://reddit.com"):]
            if perma.startswith("https://www.reddit.com"):
                perma = perma[len("https://www.reddit.com"):]
            js = ("const u=%r.replace(/\\/$/,'')+'.json?limit=40&sort=top';"
                  "const r=await fetch(u,{credentials:'include'});const j=await r.json();"
                  "const post=j[0].data.children[0].data;"
                  "const cmts=(j[1].data.children||[]).filter(x=>x.kind==='t1').map(x=>({author:x.data.author,"
                  "score:x.data.score,body:(x.data.body||'').slice(0,700)}));"
                  "return JSON.stringify({title:post.title,self:(post.selftext||'').slice(0,1500),"
                  "score:post.score,sub:post.subreddit,comments:cmts.slice(0,20)});") % perma
            print(c.evalfetch(js))
        else:
            print("unknown mode", mode)
    finally:
        c.close()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Drive agent Chrome (CDP :9223): open a fresh tab at URL, eval JS, print JSON result.
Used for headless Stage 0A web verification (localhost secure context).
Usage: uv run --with websocket-client python3 cdp.py <url> "<js_expr>" [wait_seconds]
"""
import json, sys, time, urllib.request

PORT = 9223


def http_json(p):
    return json.load(urllib.request.urlopen(f"http://localhost:{PORT}{p}", timeout=8))


class CDP:
    def __init__(self):
        import websocket
        ver = http_json("/json/version")
        self.ws = websocket.create_connection(ver["webSocketDebuggerUrl"], max_size=None,
                                              timeout=40, suppress_origin=True)
        self._id = 0

    def send(self, method, params=None, sid=None):
        self._id += 1
        m = {"id": self._id, "method": method, "params": params or {}}
        if sid:
            m["sessionId"] = sid
        self.ws.send(json.dumps(m))
        while True:
            r = json.loads(self.ws.recv())
            if r.get("id") == self._id:
                if "error" in r:
                    raise RuntimeError(r["error"])
                return r.get("result", {})

    def open(self, url):
        tid = self.send("Target.createTarget", {"url": "about:blank"})["targetId"]
        sid = self.send("Target.attachToTarget", {"targetId": tid, "flatten": True})["sessionId"]
        self.send("Page.enable", sid=sid)
        self.send("Runtime.enable", sid=sid)
        self.send("Page.navigate", {"url": url}, sid=sid)
        self._sid, self._tid = sid, tid

    def eval(self, expr):
        r = self.send("Runtime.evaluate",
                      {"expression": expr, "awaitPromise": True, "returnByValue": True},
                      sid=self._sid)
        if r.get("exceptionDetails"):
            return {"__exception__": json.dumps(r["exceptionDetails"])[:400]}
        return r["result"].get("value")

    def close(self):
        try:
            self.send("Target.closeTarget", {"targetId": self._tid})
        except Exception:
            pass
        self.ws.close()


if __name__ == "__main__":
    url, expr = sys.argv[1], sys.argv[2]
    wait = float(sys.argv[3]) if len(sys.argv) > 3 else 5.0
    c = CDP()
    c.open(url)
    time.sleep(wait)
    print(json.dumps(c.eval(expr)))
    c.close()

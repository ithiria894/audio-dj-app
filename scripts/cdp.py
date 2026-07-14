#!/usr/bin/env python3
"""Drive agent Chrome (CDP :9223) — persistent tabs for Stage 0A web verification.
suppress_origin=True is required (Chrome rejects a default Origin header on CDP).
Port 9223 must stay localhost-only (see docs/dev/browser-automation.md).

Subcommands (targetId persists across invocations, so open once then eval many times):
  open  <url>              -> opens a tab, prints its targetId (does NOT close)
  eval  <targetId> "<js>"  -> attaches to that tab, prints JSON result of the expr
  close <targetId>         -> closes the tab
  once  <url> "<js>" [wait]-> open, wait, eval, close (one-shot; default wait 5s)
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

    def create(self, url):
        return self.send("Target.createTarget", {"url": url})["targetId"]

    def attach(self, tid):
        sid = self.send("Target.attachToTarget", {"targetId": tid, "flatten": True})["sessionId"]
        self.send("Runtime.enable", sid=sid)
        return sid

    def eval(self, sid, expr):
        r = self.send("Runtime.evaluate",
                      {"expression": expr, "awaitPromise": True, "returnByValue": True}, sid=sid)
        if r.get("exceptionDetails"):
            return {"__exception__": json.dumps(r["exceptionDetails"])[:400]}
        return r["result"].get("value")

    def close_target(self, tid):
        self.send("Target.closeTarget", {"targetId": tid})

    def ws_close(self):
        self.ws.close()


def main():
    cmd = sys.argv[1]
    c = CDP()
    try:
        if cmd == "open":
            print(c.create(sys.argv[2]))
        elif cmd == "eval":
            tid = sys.argv[2]
            print(json.dumps(c.eval(c.attach(tid), sys.argv[3])))
        elif cmd == "close":
            c.close_target(sys.argv[2])
            print("closed")
        elif cmd == "once":
            wait = float(sys.argv[4]) if len(sys.argv) > 4 else 5.0
            tid = c.create(sys.argv[2])
            time.sleep(wait)
            print(json.dumps(c.eval(c.attach(tid), sys.argv[3])))
            c.close_target(tid)
        else:
            print("unknown subcommand", cmd)
    finally:
        c.ws_close()


if __name__ == "__main__":
    main()

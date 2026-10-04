import json
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path += [HERE, os.path.join(HERE, "training")]
from features import run_features
from predict import load_model, replay_with_fix, explain
from search_fix import hybrid_order, anomaly, search_fix

PORT = 8000
model, base, seen = load_model()
rows = {}
for line in open(os.path.join(HERE, "dataset", "traces.jsonl")):
    r = json.loads(line)
    rows[r["run_id"]] = r
failed = [r for r in rows.values() if r["split"].startswith("test") and not r["success"]]
_summary = None


def analyze(r):
    order = [int(i) for i in hybrid_order(model, base, seen, r)]
    feats = run_features(r, base)
    an = anomaly(r, base, seen)
    k = order[0]
    attempts = []
    for i in order[:3]:
        st, ok = replay_with_fix(r, i)
        attempts.append({"step": i, "fixed": bool(ok), "rerun": len(st)})
        if ok:
            break
    st, ok = replay_with_fix(r, k)
    steps = []
    for i, s in enumerate(r["steps"]):
        d = {x: s[x] for x in ["idx", "type", "tool", "latency_ms", "tokens",
                               "confidence", "retrieval_score", "error", "output"]}
        d["anomaly"] = min(float(an[i]), 10.0)
        steps.append(d)
    return {"run_id": r["run_id"], "fault_type": r["fault_type"], "truth": r["root_cause_step"],
            "suspect": k, "ranking": order[:3], "steps": steps,
            "evidence": explain(r, feats, k, seen), "attempts": attempts,
            "replay_rerun": len(st), "replay_ok": bool(ok),
            "original": r["steps"][-1]["output"], "replayed": st[-1]["output"],
            "expected": r["task"]["expected"]}


def summary():
    global _summary
    if _summary is None:
        agg = {}
        for r in failed:
            attempt, rerun = search_fix(r, model, base, seen)
            s = agg.setdefault(r["fault_type"], {"n": 0, "at1": 0, "at3": 0, "rerun": 0, "full": 0})
            s["n"] += 1
            s["at1"] += attempt == 1
            s["at3"] += attempt > 0
            s["rerun"] += rerun
            s["full"] += len(r["steps"])
        _summary = [{"fault": f, "runs": s["n"], "fixed1": s["at1"] / s["n"],
                     "fixed3": s["at3"] / s["n"], "cost": s["rerun"] / s["full"]}
                    for f, s in sorted(agg.items())]
    return _summary


class Handler(BaseHTTPRequestHandler):
    def reply(self, body, ctype="application/json"):
        b = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if u.path == "/":
            page = open(os.path.join(HERE, "web", "index.html"), "rb").read()
            return self.reply(page, "text/html; charset=utf-8")
        if u.path == "/api/runs":
            return self.reply([{"run_id": r["run_id"], "fault_type": r["fault_type"]}
                               for r in sorted(failed, key=lambda r: r["run_id"])])
        if u.path == "/api/run":
            r = rows.get(int(q.get("id", ["-1"])[0]))
            if r and not r["success"]:
                return self.reply(analyze(r))
        if u.path == "/api/summary":
            return self.reply(summary())
        self.send_response(404)
        self.end_headers()

    def log_message(self, *a):
        pass


print(f"Black Box running at http://localhost:{PORT}  (Ctrl+C to stop)")
HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()

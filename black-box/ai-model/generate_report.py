import json
import os
import sys
import html
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.append(HERE)
sys.path.append(os.path.join(HERE, "training"))
from features import run_features
from predict import load_model, replay_with_fix, explain, TRACES
from search_fix import hybrid_order, search_fix

model, base, seen = load_model()
rows = [json.loads(l) for l in open(TRACES)]
failed = [r for r in rows if r["split"].startswith("test") and not r["success"]]

# ---- results table ----
stats = defaultdict(lambda: {"n": 0, "at1": 0, "atK": 0, "rerun": 0, "full": 0})
for r in failed:
    attempt, rerun = search_fix(r, model, base, seen)
    s = stats[r["fault_type"]]
    s["n"] += 1
    s["at1"] += attempt == 1
    s["atK"] += attempt > 0
    s["rerun"] += rerun
    s["full"] += len(r["steps"])

table = ""
for ft in sorted(stats):
    s = stats[ft]
    table += (f"<tr><td>{ft}</td><td>{s['n']}</td><td>{s['at1']/s['n']:.0%}</td>"
              f"<td>{s['atK']/s['n']:.0%}</td><td>{s['rerun']/s['full']:.0%}</td></tr>")
m1 = sum(s["at1"] / s["n"] for s in stats.values()) / len(stats)
m3 = sum(s["atK"] / s["n"] for s in stats.values()) / len(stats)
mc = sum(s["rerun"] / s["full"] for s in stats.values()) / len(stats)
table += (f"<tr class='avg'><td>equal-weighted average</td><td></td><td>{m1:.0%}</td>"
          f"<td>{m3:.0%}</td><td>{mc:.0%}</td></tr>")


# ---- one card per example run ----
def card(r):
    order = [int(i) for i in hybrid_order(model, base, seen, r)]
    k, truth = order[0], r["root_cause_step"]
    feats = run_features(r, base)
    ev = "".join(f"<li>{html.escape(e)}</li>" for e in explain(r, feats, k, seen))
    steps, ok = replay_with_fix(r, k)
    attempt, _ = search_fix(r, model, base, seen)
    body = ""
    for s in r["steps"]:
        i = s["idx"]
        cls = ("skipped " if i < k else "") + ("suspect " if i == k else "") + ("truth" if i == truth else "")
        tag = ("&#9664; suspected " if i == k else "") + ("&#9733; true cause" if i == truth else "")
        body += (f"<tr class='{cls}'><td>{i}</td><td>{s['type']}</td><td>{s['tool']}</td>"
                 f"<td>{s['confidence']:.2f}</td><td>{s['latency_ms']:.0f}</td><td>{tag}</td></tr>")
    verdict = "correct" if k == truth else f"wrong (true cause was step {truth})"
    found = f"fixed on attempt {attempt}" if attempt else "not fixed within top 3"
    return f"""<div class='card'>
<h3>Run {r['run_id']} &mdash; fault: {r['fault_type']}</h3>
<p><b>Diagnosis:</b> step {k} ({r['steps'][k]['type']}) &mdash; top-1 is {verdict}. Search: {found}.</p>
<p><b>Evidence:</b></p><ul>{ev}</ul>
<table><tr><th>step</th><th>type</th><th>tool</th><th>conf.</th><th>latency ms</th><th></th></tr>{body}</table>
<p class='note'>Greyed rows were skipped by checkpointed replay (replay re-ran {len(steps)} of {len(r['steps'])} steps).</p>
<p><b>Trace comparison:</b> original output = {r['steps'][-1]['output']},
replayed = {steps[-1]['output']}, expected = {r['task']['expected']}
&rarr; {"fixed" if ok else "still failing"}</p></div>"""


cards = ""
for ft in ["bad_retrieval", "hallucination", "tool_error", "wrong_tool", "silent_corruption"]:
    pick = [r for r in failed if r["fault_type"] == ft]
    if pick:
        cards += card(pick[0])

css = """body{font-family:Segoe UI,Arial,sans-serif;max-width:900px;margin:30px auto;padding:0 16px;color:#222}
table{border-collapse:collapse;width:100%;margin:8px 0}td,th{border:1px solid #ccc;padding:4px 8px;text-align:left;font-size:14px}
th{background:#f0f0f0}.card{border:1px solid #bbb;border-radius:8px;padding:12px 18px;margin:20px 0}
tr.skipped td{color:#aaa;background:#fafafa}tr.suspect td{background:#fff3cd}tr.truth td{font-weight:bold}
tr.avg td{font-weight:bold;background:#eef}.note{color:#666;font-size:13px}"""

page = f"""<html><head><meta charset='utf-8'><title>Black Box report</title><style>{css}</style></head><body>
<h1>Black Box &mdash; failure diagnosis report</h1>
<p>Held-out failed runs: {len(failed)}. Results come from a simulated agent, not a real one.</p>
<h2>Results (search: fix top-3 suspects in order)</h2>
<table><tr><th>fault type</th><th>runs</th><th>fixed on 1st try</th><th>fixed within 3</th>
<th>steps re-run vs 1 full re-run</th></tr>{table}</table>
<h2>Example diagnoses</h2>{cards}</body></html>"""

out = os.path.join(HERE, "report.html")
open(out, "w", encoding="utf-8").write(page)
print("Wrote", out)
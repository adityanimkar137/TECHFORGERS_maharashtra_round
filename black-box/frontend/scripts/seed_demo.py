"""Creates demo runs in the REAL backend so the frontend has data to show.
Usage (backend must be running):  python scripts/seed_demo.py [http://localhost:8000]
"""
import json, sys, urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"

def post(path, body):
    req = urllib.request.Request(BASE + path, json.dumps(body).encode(), {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req))

def make(task, status, final, reason, steps):
    run = post("/runs/", {"task": task, "status": status, "final_output": final, "failure_reason": reason})
    for i, (name, st, inp, out, err) in enumerate(steps, 1):
        post(f"/runs/{run['id']}/steps/", {"step_number": i, "name": name, "status": st, "input_data": inp, "output_data": out, "error_message": err})
    print("created run", run["id"], status)

prices = "Acer: ₹44990, HP: ₹47490, Lenovo: ₹39990"
make("Find cheapest laptop under ₹50,000", "failed", "HP: ₹4749 is the cheapest", "Incorrect product prices", [
    ("Understand Request", "success", "Find cheapest laptop under ₹50,000", "intent: find_cheapest_product", None),
    ("Search Products", "success", "laptop, max 50000", "Acer, HP, Lenovo", None),
    ("Extract Product Prices", "failed", prices, "Acer: ₹44.99, HP: ₹4749, Lenovo: ₹3.999", "Thousands separator parsed as decimal point"),
    ("Compare Prices", "failed", "Acer: 44.99, HP: 4749, Lenovo: 3.999", "HP", "Comparison used corrupted prices"),
    ("Generate Answer", "failed", "HP", "HP: ₹4749 is the cheapest", "Final answer contains incorrect price"),
])
make("Summarise ticket #8841 and draft reply", "success", "Reply drafted", None, [
    ("Read Ticket", "success", "ticket 8841", "refund request", None),
    ("Draft Reply", "success", "refund request", "Reply drafted", None),
])

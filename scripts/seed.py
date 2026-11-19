"""Re-seed the dockerized knowledge base.

Reads data.txt (a python file defining raw_data) and POSTs each fact to the
backend /ingest endpoint. Usage:

    python scripts/seed.py                      # defaults to http://localhost:8000/api/v1/rag
    python scripts/seed.py http://localhost:8000/api/v1/rag
"""

import ast
import re
import sys

import requests

BACKEND = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000/api/v1/rag"

raw = open("data.txt", encoding="utf-8").read()
m = re.search(r"raw_data\s*=\s*(\[.*?\])", raw, re.DOTALL)
if not m:
    raise SystemExit("could not find raw_data list in data.txt")

body = m.group(1)
#data.txt has comment lines inside the list — literal_eval can't parse those, strip them
body = "\n".join(line for line in body.splitlines() if not line.strip().startswith("#"))

facts = [d for d in ast.literal_eval(body) if d.get("text", "").strip()]
print(f"seeding {len(facts)} facts into {BACKEND} ...")

ok = failed = 0
for i, f in enumerate(facts, 1):
    r = requests.post(
        f"{BACKEND}/ingest",
        json={"text": f["text"], "source_name": f.get("source", "seed")},
        timeout=120,
    )
    if r.status_code == 200:
        ok += 1
        print(f"  [{i}/{len(facts)}] ok")
    else:
        failed += 1
        print(f"  [{i}/{len(facts)}] FAILED {r.status_code}: {r.text[:200]}")

print(f"done: {ok} ingested, {failed} failed")

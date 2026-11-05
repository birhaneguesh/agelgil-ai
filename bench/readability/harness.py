#!/usr/bin/env python
"""Run both locked models against all 60 held-out items with locked prompts and parameters.

Writes bench/readability/outputs/raw.jsonl — one JSON object per (item, model) pair.

Fields per line:
  item_id, model, misconception_id, sim, question,
  hint (string or "" if grammar failed),
  grammar_ok (bool), tag_ended (bool),
  latency_ms, tokens_out

A run that fails to parse JSON, or whose 'hint' is empty, produces:
  hint=""  grammar_ok=false  tag_ended=false  latency_ms=<measured>

The analysis step assigns 0/0/0 to those items. Grammar failure is not retried here;
P5.04 owns the fallback path. The harness must faithfully represent the pipeline that P5.03
will run.

Usage:
    python bench/readability/harness.py            # full run (120 calls)
    python bench/readability/harness.py --limit 2  # smoke (2 items × 2 models)
"""
import argparse
import json
import os
import sys
import time
import urllib.request

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HELD = os.path.join(ROOT, "bench/readability/held_out.yaml")
SYS_TXT = os.path.join(ROOT, "docs/prompts/system.txt")
USR_TMPL = os.path.join(ROOT, "docs/prompts/user.tmpl")
SCHEMA_JSON = os.path.join(ROOT, "docs/prompts/schema.json")
OUT = os.path.join(ROOT, "bench/readability/outputs/raw.jsonl")

MODELS = ["qwen2.5:0.5b-instruct-q4_K_M", "tinyllama:1.1b-chat-v1-q4_K_M"]

PARAMS = {
    "temperature": 0.7,
    "top_p": 0.9,
    "num_predict": 200,
    "repeat_penalty": 1.1,
    "seed": 42,
}

MANDATORY = "This is a suggestion — check it against your simulation result."


def load_inputs():
    with open(SYS_TXT, encoding="utf-8") as f:
        system = f.read()
    with open(USR_TMPL, encoding="utf-8") as f:
        tmpl = f.read()
    with open(SCHEMA_JSON, encoding="utf-8") as f:
        schema = json.load(f)
    with open(HELD, encoding="utf-8") as f:
        items = yaml.safe_load(f)
    return system, tmpl, schema, items


def build_user(tmpl, item):
    return (tmpl.replace("{sim}", item["sim"])
                .replace("{misconception_id}", item["misconception_id"])
                .replace("{question}", item["question_text"]))


def call_ollama(model, system, user, schema):
    body = {
        "model": model,
        "system": system,
        "prompt": user,
        "stream": False,
        "format": schema,
        "options": PARAMS,
    }
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=data,
        headers={"content-type": "application/json"},
        method="POST",
    )
    t0 = time.perf_counter()
    # 120 s per call: generous for a 200-token generation on an 8 GB host; short enough
    # that a hung backend aborts on the first call (the try/except below calls sys.exit).
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.loads(r.read().decode("utf-8"))
    latency_ms = int((time.perf_counter() - t0) * 1000)
    return resp, latency_ms


def parse_hint(resp):
    raw = resp.get("response", "")
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return "", False, False
    if not isinstance(parsed, dict):
        return "", False, False
    extras = set(parsed.keys()) - {"hint"}
    if extras:
        return "", False, False
    hint = parsed.get("hint", "")
    if not isinstance(hint, str) or not hint.strip():
        return "", False, False
    tag_ended = hint.rstrip().endswith(MANDATORY)
    return hint, True, tag_ended


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None,
                    help="run only the first N items (smoke mode)")
    args = ap.parse_args()

    system, tmpl, schema, items = load_inputs()
    if args.limit:
        items = items[: args.limit]

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    n_ok = 0
    n_grammar = 0
    with open(OUT, "w", encoding="utf-8") as f:
        for item in items:
            for model in MODELS:
                user = build_user(tmpl, item)
                try:
                    resp, latency_ms = call_ollama(model, system, user, schema)
                except Exception as e:
                    print(f"FAIL: {model} / {item['id']}: {e}", file=sys.stderr)
                    sys.exit(1)
                hint, grammar_ok, tag_ended = parse_hint(resp)
                if not grammar_ok:
                    n_grammar += 1
                else:
                    n_ok += 1
                line = {
                    "item_id": item["id"],
                    "model": model,
                    "misconception_id": item["misconception_id"],
                    "sim": item["sim"],
                    "question": item["question_text"],
                    "hint": hint,
                    "grammar_ok": grammar_ok,
                    "tag_ended": tag_ended,
                    "latency_ms": latency_ms,
                    "tokens_out": resp.get("eval_count", 0),
                }
                f.write(json.dumps(line, ensure_ascii=False) + "\n")
                print(f"{item['id']:<16} {model:<32} "
                      f"{'ok' if grammar_ok else 'GRAMMAR-FAIL':<13} "
                      f"{latency_ms:>5} ms  {len(hint):>4} chars")

    print(f"\nwrote {OUT}")
    print(f"  items: {len(items)}  models: {len(MODELS)}  "
          f"total: {len(items) * len(MODELS)}  "
          f"grammar_ok: {n_ok}  grammar_fail: {n_grammar}")


if __name__ == "__main__":
    main()

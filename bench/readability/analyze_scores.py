#!/usr/bin/env python
"""Read filled score sheets + raw.jsonl, produce a verdict.

Reads:
  bench/readability/outputs/raw.jsonl
  bench/readability/score_sheets/teacher-A/{qwen,tinyllama}.md
  bench/readability/score_sheets/teacher-B/{qwen,tinyllama}.md

Writes:
  stdout: per-model verdict (PASS / FAIL / INCONCLUSIVE) + summary stats
  bench/readability/verdict.json: machine-readable verdict

Teacher sheet format (markdown table):
  | # | item_id | misconception_id | ... | grammar ok? | factual | readability | uncertainty | comment |
  Cells "factual", "readability", "uncertainty" contain 1-5, or "-" for grammar-failed items.

Verdict logic (per P2.05 locked decisions):
  grammar-fail item contributes (0,0,0).
  item passes if all three >= 3.
  model passes for teacher if:
    teacher_mean[dim] >= 3.5 for all dims
    AND teacher_pass_rate >= 0.75
  model passes overall if both teachers pass.
  disagreement: if |A[dim] - B[dim]| >= 2 on >= 15% of items => INCONCLUSIVE for that dim.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW = os.path.join(ROOT, "bench/readability/outputs/raw.jsonl")
SHEETS = {
    "teacher-A": os.path.join(ROOT, "bench/readability/score_sheets/teacher-A"),
    "teacher-B": os.path.join(ROOT, "bench/readability/score_sheets/teacher-B"),
}
VERDICT = os.path.join(ROOT, "bench/readability/verdict.json")

MODEL_SHORT = {
    "qwen2.5:0.5b-instruct-q4_K_M": "qwen",
    "tinyllama:1.1b-chat-v1-q4_K_M": "tinyllama",
}

ROW = re.compile(
    r"^\|\s*\d+\s*\|\s*([^\|]+?)\s*\|\s*([^\|]+?)\s*\|.*\|\s*(Y|N)\s*\|\s*"
    r"([0-5]|-)\s*\|\s*([0-5]|-)\s*\|\s*([0-5]|-)\s*\|",
    re.MULTILINE,
)


def load_grammar():
    """item_id -> model -> {grammar_ok}."""
    d = {}
    with open(RAW, encoding="utf-8") as f:
        for line in f:
            o = json.loads(line)
            d.setdefault(o["item_id"], {})[o["model"]] = o["grammar_ok"]
    return d


def parse_sheet(path, model_tag):
    """Return item_id -> (factual, readability, uncertainty) or (0,0,0) for grammar fails."""
    text = open(path, encoding="utf-8").read()
    scores = {}
    for m in ROW.finditer(text):
        item_id = m.group(1).strip()
        grammar_ok = m.group(3) == "Y"
        if not grammar_ok:
            scores[item_id] = (0, 0, 0)
            continue
        try:
            scores[item_id] = (int(m.group(4)), int(m.group(5)), int(m.group(6)))
        except ValueError:
            raise SystemExit(
                f"FAIL: {path}: item {item_id} has non-numeric score "
                f"({m.group(4)}, {m.group(5)}, {m.group(6)})"
            )
    if len(scores) != 60:
        raise SystemExit(f"FAIL: {path}: expected 60 rows, found {len(scores)}")
    return scores


def teacher_stats(scores):
    n = len(scores)
    totals = [0, 0, 0]
    passes = 0
    for f_, r_, u_ in scores.values():
        totals[0] += f_
        totals[1] += r_
        totals[2] += u_
        if f_ >= 3 and r_ >= 3 and u_ >= 3:
            passes += 1
    means = [t / n for t in totals]
    return means, passes / n


def evaluate():
    grammar = load_grammar()
    results = {}
    for model_tag, short in MODEL_SHORT.items():
        per_teacher = {}
        for teacher, sheet_dir in SHEETS.items():
            path = os.path.join(sheet_dir, f"{short}.md")
            if not os.path.isfile(path):
                raise SystemExit(f"FAIL: {path} missing")
            scores = parse_sheet(path, model_tag)
            means, pass_rate = teacher_stats(scores)
            per_teacher[teacher] = {
                "scores": scores,
                "means": means,
                "pass_rate": pass_rate,
            }

        # Disagreement per dimension
        dims = ["factual", "readability", "uncertainty"]
        disagreements = {}
        for di, dim in enumerate(dims):
            a = per_teacher["teacher-A"]["scores"]
            b = per_teacher["teacher-B"]["scores"]
            ids = set(a) & set(b)
            big = sum(1 for i in ids if abs(a[i][di] - b[i][di]) >= 2)
            disagreements[dim] = big / len(ids) if ids else 0.0

        # Pass condition
        a_means = per_teacher["teacher-A"]["means"]
        b_means = per_teacher["teacher-B"]["means"]
        a_pr = per_teacher["teacher-A"]["pass_rate"]
        b_pr = per_teacher["teacher-B"]["pass_rate"]
        a_ok = all(m >= 3.5 for m in a_means) and a_pr >= 0.75
        b_ok = all(m >= 3.5 for m in b_means) and b_pr >= 0.75
        model_pass = a_ok and b_ok

        # Grammar failure rate from raw.jsonl
        n_items = len(grammar)
        grammar_fails = sum(
            1 for item_scores in grammar.values()
            if not item_scores.get(model_tag, True)
        )
        grammar_rate = grammar_fails / n_items if n_items else 0.0

        if any(rate >= 0.15 for rate in disagreements.values()):
            verdict = "INCONCLUSIVE"
            reason = "disagreement >= 15% on: " + ", ".join(
                d for d, r in disagreements.items() if r >= 0.15
            )
        elif model_pass:
            verdict = "PASS"
            reason = "both teachers pass"
        else:
            verdict = "FAIL"
            fails = []
            if not a_ok: fails.append("teacher-A")
            if not b_ok: fails.append("teacher-B")
            reason = "fails for: " + ", ".join(fails)

        results[short] = {
            "model": model_tag,
            "verdict": verdict,
            "reason": reason,
            "teacher-A": {"means": a_means, "pass_rate": a_pr},
            "teacher-B": {"means": b_means, "pass_rate": b_pr},
            "disagreement": disagreements,
            "grammar_fail_rate": grammar_rate,
        }

    return results


def report(results):
    print("\n== Per-model summary ==")
    for short, r in results.items():
        print(f"\n{short} ({r['model']})")
        print(f"  verdict: {r['verdict']}  ({r['reason']})")
        for t in ("teacher-A", "teacher-B"):
            m = r[t]["means"]
            print(f"  {t}: mean factual={m[0]:.2f} read={m[1]:.2f} unc={m[2]:.2f} "
                  f"pass_rate={r[t]['pass_rate']:.1%}")
        print(f"  disagreement: " + ", ".join(
            f"{d}={r:.1%}" for d, r in r["disagreement"].items()))
        print(f"  grammar_fail_rate: {r['grammar_fail_rate']:.1%}")

    # Overall verdict
    verdicts = {s: r["verdict"] for s, r in results.items()}
    print("\n== Overall ==")
    if any(v == "INCONCLUSIVE" for v in verdicts.values()):
        print("INCONCLUSIVE — third-teacher re-score required for the dimensions listed above")
    elif verdicts.get("qwen") == "PASS" and verdicts.get("tinyllama") == "PASS":
        print("PASS — both models pass; P2.06 selects by readability mean")
    elif verdicts.get("qwen") == "PASS":
        print("PASS — qwen selected; tinyllama fails")
    elif verdicts.get("tinyllama") == "PASS":
        print("PASS — tinyllama selected; qwen fails")
    else:
        print("FAIL — both models fail; §16 #12 fires (rule + canonical only)")


def main():
    results = evaluate()
    report(results)
    with open(VERDICT, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nwrote {VERDICT}")


if __name__ == "__main__":
    main()

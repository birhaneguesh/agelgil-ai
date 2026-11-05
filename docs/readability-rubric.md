# Readability rubric — grade 9–10 English hints

Two independent science teachers score each hint on three dimensions. Each dimension is 1–5. An item **passes** only if all three scores are 3 or above. The definitions below are fixed; do not modify per session.

## Dimension 1 — Factual correctness (1–5)

| Score | Meaning |
|---|---|
| 5 | The hint is factually correct and its recommendation would help the student see the concept. No factual error. |
| 4 | Correct but could mislead a careful reader on a minor point (e.g., imprecise word choice). |
| 3 | Correct on the main point; a careful reader would not be misled. |
| 2 | Contains a factual error that would mislead a student working the simulation. |
| 1 | Substantively wrong. |

## Dimension 2 — Readability at grade 9–10 (1–5)

| Score | Meaning |
|---|---|
| 5 | A grade 9 student can read and act on it without re-reading. No vocabulary above grade level. |
| 4 | One unfamiliar word, defined inline. Simple sentences. |
| 3 | Understandable but requires effort — a long sentence, or a term not defined. A student would need the teacher. |
| 2 | Requires reading twice; contains idiom, unexplained technical vocabulary, or a dependency on a diagram. |
| 1 | Not understandable at grade level. |

## Dimension 3 — Uncertainty framing (1–5)

Does the hint **defer to the student's own observation**, rather than asserting a conclusion as fact?

| Score | Meaning |
|---|---|
| 5 | Clearly suggests an action ("check that…", "compare the…") and does not claim the answer is final. |
| 4 | Suggests an action but also asserts a conclusion in the same sentence. |
| 3 | Mixed — either the action is vague or the conclusion is stated as fact without deferring. |
| 2 | States the conclusion as fact. The student has no reason to check the simulation. |
| 1 | Asserts the answer as final and discourages further checking. |

## What is **not** scored here

- The literal presence of the mandatory uncertainty sentence (it is appended at runtime regardless — see `docs/model-selection.md` → "Mandatory sentence handling (runtime)").
- Grammar and JSON validity — handled separately by the harness; an invalid output is scored as 0 on all three dimensions and flagged in the sheet's `grammar ok?` column.

## Scoring discipline

- Read the question and the hint together, once. Score on first impression, not on analysis.
- Score each dimension independently; do not anchor on a prior row.
- Do not discuss scores with the other teacher before recording.
- If a hint is empty or ungrammatical, mark 0 in the grammar-ok column and do not score — the analysis script assigns 0/0/0.

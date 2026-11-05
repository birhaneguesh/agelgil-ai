
## Prompt and runtime contract

- [ ] **P5.03 must append the mandatory uncertainty sentence if the model omitted it.** The 0.5B model does not reliably comply with a trailing-tag instruction. Appending is idempotent; the sentence is not duplicated when present. Scoring (P2.05) evaluates the hint's *content* framing, not literal tag presence. See `docs/model-selection.md` → "Mandatory sentence handling (runtime)".

## Readability scoring (P2.05)

- [ ] **P2.05 harness complete on 2026-11-05; teacher session pending.** Score sheets ready at `bench/readability/score_sheets/`. §16 #1 and §16 #12 remain open until the session runs and Step 10 is re-run. Record the scheduled date here: scheduled = ______________.

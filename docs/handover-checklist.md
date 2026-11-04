
## Prompt and runtime contract

- [ ] **P5.03 must append the mandatory uncertainty sentence if the model omitted it.** The 0.5B model does not reliably comply with a trailing-tag instruction. Appending is idempotent; the sentence is not duplicated when present. Scoring (P2.05) evaluates the hint's *content* framing, not literal tag presence. See `docs/model-selection.md` → "Mandatory sentence handling (runtime)".

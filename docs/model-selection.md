# Model selection

Authoritative record for P2.05 scoring and P5.03 runtime. P5.03 reads this file; it does not define its own values.

## Candidate models

| Role | Ollama tag | GGUF source | Quantization | SHA-256 |
|---|---|---|---|---|
| Primary | qwen2.5:0.5b-instruct-q4_K_M | Qwen/Qwen2.5-0.5B-Instruct-GGUF | Q4_K_M | 74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db |
| Secondary | tinyllama:1.1b-chat-v1-q4_K_M | TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF | Q4_K_M | 9fecc3b3cd76bba89d504f29b616eedf7da85b96540e490ca5824d3f7d2776a0 |

## Host environment

- Ollama for Windows version: 0.40.14
- GGUF location on the dev host: `/c/Users/User/agelgil-models` (outside the repo; not committed)
- Host: Windows 10, 8 GB RAM. Ollama peak with a 0.5B Q4 model: ~1.5 GB. Docker Desktop must be stopped during P2.05.

## Modelfile PARAMETER defaults

Ollama's stored defaults from `ollama create`. The prompt-template lock step confirms or revises; when revised, both this file and the Modelfiles are updated and `ollama create` is re-run.

| Parameter | Value |
|---|---|
| temperature | 0.7 |
| top_p | 0.9 |
| num_predict | 200 |
| repeat_penalty | 1.1 |
| seed | 42 |

## Port conflict

The split dev stack (P1.02) starts `mock-slm` on `127.0.0.1:11434`. Ollama uses the same port. P2.05 stops the dev stack via `./scripts/dev-down.sh` before scoring. P5.03 handles this at runtime (mock-slm replaced by real Ollama; one or the other on the host, never both).

## Prompt template (locked)

The following three files are the literal strings the scoring step (P2.05) and the runtime (P5.03) use. They are read from disk; P5.03 does not re-derive them. Substitution of `{sim}`, `{misconception_id}`, `{question}` in `user.tmpl` is done by the caller before the request is sent.

| Artifact | Path |
|---|---|
| System prompt | `docs/prompts/system.txt` |
| User template | `docs/prompts/user.tmpl` |
| Output schema | `docs/prompts/schema.json` |

## Locked sampling parameters

Applied at scoring (P2.05) and at runtime (P5.03). These are the same values stored in the Modelfiles (see "Modelfile PARAMETER defaults" above); a change here requires re-running `ollama create` and re-scoring in P2.05.

| Parameter | Value |
|---|---|
| temperature | 0.7 |
| top_p | 0.9 |
| num_predict | 200 |
| repeat_penalty | 1.1 |
| seed | 42 |
| format | json |
| quantization | Q4_K_M |

## Change discipline

Any change to `system.txt`, `user.tmpl`, `schema.json`, or the locked parameters above invalidates the P2.05 readability verdict for the affected model. That model must be re-scored before P2.06 closes. Do not edit these files without adding a dated entry to `docs/handover-checklist.md` recording what changed and that re-scoring is required.

## Mandatory sentence handling (runtime)

The mandatory uncertainty sentence is **appended by the runtime (P5.03) if the model omitted it**. It is a deterministic post-processing step, not a model behavior. The system prompt is directive and raises the model's compliance rate, but compliance is not guaranteed for a 0.5B model and is not load-bearing after the append.

P5.03's append logic:

1. Parse the model's JSON. If parsing fails, use the canonical fallback (P5.04).
2. If `hint` does not end with (or contain) the mandatory sentence, append:
   `\nThis is a suggestion — check it against your simulation result.`
3. Return the hint.

The append is idempotent: if the sentence is present, it is not duplicated.

## Grammar-failure handling (scoring)

At scoring time (P2.05), an item where the model fails to produce JSON that validates against `schema.json` is counted as a scoring failure for that item, not skipped. The per-model failure rate is recorded alongside the readability scores.

Scoring does **not** check for the literal mandatory sentence in the model's output — that is a runtime concern (see "Mandatory sentence handling" above). The "uncertainty framing" rubric evaluates the *content* of the hint: does it suggest checking, avoid overclaiming, and defer to the student's own observation? A hint like "Check if…" or "Try comparing…" passes the content test even if the tag is absent.
## Readability verdict

**Overall:** PENDING — teacher session scheduled (see `docs/handover-checklist.md`).
§16 #1 and §16 #12 remain open until the verdict is recorded here.

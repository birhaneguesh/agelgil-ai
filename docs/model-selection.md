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

## Prompt template

_Filled by the prompt-template lock step._ Until filled, P2.05 cannot begin and P5.03 cannot ship.

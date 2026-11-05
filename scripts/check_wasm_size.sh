#!/usr/bin/env bash
# Enforce MVP-FINAL §6's compressed WASM budget (< 2 MB).
# Reads the committed artifact; does not rebuild. P3.06 may add a rebuild check.
set -euo pipefail

WASM=frontend/wasm/pkg/agelgil_wasm_bg.wasm
[[ -f "$WASM" ]] || { echo "FAIL: $WASM not found (run wasm-pack build)"; exit 1; }

uncompressed=$(stat -c%s "$WASM" 2>/dev/null || wc -c < "$WASM")
compressed=$(gzip -9 -c "$WASM" | wc -c)
budget=$((2 * 1024 * 1024))

echo "wasm uncompressed: ${uncompressed} bytes"
echo "wasm compressed:   ${compressed} bytes (budget ${budget})"

[ "$compressed" -lt "$budget" ] || { echo "FAIL: compressed wasm over budget"; exit 1; }
echo "ok"

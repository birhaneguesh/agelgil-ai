#!/usr/bin/env bash
# Start the split dev stack on the host (no Docker). Writes PIDs to /tmp/agelgil-dev/.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PID_DIR="/tmp/agelgil-dev"
mkdir -p "$PID_DIR"

if [[ ! -d "$ROOT/.venv" ]]; then
  echo "error: .venv missing at $ROOT. Run the venv creation in P1.02 Step 2." >&2
  exit 1
fi

PY="$ROOT/.venv/Scripts/python.exe"
[[ -x "$PY" ]] || PY="$ROOT/.venv/bin/python"

# 1. mock SLM on 11434
"$PY" -m uvicorn api.app.mocks.slm:app --host 127.0.0.1 --port 11434 --log-level warning \
  > "$PID_DIR/mock-slm.log" 2>&1 &
echo $! > "$PID_DIR/mock-slm.pid"

# 2. api on 8000
AGELGIL_MOCK_SLM_URL="http://127.0.0.1:11434" \
  "$PY" -m uvicorn api.app.main:app --host 127.0.0.1 --port 8000 --reload --log-level warning \
  > "$PID_DIR/api.log" 2>&1 &
echo $! > "$PID_DIR/api.pid"

# 3. writer
"$PY" -m writer.app.worker \
  > "$PID_DIR/writer.log" 2>&1 &
echo $! > "$PID_DIR/writer.pid"

# 4. Vite
( cd "$ROOT/frontend" && npm run dev -- --host 127.0.0.1 --port 5173 ) \
  > "$PID_DIR/vite.log" 2>&1 &
echo $! > "$PID_DIR/vite.pid"

sleep 3
echo "PIDs:"
for s in mock-slm api writer vite; do
  printf "  %-10s %s\n" "$s" "$(cat "$PID_DIR/$s.pid")"
done

echo
echo "Tail logs: tail -f $PID_DIR/*.log"
echo "Stop:      kill \$(cat $PID_DIR/*.pid)"

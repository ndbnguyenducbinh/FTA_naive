#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "======================================================================="
echo "  🚀 NEURO-SYMBOLIC DIAGNOSTIC COPILOT (PROTOTYPE LAUNCHER)"
echo "======================================================================="

# Check virtual environment
if [ ! -d ".venv" ]; then
    echo "[!] Creating virtual environment .venv..."
    python3 -m venv .venv
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install -r requirements.txt
fi

echo "[*] Running Unit Tests (100% Math Verification)..."
.venv/bin/python -m unittest discover tests -v

PORT=${PORT:-8000}
if fuser $PORT/tcp >/dev/null 2>&1 || lsof -ti:$PORT >/dev/null 2>&1 ; then
    echo "[!] Port $PORT is occupied. Cleaning up stale server process..."
    fuser -k $PORT/tcp 2>/dev/null || kill -9 $(lsof -t -i:$PORT) 2>/dev/null || true
    sleep 0.5
fi

echo ""
echo "[*] Launching FastAPI Prototype Server..."
echo "    -> Dashboard UI:      http://localhost:$PORT"
echo "    -> Swagger API Docs:  http://localhost:$PORT/docs"
echo "======================================================================="
exec .venv/bin/python run_server.py


#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-4173}"
HOST="${HOST:-0.0.0.0}"

exec python3 app.py --host "$HOST" --port "$PORT"

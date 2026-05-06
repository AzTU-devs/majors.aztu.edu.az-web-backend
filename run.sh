#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

python scripts/init_db.py
python scripts/seed.py
exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

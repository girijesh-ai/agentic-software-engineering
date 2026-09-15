#!/usr/bin/env bash
# Idempotent environment setup. Safe to re-run at the start of any session.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../../../.."
docker compose up -d --wait db mailpit
(cd backend && FASTAPI_ENV=development uv run bash scripts/prestart.sh)
echo "Environment ready. Read PROGRESS.md and features.json next."

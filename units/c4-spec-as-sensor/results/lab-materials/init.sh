#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"
docker compose up -d --wait db mailpit
(cd backend && FASTAPI_ENV=development uv run bash scripts/prestart.sh)
echo "Environment ready."

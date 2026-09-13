#!/usr/bin/env bash
# Arm B setup: remove every B1 reference test so the agent can't see or
# accidentally satisfy them - it must write its own, blind.
set -euo pipefail
rm -f backend/tests/ablation/test_task1_search.py \
      backend/tests/ablation/test_task2_archive.py \
      backend/tests/ablation/test_task3_login_rate_limit.py \
      backend/tests/ablation/test_task4_item_count.py \
      backend/tests/ablation/test_task5_protect_user_deletion.py

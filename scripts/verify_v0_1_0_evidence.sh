#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"

python3 "$SCRIPT_DIR/verify_v0_1_0_evidence.py" \
  --source "$REPO_ROOT/../millrace-rs"

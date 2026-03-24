#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOTSTRAP="${SCRIPT_DIR}/bootstrap-macos.sh"

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  exec bash "${BOOTSTRAP}" --help
fi

exec bash "${BOOTSTRAP}" doctor "$@"

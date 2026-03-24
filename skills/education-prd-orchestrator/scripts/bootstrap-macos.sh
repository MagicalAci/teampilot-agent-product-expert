#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BOOTSTRAP_PY="${SCRIPT_DIR}/bootstrap_product_planning_tools.py"
PYTHON_FORMULA="${EPPO_PYTHON_FORMULA:-python@3.11}"

print_help() {
  cat <<'EOF'
Usage:
  bash scripts/bootstrap-macos.sh [doctor|repair] [--json]

Commands:
  doctor   Ensure the managed runtime exists and dependencies are installed.
  repair   Reinstall dependencies even if the hash did not change.

Environment overrides:
  EPPO_MANAGED_ROOT    Override managed runtime root.
  EPPO_PYTHON_FORMULA  Override Homebrew Python formula.
  EPPO_SKIP_SYSTEM_INSTALL=1  Disable automatic Homebrew/Python installation.
EOF
}

die() {
  printf 'bootstrap error: %s\n' "$*" >&2
  exit 1
}

brew_bin() {
  if command -v brew >/dev/null 2>&1; then
    command -v brew
    return 0
  fi
  if [[ -x /opt/homebrew/bin/brew ]]; then
    printf '/opt/homebrew/bin/brew\n'
    return 0
  fi
  if [[ -x /usr/local/bin/brew ]]; then
    printf '/usr/local/bin/brew\n'
    return 0
  fi
  return 1
}

load_brew_env() {
  local resolved_brew
  resolved_brew="$(brew_bin || true)"
  if [[ -n "${resolved_brew}" ]]; then
    eval "$("${resolved_brew}" shellenv)"
  fi
}

ensure_macos() {
  if [[ "$(uname -s)" != "Darwin" ]]; then
    die "bootstrap-macos.sh 目前只支持 macOS。"
  fi
}

ensure_homebrew() {
  local resolved_brew
  resolved_brew="$(brew_bin || true)"
  if [[ -n "${resolved_brew}" ]]; then
    load_brew_env
    return 0
  fi
  if [[ "${EPPO_SKIP_SYSTEM_INSTALL:-0}" == "1" ]]; then
    die "当前未找到 Homebrew，且已禁用自动安装。"
  fi
  if ! command -v curl >/dev/null 2>&1; then
    die "当前未找到 curl，无法自动安装 Homebrew。"
  fi
  if ! xcode-select -p >/dev/null 2>&1; then
    xcode-select --install >/dev/null 2>&1 || true
  fi
  NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  load_brew_env
}

ensure_python() {
  if command -v python3 >/dev/null 2>&1; then
    return 0
  fi
  if [[ "${EPPO_SKIP_SYSTEM_INSTALL:-0}" == "1" ]]; then
    die "当前未找到 python3，且已禁用自动安装。"
  fi
  ensure_homebrew
  if ! brew list --versions "${PYTHON_FORMULA}" >/dev/null 2>&1; then
    brew install "${PYTHON_FORMULA}"
  fi
  load_brew_env
  command -v python3 >/dev/null 2>&1 || die "python3 自动安装后仍不可用。"
}

main() {
  local command="${1:-doctor}"
  if [[ "${command}" == "--help" || "${command}" == "-h" ]]; then
    print_help
    return 0
  fi

  ensure_macos
  load_brew_env
  ensure_python
  exec python3 "${BOOTSTRAP_PY}" "${command}" "${@:2}"
}

main "$@"

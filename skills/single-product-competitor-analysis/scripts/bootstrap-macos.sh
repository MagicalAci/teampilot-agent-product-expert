#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
RUNNER="${SCRIPT_DIR}/run_pipeline.py"
FRAME_EXTRACTOR="${SCRIPT_DIR}/extract_video_frames.py"
MANAGED_ROOT="${SPCA_MANAGED_ROOT:-${HOME}/.cursor/skills-runtime/single-product-competitor-analysis}"
VENV_DIR="${MANAGED_ROOT}/venv"
LOG_DIR="${MANAGED_ROOT}/logs"
REQUIREMENTS_FILE="${SPCA_REQUIREMENTS_FILE:-${SKILL_ROOT}/requirements.txt}"
REQUIREMENTS_HASH_FILE="${MANAGED_ROOT}/requirements.sha256"
PYTHON_FORMULA="${SPCA_PYTHON_FORMULA:-python@3.11}"
FFMPEG_FORMULA="${SPCA_FFMPEG_FORMULA:-ffmpeg}"

print_help() {
  cat <<'EOF'
Usage:
  bash scripts/bootstrap-macos.sh <command> [args...]

Commands:
  doctor
  repair
  init --task-card <task-card.json>
  collect --task-card <task-card.json>
  analyze --task-card <task-card.json>
  export --task-card <task-card.json>
  validate --task-card <task-card.json>
  extract-frames --input <video> --output-dir <frames-dir> [--fps 1 | --every-n-frames 10]

Environment overrides:
  SPCA_MANAGED_ROOT       Override managed runtime root.
  SPCA_PYTHON_FORMULA     Override Homebrew Python formula.
  SPCA_FFMPEG_FORMULA     Override Homebrew ffmpeg formula.
  SPCA_FFMPEG_BIN         Override ffmpeg binary used by extract-frames.
  SPCA_REQUIREMENTS_FILE  Override requirements.txt path.
  SPCA_SKIP_PIP_SYNC      Set to 1 to skip pip install and hash sync.
  SPCA_SKIP_SYSTEM_INSTALL Set to 1 to disable Homebrew auto-install.
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
  if [[ "${SPCA_SKIP_SYSTEM_INSTALL:-0}" == "1" ]]; then
    die "当前未找到 Homebrew，且 SPCA_SKIP_SYSTEM_INSTALL=1，无法自动安装。"
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

ensure_brew_formula() {
  local formula="$1"
  if [[ "${SPCA_SKIP_SYSTEM_INSTALL:-0}" == "1" ]]; then
    return 0
  fi
  ensure_homebrew
  if ! brew list --versions "${formula}" >/dev/null 2>&1; then
    brew install "${formula}"
  fi
}

resolve_python_bin() {
  local brew_prefix
  if [[ -x "${VENV_DIR}/bin/python" ]]; then
    printf '%s\n' "${VENV_DIR}/bin/python"
    return 0
  fi
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return 0
  fi
  brew_prefix="$(brew --prefix "${PYTHON_FORMULA}" 2>/dev/null || true)"
  if [[ -n "${brew_prefix}" && -x "${brew_prefix}/bin/python3" ]]; then
    printf '%s\n' "${brew_prefix}/bin/python3"
    return 0
  fi
  return 1
}

ensure_python_runtime() {
  local python_bin desired_hash current_hash
  mkdir -p "${MANAGED_ROOT}" "${LOG_DIR}"
  python_bin="$(resolve_python_bin || true)"
  if [[ -z "${python_bin}" ]]; then
    ensure_brew_formula "${PYTHON_FORMULA}"
    python_bin="$(resolve_python_bin || true)"
  fi
  if [[ -z "${python_bin}" ]]; then
    die "未找到可用的 python3，且自动安装失败。"
  fi
  if [[ ! -x "${VENV_DIR}/bin/python" ]]; then
    "${python_bin}" -m venv "${VENV_DIR}"
  fi
  if [[ "${SPCA_SKIP_PIP_SYNC:-0}" == "1" ]]; then
    return 0
  fi

  desired_hash="$(shasum -a 256 "${REQUIREMENTS_FILE}" | awk '{print $1}')"
  current_hash=""
  if [[ -f "${REQUIREMENTS_HASH_FILE}" ]]; then
    current_hash="$(tr -d '\n' < "${REQUIREMENTS_HASH_FILE}")"
  fi
  if [[ "${current_hash}" != "${desired_hash}" || ! -f "${VENV_DIR}/.deps-ready" ]]; then
    "${VENV_DIR}/bin/python" -m pip install --upgrade pip
    "${VENV_DIR}/bin/python" -m pip install -r "${REQUIREMENTS_FILE}"
    printf '%s' "${desired_hash}" > "${REQUIREMENTS_HASH_FILE}"
    : > "${VENV_DIR}/.deps-ready"
  fi
}

resolve_ffmpeg_bin() {
  local brew_prefix
  if [[ -n "${SPCA_FFMPEG_BIN:-}" && -x "${SPCA_FFMPEG_BIN}" ]]; then
    printf '%s\n' "${SPCA_FFMPEG_BIN}"
    return 0
  fi
  if command -v ffmpeg >/dev/null 2>&1; then
    command -v ffmpeg
    return 0
  fi
  brew_prefix="$(brew --prefix "${FFMPEG_FORMULA}" 2>/dev/null || true)"
  if [[ -n "${brew_prefix}" && -x "${brew_prefix}/bin/ffmpeg" ]]; then
    printf '%s\n' "${brew_prefix}/bin/ffmpeg"
    return 0
  fi
  return 1
}

ensure_ffmpeg() {
  local ffmpeg_bin
  ffmpeg_bin="$(resolve_ffmpeg_bin || true)"
  if [[ -z "${ffmpeg_bin}" ]]; then
    ensure_brew_formula "${FFMPEG_FORMULA}"
    ffmpeg_bin="$(resolve_ffmpeg_bin || true)"
  fi
  if [[ -z "${ffmpeg_bin}" ]]; then
    die "未找到可用的 ffmpeg，且自动安装失败。"
  fi
  export SPCA_FFMPEG_BIN="${ffmpeg_bin}"
}

run_python() {
  "${VENV_DIR}/bin/python" "$@"
}

run_doctor() {
  mkdir -p "${LOG_DIR}"
  run_python "${RUNNER}" doctor --json | tee "${LOG_DIR}/doctor.json"
}

force_repair() {
  rm -f "${REQUIREMENTS_HASH_FILE}" "${VENV_DIR}/.deps-ready"
}

main() {
  local command="${1:-}"
  if [[ -z "${command}" || "${command}" == "--help" || "${command}" == "-h" ]]; then
    print_help
    return 0
  fi

  shift || true
  ensure_macos
  load_brew_env

  case "${command}" in
    doctor)
      ensure_python_runtime
      ensure_ffmpeg
      run_doctor
      ;;
    repair)
      force_repair
      ensure_python_runtime
      ensure_ffmpeg
      run_doctor
      ;;
    init|collect|analyze|export|validate)
      ensure_python_runtime
      ensure_ffmpeg
      run_python "${RUNNER}" "${command}" "$@"
      ;;
    extract-frames)
      ensure_python_runtime
      ensure_ffmpeg
      run_python "${FRAME_EXTRACTOR}" "$@"
      ;;
    *)
      print_help
      die "不支持的命令: ${command}"
      ;;
  esac
}

main "$@"

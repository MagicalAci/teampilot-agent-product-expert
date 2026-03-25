#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"

print_help() {
  cat <<'EOF'
用法:
  bash scripts/bootstrap.sh [--with-stack] [--deerflow] [--mediacrawler] [--xhs-downloader] [--doctor] [--dry-run] [--json]

说明:
  research-toolkit 跨平台首启命令（macOS / Linux）。
  优先确保宿主机具备 python3；随后调用统一 CLI 完成 runtime bootstrap，
  并可选安装 DeerFlow / MediaCrawler / XHS-Downloader，最后输出 doctor 结果。

推荐:
  bash scripts/bootstrap.sh --with-stack --doctor
EOF
}

refresh_path() {
  export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:$HOME/.cargo/bin:$HOME/.local/share/uv/bin:$PATH"
}

ensure_homebrew() {
  if command -v brew >/dev/null 2>&1; then
    return 0
  fi
  NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  refresh_path
}

run_system_install() {
  if [[ "${EUID:-$(id -u)}" -eq 0 ]]; then
    "$@"
    return
  fi
  if command -v sudo >/dev/null 2>&1; then
    sudo "$@"
    return
  fi
  echo "错误: 自动安装宿主依赖需要 sudo 或 root 权限。"
  exit 1
}

ensure_python3() {
  refresh_path
  if command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    return 0
  fi

  local system
  system="$(uname -s)"
  if [[ "$system" == "Darwin" ]]; then
    ensure_homebrew
    brew install python
  elif [[ "$system" == "Linux" ]]; then
    if command -v apt-get >/dev/null 2>&1; then
      run_system_install apt-get update
      run_system_install apt-get install -y python3 python3-venv python3-pip
    elif command -v dnf >/dev/null 2>&1; then
      run_system_install dnf install -y python3
    elif command -v yum >/dev/null 2>&1; then
      run_system_install yum install -y python3
    elif command -v pacman >/dev/null 2>&1; then
      run_system_install pacman -Sy --noconfirm python
    elif command -v zypper >/dev/null 2>&1; then
      run_system_install zypper --non-interactive install python3
    else
      echo "错误: 未检测到受支持的包管理器，无法自动安装 python3。"
      exit 1
    fi
  else
    echo "错误: 当前系统 $system 暂不支持自动安装 python3。建议使用 macOS / Linux，Windows 请优先使用 WSL2。"
    exit 1
  fi

  refresh_path
  if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "错误: 自动安装后仍未找到 ${PYTHON_BIN}。"
    exit 1
  fi
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  print_help
  exit 0
fi

ensure_python3
exec "$PYTHON_BIN" "$SCRIPT_DIR/run_pipeline.py" bootstrap-release "$@"

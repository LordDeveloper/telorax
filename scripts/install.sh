#!/usr/bin/env bash
set -euo pipefail

echo 'Telorax installer (loading...)' >&2

REPO="${INSTALL_REPO:-LordDeveloper/telorax}"
RELEASE_REPO_NAME="${RELEASE_REPO_NAME:-telorax}"
ARCH="${INSTALL_ARCH:-}"
CONFIG_DIR="${CONFIG_DIR:-/etc/telorax}"
ENV_FILE="${CONFIG_DIR}/.env"
SKIP_DEPS="${INSTALL_SKIP_DEPS:-0}"
DEPS_MODE="${DEPS_MODE:-local}"

SCRIPT_PATH="${BASH_SOURCE[0]:-}"
if [[ -n "${SCRIPT_PATH}" && "${SCRIPT_PATH}" != bash && -f "${SCRIPT_PATH}" ]]; then
  SCRIPT_DIR="$(cd "$(dirname "${SCRIPT_PATH}")" && pwd)"
else
  SCRIPT_DIR=""
fi

_usage() {
  cat <<'EOF'
Telorax installer

Usage:
  install.sh [install] [--skip-deps]
  install.sh upgrade
  install.sh deps install|status|start|stop|restart|provision

Examples:
  curl -fsSL .../install.sh | sudo bash
  curl -fsSL .../install.sh | sudo bash -s -- deps status
  INSTALL_SKIP_DEPS=1 curl -fsSL .../install.sh | sudo bash
  DEPS_MODE=system curl -fsSL .../install.sh | sudo bash
EOF
}

_source_deps() {
  if [[ -n "${TELORAX_DEPS_SCRIPT:-}" && -f "${TELORAX_DEPS_SCRIPT}" ]]; then
    # shellcheck source=/dev/null
    source "${TELORAX_DEPS_SCRIPT}"
    return
  fi

  if [[ -n "${SCRIPT_DIR}" && -f "${SCRIPT_DIR}/deps.sh" ]]; then
    # shellcheck source=/dev/null
    source "${SCRIPT_DIR}/deps.sh"
    return
  fi

  if [[ -f /usr/share/telorax/deps.sh ]]; then
    # shellcheck source=/dev/null
    source /usr/share/telorax/deps.sh
    return
  fi

  local tag="${1:-latest}"
  local deps_url
  if [[ "${tag}" == latest ]]; then
    tag="$(
      curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" \
        | sed -n 's/.*"tag_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' \
        | head -n 1
    )"
  fi
  deps_url="https://github.com/${REPO}/releases/download/${tag}/deps.sh"
  local tmp_deps
  tmp_deps="$(mktemp /tmp/telorax-deps.XXXXXX.sh)"
  curl -fsSL -o "${tmp_deps}" "${deps_url}"
  # shellcheck source=/dev/null
  source "${tmp_deps}"
  rm -f "${tmp_deps}"
}

_require_root() {
  if [[ "$(id -u)" -ne 0 ]]; then
    echo 'This installer must run as root. Use: curl ... | sudo bash' >&2
    exit 1
  fi
}

_source_release_name() {
  if [[ -n "${SCRIPT_DIR}" && -f "${SCRIPT_DIR}/release-name.sh" ]]; then
    # shellcheck source=release-name.sh
    source "${SCRIPT_DIR}/release-name.sh"
    return
  fi
  if [[ -f /usr/share/telorax/release-name.sh ]]; then
    # shellcheck source=/usr/share/telorax/release-name.sh
    source /usr/share/telorax/release-name.sh
    return
  fi
  release_artifact_name() {
    local version="$1"
    local arch="$2"
    local ext="${3:-}"
    if [[ -n "${ext}" ]]; then
      printf '%s.%s-%s.%s\n' "${RELEASE_REPO_NAME}" "${version}" "${arch}" "${ext}"
    else
      printf '%s.%s-%s\n' "${RELEASE_REPO_NAME}" "${version}" "${arch}"
    fi
  }
}

_detect_arch() {
  case "$(uname -m)" in
    x86_64) ARCH=amd64 ;;
    aarch64|arm64) ARCH=arm64 ;;
    *)
      echo "Unsupported architecture: $(uname -m). Supported: amd64, arm64." >&2
      exit 1
      ;;
  esac
}

_require_linux() {
  if [[ "$(uname -s)" != 'Linux' ]]; then
    echo 'Telorax releases are currently built for Linux only.' >&2
    exit 1
  fi

  _detect_arch
}

_fetch_latest_tag() {
  curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" \
    | sed -n 's/.*"tag_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' \
    | head -n 1
}

_install_app() {
  local tag="$1"
  local version pkg_name pkg_url tmp_pkg
  version="${tag#v}"
  _source_release_name

  if command -v dpkg >/dev/null 2>&1; then
    pkg_name="$(release_artifact_name "${version}" "${ARCH}" deb)"
    pkg_url="https://github.com/${REPO}/releases/download/${tag}/${pkg_name}"
    tmp_pkg="$(mktemp /tmp/telorax.XXXXXX.deb)"
    echo "Downloading ${pkg_url} ..."
    curl -fsSL -o "${tmp_pkg}" "${pkg_url}"
    echo 'Installing Telorax package (deb) ...'
    dpkg -i "${tmp_pkg}" || apt-get install -f -y
    rm -f "${tmp_pkg}"
    return
  fi

  if command -v rpm >/dev/null 2>&1; then
    pkg_name="$(release_artifact_name "${version}" "${ARCH}" rpm)"
    pkg_url="https://github.com/${REPO}/releases/download/${tag}/${pkg_name}"
    tmp_pkg="$(mktemp /tmp/telorax.XXXXXX.rpm)"
    echo "Downloading ${pkg_url} ..."
    curl -fsSL -o "${tmp_pkg}" "${pkg_url}"
    echo 'Installing Telorax package (rpm) ...'
    rpm -Uvh "${tmp_pkg}"
    rm -f "${tmp_pkg}"
    return
  fi

  echo 'Neither dpkg nor rpm found. Install a supported package manager or use the wheel method from README.' >&2
  exit 1
}

_ensure_env_file() {
  mkdir -p "${CONFIG_DIR}"
  if [[ ! -f "${ENV_FILE}" ]]; then
    if [[ -f "${CONFIG_DIR}/env.example" ]]; then
      cp "${CONFIG_DIR}/env.example" "${ENV_FILE}"
    else
      cat > "${ENV_FILE}" <<'EOF'
APP_TIMEZONE=UTC
APP_HOST=0.0.0.0
APP_PORT=8000

AUTH_USERNAME=telorax
AUTH_PASSWORD=changeme

DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3307
DB_NAME=telorax
DB_USER=telorax
DB_PASSWORD=secret

REDIS_HOST=127.0.0.1
REDIS_PORT=6380
REDIS_DB=0

LOG_LEVEL=INFO
LOG_JSON=true
EOF
    fi
    echo "Created default config at ${ENV_FILE}"
  fi

  if [[ -f "${ENV_FILE}" ]]; then
    chmod 600 "${ENV_FILE}"
    if id telorax >/dev/null 2>&1; then
      chown telorax:telorax "${ENV_FILE}"
    fi
  fi
}

_enable_telorax_service() {
  if command -v systemctl >/dev/null 2>&1; then
    systemctl daemon-reload
    systemctl enable telorax
    systemctl restart telorax
    echo 'Telorax service enabled and started.'
  fi
}

_install_all() {
  local tag="$1"
  _ensure_env_file

  echo 'Installing Telorax application package ...'
  _install_app "${tag}"

  if command -v telorax >/dev/null 2>&1; then
    echo 'Running database migrations ...'
    telorax migrate || true
  fi

  if [[ "${SKIP_DEPS}" != 1 ]]; then
    echo "Installing infrastructure dependencies (mode: ${DEPS_MODE}) ..."
    if ! deps_install; then
      echo 'Warning: dependency setup failed. Telorax is installed; fix deps and run: telorax deps install' >&2
    fi
  else
    echo 'Skipping dependency installation (INSTALL_SKIP_DEPS=1).'
  fi

  _enable_telorax_service

  echo
  echo "Installed successfully: telorax ${tag#v}"
  telorax version
  if [[ "${SKIP_DEPS}" != 1 ]]; then
    deps_status || true
  fi
  telorax doctor || true
}

_handle_deps_command() {
  local action="${1:-}"
  case "${action}" in
    install) deps_install ;;
    status) deps_status ;;
    start) deps_start ;;
    stop) deps_stop ;;
    restart) deps_restart ;;
    provision) deps_provision ;;
    *)
      echo "Unknown deps action: ${action}" >&2
      _usage
      exit 1
      ;;
  esac
}

main() {
  echo 'Telorax installer'
  _require_root
  _require_linux

  local command="${1:-install}"
  shift || true

  case "${command}" in
    -h|--help|help)
      _usage
      exit 0
      ;;
    deps)
      _source_deps
      _handle_deps_command "${1:-status}"
      ;;
    install)
      while [[ $# -gt 0 ]]; do
        case "$1" in
          --skip-deps) SKIP_DEPS=1; shift ;;
          *) echo "Unknown option: $1" >&2; _usage; exit 1 ;;
        esac
      done
      _run_install
      ;;
    upgrade)
      SKIP_DEPS=1
      _run_install
      ;;
    *)
      echo "Unknown command: ${command}" >&2
      _usage
      exit 1
      ;;
  esac
}

_run_install() {
  local tag
  echo "Fetching latest release from github.com/${REPO} ..."
  tag="$(_fetch_latest_tag)"
  if [[ -z "${tag}" ]]; then
    echo 'Could not resolve latest release tag.' >&2
    exit 1
  fi
  _source_deps "${tag}"
  _install_all "${tag}"
}

_script_is_entrypoint() {
  if [[ "${TELORAX_INSTALL_SOURCED:-}" == 1 ]]; then
    return 1
  fi
  if [[ -n "${BASH_SOURCE[0]:-}" ]]; then
    [[ "${BASH_SOURCE[0]}" == "${0}" ]]
    return
  fi
  return 0
}

if _script_is_entrypoint; then
  main "$@"
fi

#!/usr/bin/env bash
# Upgrade Telorax to a newer release and apply database migrations.
set -euo pipefail

UPGRADE_SCRIPT_VERSION='1'

_script_dir() {
  if [[ -n "${BASH_SOURCE[0]:-}" && "${BASH_SOURCE[0]}" != bash ]]; then
    cd "$(dirname "${BASH_SOURCE[0]}")" && pwd
    return
  fi
  echo '/usr/share/telorax'
}

_source_install_lib() {
  local script_dir="$(_script_dir)"
  local candidates=(
    /usr/share/telorax/install.sh
    "${script_dir}/install.sh"
  )

  for path in "${candidates[@]}"; do
    if [[ -f "${path}" ]]; then
      TELORAX_INSTALL_SOURCED=1
      # shellcheck source=/dev/null
      source "${path}"
      return
    fi
  done

  echo 'install.sh not found. Reinstall Telorax or run install.sh from release assets.' >&2
  exit 1
}

_installed_version() {
  if command -v telorax >/dev/null 2>&1; then
    telorax version | awk '{print $2}' | tr -d 'v'
    return
  fi
  echo 'unknown'
}

_version_lt() {
  local left="$1"
  local right="$2"
  [[ "$(printf '%s\n' "${left}" "${right}" | sort -V | head -n1)" == "${left}" && "${left}" != "${right}" ]]
}

upgrade_check() {
  _source_install_lib
  local installed latest tag
  installed="$(_installed_version)"
  tag="$(_fetch_latest_tag)"
  latest="${tag#v}"

  echo "Upgrade script: v${UPGRADE_SCRIPT_VERSION}"
  echo "Installed: ${installed}"
  echo "Latest:    ${latest} (${tag})"

  if [[ "${installed}" == unknown ]]; then
    echo 'Status:    telorax CLI not found'
    return
  fi
  if [[ "${installed}" == "${latest}" ]]; then
    echo 'Status:    up to date'
  elif _version_lt "${installed}" "${latest}"; then
    echo 'Status:    update available'
  else
    echo 'Status:    installed version is ahead of latest release'
  fi
}

upgrade_run() {
  local tag="${1:-}"
  _source_install_lib
  _require_root
  _require_linux

  if [[ -z "${tag}" ]]; then
    tag="$(_fetch_latest_tag)"
  fi
  if [[ -z "${tag}" ]]; then
    echo 'Could not resolve release tag.' >&2
    exit 1
  fi

  local latest="${tag#v}" installed
  installed="$(_installed_version)"

  if [[ "${installed}" == "${latest}" && "${TELORAX_FORCE_REINSTALL:-0}" != 1 ]]; then
    echo "Already on ${latest}."
  else
    if [[ "${installed}" == "${latest}" ]]; then
      echo "Reinstalling Telorax ${latest} ..."
    else
      echo "Upgrading Telorax ${installed} -> ${latest} ..."
    fi
    _install_app "${tag}"
  fi

  echo 'Running database migrations ...'
  telorax migrate

  if command -v systemctl >/dev/null 2>&1; then
    systemctl daemon-reload || true
    if systemctl is-enabled telorax.service >/dev/null 2>&1; then
      systemctl restart telorax.service
      echo 'Telorax service restarted.'
    fi
  fi

  telorax doctor || true
  echo "Upgrade complete: ${latest}"
}

_script_is_entrypoint() {
  if [[ -n "${BASH_SOURCE[0]:-}" ]]; then
    [[ "${BASH_SOURCE[0]}" == "${0}" ]]
    return
  fi
  return 0
}

if _script_is_entrypoint; then
  action="${1:-check}"
  case "${action}" in
    check|status) upgrade_check ;;
    run|upgrade) upgrade_run "${2:-}" ;;
    *)
      echo "Unknown action: ${action}" >&2
      echo 'Usage: upgrade.sh check|run [tag]' >&2
      exit 1
      ;;
  esac
fi

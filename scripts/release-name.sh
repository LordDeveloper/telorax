#!/usr/bin/env bash
# Shared release artifact naming: REPO_NAME.version-architecture[.ext]
set -euo pipefail

RELEASE_REPO_NAME="${RELEASE_REPO_NAME:-telorax}"

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

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  release_artifact_name "${1:?version}" "${2:?arch}" "${3:-}"
fi

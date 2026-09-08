#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
DOCS_DIR="${ROOT}/docs"

if ! command -v npm >/dev/null 2>&1; then
  echo 'npm is required to build docs.' >&2
  exit 1
fi

cd "${DOCS_DIR}"

if [ -f package-lock.json ]; then
  npm ci
else
  npm install
fi

npm run build

if [ ! -f dist/index.html ]; then
  echo 'Docs build failed: dist/index.html missing.' >&2
  exit 1
fi

echo "Built docs at ${DOCS_DIR}/dist"

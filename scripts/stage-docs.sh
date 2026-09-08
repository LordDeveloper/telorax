#!/usr/bin/env bash
# Copy built API docs into a package staging tree.
set -euo pipefail

DOCS_SRC="${1:?usage: stage-docs.sh DOCS_SRC DEST_DIR}"
DEST_DIR="${2:?usage: stage-docs.sh DOCS_SRC DEST_DIR}"

if [ ! -d "${DOCS_SRC}" ] || [ ! -f "${DOCS_SRC}/index.html" ]; then
  echo "Docs not found at ${DOCS_SRC}. Run scripts/build-docs.sh first." >&2
  exit 1
fi

mkdir -p "${DEST_DIR}"
cp -a "${DOCS_SRC}/." "${DEST_DIR}/"
echo "Staged docs: ${DOCS_SRC} -> ${DEST_DIR}"

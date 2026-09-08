#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=release-name.sh
source "${SCRIPT_DIR}/release-name.sh"

VERSION="${1:?usage: package-deb.sh VERSION ARCH WHEEL_PATH}"
ARCH="${2:-amd64}"
WHEEL_PATH="${3:?usage: package-deb.sh VERSION ARCH WHEEL_PATH}"
PKG_ROOT="$(mktemp -d "/tmp/telorax.${VERSION}-${ARCH}.XXXXXX")"
DEB_FILE="$(release_artifact_name "${VERSION}" "${ARCH}" deb)"
WHEEL_NAME="$(basename "${WHEEL_PATH}")"

trap 'rm -rf "${PKG_ROOT}"' EXIT

mkdir -p "${PKG_ROOT}/DEBIAN" \
  "${PKG_ROOT}/usr/local/bin" \
  "${PKG_ROOT}/etc/telorax" \
  "${PKG_ROOT}/lib/systemd/system" \
  "${PKG_ROOT}/usr/share/telorax" \
  "${PKG_ROOT}/opt/telorax/wheels"

cp "${WHEEL_PATH}" "${PKG_ROOT}/opt/telorax/wheels/${WHEEL_NAME}"
cp packaging/telorax.service "${PKG_ROOT}/lib/systemd/system/telorax.service"
cp packaging/env.example "${PKG_ROOT}/etc/telorax/env.example"
cp scripts/deps.sh "${PKG_ROOT}/usr/share/telorax/deps.sh"
chmod 755 "${PKG_ROOT}/usr/share/telorax/deps.sh"

cat > "${PKG_ROOT}/usr/local/bin/telorax" <<'EOF'
#!/bin/sh
exec /opt/telorax/venv/bin/telorax "$@"
EOF
chmod 755 "${PKG_ROOT}/usr/local/bin/telorax"

{
  echo 'Package: telorax'
  echo "Version: ${VERSION}"
  echo 'Section: utils'
  echo 'Priority: optional'
  echo "Architecture: ${ARCH}"
  echo 'Maintainer: Telorax Team'
  echo 'Depends: python3 (>= 3.11), python3-venv, python3-pip'
  echo 'Description: Telegram account automation platform'
} > "${PKG_ROOT}/DEBIAN/control"

cat > "${PKG_ROOT}/DEBIAN/postinst" <<EOF
#!/bin/sh
set -e
mkdir -p /etc/telorax
if [ ! -f /etc/telorax/.env ]; then
  cp /etc/telorax/env.example /etc/telorax/.env
  chmod 600 /etc/telorax/.env
fi
python3 -m venv /opt/telorax/venv
/opt/telorax/venv/bin/pip install --upgrade pip
/opt/telorax/venv/bin/pip install "/opt/telorax/wheels/${WHEEL_NAME}"
systemctl daemon-reload || true
EOF
chmod 755 "${PKG_ROOT}/DEBIAN/postinst"

dpkg-deb --build "${PKG_ROOT}" "${DEB_FILE}"
echo "Built ${DEB_FILE}"

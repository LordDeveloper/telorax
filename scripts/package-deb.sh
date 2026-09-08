#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:?usage: package-deb.sh VERSION}"
ARCH="${2:-amd64}"
BINARY_PATH="${3:-dist/telorax}"
PKG_ROOT="telorax_${VERSION}_linux_${ARCH}"

mkdir -p "${PKG_ROOT}/DEBIAN" \
  "${PKG_ROOT}/usr/local/bin" \
  "${PKG_ROOT}/etc/telorax" \
  "${PKG_ROOT}/lib/systemd/system" \
  "${PKG_ROOT}/usr/share/telorax"

cp "${BINARY_PATH}" "${PKG_ROOT}/usr/local/bin/telorax"
cp packaging/telorax.service "${PKG_ROOT}/lib/systemd/system/telorax.service"
cp packaging/env.example "${PKG_ROOT}/etc/telorax/env.example"
cp scripts/deps.sh "${PKG_ROOT}/usr/share/telorax/deps.sh"
chmod 755 "${PKG_ROOT}/usr/share/telorax/deps.sh"

{
  echo 'Package: telorax'
  echo "Version: ${VERSION}"
  echo 'Section: utils'
  echo 'Priority: optional'
  echo "Architecture: ${ARCH}"
  echo 'Maintainer: Telorax Team'
  echo 'Description: Telegram account automation platform'
} > "${PKG_ROOT}/DEBIAN/control"

cat > "${PKG_ROOT}/DEBIAN/postinst" <<'EOF'
#!/bin/sh
set -e
mkdir -p /etc/telorax
if [ ! -f /etc/telorax/.env ]; then
  cp /etc/telorax/env.example /etc/telorax/.env
  chmod 600 /etc/telorax/.env
fi
systemctl daemon-reload || true
EOF
chmod 755 "${PKG_ROOT}/DEBIAN/postinst"

dpkg-deb --build "${PKG_ROOT}"
mv "${PKG_ROOT}.deb" "telorax_${VERSION}_linux_${ARCH}.deb"

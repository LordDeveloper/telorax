#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:?usage: package-rpm.sh VERSION ARCH WHEEL_PATH}"
ARCH="${2:-amd64}"
WHEEL_PATH="${3:?usage: package-rpm.sh VERSION ARCH WHEEL_PATH}"

case "${ARCH}" in
  amd64) RPM_ARCH=x86_64 ;;
  arm64) RPM_ARCH=aarch64 ;;
  *)
    echo "Unsupported arch: ${ARCH}" >&2
    exit 1
    ;;
esac

WHEEL_NAME="$(basename "${WHEEL_PATH}")"
WORK="$(mktemp -d)"
trap 'rm -rf "${WORK}"' EXIT

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=release-name.sh
source "${SCRIPT_DIR}/release-name.sh"

ROOT="${WORK}/root"
mkdir -p "${ROOT}/opt/telorax/wheels" \
  "${ROOT}/usr/local/bin" \
  "${ROOT}/etc/telorax" \
  "${ROOT}/lib/systemd/system" \
  "${ROOT}/usr/share/telorax"

cp "${WHEEL_PATH}" "${ROOT}/opt/telorax/wheels/${WHEEL_NAME}"
cp packaging/telorax.service "${ROOT}/lib/systemd/system/telorax.service"
cp packaging/telorax-redis.service "${ROOT}/lib/systemd/system/telorax-redis.service"
cp packaging/telorax-mariadb.service "${ROOT}/lib/systemd/system/telorax-mariadb.service"
cp packaging/env.example "${ROOT}/etc/telorax/env.example"
cp scripts/deps.sh "${ROOT}/usr/share/telorax/deps.sh"
cp packaging/telorax-redis.service "${ROOT}/usr/share/telorax/telorax-redis.service"
cp packaging/telorax-mariadb.service "${ROOT}/usr/share/telorax/telorax-mariadb.service"
chmod 755 "${ROOT}/usr/share/telorax/deps.sh"

DOCS_SRC="${DOCS_SRC:-${SCRIPT_DIR}/../docs/dist}"
"${SCRIPT_DIR}/stage-docs.sh" "${DOCS_SRC}" "${ROOT}/usr/share/telorax/docs"

cat > "${ROOT}/usr/local/bin/telorax" <<'EOF'
#!/bin/sh
exec /opt/telorax/venv/bin/telorax "$@"
EOF
chmod 755 "${ROOT}/usr/local/bin/telorax"

cat > "${WORK}/telorax.spec" <<SPEC
Name:           telorax
Version:        ${VERSION}
Release:        1%{?dist}
Summary:        Telegram account automation platform
License:        MIT
BuildArch:      ${RPM_ARCH}
AutoReqProv:    no
Requires:       python3 >= 3.11
Requires:       python3-pip

%description
Telorax Telegram account automation platform.

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}
cp -a ${ROOT}/. %{buildroot}/

%files
/opt/telorax
/usr/local/bin/telorax
/etc/telorax/env.example
/lib/systemd/system/telorax.service
/lib/systemd/system/telorax-redis.service
/lib/systemd/system/telorax-mariadb.service
/usr/share/telorax/deps.sh
/usr/share/telorax/telorax-redis.service
/usr/share/telorax/telorax-mariadb.service
/usr/share/telorax/docs

%post
set -e
if ! id telorax >/dev/null 2>&1; then
  useradd --system --home /opt/telorax --shell /sbin/nologin telorax
fi
mkdir -p /etc/telorax /opt/telorax/data/mysql /opt/telorax/data/redis /opt/telorax/run /opt/telorax/config
if [ ! -f /etc/telorax/.env ]; then
  cp /etc/telorax/env.example /etc/telorax/.env
  chmod 600 /etc/telorax/.env
fi
python3 -m venv /opt/telorax/venv
/opt/telorax/venv/bin/pip install --upgrade pip
/opt/telorax/venv/bin/pip install "/opt/telorax/wheels/${WHEEL_NAME}"
chown -R telorax:telorax /opt/telorax/venv
systemctl daemon-reload || true
SPEC

mkdir -p "${HOME}/rpmbuild"/{BUILD,RPMS,SOURCES,SPECS,SRPMS,BUILDROOT}
cp "${WORK}/telorax.spec" "${HOME}/rpmbuild/SPECS/"

rpmbuild -bb "${HOME}/rpmbuild/SPECS/telorax.spec"

RPM_FILE="$(ls -1 "${HOME}/rpmbuild/RPMS/${RPM_ARCH}/telorax-${VERSION}"*.rpm | head -n 1)"
OUT="$(release_artifact_name "${VERSION}" "${ARCH}" rpm)"
cp -f "${RPM_FILE}" "${OUT}"
echo "Built ${OUT}"

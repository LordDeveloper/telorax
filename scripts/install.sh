#!/usr/bin/env bash
set -euo pipefail

REPO="${TELORAX_REPO:-LordDeveloper/telorax}"
ARCH="${TELORAX_ARCH:-amd64}"
CONFIG_DIR="${TELORAX_CONFIG_DIR:-/etc/telorax}"
ENV_FILE="${CONFIG_DIR}/.env"

if [[ "$(id -u)" -ne 0 ]]; then
  echo 'This installer must run as root. Use: curl ... | sudo bash' >&2
  exit 1
fi

if [[ "$(uname -s)" != 'Linux' ]]; then
  echo 'Telorax releases are currently built for Linux only.' >&2
  exit 1
fi

if [[ "$(uname -m)" != 'x86_64' ]]; then
  echo "Unsupported architecture: $(uname -m). Only amd64 is supported." >&2
  exit 1
fi

echo "Fetching latest release from github.com/${REPO} ..."
TAG=$(
  curl -fsSL "https://api.github.com/repos/${REPO}/releases/latest" \
    | sed -n 's/.*"tag_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' \
    | head -n 1
)

if [[ -z "${TAG}" ]]; then
  echo 'Could not resolve latest release tag.' >&2
  exit 1
fi

VERSION="${TAG#v}"
DEB_NAME="telorax_${VERSION}_linux_${ARCH}.deb"
DEB_URL="https://github.com/${REPO}/releases/download/${TAG}/${DEB_NAME}"
TMP_DEB="$(mktemp /tmp/telorax.XXXXXX.deb)"

echo "Downloading ${DEB_URL} ..."
curl -fsSL -o "${TMP_DEB}" "${DEB_URL}"

echo 'Installing package ...'
if command -v dpkg >/dev/null 2>&1; then
  dpkg -i "${TMP_DEB}" || apt-get install -f -y
else
  echo 'dpkg not found. Install dpkg or use the binary install method from README.' >&2
  rm -f "${TMP_DEB}"
  exit 1
fi

rm -f "${TMP_DEB}"

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
DB_PORT=3306
DB_NAME=telorax
DB_USER=telorax
DB_PASSWORD=secret

REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0

LOG_LEVEL=INFO
LOG_JSON=true
EOF
  fi
  chmod 600 "${ENV_FILE}"
  echo "Created default config at ${ENV_FILE}"
fi

if command -v systemctl >/dev/null 2>&1; then
  systemctl daemon-reload
  systemctl enable telorax
  systemctl restart telorax
  echo 'Telorax service enabled and started.'
fi

echo
echo "Installed successfully: telorax ${VERSION}"
telorax version
telorax doctor

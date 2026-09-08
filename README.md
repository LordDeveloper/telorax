# Telorax

**Run Telegram account farms like infrastructure — not scripts duct-taped together.**

Telorax is a platform for operating real Telegram accounts at scale: queue engagement work, track fulfillment, manage sessions, and expose a clean HTTP API. Think of it as the control plane between your account pool and the actions you need done — views, joins, reactions, poll votes, and more.

Built in Python with a proper service layer, async I/O, and packaging that actually installs on a bare Linux box.

---

## What you get

- **Account pool management** — operational state, rate limits, reliability scoring
- **Operations queue** — submit batch work (`target_count` + engagement kind + target spec), track progress
- **HTTP API** — `/v1/operations` for creating and inspecting queued work
- **CLI + TUI** — `telorax` dashboard for local ops, `telorax serve` for headless production
- **Sensible installs** — one-liner script, `.deb`, `.rpm`, or wheel; amd64 and arm64
- **Deps handled** — optional auto-install of MariaDB/MySQL and Redis on Debian/Ubuntu

Supported engagement kinds: `VIEW`, `SUBSCRIBE`, `POLL_VOTE`, `REACTION`, `SPONSORED`, `SEARCH_VIEW`, `BUTTON_CLICK`, `BOT_START`.

---

## Quick start (recommended)

Full install — Telorax + MariaDB + Redis + database provisioning:

```bash
curl -fsSL https://github.com/LordDeveloper/telorax/releases/latest/download/install.sh | sudo bash
```

Telorax only (you bring your own MySQL and Redis):

```bash
INSTALL_SKIP_DEPS=1 curl -fsSL https://github.com/LordDeveloper/telorax/releases/latest/download/install.sh | sudo bash
```

Then configure, migrate, and verify:

```bash
sudo telorax config init
sudo nano /etc/telorax/.env
telorax migrate
telorax doctor
sudo systemctl enable --now telorax
```

The installer detects your CPU architecture and picks the right package (`.deb` on Debian/Ubuntu, `.rpm` on RHEL-family distros).

---

## Dependency management

`install.sh` can install and manage MariaDB and Redis for you. Same commands exist in the CLI:

```bash
# via install script
curl -fsSL .../install.sh | sudo bash -s -- deps install
curl -fsSL .../install.sh | sudo bash -s -- deps status
curl -fsSL .../install.sh | sudo bash -s -- deps restart

# via CLI (after install)
sudo telorax deps install      # apt: mariadb-server + redis-server
sudo telorax deps status       # service + DB + redis ping checks
sudo telorax deps provision    # create DB/user from /etc/telorax/.env
sudo telorax deps restart
```

On Debian/Ubuntu, Redis is wired through `redis-server.service` (not the `redis.service` alias) so `systemctl enable` works reliably.

---

## Manual install

### `.deb` (Debian / Ubuntu)

```bash
TAG=$(curl -fsSL https://api.github.com/repos/LordDeveloper/telorax/releases/latest \
  | sed -n 's/.*"tag_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)
VERSION="${TAG#v}"
ARCH=$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/')
curl -fsSL -o /tmp/telorax.deb \
  "https://github.com/LordDeveloper/telorax/releases/download/${TAG}/telorax.${VERSION}-${ARCH}.deb"
sudo dpkg -i /tmp/telorax.deb
sudo apt-get install -f -y
sudo systemctl enable --now telorax
telorax doctor
```

### `.rpm` (RHEL / Fedora / Amazon Linux)

```bash
TAG=$(curl -fsSL https://api.github.com/repos/LordDeveloper/telorax/releases/latest \
  | sed -n 's/.*"tag_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)
VERSION="${TAG#v}"
ARCH=$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/')
curl -fsSL -o /tmp/telorax.rpm \
  "https://github.com/LordDeveloper/telorax/releases/download/${TAG}/telorax.${VERSION}-${ARCH}.rpm"
sudo rpm -Uvh /tmp/telorax.rpm
sudo systemctl enable --now telorax
```

### Wheel (any Linux with Python 3.11+)

```bash
TAG=...   # same as above
VERSION="${TAG#v}"
python3 -m venv /opt/telorax/venv
/opt/telorax/venv/bin/pip install \
  "https://github.com/LordDeveloper/telorax/releases/download/${TAG}/telorax.${VERSION}-any.whl"
sudo ln -sf /opt/telorax/venv/bin/telorax /usr/local/bin/telorax
```

---

## Configuration

Single flat env file — no prefix soup:

```
/etc/telorax/.env
```

Example:

```env
APP_TIMEZONE=UTC
APP_HOST=0.0.0.0
APP_PORT=8000

AUTH_USERNAME=telorax
AUTH_PASSWORD=change-me

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
```

`DATABASE_URL` and `REDIS_URL` are derived automatically — you don't maintain duplicate connection strings.

```bash
sudo telorax config init
telorax config validate
```

For local development, point at a different file:

```bash
export ENV_FILE=./.env
```

---

## Running

**Interactive dashboard**

```bash
telorax
```

**Production API server**

```bash
telorax serve
# or via systemd (installed by default)
sudo systemctl status telorax
sudo journalctl -u telorax -f
```

**Health check**

```bash
telorax doctor
curl -s localhost:8000/v1/status
```

---

## API sketch

Create an operation (e.g. 500 views on a channel):

```bash
curl -s -X POST localhost:8000/v1/operations \
  -H 'Content-Type: application/json' \
  -d '{
    "engagement_kind": "VIEW",
    "target_count": 500,
    "target_spec": {"peer_ref": "@yourchannel"}
  }'
```

List queued operations:

```bash
curl -s localhost:8000/v1/operations/queued
```

---

## Requirements

| Component | Version | Auto-installed |
|-----------|---------|----------------|
| Linux | amd64 or arm64 | — |
| Python | 3.11+ (bundled in packages via venv) | yes |
| MariaDB / MySQL | 10.6+ | `install.sh` / `telorax deps install` |
| Redis | 7+ | `install.sh` / `telorax deps install` |

Debian/Ubuntu 22.04+ and RHEL-family 8+ are the primary targets.

---

## Releases

Every push to `main` triggers CI that:

1. Runs tests (ruff, mypy, pytest)
2. Builds a universal wheel
3. Packages `.deb` and `.rpm` for **amd64** and **arm64**
4. Tags a new patch version and publishes a GitHub Release

**Naming:** `telorax.<version>-<architecture>.<ext>`

| Asset | Platform |
|-------|----------|
| `telorax.*-amd64.deb` | Debian / Ubuntu (x86_64) |
| `telorax.*-arm64.deb` | Debian / Ubuntu (aarch64) |
| `telorax.*-amd64.rpm` | RHEL / Fedora / Amazon (x86_64) |
| `telorax.*-arm64.rpm` | RHEL / Fedora / Amazon (aarch64) |
| `telorax.*-any.whl` | Any Linux, any arch |
| `install.sh`, `deps.sh`, `SHA256SUMS` | Installer helpers |

Commits with `[skip ci]` (e.g. automated version bumps) do not re-trigger releases.

---

## Development

```bash
git clone https://github.com/LordDeveloper/telorax.git
cd telorax
python -m pip install -e ".[dev]"
export ENV_FILE=./.env
pytest
ruff check telorax tests
mypy telorax/
```

Architecture: domain entities → application services → infrastructure repos → FastAPI / CLI. DI via `dependency-injector`.

---

## License

See repository for license details.

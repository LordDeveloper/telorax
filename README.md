# Telorax

Platform اتوماسیون Telegram account — مدیریت farm اکانت و اجرای operationهای engagement.

---

## نصب روی سرور (Ubuntu / Debian)

### روش ۱ — یک خط (پیشنهادی)

نصب کامل Telorax به‌همراه MariaDB/MySQL و Redis:

```bash
curl -fsSL https://github.com/LordDeveloper/telorax/releases/latest/download/install.sh | sudo bash
```

فقط نصب Telorax (بدون دیتابیس و Redis):

```bash
INSTALL_SKIP_DEPS=1 curl -fsSL https://github.com/LordDeveloper/telorax/releases/latest/download/install.sh | sudo bash
```

مدیریت پیش‌نیازها (MariaDB/MySQL و Redis):

```bash
curl -fsSL https://github.com/LordDeveloper/telorax/releases/latest/download/install.sh | sudo bash -s -- deps install
curl -fsSL https://github.com/LordDeveloper/telorax/releases/latest/download/install.sh | sudo bash -s -- deps status
curl -fsSL https://github.com/LordDeveloper/telorax/releases/latest/download/install.sh | sudo bash -s -- deps restart
```

بعد از نصب، از CLI هم می‌توانید استفاده کنید:

```bash
sudo telorax deps install
sudo telorax deps status
sudo telorax deps restart
sudo telorax deps provision   # create/update DB and user from .env
```

### روش ۲ — نصب دستی با `.deb`

```bash
TAG=$(curl -fsSL https://api.github.com/repos/LordDeveloper/telorax/releases/latest | sed -n 's/.*"tag_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)
VERSION="${TAG#v}"
curl -fsSL -o /tmp/telorax.deb "https://github.com/LordDeveloper/telorax/releases/download/${TAG}/telorax.${VERSION}-amd64.deb"
sudo dpkg -i /tmp/telorax.deb
sudo apt-get install -f -y
sudo systemctl enable --now telorax
telorax doctor
```

### روش ۳ — wheel (بدون .deb)

```bash
TAG=$(curl -fsSL https://api.github.com/repos/LordDeveloper/telorax/releases/latest | sed -n 's/.*"tag_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)
VERSION="${TAG#v}"
python3 -m venv /opt/telorax/venv
/opt/telorax/venv/bin/pip install "https://github.com/LordDeveloper/telorax/releases/download/${TAG}/telorax.${VERSION}-any.whl"
sudo ln -sf /opt/telorax/venv/bin/telorax /usr/local/bin/telorax
telorax version
```

---

## تنظیمات

فایل env در مسیر ثابت:

```
/etc/telorax/.env
```

نمونه:

```env
APP_TIMEZONE=Asia/Tehran
APP_HOST=0.0.0.0
APP_PORT=8000

AUTH_USERNAME=telorax
AUTH_PASSWORD=your-secret

DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=telorax
DB_USER=telorax
DB_PASSWORD=secret

REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
```

`DATABASE_URL` و `REDIS_URL` به صورت خودکار از همین مقادیر ساخته می‌شوند.

ساخت config اولیه:

```bash
sudo telorax config init
sudo nano /etc/telorax/.env
sudo chmod 600 /etc/telorax/.env
telorax config validate
```

---

## بعد از نصب

```bash
sudo nano /etc/telorax/.env
telorax migrate
telorax doctor
sudo systemctl status telorax
sudo journalctl -u telorax -f
```

### TUI Dashboard

```bash
telorax
```

### Headless (production)

```bash
telorax serve
```

---

## پیش‌نیازها

| سرویس | نسخه پیشنهادی | نصب خودکار |
|--------|----------------|-------------|
| Ubuntu / Debian | 22.04 / 24.04 | — |
| MariaDB / MySQL | 10.6+ | `install.sh` / `telorax deps install` |
| Redis | 7+ | `install.sh` / `telorax deps install` |

`install.sh` به‌صورت پیش‌فرض MariaDB و Redis را با `apt` نصب می‌کند، سرویس‌ها را enable/start می‌کند و دیتابیس `telorax` را طبق `/etc/telorax/.env` می‌سازد.

---

## Release

با هر push به `main`، CI به‌صورت خودکار:

1. آخرین tag را می‌خواند و patch را یکی زیاد می‌کند (اولین release: `v0.1.0`)
2. تست، بیلد باینری و `.deb` را اجرا می‌کند
3. tag جدید و GitHub Release می‌سازد

Assetهای هر release:

```
telorax
telorax_{version}_linux_amd64.deb
install.sh
deps.sh
SHA256SUMS
```

برای جلوگیری از loop، commitهای `[skip ci]` (مثل bump خودکار version) release را دوباره trigger نمی‌کنند.

---

## Development

```bash
git clone https://github.com/LordDeveloper/telorax.git
cd telorax
python -m pip install -e ".[dev]"
export ENV_FILE=./.env
pytest
ruff check .
mypy telorax/
```

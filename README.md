# Telorax

Platform اتوماسیون Telegram account — مدیریت farm اکانت و اجرای campaignهای engagement.

---

## نصب روی سرور (Ubuntu / Debian)

### روش ۱ — یک خط (پیشنهادی)

```bash
curl -fsSL https://github.com/LordDeveloper/telorax/releases/latest/download/install.sh | sudo bash
```

### روش ۲ — نصب دستی با `.deb`

```bash
TAG=$(curl -fsSL https://api.github.com/repos/LordDeveloper/telorax/releases/latest | sed -n 's/.*"tag_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)
VERSION="${TAG#v}"
curl -fsSL -o /tmp/telorax.deb "https://github.com/LordDeveloper/telorax/releases/download/${TAG}/telorax_${VERSION}_linux_amd64.deb"
sudo dpkg -i /tmp/telorax.deb
sudo apt-get install -f -y
sudo systemctl enable --now telorax
telorax doctor
```

### روش ۳ — باینری standalone

```bash
TAG=$(curl -fsSL https://api.github.com/repos/LordDeveloper/telorax/releases/latest | sed -n 's/.*"tag_name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n 1)
curl -fsSL -o /tmp/telorax "https://github.com/LordDeveloper/telorax/releases/download/${TAG}/telorax"
sudo install -m 755 /tmp/telorax /usr/local/bin/telorax
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

| سرویس | نسخه پیشنهادی |
|--------|----------------|
| Ubuntu | 22.04 / 24.04 |
| MariaDB / MySQL | 10.6+ |
| Redis | 7+ |

---

## Release

هر tag با فرمت `v*.*.*` باعث ساخت خودکار release می‌شود:

```
telorax
telorax_{version}_linux_amd64.deb
install.sh
SHA256SUMS
```

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

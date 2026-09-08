#!/usr/bin/env bash
# Telorax infrastructure dependencies: MariaDB/MySQL and Redis.
set -euo pipefail

CONFIG_DIR="${CONFIG_DIR:-/etc/telorax}"
ENV_FILE="${ENV_FILE:-${CONFIG_DIR}/.env}"

_load_env_value() {
  local key="$1"
  local default="$2"
  if [[ -f "${ENV_FILE}" ]]; then
    local line
    line="$(grep -E "^${key}=" "${ENV_FILE}" | tail -n 1 || true)"
    if [[ -n "${line}" ]]; then
      echo "${line#*=}"
      return
    fi
  fi
  echo "${default}"
}

_ensure_root() {
  if [[ "$(id -u)" -ne 0 ]]; then
    echo 'This command must run as root.' >&2
    exit 1
  fi
}

_ensure_apt() {
  if ! command -v apt-get >/dev/null 2>&1; then
    echo 'Only Debian/Ubuntu systems with apt-get are supported.' >&2
    exit 1
  fi
}

_service_name() {
  local base="$1"
  if systemctl list-unit-files "${base}.service" --no-legend 2>/dev/null | grep -q "${base}.service"; then
    echo "${base}"
    return
  fi
  case "${base}" in
    mysql)
      if systemctl list-unit-files mariadb.service --no-legend 2>/dev/null | grep -q mariadb.service; then
        echo 'mariadb'
        return
      fi
      ;;
    mariadb)
      if systemctl list-unit-files mysql.service --no-legend 2>/dev/null | grep -q mysql.service; then
        echo 'mysql'
        return
      fi
      ;;
    redis)
      if systemctl list-unit-files redis-server.service --no-legend 2>/dev/null | grep -q redis-server.service; then
        echo 'redis-server'
        return
      fi
      if systemctl list-unit-files redis.service --no-legend 2>/dev/null | grep -q redis.service; then
        echo 'redis'
        return
      fi
      ;;
  esac
  echo "${base}"
}

_deps_install_packages() {
  _ensure_root
  _ensure_apt

  export DEBIAN_FRONTEND=noninteractive
  apt-get update
  apt-get install -y mariadb-server redis-server curl ca-certificates

  systemctl enable "$(_service_name mariadb)"
  systemctl enable "$(_service_name redis)"
  systemctl start "$(_service_name mariadb)"
  systemctl start "$(_service_name redis)"
}

_deps_provision_database() {
  _ensure_root

  local db_name db_user db_password
  db_name="$(_load_env_value DB_NAME telorax)"
  db_user="$(_load_env_value DB_USER telorax)"
  db_password="$(_load_env_value DB_PASSWORD secret)"

  if ! command -v mysql >/dev/null 2>&1; then
    echo 'mysql client not found. Run deps install first.' >&2
    exit 1
  fi

  mysql --protocol=socket -uroot <<SQL
CREATE DATABASE IF NOT EXISTS \`${db_name}\`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '${db_user}'@'localhost' IDENTIFIED BY '${db_password}';
ALTER USER '${db_user}'@'localhost' IDENTIFIED BY '${db_password}';
GRANT ALL PRIVILEGES ON \`${db_name}\`.* TO '${db_user}'@'localhost';
FLUSH PRIVILEGES;
SQL

  echo "Database ready: ${db_name} (user: ${db_user})"
}

deps_install() {
  _deps_install_packages
  _deps_provision_database
  echo 'Dependencies installed: MariaDB/MySQL and Redis.'
}

deps_status() {
  local db_service redis_service
  db_service="$(_service_name mariadb)"
  redis_service="$(_service_name redis)"

  echo "MariaDB/MySQL (${db_service}): $(systemctl is-active "${db_service}" 2>/dev/null || echo 'missing')"
  echo "Redis (${redis_service}): $(systemctl is-active "${redis_service}" 2>/dev/null || echo 'missing')"

  if command -v mysql >/dev/null 2>&1; then
    local db_name db_user
    db_name="$(_load_env_value DB_NAME telorax)"
    db_user="$(_load_env_value DB_USER telorax)"
    if mysql --protocol=socket -uroot -e "USE \`${db_name}\`;" >/dev/null 2>&1; then
      echo "Database '${db_name}': OK"
    else
      echo "Database '${db_name}': missing"
    fi
    if mysql --protocol=socket -uroot -Nse "SELECT 1 FROM mysql.user WHERE User='${db_user}' AND Host='localhost';" | grep -q 1; then
      echo "Database user '${db_user}': OK"
    else
      echo "Database user '${db_user}': missing"
    fi
  fi

  if command -v redis-cli >/dev/null 2>&1; then
    local redis_host redis_port
    redis_host="$(_load_env_value REDIS_HOST 127.0.0.1)"
    redis_port="$(_load_env_value REDIS_PORT 6379)"
    if redis-cli -h "${redis_host}" -p "${redis_port}" ping 2>/dev/null | grep -q PONG; then
      echo "Redis ping (${redis_host}:${redis_port}): OK"
    else
      echo "Redis ping (${redis_host}:${redis_port}): failed"
    fi
  fi
}

_deps_manage() {
  _ensure_root
  local action="$1"
  local db_service redis_service
  db_service="$(_service_name mariadb)"
  redis_service="$(_service_name redis)"

  systemctl "${action}" "${db_service}"
  systemctl "${action}" "${redis_service}"
  echo "Services ${action}ed: ${db_service}, ${redis_service}"
}

deps_start() { _deps_manage start; }
deps_stop() { _deps_manage stop; }
deps_restart() { _deps_manage restart; }

deps_provision() { _deps_provision_database; }

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  action="${1:-status}"
  case "${action}" in
    install) deps_install ;;
    status) deps_status ;;
    start) deps_start ;;
    stop) deps_stop ;;
    restart) deps_restart ;;
    provision) deps_provision ;;
    *)
      echo "Unknown action: ${action}" >&2
      echo 'Usage: deps.sh install|status|start|stop|restart|provision' >&2
      exit 1
      ;;
  esac
fi

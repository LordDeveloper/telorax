#!/usr/bin/env bash
# Telorax infrastructure dependencies: MariaDB/MySQL and Redis.
# Default mode (local): isolated instances under /opt/telorax — no systemctl enable on aliases.
set -euo pipefail

CONFIG_DIR="${CONFIG_DIR:-/etc/telorax}"
ENV_FILE="${ENV_FILE:-${CONFIG_DIR}/.env}"
TELORAX_ROOT="${TELORAX_ROOT:-/opt/telorax}"
DEPS_MODE="${DEPS_MODE:-local}"  # local | system
LOCAL_MYSQL_PORT="${LOCAL_MYSQL_PORT:-3307}"
LOCAL_REDIS_PORT="${LOCAL_REDIS_PORT:-6380}"

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

_set_env_value() {
  local key="$1"
  local value="$2"
  mkdir -p "${CONFIG_DIR}"
  if [[ ! -f "${ENV_FILE}" ]]; then
    touch "${ENV_FILE}"
    chmod 600 "${ENV_FILE}"
  fi
  if grep -qE "^${key}=" "${ENV_FILE}"; then
    sed -i "s|^${key}=.*|${key}=${value}|" "${ENV_FILE}"
  else
    printf '%s=%s\n' "${key}" "${value}" >> "${ENV_FILE}"
  fi
}

_ensure_root() {
  if [[ "$(id -u)" -ne 0 ]]; then
    echo 'This command must run as root.' >&2
    exit 1
  fi
}

_ensure_apt() {
  if ! command -v apt-get >/dev/null 2>&1; then
    echo 'Automatic dependency install requires apt-get (Debian/Ubuntu).' >&2
    exit 1
  fi
}

_mysqld_bin() {
  if command -v mariadbd >/dev/null 2>&1; then
    command -v mariadbd
    return
  fi
  command -v mysqld
}

_mysql_client() {
  if command -v mariadb >/dev/null 2>&1; then
    echo mariadb
    return
  fi
  echo mysql
}

_system_service_name() {
  local base="$1"
  case "${base}" in
    mysql|mariadb)
      if systemctl list-unit-files mariadb.service --no-legend 2>/dev/null | awk '{print $1}' | grep -qx 'mariadb.service'; then
        echo 'mariadb'
        return
      fi
      if systemctl list-unit-files mysql.service --no-legend 2>/dev/null | awk '{print $1}' | grep -qx 'mysql.service'; then
        echo 'mysql'
        return
      fi
      ;;
    redis)
      # Never return bare "redis" — on Debian/Ubuntu it is an alias and systemctl enable fails.
      if [[ -f /lib/systemd/system/redis-server.service || -f /usr/lib/systemd/system/redis-server.service ]]; then
        echo 'redis-server'
        return
      fi
      if systemctl cat redis-server.service >/dev/null 2>&1; then
        echo 'redis-server'
        return
      fi
      ;;
  esac

  if systemctl list-unit-files "${base}.service" --no-legend 2>/dev/null | awk '{print $1}' | grep -qx "${base}.service"; then
    echo "${base}"
    return
  fi
  echo "${base}"
}

_systemctl_unit() {
  local action="$1"
  local service="$2"
  systemctl "${action}" "${service}.service"
}

_ensure_telorax_layout() {
  mkdir -p \
    "${TELORAX_ROOT}/data/mysql" \
    "${TELORAX_ROOT}/data/redis" \
    "${TELORAX_ROOT}/run" \
    "${TELORAX_ROOT}/config" \
    "${TELORAX_ROOT}/wheels"
}

_install_packages() {
  _ensure_root
  _ensure_apt
  export DEBIAN_FRONTEND=noninteractive
  apt-get update
  apt-get install -y mariadb-server redis-server curl ca-certificates
}

_local_write_configs() {
  cat > "${TELORAX_ROOT}/config/my.cnf" <<EOF
[mysqld]
basedir=/usr
datadir=${TELORAX_ROOT}/data/mysql
socket=${TELORAX_ROOT}/run/mysqld.sock
port=${LOCAL_MYSQL_PORT}
bind-address=127.0.0.1
pid-file=${TELORAX_ROOT}/run/mysqld.pid
skip-name-resolve=1
character-set-server=utf8mb4
collation-server=utf8mb4_unicode_ci

[client]
socket=${TELORAX_ROOT}/run/mysqld.sock
port=${LOCAL_MYSQL_PORT}
EOF

  cat > "${TELORAX_ROOT}/config/redis.conf" <<EOF
bind 127.0.0.1
port ${LOCAL_REDIS_PORT}
dir ${TELORAX_ROOT}/data/redis
pidfile ${TELORAX_ROOT}/run/redis.pid
daemonize no
supervised no
EOF
}

_local_init_mysql() {
  if [[ -d "${TELORAX_ROOT}/data/mysql/mysql" ]]; then
    return
  fi

  local mysqld_bin
  mysqld_bin="$(_mysqld_bin)"

  echo "Initializing Telorax MariaDB data directory at ${TELORAX_ROOT}/data/mysql ..."
  chown -R mysql:mysql "${TELORAX_ROOT}/data/mysql" "${TELORAX_ROOT}/run"
  chmod 750 "${TELORAX_ROOT}/data/mysql"

  if command -v mariadb-install-db >/dev/null 2>&1; then
    mariadb-install-db --user=mysql --basedir=/usr --datadir="${TELORAX_ROOT}/data/mysql"
  elif command -v mysql_install_db >/dev/null 2>&1; then
    mysql_install_db --user=mysql --basedir=/usr --datadir="${TELORAX_ROOT}/data/mysql"
  else
    "${mysqld_bin}" --defaults-file="${TELORAX_ROOT}/config/my.cnf" --initialize-insecure --user=mysql
  fi
}

_local_install_units() {
  local unit_dir='/lib/systemd/system'
  if [[ ! -d "${unit_dir}" ]]; then
    unit_dir='/usr/lib/systemd/system'
  fi

  if [[ -f /usr/share/telorax/telorax-redis.service ]]; then
    cp /usr/share/telorax/telorax-redis.service "${unit_dir}/telorax-redis.service"
    cp /usr/share/telorax/telorax-mariadb.service "${unit_dir}/telorax-mariadb.service"
  elif [[ -n "${BASH_SOURCE[0]:-}" && -f "$(dirname "${BASH_SOURCE[0]}")/../packaging/telorax-redis.service" ]]; then
    cp "$(dirname "${BASH_SOURCE[0]}")/../packaging/telorax-redis.service" "${unit_dir}/telorax-redis.service"
    cp "$(dirname "${BASH_SOURCE[0]}")/../packaging/telorax-mariadb.service" "${unit_dir}/telorax-mariadb.service"
  else
    cat > "${unit_dir}/telorax-redis.service" <<'EOF'
[Unit]
Description=Telorax isolated Redis
After=network.target
PartOf=telorax.service

[Service]
Type=simple
User=redis
Group=redis
ExecStart=/usr/bin/redis-server /opt/telorax/config/redis.conf
RuntimeDirectory=telorax
RuntimeDirectoryMode=0755
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
    cat > "${unit_dir}/telorax-mariadb.service" <<'EOF'
[Unit]
Description=Telorax isolated MariaDB
After=network.target
PartOf=telorax.service

[Service]
Type=simple
User=mysql
Group=mysql
ExecStart=/usr/sbin/mysqld --defaults-file=/opt/telorax/config/my.cnf
PIDFile=/opt/telorax/run/mysqld.pid
Restart=on-failure
RestartSec=5
TimeoutStartSec=120

[Install]
WantedBy=multi-user.target
EOF
  fi

  chown -R redis:redis "${TELORAX_ROOT}/data/redis" 2>/dev/null || true
  chown -R mysql:mysql "${TELORAX_ROOT}/data/mysql" "${TELORAX_ROOT}/run" 2>/dev/null || true
  systemctl daemon-reload
}

_local_configure_env() {
  _set_env_value DB_HOST 127.0.0.1
  _set_env_value DB_PORT "${LOCAL_MYSQL_PORT}"
  _set_env_value REDIS_HOST 127.0.0.1
  _set_env_value REDIS_PORT "${LOCAL_REDIS_PORT}"
  echo "Updated ${ENV_FILE} for local Telorax services (MySQL:${LOCAL_MYSQL_PORT}, Redis:${LOCAL_REDIS_PORT})."
}

_local_start() {
  _systemctl_unit enable telorax-mariadb
  _systemctl_unit enable telorax-redis
  _systemctl_unit start telorax-mariadb
  _systemctl_unit start telorax-redis
}

_local_stop() {
  _systemctl_unit stop telorax-redis || true
  _systemctl_unit stop telorax-mariadb || true
}

_deps_install_local() {
  _ensure_telorax_layout
  _install_packages
  _local_write_configs
  _local_init_mysql
  _local_install_units
  _local_configure_env
  _local_start
}

_deps_install_system() {
  _install_packages
  local db_service redis_service
  db_service="$(_system_service_name mariadb)"
  redis_service="$(_system_service_name redis)"
  _systemctl_unit enable "${db_service}"
  _systemctl_unit enable "${redis_service}"
  _systemctl_unit start "${db_service}"
  _systemctl_unit start "${redis_service}"
  _set_env_value DB_PORT 3306
  _set_env_value REDIS_PORT 6379
}

_provision_database() {
  _ensure_root

  local db_name db_user db_password mysql_cmd=()
  db_name="$(_load_env_value DB_NAME telorax)"
  db_user="$(_load_env_value DB_USER telorax)"
  db_password="$(_load_env_value DB_PASSWORD secret)"

  if ! command -v "$(_mysql_client)" >/dev/null 2>&1; then
    echo 'mysql client not found. Run deps install first.' >&2
    exit 1
  fi

  if [[ "${DEPS_MODE}" == local ]]; then
    mysql_cmd=(--protocol=socket --socket="${TELORAX_ROOT}/run/mysqld.sock" -uroot)
  else
    mysql_cmd=(--protocol=socket -uroot)
  fi

  "${mysql_cmd[@]}" <<SQL
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
  echo "Installing dependencies (mode: ${DEPS_MODE}) ..."
  if [[ "${DEPS_MODE}" == system ]]; then
    _deps_install_system
  else
    _deps_install_local
  fi
  _provision_database
  echo 'Dependencies installed under Telorax environment.'
}

deps_status() {
  if [[ "${DEPS_MODE}" == local ]]; then
    echo "Mode: local (${TELORAX_ROOT})"
    echo "MariaDB (telorax-mariadb): $(systemctl is-active telorax-mariadb.service 2>/dev/null || echo 'missing')"
    echo "Redis (telorax-redis): $(systemctl is-active telorax-redis.service 2>/dev/null || echo 'missing')"
  else
    local db_service redis_service
    db_service="$(_system_service_name mariadb)"
    redis_service="$(_system_service_name redis)"
    echo 'Mode: system'
    echo "MariaDB/MySQL (${db_service}): $(systemctl is-active "${db_service}.service" 2>/dev/null || echo 'missing')"
    echo "Redis (${redis_service}): $(systemctl is-active "${redis_service}.service" 2>/dev/null || echo 'missing')"
  fi

  if command -v "$(_mysql_client)" >/dev/null 2>&1; then
    local db_name db_user mysql_cmd=()
    db_name="$(_load_env_value DB_NAME telorax)"
    db_user="$(_load_env_value DB_USER telorax)"
    if [[ "${DEPS_MODE}" == local ]]; then
      mysql_cmd=(--protocol=socket --socket="${TELORAX_ROOT}/run/mysqld.sock" -uroot)
    else
      mysql_cmd=(--protocol=socket -uroot)
    fi
    if "${mysql_cmd[@]}" -e "USE \`${db_name}\`;" >/dev/null 2>&1; then
      echo "Database '${db_name}': OK"
    else
      echo "Database '${db_name}': missing"
    fi
    if "${mysql_cmd[@]}" -Nse "SELECT 1 FROM mysql.user WHERE User='${db_user}' AND Host='localhost';" | grep -q 1; then
      echo "Database user '${db_user}': OK"
    else
      echo "Database user '${db_user}': missing"
    fi
  fi

  if command -v redis-cli >/dev/null 2>&1; then
    local redis_host redis_port
    redis_host="$(_load_env_value REDIS_HOST 127.0.0.1)"
    redis_port="$(_load_env_value REDIS_PORT "${LOCAL_REDIS_PORT}")"
    if redis-cli -h "${redis_host}" -p "${redis_port}" ping 2>/dev/null | grep -q PONG; then
      echo "Redis ping (${redis_host}:${redis_port}): OK"
    else
      echo "Redis ping (${redis_host}:${redis_port}): failed"
    fi
  fi
}

_deps_manage_local() {
  _ensure_root
  local action="$1"
  _systemctl_unit "${action}" telorax-mariadb
  _systemctl_unit "${action}" telorax-redis
  echo "Local Telorax services ${action}ed."
}

_deps_manage_system() {
  _ensure_root
  local action="$1"
  local db_service redis_service
  db_service="$(_system_service_name mariadb)"
  redis_service="$(_system_service_name redis)"
  systemctl "${action}" "${db_service}.service"
  systemctl "${action}" "${redis_service}.service"
  echo "System services ${action}ed: ${db_service}, ${redis_service}"
}

deps_start() {
  if [[ "${DEPS_MODE}" == local ]]; then _deps_manage_local start; else _deps_manage_system start; fi
}
deps_stop() {
  if [[ "${DEPS_MODE}" == local ]]; then _deps_manage_local stop; else _deps_manage_system stop; fi
}
deps_restart() {
  if [[ "${DEPS_MODE}" == local ]]; then _deps_manage_local restart; else _deps_manage_system restart; fi
}

deps_provision() { _provision_database; }

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
      echo 'Env: DEPS_MODE=local|system (default: local)' >&2
      exit 1
      ;;
  esac
fi

#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

ENV_FILE="${ENV_FILE:-${REPO_ROOT}/.env.prod}"
COMPOSE_FILE_BASE="${COMPOSE_FILE_BASE:-${REPO_ROOT}/docker-compose.yml}"
COMPOSE_FILE_PROD="${COMPOSE_FILE_PROD:-${REPO_ROOT}/docker-compose.prod.yml}"
BACKUP_ROOT="${BACKUP_ROOT:-${REPO_ROOT}/backups/postgres/prod}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"

timestamp="$(date +%Y-%m-%d_%H-%M-%S)"
backup_file="${BACKUP_ROOT}/church_prod_db_${timestamp}.sql.gz"
tmp_file="${backup_file}.in_progress"

mkdir -p "${BACKUP_ROOT}"

cleanup_tmp() {
  if [[ -f "${tmp_file}" ]]; then
    rm -f "${tmp_file}"
  fi
}

trap cleanup_tmp ERR

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Arquivo de ambiente nao encontrado: ${ENV_FILE}" >&2
  exit 1
fi

echo "[backup] Iniciando backup em ${timestamp}"

docker compose \
  --env-file "${ENV_FILE}" \
  -f "${COMPOSE_FILE_BASE}" \
  -f "${COMPOSE_FILE_PROD}" \
  exec -T db sh -lc '
    set -e
    pg_dump \
      -U "$POSTGRES_USER" \
      -d "$POSTGRES_DB" \
      --clean \
      --if-exists \
      --no-owner \
      --no-privileges
  ' | gzip -9 > "${tmp_file}"

mv "${tmp_file}" "${backup_file}"
ln -sfn "$(basename "${backup_file}")" "${BACKUP_ROOT}/latest.sql.gz"

find "${BACKUP_ROOT}" -type f -name '*.sql.gz' -mtime +"${RETENTION_DAYS}" -delete

trap - ERR

echo "[backup] Backup concluido: ${backup_file}"

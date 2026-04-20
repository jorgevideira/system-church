#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

ENV_FILE="${ENV_FILE:-${REPO_ROOT}/.env.prod}"
COMPOSE_FILE_BASE="${COMPOSE_FILE_BASE:-${REPO_ROOT}/docker-compose.yml}"
COMPOSE_FILE_PROD="${COMPOSE_FILE_PROD:-${REPO_ROOT}/docker-compose.prod.yml}"
BACKUP_SCRIPT="${REPO_ROOT}/scripts/backup_prod_db.sh"

usage() {
  cat <<'EOF'
Uso:
  scripts/restore_prod_db.sh /caminho/para/backup.sql.gz [--yes]

Exemplo:
  scripts/restore_prod_db.sh backups/postgres/prod/church_prod_db_2026-04-19_00-00-00.sql.gz
EOF
}

if [[ $# -lt 1 || $# -gt 2 ]]; then
  usage
  exit 1
fi

BACKUP_FILE="$1"
AUTO_CONFIRM="${2:-}"

if [[ ! -f "${BACKUP_FILE}" ]]; then
  echo "Backup nao encontrado: ${BACKUP_FILE}" >&2
  exit 1
fi

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Arquivo de ambiente nao encontrado: ${ENV_FILE}" >&2
  exit 1
fi

if [[ "${AUTO_CONFIRM}" != "--yes" ]]; then
  echo "ATENCAO: esta operacao vai substituir o banco de producao pelo conteudo do backup:"
  echo "  ${BACKUP_FILE}"
  echo
  read -r -p "Digite RESTORE para continuar: " confirm
  if [[ "${confirm}" != "RESTORE" ]]; then
    echo "Restore cancelado."
    exit 1
  fi
fi

if [[ -x "${BACKUP_SCRIPT}" ]]; then
  echo "[restore] Gerando backup de seguranca antes do restore"
  "${BACKUP_SCRIPT}"
fi

echo "[restore] Parando servicos da aplicacao"
docker compose \
  --env-file "${ENV_FILE}" \
  -f "${COMPOSE_FILE_BASE}" \
  -f "${COMPOSE_FILE_PROD}" \
  stop nginx backend celery_worker celery_beat

echo "[restore] Encerrando conexoes ativas no banco"
docker compose \
  --env-file "${ENV_FILE}" \
  -f "${COMPOSE_FILE_BASE}" \
  -f "${COMPOSE_FILE_PROD}" \
  exec -T db sh -lc '
    set -e
    psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d postgres <<SQL
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '\'''"$POSTGRES_DB"'\'' AND pid <> pg_backend_pid();
SQL
  '

echo "[restore] Restaurando backup ${BACKUP_FILE}"
gunzip -c "${BACKUP_FILE}" | docker compose \
  --env-file "${ENV_FILE}" \
  -f "${COMPOSE_FILE_BASE}" \
  -f "${COMPOSE_FILE_PROD}" \
  exec -T db sh -lc '
    set -e
    psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"
  '

echo "[restore] Subindo servicos novamente"
docker compose \
  --env-file "${ENV_FILE}" \
  -f "${COMPOSE_FILE_BASE}" \
  -f "${COMPOSE_FILE_PROD}" \
  up -d nginx backend celery_worker celery_beat

echo "[restore] Restore concluido com sucesso."

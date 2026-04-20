#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

LOG_DIR="${REPO_ROOT}/backups/logs"
CRON_FILE_LOCK="/tmp/system-church-prod-db-backup.lock"
BACKUP_SCRIPT="${REPO_ROOT}/scripts/backup_prod_db.sh"
LOG_FILE="${LOG_DIR}/prod-db-backup.log"

mkdir -p "${LOG_DIR}"

CRON_LINE="0 0 * * * /usr/bin/flock -n ${CRON_FILE_LOCK} ${BACKUP_SCRIPT} >> ${LOG_FILE} 2>&1"

TMP_CRON="$(mktemp)"
crontab -l 2>/dev/null > "${TMP_CRON}" || true

if grep -Fqx "${CRON_LINE}" "${TMP_CRON}"; then
  echo "Cron ja instalado:"
  echo "${CRON_LINE}"
  rm -f "${TMP_CRON}"
  exit 0
fi

printf '%s\n' "${CRON_LINE}" >> "${TMP_CRON}"
crontab "${TMP_CRON}"
rm -f "${TMP_CRON}"

echo "Cron instalado com sucesso:"
echo "${CRON_LINE}"
echo
echo "Observacao: o horario segue o fuso horario do servidor."

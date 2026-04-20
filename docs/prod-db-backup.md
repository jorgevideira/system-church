# Backup diario do banco de producao

Este projeto roda o banco de producao em PostgreSQL via Docker Compose usando `.env.prod`.

Os scripts abaixo foram adicionados para automatizar backup e restore:

- `scripts/backup_prod_db.sh`
- `scripts/install_prod_backup_cron.sh`
- `scripts/restore_prod_db.sh`

## O que o backup faz

- executa `pg_dump` dentro do container `db`
- gera um arquivo compactado `.sql.gz`
- salva em `backups/postgres/prod/`
- cria/atualiza o atalho `backups/postgres/prod/latest.sql.gz`
- remove backups com mais de `30` dias por padrao

Formato de arquivo esperado:

```text
backups/postgres/prod/church_prod_db_YYYY-MM-DD_HH-MM-SS.sql.gz
```

## Instalar o cron da meia-noite

No servidor de producao, dentro da raiz do projeto:

```bash
chmod +x scripts/backup_prod_db.sh scripts/install_prod_backup_cron.sh scripts/restore_prod_db.sh
./scripts/install_prod_backup_cron.sh
```

O cron instalado fica assim:

```cron
0 0 * * * /usr/bin/flock -n /tmp/system-church-prod-db-backup.lock /opt/system-church/scripts/backup_prod_db.sh >> /opt/system-church/backups/logs/prod-db-backup.log 2>&1
```

Importante:

- esse horario segue o fuso do servidor
- se o servidor estiver em UTC e voce quiser meia-noite no horario de Brasilia, ajuste o timezone do host antes
- `flock` evita duas execucoes simultaneas do backup

## Rodar um backup manualmente

```bash
./scripts/backup_prod_db.sh
```

## Listar backups disponiveis

```bash
ls -lh backups/postgres/prod/
```

## Restaurar um backup de um dia especifico

Exemplo:

```bash
./scripts/restore_prod_db.sh backups/postgres/prod/church_prod_db_2026-04-19_00-00-00.sql.gz
```

O script de restore:

- pede confirmacao
- faz um backup de seguranca antes de restaurar
- para `nginx`, `backend`, `celery_worker` e `celery_beat`
- encerra conexoes ativas no banco
- aplica o dump com `psql`
- sobe os servicos novamente

## Restore sem prompt de confirmacao

```bash
./scripts/restore_prod_db.sh backups/postgres/prod/church_prod_db_2026-04-19_00-00-00.sql.gz --yes
```

## Procedimento recomendado em incidente

1. Identifique o horario do problema.
2. Escolha o backup imediatamente anterior ao incidente.
3. Execute o restore.
4. Valide login, dashboards e os fluxos principais.
5. Confira os logs da API e do worker apos a volta.

## Observacoes de seguranca

- Os backups ficam no proprio servidor. Para uma estrategia mais robusta, o ideal e tambem copiar esses arquivos para armazenamento externo.
- O restore substitui o estado atual do banco pelo conteudo do arquivo informado.
- Antes de qualquer restore, confirme se o backup escolhido e realmente o ponto desejado.

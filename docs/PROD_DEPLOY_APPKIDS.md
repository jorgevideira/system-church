# Deploy Producao (AppKids / Ministerio Infantil)

Este guia foca em colocar em producao as mudancas que adicionam o AppKids e demais schemas novos, sem perder dados.

## Premissas

- Producao usa Postgres via Docker Compose.
- As migrations sao controladas por Alembic (pasta `backend/alembic/versions/`).
- O deploy de producao roda com `.env.prod` (nao versionado).

## Passo a passo seguro

1. Atualize o codigo no servidor (branch `prod`) e suba os containers com build
   - `docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml up -d --build`

2. Faça backup do banco antes de migrar
   - `docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > backup_pre_migracao.sql`

3. Preflight (evita falha da migration 030)
   - A migration `030_child_checkin_email_unique_and_recovery` cria um indice unico em:
     - `(tenant_id, lower(email))` para `child_checkin_families`
   - Se existir email duplicado por tenant (case-insensitive), o upgrade falha.
   - Rode:
     - `docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml exec backend python backend/scripts/preflight_child_checkin_email_uniqueness.py`
   - Se der erro, corrija as duplicidades antes de continuar (ex.: ajustar email, ou deixar vazio em um dos registros).

4. Rode as migrations
   - `docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml exec backend bash ./run_migrations.sh`

5. Reinicie os servicos para carregar o novo schema
   - `docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml restart backend celery_worker celery_beat nginx`

6. Verificacoes rapidas
   - Health do backend responde.
   - Login normal continua funcionando.
   - AppKids abre e endpoints nao retornam 404 (ver item abaixo).

## Variaveis de ambiente (producao)

No `.env.prod`, garanta:

- `CHILD_CHECKIN_DEV_ENABLED=true`
  - Sem isso, os endpoints do AppKids retornam 404: "Child check-in module is disabled".

Para envio de carteirinha e recuperacao de senha, configure SMTP (global ou por tenant, conforme uso do sistema):

- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`

## Rollback (se necessario)

1. Derrube os containers do backend/celery/nginx e volte o codigo para o commit anterior.
2. Restaure o banco:
   - `psql` com o `backup_pre_migracao.sql`

Observacao: downgrade Alembic nem sempre e seguro em producao; backup e o caminho mais confiavel.


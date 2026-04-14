# Seed Dev Data (Organograma de Células)

Este projeto tem um script para popular o **ambiente de dev** com dados mocados:

- 20 células
- 20 líderes (1 líder por célula)
- 4 discipuladores (5 células por discipulador)
- 2 pastores de rede (2 discipuladores por pastor)
- membros (visitantes/assíduos/membros) aleatórios por célula
- reuniões + frequência (fevereiro, março e abril de 2026)

O script chama a **API** e respeita uma trava para não rodar em prod por engano.

## Rodar

```bash
python3 backend/scripts/seed_cells_orgchart_dev.py \
  --base-url https://dev.jpmit.top \
  --admin-email SEU_EMAIL_ADMIN \
  --admin-password SUA_SENHA_ADMIN
```

Por padrão, ele cria usuários com senha `SeedPass123!` (você pode alterar com `--user-password`).

### Dicas (mais rápido)

- Para garantir o **organograma** primeiro (sem criar reuniões/frequência):

```bash
python3 backend/scripts/seed_cells_orgchart_dev.py \
  --base-url https://dev.jpmit.top \
  --admin-email SEU_EMAIL_ADMIN \
  --admin-password SUA_SENHA_ADMIN \
  --skip-meetings
```

- Para preencher **reuniões + frequência** depois (sem criar mais pessoas):

```bash
python3 backend/scripts/seed_cells_orgchart_dev.py \
  --base-url https://dev.jpmit.top \
  --admin-email SEU_EMAIL_ADMIN \
  --admin-password SUA_SENHA_ADMIN \
  --skip-people
```

### Evitar senha na linha de comando

Você também pode setar as credenciais via env vars:

- `ADMIN_EMAIL`
- `ADMIN_PASSWORD`

## Observações

- O script **só roda** em URL que contenha `dev` ou que seja `localhost/127.0.0.1`.
- Para forçar fora disso, use `--allow-non-dev` (não recomendado).

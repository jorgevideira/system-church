# System Church

Plataforma de gestao financeira para igrejas com foco em controle operacional, organizacao de lancamentos e visao gerencial em dashboards.

O projeto combina backend robusto (FastAPI + SQLAlchemy + Celery) com frontend web leve (HTML/CSS/JS) e recursos praticos para rotina financeira: importacao de extratos, categorizacao com apoio de IA, anexos por lancamento e analytics de decisao.

## Destaques

- Autenticacao JWT com refresh token
- Modulo de lancamentos com filtros avancados, ordenacao e paginacao
- Cadastro e gestao de categorias e ministerios
- Importacao de extratos (CSV, OFX e PDF) com tratamento de duplicidades
- Anexos por lancamento (imagem/PDF) com compactacao e download
- Dashboard gerencial com:
	- Filtros por periodo, categoria, ministerio, tipo e banco
	- KPIs de entradas, saidas e saldo
	- Comparativos mensais (ultimos 6 meses)
	- Grafico de linha (saldo/entrada/saida)
	- Grafico de pizza (composicao de despesas por categoria)
	- Orcamento mensal por categoria/ministerio
	- Central de alertas operacionais e de meta
	- Drill-down para abrir lancamentos filtrados

## Stack Tecnologica

| Camada | Tecnologia |
|---|---|
| API | FastAPI |
| ORM | SQLAlchemy 2.x |
| Migracoes | Alembic |
| Background Jobs | Celery |
| Broker/Cache | Redis |
| Banco de Dados | PostgreSQL |
| IA/Classificacao | scikit-learn, pandas, numpy |
| Frontend | HTML + CSS + JavaScript (vanilla) |
| Infra | Docker + Docker Compose + Nginx |

## Arquitetura

Para detalhes tecnicos de arquitetura, consulte [ARCHITECTURE.md](ARCHITECTURE.md).

## Evolucao SaaS

O produto agora possui uma direcao clara de evolucao para se tornar uma plataforma multi-igrejas, web/mobile, com permissoes mais granulares, eventos com inscricoes publicas e pagamentos online.

Documentos de referencia:

- [Arquitetura alvo SaaS](docs/target-architecture.md)
- [Roadmap de evolucao](docs/saas-evolution-roadmap.md)

## Como Rodar (Docker)

### 1) Clonar repositorio

```bash
git clone https://github.com/jorgevideira/system-church.git
cd system-church
```

### 2) Preparar ambiente

Para desenvolvimento/teste:

```bash
cp .env.dev.example .env.dev
```

Para producao:

```bash
cp .env.prod.example .env.prod
```

Edite o arquivo de ambiente correspondente e ajuste segredos, URLs e senhas.

### 3) Subir servicos

```bash
docker compose --env-file .env.dev -f docker-compose.yml -f docker-compose.dev.yml up --build -d
```

### 4) Migrar banco (primeira execucao)

```bash
docker compose --env-file .env.dev -f docker-compose.yml -f docker-compose.dev.yml exec backend alembic upgrade head
```

## Ambientes Separados

O projeto agora pode rodar com dois ambientes independentes na mesma maquina:

- `dev`: ambiente de teste/homologacao ligado a branch `dev`
- `main`: ambiente de producao ligado a branch `main`

Cada ambiente usa:

- `COMPOSE_PROJECT_NAME` diferente
- banco PostgreSQL diferente
- Redis diferente
- volumes Docker diferentes
- portas HTTP/API diferentes

### Subir ambiente `dev`

```bash
cp .env.dev.example .env.dev
docker compose --env-file .env.dev -f docker-compose.yml -f docker-compose.dev.yml up --build -d
docker compose --env-file .env.dev -f docker-compose.yml -f docker-compose.dev.yml exec backend alembic upgrade head
```

Portas padrao de `dev`:

- Frontend: `http://localhost:8088`
- API: `http://localhost:8001`
- PostgreSQL: `localhost:5433`
- Redis: `localhost:6380`

### Subir ambiente `main` / producao

```bash
cp .env.prod.example .env.prod
docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml up --build -d
docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml exec backend alembic upgrade head
```

Porta padrao de producao:

- Frontend/Nginx: `http://localhost:8089`

Se voce usa um proxy reverso, conecte o Nginx de producao na rede externa `proxy_manager`.

### Parar cada ambiente

```bash
docker compose --env-file .env.dev -f docker-compose.yml -f docker-compose.dev.yml down
docker compose --env-file .env.prod -f docker-compose.yml -f docker-compose.prod.yml down
```

### Fluxo de branches recomendado

```bash
git checkout -b dev
git push -u origin dev
```

Fluxo sugerido:

- desenvolver e validar em `dev`
- promover para `main` somente depois dos testes

## Endpoints Locais

- `dev` Frontend (via Nginx): `http://localhost:8088`
- `dev` API: `http://localhost:8001`
- `dev` Swagger: `http://localhost:8001/docs`
- `dev` ReDoc: `http://localhost:8001/redoc`
- `prod` Frontend (via Nginx): `http://localhost:8089`

## Credenciais Iniciais

Por padrao no ambiente local, o sistema inicia com:

- Usuario: `admin@church.com`
- Senha: `admin123`

Recomendado trocar em ambientes nao locais.

## Desenvolvimento Local (Sem Docker)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# a partir da raiz do projeto: copiar .env.example para .env e ajustar variaveis

alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Em outro terminal:

```bash
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
```

## Estrutura de Pastas

```text
system-church/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── middleware/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── tasks/
│   │   └── utils/
│   ├── alembic/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── docker-compose.yml
├── nginx.conf
├── ARCHITECTURE.md
└── README.md
```

## Variaveis de Ambiente (Principais)

| Variavel | Uso |
|---|---|
| `DATABASE_URL` | Conexao do PostgreSQL |
| `SECRET_KEY` | Assinatura JWT |
| `ALGORITHM` | Algoritmo JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiracao access token |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Expiracao refresh token |
| `REDIS_URL` | Redis |
| `CELERY_BROKER_URL` | Broker do Celery |
| `CELERY_RESULT_BACKEND` | Backend de resultado do Celery |
| `UPLOAD_DIR` | Pasta de uploads |
| `ATTACHMENT_DIR` | Pasta de anexos de lancamentos |
| `MAX_FILE_SIZE` | Limite de upload |
| `BACKEND_CORS_ORIGINS` | CORS permitido |

## Roadmap Sugerido

- Dashboard executivo com exportacao PDF/Excel
- Metas anuais por ministerio
- Modo multi-igreja (multi-tenant)
- Testes automatizados de fluxo frontend

## Licenca

Distribuido sob licenca MIT. Veja [LICENSE](LICENSE).

# 🔧 Instruções para Corrigir o Erro de Login

## Problema Identificado

✅ **Root Cause Encontrado:**
- Novas colunas foram adicionadas ao modelo `Receivable`, mas o banco de dados não foi atualizado
- Erro: `loadReceivables`  retorna **500 (Internal Server Error)**
- Esta é a causa da mensagem: **"Sessao invalida: An unexpected error occurred"**

## Solução Aplicada

Foram feitas as seguintes mudanças:

### 1. ✅ Criada migração Alembic
- Arquivo: `backend/alembic/versions/001_initial_schema.py`
- Define todas as tabelas do banco de dados
- Inclui todas as colunas novas (revenue_profile, receipt_method, attachment_*, received_at)

### 2. ✅ Modificado backend/app/main.py
- Adicionada função `run_migrations()`
- Executa automaticamente `alembic upgrade head` ao iniciar o servidor
- Não vai quebrar se as migrações já foram aplicadas

### 3. ✅ Modificado backend/app/initial_setup.py
- Removida chamada duplicada `Base.metadata.create_all()`
- Deixamos apenas Alembic responsável pelas migrações

---

## ✨ Como Usar

### Passo 1: Reiniciar os Containers

```bash
# Parar os containers
docker-compose down

# Iniciar novamente (as migrações rodarão automaticamente)
docker-compose up -d
```

Ou, se estiver em uma aplicação rodando:
```bash
docker-compose restart backend
```

### Passo 2: Fazer Login

Use as credenciais padrão:
- **Email:** `admin@church.com`
- **Senha:** `admin123`

### Passo 3: Verificar Console (F12)

Abra o navegador e pressione **F12** para abrir DevTools:
- **Aba Console**: Você deve ver `Rendering dashboard...` sem erros
- **Aba Network**: Nenhuma requisição 500 ou 401

---

## 🔍 Se Ainda Tiver Problemas

### Verificar Logs do Backend
```bash
docker-compose logs backend
```

### Executar Migração Manualmente (se necessário)
```bash
docker-compose exec backend alembic upgrade head
```

### Resetar Banco de Dados Completamente
```bash
docker-compose down -v  # remove volumes
docker-compose up -d
```

---

## 📋 Resumo das Mudanças

| Arquivo | Mudança |
|---------|----------|
| `backend/alembic/versions/001_initial_schema.py` | ✅ Criado - Migração inicial |
| `backend/app/main.py` | ✅ Modificado - Adiciona run_migrations() |
| `backend/app/initial_setup.py` | ✅ Modificado - Remove create_all() |
| `frontend/app.js` | ✅ Modificado - Logs detalhados de erro |

---

## 🎯 Próximas Ações

1. **Reinicie os containers**
2. **Tente fazer login** (admin@church.com / admin123)
3. **Compartilhe conosco** se houver novos erros no console (F12)

---

**Status:** ✅ Pronto para deploy

#!/bin/bash
# Script para executar as migrações do banco de dados

cd "$(dirname "$0")" || exit 1

echo "🚀 Iniciando migração do banco de dados..."
echo ""

# Verifica se está em um container Docker
if [ -f "/.dockerenv" ]; then
    echo "✅ Executando dentro do container Docker"
    cd /app
    alembic upgrade head
else
    echo "❌ Erro: Este script deve ser executado dentro do container Docker"
    echo ""
    echo "Para executar as migrações, use:"
    echo "  docker compose exec backend bash ./run_migrations.sh"
    echo ""
    exit 1
fi

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migrações aplicadas com sucesso!"
else
    echo ""
    echo "❌ Erro ao aplicar migrações"
    exit 1
fi

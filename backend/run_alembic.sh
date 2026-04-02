#!/bin/bash

# Go to backend directory
cd /root/system-church/backend || exit 1

# Install requirements (skip updating pip to avoid hangs)
echo "Installing dependencies..."
python3 -m pip install -q -r requirements.txt --no-input

# Verify alembic is installed
echo "Verifying alembic installation..."
python3 -c "import alembic; print('Alembic installed successfully')"

# Run the migration with verbose output
echo ""
echo "========================================"
echo "Running migration: alembic upgrade head"
echo "========================================"

# Use /home/jorge/.local/bin/alembic directly
/home/jorge/.local/bin/alembic upgrade head 2>&1 || {
    echo "Migration failed! Trying with --sql to see what would be executed..."
    /home/jorge/.local/bin/alembic upgrade head --sql
    exit 1
}

echo ""
echo "========================================"
echo "Migration completed successfully!"
echo "========================================"

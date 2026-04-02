#!/bin/bash
cd /root/system-church/backend

echo "Installing dependencies..."
python3 -m pip install -q alembic sqlalchemy

echo "Running migration..."
python3 << 'EOFPYTHON'
import sys
sys.path.insert(0, ".")
from alembic.config import Config
from alembic import command

cfg = Config("alembic.ini")
print("Executing: alembic upgrade head")
command.upgrade(cfg, "head")
print("✓ Migration completed!")
EOFPYTHON

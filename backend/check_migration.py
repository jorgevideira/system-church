#!/usr/bin/env python3
"""Check current migration version"""
import sys
from alembic.config import Config
from alembic import command
from sqlalchemy import text, create_engine

# Get database URL
from app.core.config import settings

print("=" * 60)
print("CHECKING MIGRATION STATUS")
print("=" * 60)
print(f"\nDatabase URL: {settings.DATABASE_URL}")

# Check current migration version
try:
    cfg = Config("alembic.ini")
    cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
    
    # Check what version is currently applied
    print("\nCurrent migration version:")
    command.current(cfg)
    
    print("\nAvailable migration versions:")
    command.heads(cfg)
    
except Exception as e:
    print(f"Error checking migrations: {e}")
    
# Try to connect to database and check tables
print("\n" + "=" * 60)
print("Checking database tables...")
try:
    engine = create_engine(settings.DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name
        """))
        tables = result.fetchall()
        print(f"\nTotal tables: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
            
except Exception as e:
    print(f"Error querying database: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)

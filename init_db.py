#!/usr/bin/env python3
"""
Initialize the database with all tables using Alembic migrations.
Run this ONCE after setting up Postgres:
    python init_db.py
"""
import os
from alembic.config import Config
from alembic import command
from app.database import engine
from sqlalchemy import inspect

def init_db():
    print("🚀 Starting database initialization via Alembic...")
    
    # 1. Setup Alembic configuration
    # This assumes init_db.py is in the root, same as alembic.ini
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ini_path = os.path.join(base_dir, "alembic.ini")
    
    alembic_cfg = Config(ini_path)
    
    # 2. Run the migration to 'head'
    # This creates the tables AND the version record
    try:
        command.upgrade(alembic_cfg, "head")
        print("✅ Database schema migrated to latest version!")
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return
    
    # 3. Verify created tables
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\nCurrent tables in database ({len(tables)} total):")
    for table in sorted(tables):
        print(f"  - {table}")

if __name__ == "__main__":
    init_db()
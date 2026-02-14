#!/usr/bin/env python3
"""
Initialize the database with all tables.
Run this ONCE after setting up Postgres:
    python init_db.py
"""
from app.database import Base, engine
from app.models import User, Member, DiningRoom, TableEntity, Reservation, ReservationAttendee

def init_db():
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully!")
    
    # Print created tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\nCreated {len(tables)} tables:")
    for table in sorted(tables):
        print(f"  - {table}")

if __name__ == "__main__":
    init_db()

#!/usr/bin/env python3
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Import your models
from app.models.table_entity import TableEntity
from app.models.seat import Seat
from app.models.user import User

load_dotenv()

# Get the URL and verify it exists to satisfy Pylance
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    print("❌ ERROR: DATABASE_URL not found in environment or .env file.")
    sys.exit(1)

# Pylance now knows DATABASE_URL is definitely a 'str'
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def generate_seats():
    db = SessionLocal()
    try:
        # Get the first admin to act as creator
        admin = db.query(User).filter(User.role == "admin").first()
        admin_id = admin.id if admin else None

        tables = db.query(TableEntity).all()
        print(f"Found {len(tables)} tables. Checking for missing seats...")

        seats_created = 0
        for table in tables:
            # Check how many seats currently exist for this table
            existing_seats_count = db.query(Seat).filter(Seat.table_id == table.id).count()
            
            # Cast table.seat_count to int just in case it's stored as a string
            target_count = int(table.seat_count) if table.seat_count else 0
            seats_to_create = target_count - existing_seats_count
            
            if seats_to_create > 0:
                print(f"Table {table.table_number}: Adding {seats_to_create} seats...")
                for i in range(existing_seats_count + 1, target_count + 1):
                    new_seat = Seat(
                        table_id=table.id,
                        seat_number=i,
                        is_available=True,
                        is_accessible=False,
                        created_by_user_id=admin_id
                    )
                    db.add(new_seat)
                    seats_created += 1
        
        db.commit()
        print(f"\n✅ Success! Created {seats_created} new seat records.")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_seats()

  
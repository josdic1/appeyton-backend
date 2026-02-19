#!/usr/bin/env python3
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Import models
from app.models.table_entity import TableEntity
from app.models.seat import Seat
from app.models.user import User

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ ERROR: DATABASE_URL not found in environment.")
    sys.exit(1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def generate_seats():
    db = SessionLocal()
    try:
        # 1. Fallback for Audit Fields
        admin = db.query(User).filter(User.role == "admin").first()
        if not admin:
            print("⚠️ Warning: No admin user found. Audit fields may fail if required.")
            # If your schema allows nulls, this is fine. If not, we might need a system ID.
        
        admin_id = admin.id if admin else None

        tables = db.query(TableEntity).all()
        print(f"🔍 Found {len(tables)} tables. Syncing seat records...")

        total_created = 0
        positions = ["top", "right", "bottom", "left", "top-right", "bottom-right", "bottom-left", "top-left"]

        for table in tables:
            # 2. Identify the Gap
            existing_count = db.query(Seat).filter(Seat.table_id == table.id).count()
            target_count = int(table.seat_count) if table.seat_count else 0
            
            diff = target_count - existing_count
            
            if diff > 0:
                print(f"🪑 Table {table.table_number}: Adding {diff} missing seats...")
                for i in range(existing_count + 1, target_count + 1):
                    new_seat = Seat(
                        table_id=table.id,
                        seat_number=i,
                        # Use the same position logic as your admin_tables.py for consistency
                        position=positions[(i-1) % len(positions)],
                        is_available=True,
                        is_accessible=False,
                        created_by_user_id=admin_id,
                        updated_by_user_id=admin_id
                    )
                    db.add(new_seat)
                    total_created += 1
        
        # 3. Finalize
        if total_created > 0:
            db.commit()
            print(f"\n✅ Success! Created {total_created} new seat records.")
        else:
            print("\n✨ Everything looks good. No new seats needed.")

    except Exception as e:
        db.rollback()
        print(f"❌ Error during generation: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_seats()
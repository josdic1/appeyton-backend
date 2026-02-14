#!/usr/bin/env python3
"""
Seed the database with initial data.
Run after init_db.py:
    python seed_db.py
"""
from app.database import SessionLocal
from app.models.user import User
from app.models.dining_room import DiningRoom
from app.models.table_entity import TableEntity

def seed_db():
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        admin = db.query(User).filter(User.email == "josh@josh.com").first()
        if admin:
            print("⚠️  Admin user already exists. Skipping seed.")
            return
        
        print("Creating admin user...")
        admin = User(
            email="josh@josh.com",
            name="Josh Dickenz",
            phone="555-0100",
            role="admin",
            membership_status="active",
            guest_allowance=10,
        )
        admin.set_password("1111")  # CHANGE THIS IN PRODUCTION
        db.add(admin)
        db.flush()  # Get admin.id
        
        print("Creating sample dining rooms...")
        oak_room = DiningRoom(
            name="Oak Room",
            capacity=40,
            is_active=True,
            display_order=1,
            created_by_user_id=admin.id,
            updated_by_user_id=admin.id,
        )
        pine_room = DiningRoom(
            name="Pine Room",
            capacity=30,
            is_active=True,
            display_order=2,
            created_by_user_id=admin.id,
            updated_by_user_id=admin.id,
        )
        db.add_all([oak_room, pine_room])
        db.flush()
        
        print("Creating sample tables...")
        # Oak Room tables
        for i in range(1, 9):
            table = TableEntity(
                dining_room_id=oak_room.id,
                table_number=i,
                seat_count=4 if i <= 6 else 6,
                created_by_user_id=admin.id,
                updated_by_user_id=admin.id,
            )
            db.add(table)
        
        # Pine Room tables
        for i in range(1, 7):
            table = TableEntity(
                dining_room_id=pine_room.id,
                table_number=i,
                seat_count=4 if i <= 4 else 8,
                created_by_user_id=admin.id,
                updated_by_user_id=admin.id,
            )
            db.add(table)
        
        db.commit()
        print("✅ Database seeded successfully!")
        print("\n📝 Login credentials:")
        print("   Email: admin@sterling.local")
        print("   Password: admin123")
        print("\n⚠️  CHANGE THE ADMIN PASSWORD IMMEDIATELY!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()

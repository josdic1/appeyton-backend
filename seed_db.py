# seed_db.py
import sys
import bcrypt
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

from app.database import Base
from app.models.user import User
from app.models.member import Member
from app.models.dining_room import DiningRoom
from app.models.table_entity import TableEntity
from app.models.menu_item import MenuItem

load_dotenv()

# #3 — Production guard
# Prevents accidental wipe of production database
if os.getenv("ENVIRONMENT") == "production":
    print("❌ Refusing to seed a production database. Aborting.")
    sys.exit(1)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env file")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def drop_all_tables():
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("✅ All tables dropped")


def create_all_tables():
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created")


def seed_data():
    db = SessionLocal()
    
    try:
        print("\n🌱 Seeding database...")
        
        # ============================================================
        # USERS
        # ============================================================
        print("\nCreating users...")
        
        josh = User(
            email="josh@josh.com",
            name="Josh Dicker",
            phone="555-1212",
            password_hash=hash_password("1111"),
            role="admin",
            membership_status="active",
            guest_allowance=10
        )
        db.add(josh)
        db.flush()
        
        jill = User(
            email="jill@a.com",
            name="Jill Kaiser",
            phone="555-1234",
            password_hash=hash_password("1111"),
            role="admin",
            membership_status="active",
            guest_allowance=8
        )
        db.add(jill)
        db.flush()
        
        mark = User(
            email="mark@s.com",
            name="Mark Cranberry",
            phone="555-1234",
            password_hash=hash_password("1111"),
            role="staff",
            membership_status="active",
            guest_allowance=0
        )
        db.add(mark)
        db.flush()
        
        jenna = User(
            email="jenns@s.com",
            name="Jenna Wray",
            phone="555-1234",
            password_hash=hash_password("1111"),
            role="staff",
            membership_status="active",
            guest_allowance=0
        )
        db.add(jenna)
        db.flush()
        
        gabe = User(
            email="gabe@m.com",
            name="Gabe Scott",
            phone="555-1112",
            password_hash=hash_password("1111"),
            role="member",
            membership_status="active",
            guest_allowance=4
        )
        db.add(gabe)
        db.flush()
        
        sarah = User(
            email="sarah@m.com",
            name="Sarah Scott",
            phone="555-1111",
            password_hash=hash_password("1111"),
            role="member",
            membership_status="active",
            guest_allowance=6
        )
        db.add(sarah)
        db.flush()
        
        jaime = User(
            email="jaime@m.com",
            name="Jaime Aker",
            phone="555-1113",
            password_hash=hash_password("1111"),
            role="member",
            membership_status="active",
            guest_allowance=5
        )
        db.add(jaime)
        db.flush()
        
        print(f"✅ Created {db.query(User).count()} users")
        
        # ============================================================
        # MEMBERS (Family Members)
        # ============================================================
        print("\nCreating family members...")
        
        sarah_self = Member(
            user_id=sarah.id,
            created_by_user_id=sarah.id,
            name="Sarah Scott",
            relation="Self",
            dietary_restrictions={"preferences": ["no cilantro"], "notes": "Prefers white wine"}
        )
        db.add(sarah_self)
        
        reed = Member(
            user_id=sarah.id,
            created_by_user_id=sarah.id,
            name="Reed Edwards",
            relation="Spouse",
            dietary_restrictions={"allergies": ["shellfish"], "preferences": ["medium-rare steak"]}
        )
        db.add(reed)
        
        zoe = Member(
            user_id=sarah.id,
            created_by_user_id=sarah.id,
            name="Zoe Scott-Edwards",
            relation="Daughter",
            dietary_restrictions={"allergies": ["tree nuts"], "preferences": ["no vegetables"], "notes": "Picky eater"}
        )
        db.add(zoe)
        
        jaime_self = Member(
            user_id=jaime.id,
            created_by_user_id=jaime.id,
            name="Jaime Aker",
            relation="Self",
            dietary_restrictions={"preferences": ["vegetarian"], "notes": "Loves spicy food"}
        )
        db.add(jaime_self)
        
        nat = Member(
            user_id=jaime.id,
            created_by_user_id=jaime.id,
            name="Nat Aker",
            relation="Spouse",
            dietary_restrictions={"allergies": ["dairy", "gluten"], "preferences": ["vegan options preferred"]}
        )
        db.add(nat)
        
        nolan = Member(
            user_id=jaime.id,
            created_by_user_id=jaime.id,
            name="Nolan Aker",
            relation="Son",
            dietary_restrictions={"allergies": ["peanuts", "eggs"], "notes": "Severe peanut allergy - EpiPen required"}
        )
        db.add(nolan)
        
        gabe_self = Member(
            user_id=gabe.id,
            created_by_user_id=gabe.id,
            name="Gabe Scott",
            relation="Self",
            dietary_restrictions={"preferences": ["rare steak", "bourbon"], "notes": "Carnivore"}
        )
        db.add(gabe_self)
        
        palmer = Member(
            user_id=gabe.id,
            created_by_user_id=gabe.id,
            name="Palmer Scott",
            relation="Daughter",
            dietary_restrictions={"preferences": ["pasta", "chicken fingers"], "notes": "Age 8"}
        )
        db.add(palmer)
        
        miller = Member(
            user_id=gabe.id,
            created_by_user_id=gabe.id,
            name="Miller Scott",
            relation="Daughter",
            dietary_restrictions={"allergies": ["fish"], "preferences": ["pizza", "mac and cheese"], "notes": "Age 5"}
        )
        db.add(miller)
        
        print(f"✅ Created {db.query(Member).count()} family members")
        
        # ============================================================
        # DINING ROOMS
        # ============================================================
        print("\nCreating dining rooms...")
        
        main_hall = DiningRoom(
            name="Main Dining Hall",
            is_active=True,
            display_order=1,
            meta={"description": "Primary dining space with chandelier"},
            created_by_user_id=josh.id,
            updated_by_user_id=josh.id
        )
        db.add(main_hall)
        db.flush()
        
        private_room = DiningRoom(
            name="Private Room",
            is_active=True,
            display_order=2,
            meta={"description": "Intimate setting for special occasions"},
            created_by_user_id=josh.id,
            updated_by_user_id=josh.id
        )
        db.add(private_room)
        db.flush()
        
        terrace = DiningRoom(
            name="Terrace",
            is_active=True,
            display_order=3,
            meta={"description": "Outdoor seating with garden views", "seasonal": "Spring-Fall only"},
            created_by_user_id=josh.id,
            updated_by_user_id=josh.id
        )
        db.add(terrace)
        db.flush()
        
        print(f"✅ Created {db.query(DiningRoom).count()} dining rooms")
        
        # ============================================================
        # TABLES
        # ============================================================
        print("\nCreating tables...")
        
        tables_data = [
            (main_hall.id, 1, 4, 50, 50),
            (main_hall.id, 2, 4, 150, 50),
            (main_hall.id, 3, 6, 250, 50),
            (main_hall.id, 4, 6, 350, 50),
            (main_hall.id, 5, 8, 50, 150),
            (main_hall.id, 6, 8, 250, 150),
            (main_hall.id, 7, 2, 450, 50),
            (main_hall.id, 8, 2, 450, 100),
            (private_room.id, 1, 10, 100, 100),
            (private_room.id, 2, 6, 300, 100),
            (terrace.id, 1, 4, 50, 50),
            (terrace.id, 2, 4, 200, 50),
            (terrace.id, 3, 4, 350, 50),
            (terrace.id, 4, 2, 150, 150),
        ]
        
        for room_id, table_num, seats, pos_x, pos_y in tables_data:
            table = TableEntity(
                dining_room_id=room_id,
                table_number=table_num,
                seat_count=seats,
                position_x=pos_x,
                position_y=pos_y,
                created_by_user_id=josh.id,
                updated_by_user_id=josh.id
            )
            db.add(table)
        
        db.flush()
        print(f"✅ Created {db.query(TableEntity).count()} tables")
        
        # ============================================================
        # MENU ITEMS
        # ============================================================
        print("\nCreating menu items...")
        
        menu_items = [
            ("Oysters Rockefeller", "Fresh oysters with spinach and parmesan", "appetizer", 18.00, True, ["shellfish"], 1),
            ("Caesar Salad", "Romaine, parmesan, croutons, classic dressing", "appetizer", 14.00, True, [], 2),
            ("Burrata & Tomatoes", "Creamy burrata with heirloom tomatoes and basil", "appetizer", 16.00, True, ["vegetarian"], 3),
            ("Shrimp Cocktail", "Jumbo shrimp with cocktail sauce", "appetizer", 19.00, True, ["shellfish"], 4),
            ("French Onion Soup", "Caramelized onions, gruyere, sourdough", "appetizer", 12.00, True, [], 5),
            ("Ribeye Steak", "16oz USDA Prime, aged 28 days", "entree", 58.00, True, [], 1),
            ("Filet Mignon", "8oz center cut tenderloin", "entree", 52.00, True, [], 2),
            ("Grilled Salmon", "Atlantic salmon with lemon butter", "entree", 38.00, True, ["fish"], 3),
            ("Lobster Tail", "Maine lobster tail with drawn butter", "entree", 62.00, True, ["shellfish"], 4),
            ("Roasted Chicken", "Half chicken with herbs and roasted vegetables", "entree", 32.00, True, [], 5),
            ("Vegetarian Risotto", "Seasonal vegetables, parmesan, truffle oil", "entree", 28.00, True, ["vegetarian"], 6),
            ("Lamb Chops", "Grilled New Zealand lamb with mint jus", "entree", 48.00, True, [], 7),
            ("Truffle Fries", "Hand-cut fries with truffle oil and parmesan", "side", 12.00, True, [], 1),
            ("Creamed Spinach", "Classic steakhouse style", "side", 10.00, True, [], 2),
            ("Asparagus", "Grilled with lemon and olive oil", "side", 11.00, True, ["vegan"], 3),
            ("Mac & Cheese", "Five cheese blend", "side", 13.00, True, [], 4),
            ("Crème Brûlée", "Classic French custard with caramelized sugar", "dessert", 14.00, True, [], 1),
            ("Chocolate Lava Cake", "Warm chocolate cake with vanilla ice cream", "dessert", 15.00, True, [], 2),
            ("New York Cheesecake", "Classic cheesecake with berry compote", "dessert", 13.00, True, [], 3),
            ("Tiramisu", "House-made Italian classic", "dessert", 14.00, True, [], 4),
            ("Coffee", "Freshly brewed", "beverage", 4.00, True, [], 1),
            ("Espresso", "Double shot", "beverage", 5.00, True, [], 2),
            ("Iced Tea", "House-brewed sweet or unsweet", "beverage", 4.00, True, [], 3),
        ]
        
        for name, desc, category, price, available, tags, order in menu_items:
            item = MenuItem(
                name=name,
                description=desc,
                category=category,
                price=price,
                is_available=available,
                dietary_tags=tags if tags else None,
                display_order=order,
                created_by_user_id=josh.id,
                updated_by_user_id=josh.id
            )
            db.add(item)
        
        db.flush()
        print(f"✅ Created {db.query(MenuItem).count()} menu items")
        
        # ============================================================
        # COMMIT ALL
        # ============================================================
        db.commit()
        
        print("\n" + "="*60)
        print("✅ Database seeded successfully!")
        print("="*60)
        print("\n📊 Summary:")
        print(f"   Users: {db.query(User).count()}")
        print(f"   Family Members: {db.query(Member).count()}")
        print(f"   Dining Rooms: {db.query(DiningRoom).count()}")
        print(f"   Tables: {db.query(TableEntity).count()}")
        print(f"   Menu Items: {db.query(MenuItem).count()}")
        
        print("\n👤 Login Credentials:")
        print("   Admins:")
        print("     josh@josh.com / 1111")
        print("     jill@a.com / 1111")
        print("   Staff:")
        print("     mark@s.com / 1111")
        print("     jenns@s.com / 1111")
        print("   Members:")
        print("     gabe@m.com / 1111")
        print("     sarah@m.com / 1111")
        print("     jaime@m.com / 1111")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🗑️  WARNING: This will delete ALL existing data!")
    response = input("Are you sure you want to continue? (yes/no): ")
    
    if response.lower() == 'yes':
        drop_all_tables()
        create_all_tables()
        seed_data()
    else:
        print("❌ Aborted")
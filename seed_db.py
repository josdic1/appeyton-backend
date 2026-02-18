# seed_db.py
import sys
import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

from app.database import Base
from app.models.user import User
from app.models.member import Member
from app.models.dining_room import DiningRoom
from app.models.table_entity import TableEntity
from app.models.menu_item import MenuItem
from app.models.seat import Seat  # <--- CRITICAL IMPORT

load_dotenv()

# Production guard
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
        # 1. USERS
        # ============================================================
        print("\nCreating users...")
        
        josh = User(email="josh@josh.com", name="Josh Dicker", phone="555-1212", password_hash=hash_password("1111"), role="admin", membership_status="active", guest_allowance=10)
        jill = User(email="jill@a.com", name="Jill Kaiser", phone="555-1234", password_hash=hash_password("1111"), role="admin", membership_status="active", guest_allowance=8)
        mark = User(email="mark@s.com", name="Mark Cranberry", phone="555-1234", password_hash=hash_password("1111"), role="staff", membership_status="active", guest_allowance=0)
        jenna = User(email="jenns@s.com", name="Jenna Wray", phone="555-1234", password_hash=hash_password("1111"), role="staff", membership_status="active", guest_allowance=0)
        gabe = User(email="gabe@m.com", name="Gabe Scott", phone="555-1112", password_hash=hash_password("1111"), role="member", membership_status="active", guest_allowance=4)
        sarah = User(email="sarah@m.com", name="Sarah Scott", phone="555-1111", password_hash=hash_password("1111"), role="member", membership_status="active", guest_allowance=6)
        jaime = User(email="jaime@m.com", name="Jaime Aker", phone="555-1113", password_hash=hash_password("1111"), role="member", membership_status="active", guest_allowance=5)
        
        db.add_all([josh, jill, mark, jenna, gabe, sarah, jaime])
        db.flush() 
        print(f"✅ Created {db.query(User).count()} users")
        
        # ============================================================
        # 2. FAMILY MEMBERS
        # ============================================================
        print("\nCreating family members...")
        
        # Sarah's Family
        db.add(Member(user_id=sarah.id, created_by_user_id=sarah.id, name="Sarah Scott", relation="Self", dietary_restrictions={"preferences": ["no cilantro"], "notes": "Prefers white wine"}))
        db.add(Member(user_id=sarah.id, created_by_user_id=sarah.id, name="Reed Edwards", relation="Spouse", dietary_restrictions={"allergies": ["shellfish"], "preferences": ["medium-rare steak"]}))
        db.add(Member(user_id=sarah.id, created_by_user_id=sarah.id, name="Zoe Scott-Edwards", relation="Daughter", dietary_restrictions={"allergies": ["tree nuts"], "preferences": ["no vegetables"], "notes": "Picky eater"}))

        # Jaime's Family
        db.add(Member(user_id=jaime.id, created_by_user_id=jaime.id, name="Jaime Aker", relation="Self", dietary_restrictions={"preferences": ["vegetarian"], "notes": "Loves spicy food"}))
        db.add(Member(user_id=jaime.id, created_by_user_id=jaime.id, name="Nat Aker", relation="Spouse", dietary_restrictions={"allergies": ["dairy", "gluten"], "preferences": ["vegan options preferred"]}))
        db.add(Member(user_id=jaime.id, created_by_user_id=jaime.id, name="Nolan Aker", relation="Son", dietary_restrictions={"allergies": ["peanuts", "eggs"], "notes": "Severe peanut allergy - EpiPen required"}))

        # Gabe's Family
        db.add(Member(user_id=gabe.id, created_by_user_id=gabe.id, name="Gabe Scott", relation="Self", dietary_restrictions={"preferences": ["rare steak", "bourbon"], "notes": "Carnivore"}))
        db.add(Member(user_id=gabe.id, created_by_user_id=gabe.id, name="Palmer Scott", relation="Daughter", dietary_restrictions={"preferences": ["pasta", "chicken fingers"], "notes": "Age 8"}))
        db.add(Member(user_id=gabe.id, created_by_user_id=gabe.id, name="Miller Scott", relation="Daughter", dietary_restrictions={"allergies": ["fish"], "preferences": ["pizza", "mac and cheese"], "notes": "Age 5"}))
        
        print(f"✅ Created {db.query(Member).count()} family members")
        
        # ============================================================
        # 3. DINING ROOMS (ABEYTON FLOOR PLANS)
        # ============================================================
        print("\nCreating dining rooms...")
        
        pool = DiningRoom(name="Pool", is_active=True, display_order=1, created_by_user_id=josh.id)
        living_room = DiningRoom(name="Living Room", is_active=True, display_order=2, created_by_user_id=josh.id)
        croquet = DiningRoom(name="Croquet Court", is_active=True, display_order=3, created_by_user_id=josh.id)
        breakfast = DiningRoom(name="Breakfast Nook", is_active=True, display_order=4, created_by_user_id=josh.id)
        card_room = DiningRoom(name="Card Room", is_active=True, display_order=5, created_by_user_id=josh.id)

        db.add_all([pool, living_room, croquet, breakfast, card_room])
        db.flush()
        
        print(f"✅ Created {db.query(DiningRoom).count()} dining rooms")
        
        # ============================================================
        # 4. TABLES (ABEYTON CONFIGURATION)
        # ============================================================
        print("\nCreating tables...")
        
        # Format: (Room Object, Table Number, Seat Count, X, Y)
        tables_data = [
            # --- POOL (Cabanas & Lounge) ---
            (pool, 1, 6, 50, 50),   # Cabana 1
            (pool, 2, 6, 200, 50),  # Cabana 2
            (pool, 3, 4, 350, 50),  # Poolside Table
            (pool, 4, 4, 50, 200),  # Poolside Table

            # --- LIVING ROOM (Lounge Seating) ---
            (living_room, 1, 8, 150, 150), # Central Sofa Area
            (living_room, 2, 4, 50, 50),   # Corner Nook
            (living_room, 3, 4, 300, 50),  # Window Side

            # --- CROQUET COURT (Outdoor) ---
            (croquet, 1, 6, 100, 100), # Courtside Table 1
            (croquet, 2, 6, 250, 100), # Courtside Table 2

            # --- BREAKFAST NOOK ---
            (breakfast, 1, 6, 150, 150), # Main Round Table

            # --- CARD ROOM (Gaming Tables) ---
            (card_room, 1, 4, 100, 100), # Card Table 1
            (card_room, 2, 4, 250, 100), # Card Table 2
            (card_room, 3, 4, 100, 250), # Card Table 3
        ]
        
        for room_obj, table_num, seats, pos_x, pos_y in tables_data:
            table = TableEntity(
                dining_room_id=room_obj.id,
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
        # 5. GENERATE INDIVIDUAL SEATS
        # ============================================================
        print("\nGenerating individual seat records...")
        all_tables = db.query(TableEntity).all()
        seat_count = 0
        for t in all_tables:
            for i in range(1, t.seat_count + 1):
                 db.add(Seat(table_id=t.id, seat_number=i, is_available=True, created_by_user_id=josh.id))
                 seat_count += 1
        print(f"✅ Created {seat_count} seats")

        # ============================================================
        # 6. MENU ITEMS
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
            db.add(MenuItem(name=name, description=desc, category=category, price=price, is_available=available, dietary_tags=tags if tags else None, display_order=order, created_by_user_id=josh.id, updated_by_user_id=josh.id))
        
        print(f"✅ Created {len(menu_items)} menu items")
        
        # ============================================================
        # COMMIT ALL
        # ============================================================
        db.commit()
        
        print("\n" + "="*60)
        print("✅ Database seeded successfully!")
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
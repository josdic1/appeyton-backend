#!/usr/bin/env python3
"""
Add sample menu items to the database.
Run after init_db.py and seed_db.py:
    python seed_menu.py
"""
from decimal import Decimal
from app.database import SessionLocal
from app.models.user import User
from app.models.menu_item import MenuItem


def seed_menu():
    db = SessionLocal()

    try:
        # Get admin user
        admin = db.query(User).filter(User.role == "admin").first()
        if not admin:
            print("❌ No admin user found. Run seed_db.py first.")
            return

        # Check if menu items already exist
        existing = db.query(MenuItem).first()
        if existing:
            print("⚠️  Menu items already exist. Skipping seed.")
            return

        print("Creating sample menu items...")

        # Appetizers
        appetizers = [
            {"name": "Caesar Salad", "price": Decimal("12.00"), "description": "Romaine, parmesan, croutons, house Caesar dressing"},
            {"name": "Bruschetta", "price": Decimal("10.00"), "description": "Toasted bread, tomatoes, garlic, basil, olive oil"},
            {"name": "Shrimp Cocktail", "price": Decimal("16.00"), "description": "Chilled shrimp, cocktail sauce, lemon"},
        ]

        # Entrees
        entrees = [
            {"name": "Filet Mignon", "price": Decimal("42.00"), "description": "8oz beef tenderloin, mashed potatoes, asparagus"},
            {"name": "Grilled Salmon", "price": Decimal("32.00"), "description": "Atlantic salmon, wild rice, seasonal vegetables"},
            {"name": "Chicken Piccata", "price": Decimal("28.00"), "description": "Pan-seared chicken, lemon caper sauce, linguine"},
            {"name": "Vegetable Risotto", "price": Decimal("24.00"), "description": "Arborio rice, seasonal vegetables, parmesan", "dietary_tags": {"vegetarian": True}},
        ]

        # Desserts
        desserts = [
            {"name": "Chocolate Lava Cake", "price": Decimal("12.00"), "description": "Warm chocolate cake, vanilla ice cream"},
            {"name": "Crème Brûlée", "price": Decimal("10.00"), "description": "Vanilla custard, caramelized sugar"},
            {"name": "Tiramisu", "price": Decimal("11.00"), "description": "Coffee-soaked ladyfingers, mascarpone cream"},
        ]

        # Beverages
        beverages = [
            {"name": "House Red Wine", "price": Decimal("10.00"), "description": "Glass"},
            {"name": "House White Wine", "price": Decimal("10.00"), "description": "Glass"},
            {"name": "Sparkling Water", "price": Decimal("4.00"), "description": "Bottle"},
            {"name": "Coffee", "price": Decimal("3.00"), "description": "Freshly brewed"},
        ]

        # Add all items
        order = 0
        for item_data in appetizers:
            item = MenuItem(
                name=item_data["name"],
                description=item_data["description"],
                category="Appetizer",
                price=item_data["price"],
                dietary_tags=item_data.get("dietary_tags"),
                display_order=order,
                is_available=True,
                created_by_user_id=admin.id,
                updated_by_user_id=admin.id,
            )
            db.add(item)
            order += 1

        for item_data in entrees:
            item = MenuItem(
                name=item_data["name"],
                description=item_data["description"],
                category="Entree",
                price=item_data["price"],
                dietary_tags=item_data.get("dietary_tags"),
                display_order=order,
                is_available=True,
                created_by_user_id=admin.id,
                updated_by_user_id=admin.id,
            )
            db.add(item)
            order += 1

        for item_data in desserts:
            item = MenuItem(
                name=item_data["name"],
                description=item_data["description"],
                category="Dessert",
                price=item_data["price"],
                dietary_tags=item_data.get("dietary_tags"),
                display_order=order,
                is_available=True,
                created_by_user_id=admin.id,
                updated_by_user_id=admin.id,
            )
            db.add(item)
            order += 1

        for item_data in beverages:
            item = MenuItem(
                name=item_data["name"],
                description=item_data["description"],
                category="Beverage",
                price=item_data["price"],
                dietary_tags=item_data.get("dietary_tags"),
                display_order=order,
                is_available=True,
                created_by_user_id=admin.id,
                updated_by_user_id=admin.id,
            )
            db.add(item)
            order += 1

        db.commit()
        print("✅ Menu seeded successfully!")
        print(f"\nAdded:")
        print(f"  - {len(appetizers)} Appetizers")
        print(f"  - {len(entrees)} Entrees")
        print(f"  - {len(desserts)} Desserts")
        print(f"  - {len(beverages)} Beverages")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding menu: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_menu()
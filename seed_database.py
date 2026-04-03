"""
Comprehensive database seeding script with test data.
This script creates test users, categories, products with images, and inventory.

Usage:
    python seed_database.py
    
Environment Variables:
    SEED_DATA (optional): Set to 'true' to enable auto-seeding in Docker
"""

import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.security import pwd_context
from app.shared.enums import UserRole

# Import models
from app.modules.users.infrastructure.models.user import User
from app.modules.catalog.infrastructure.models.category import Category
from app.modules.catalog.infrastructure.models.product import Product
from app.modules.catalog.infrastructure.models.product_image import ProductImage
from app.modules.inventory.infrastructure.models.inventory import Inventory
from app.modules.addresses.infrastructure.models.shipping_address import ShippingAddress
from app.modules.cart.infrastructure.models.cart import Cart
from app.modules.orders.infrastructure.models.order import Order
from app.modules.reviews.infrastructure.models.review import Review


def hash_password(password: str) -> str:
    """Hash a password using the configured security settings."""
    return pwd_context.hash(password)


def reset_database(db: Session) -> None:
    """Optional: Reset database by clearing all tables (use with caution)."""
    print("🧹 Clearing database...")
    # Disable foreign key constraints for cleanup
    db.execute("PRAGMA foreign_keys=OFF")
    
    # Delete in reverse order of dependencies
    db.query(Review).delete()
    db.query(Order).delete()
    db.query(Cart).delete()
    db.query(ShippingAddress).delete()
    db.query(Inventory).delete()
    db.query(ProductImage).delete()
    db.query(Product).delete()
    db.query(Category).delete()
    db.query(User).delete()
    
    db.commit()
    print("✅ Database cleared\n")


def seed_users(db: Session) -> dict:
    """Seed test users with different roles."""
    print("👥 Seeding users...")
    
    # Check if users already exist
    if db.query(User).count() > 0:
        print("⚠️  Users already exist, skipping user seeding\n")
        return {}
    
    users = {
        "admin": User(
            email="meepsdev@gmail.com",
            password_hash=hash_password("AdminPass123!"),
            full_name="Admin User",
            role=UserRole.admin,
            is_active=True,
            created_at=datetime.utcnow(),
        ),
        "customer1": User(
            email="customer1@example.com",
            password_hash=hash_password("CustomerPass123!"),
            full_name="John Doe",
            role=UserRole.customer,
            is_active=True,
            created_at=datetime.utcnow(),
        ),
        "customer2": User(
            email="customer2@example.com",
            password_hash=hash_password("CustomerPass456!"),
            full_name="Jane Smith",
            role=UserRole.customer,
            is_active=True,
            created_at=datetime.utcnow(),
        ),
        "customer3": User(
            email="testing@example.com",
            password_hash=hash_password("TestPass789!"),
            full_name="Test User",
            role=UserRole.customer,
            is_active=True,
            created_at=datetime.utcnow(),
        ),
    }
    
    for user in users.values():
        db.add(user)
    
    db.commit()
    
    # Refresh to get IDs
    for user in users.values():
        db.refresh(user)
    
    print(f"✅ Created {len(users)} users")
    for key, user in users.items():
        print(f"   - {user.email} (ID: {user.id})")
    print()
    
    return users


def seed_categories(db: Session) -> dict:
    """Seed product categories."""
    print("📂 Seeding categories...")
    
    # Check if categories already exist
    if db.query(Category).count() > 0:
        print("⚠️  Categories already exist, loading existing categories\n")

        existing = {
            "electronics": db.query(Category).filter(Category.name == "Electronics").first(),
            "clothing": db.query(Category).filter(Category.name == "Clothing").first(),
            "home": db.query(Category).filter(Category.name == "Home & Garden").first(),
            "books": db.query(Category).filter(Category.name == "Books").first(),
            "sports": db.query(Category).filter(Category.name == "Sports & Outdoors").first(),
        }

        return {k: v for k, v in existing.items() if v is not None}
    
    categories = {
        "electronics": Category(
            name="Electronics",
            description="Electronic devices and gadgets",
        ),
        "clothing": Category(
            name="Clothing",
            description="Apparel and fashion items",
        ),
        "home": Category(
            name="Home & Garden",
            description="Home furnishings and garden supplies",
        ),
        "books": Category(
            name="Books",
            description="Physical and digital books",
        ),
        "sports": Category(
            name="Sports & Outdoors",
            description="Sports equipment and outdoor gear",
        ),
    }
    
    for category in categories.values():
        db.add(category)
    
    db.commit()
    
    # Refresh to get IDs
    for category in categories.values():
        db.refresh(category)
    
    print(f"✅ Created {len(categories)} categories")
    for key, cat in categories.items():
        print(f"   - {cat.name} (ID: {cat.id})")
    print()
    
    return categories


def seed_products(db: Session, categories: dict) -> dict:
    """Seed test products with detailed information."""
    print("📦 Seeding products...")
    
    # Check if products already exist
    if db.query(Product).count() > 0:
        print("⚠️  Products already exist, skipping\n")
        return {}
    
    products_data = [
        {
            "name": "iPhone 15 Pro",
            "description": "Latest Apple flagship smartphone with advanced camera system",
            "price": 999.99,
            "category_key": "electronics",
            "quantity": 15,
            "image_url": "https://via.placeholder.com/300?text=iPhone+15+Pro",
        },
        {
            "name": "MacBook Pro 16",
            "description": "Professional laptop with M3 Max chip",
            "price": 2499.99,
            "category_key": "electronics",
            "quantity": 8,
            "image_url": "https://via.placeholder.com/300?text=MacBook+Pro",
        },
        {
            "name": "Samsung Galaxy Watch 6",
            "description": "Advanced smartwatch with health tracking",
            "price": 399.99,
            "category_key": "electronics",
            "quantity": 20,
            "image_url": "https://via.placeholder.com/300?text=Galaxy+Watch",
        },
        {
            "name": "Nike Air Max 270",
            "description": "Comfortable athletic sneaker",
            "price": 120.00,
            "category_key": "clothing",
            "quantity": 50,
            "image_url": "https://via.placeholder.com/300?text=Nike+Air+Max",
        },
        {
            "name": "Adidas Running Shorts",
            "description": "Lightweight running shorts for performance",
            "price": 45.99,
            "category_key": "clothing",
            "quantity": 40,
            "image_url": "https://via.placeholder.com/300?text=Running+Shorts",
        },
        {
            "name": "IKEA desk lamp",
            "description": "Modern LED desk lamp with adjustable brightness",
            "price": 29.99,
            "category_key": "home",
            "quantity": 35,
            "image_url": "https://via.placeholder.com/300?text=Desk+Lamp",
        },
        {
            "name": "The Clean Coder",
            "description": "A Code of Conduct for Professional Programmers by Robert C. Martin",
            "price": 34.99,
            "category_key": "books",
            "quantity": 12,
            "image_url": "https://via.placeholder.com/300?text=Clean+Coder",
        },
        {
            "name": "Yoga Mat Premium",
            "description": "Non-slip, eco-friendly yoga mat",
            "price": 79.99,
            "category_key": "sports",
            "quantity": 25,
            "image_url": "https://via.placeholder.com/300?text=Yoga+Mat",
        },
        {
            "name": "Dumbbells Set (20kg)",
            "description": "Adjustable dumbbells perfect for home workouts",
            "price": 149.99,
            "category_key": "sports",
            "quantity": 10,
            "image_url": "https://via.placeholder.com/300?text=Dumbbells",
        },
        {
            "name": "Camping Tent 4-Person",
            "description": "Waterproof camping tent with easy setup",
            "price": 199.99,
            "category_key": "sports",
            "quantity": 8,
            "image_url": "https://via.placeholder.com/300?text=Camping+Tent",
        },
    ]
    
    products = {}
    for idx, product_data in enumerate(products_data):
        category = categories.get(product_data["category_key"])
        if not category:
            print(f"⚠️  Category '{product_data['category_key']}' not found, skipping product")
            continue
        
        product = Product(
            name=product_data["name"],
            description=product_data["description"],
            price=product_data["price"],
            category_id=category.id,
            is_active=True,
            created_at=datetime.utcnow(),
        )
        
        db.add(product)
        db.flush()  # Get the product ID
        
        # Add product image
        if product_data.get("image_url"):
            image = ProductImage(
                product_id=product.id,
                image_url=product_data["image_url"],
            )
            db.add(image)
        
        # Add inventory
        inventory = Inventory(
            product_id=product.id,
            quantity=product_data["quantity"],
        )
        db.add(inventory)
        
        products[idx] = product
    
    db.commit()
    
    # Refresh to get IDs
    for product in products.values():
        db.refresh(product)
    
    print(f"✅ Created {len(products)} products with images and inventory")
    for idx, product in products.items():
        print(f"   - {product.name} (${product.price}) - Qty: {product.inventory.quantity if product.inventory else 0}")
    print()
    
    return products


def seed_user_addresses(db: Session, users: dict) -> None:
    """Seed sample shipping addresses for users."""
    print("📍 Seeding shipping addresses...")
    
    # Check if addresses already exist
    if db.query(ShippingAddress).count() > 0:
        print("⚠️  Addresses already exist, skipping\n")
        return
    
    customer1 = users.get("customer1")
    if not customer1:
        print("⚠️  Customer1 not found, skipping addresses\n")
        return
    
    addresses = [
        ShippingAddress(
            user_id=customer1.id,
            street_address="123 Main St",
            city="New York",
            state="NY",
            postal_code="10001",
            country="USA",
            is_default=True,
        ),
        ShippingAddress(
            user_id=customer1.id,
            street_address="456 Oak Ave",
            city="Los Angeles",
            state="CA",
            postal_code="90001",
            country="USA",
            is_default=False,
        ),
    ]
    
    for address in addresses:
        db.add(address)
    
    db.commit()
    print(f"✅ Created {len(addresses)} shipping addresses\n")


def seed_sample_cart(db: Session, users: dict, products: dict) -> None:
    """Seed a sample cart for testing."""
    print("🛒 Seeding sample shopping cart...")
    
    # Check if carts already exist
    if db.query(Cart).count() > 0:
        print("⚠️  Carts already exist, skipping\n")
        return
    
    customer2 = users.get("customer2")
    if not customer2 or not products:
        print("⚠️  Customer or products not found, skipping cart\n")
        return
    
    cart = Cart(user_id=customer2.id)
    db.add(cart)
    db.flush()
    
    # Add items to cart
    product_list = list(products.values())[:3]  # First 3 products
    for product in product_list:
        from app.modules.cart.infrastructure.models.cart_item import CartItem
        
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=2,
        )
        db.add(cart_item)
    
    db.commit()
    print(f"✅ Created sample cart with {len(product_list)} items\n")


def main():
    """Run all seeding operations."""
    db = SessionLocal()
    
    try:
        print("\n" + "="*60)
        print("🚀 E-Commerce Database Seeding Script")
        print("="*60 + "\n")
        
        # Uncomment below to reset database before seeding (use with caution!)
        # reset_database(db)
        
        # Seed data in order
        users = seed_users(db)
        categories = seed_categories(db)
        products = seed_products(db, categories)
        
        if users and products:
            seed_user_addresses(db, users)
            seed_sample_cart(db, users, products)
        
        print("="*60)
        print("✅ Database seeding completed successfully!")
        print("="*60)
        print("\n📌 Test Credentials:")
        print(f"   Admin User: meepsdev@gmail.com / AdminPass123!")
        print(f"   Customer 1: customer1@example.com / CustomerPass123!")
        print(f"   Customer 2: customer2@example.com / CustomerPass456!")
        print(f"   Test User:  testing@example.com / TestPass789!")
        print("\n🔗 Access your application:")
        print("   API Docs: http://localhost:8000/docs")
        print("   ReDoc: http://localhost:8000/redoc")
        print("   Flower Dashboard: http://localhost:5555")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return 1
        
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())

"""
Database seeding script for creating initial users and categories
"""
from sqlalchemy.orm import Session
from database import SessionLocal, init_db
from models import User, Category, UserRole
from auth import get_password_hash
import uuid


def create_initial_users(db: Session):
    """Create initial admin and test users"""
    
    # Check if users already exist
    existing_users = db.query(User).count()
    if existing_users > 0:
        print(f"✓ Database already has {existing_users} users. Skipping user creation.")
        return
    
    users_to_create = [
        {
            "username": "officer",
            "email": "officer@civicfix.local",
            "password": "officer123",  # Change in production!
            "role": UserRole.MUNICIPAL_OFFICER,
            "first_name": "Municipal",
            "last_name": "Officer",
            "phone_number": "+1234567890"
        },
        {
            "username": "citizen",
            "email": "citizen@civicfix.local",
            "password": "citizen123",  # Change in production!
            "role": UserRole.CITIZEN,
            "first_name": "Test",
            "last_name": "Citizen",
            "phone_number": "+1234567891"
        }
    ]
    
    for user_data in users_to_create:
        password = user_data.pop("password")
        user = User(
            id=uuid.uuid4(),
            password_hash=get_password_hash(password),
            **user_data
        )
        db.add(user)
        print(f"✓ Created user: {user.username} ({user.email}) - Role: {user.role.value}")
    
    db.commit()
    print("\n✅ Initial users created successfully!")
    print("\n🔑 Login Credentials:")
    print("   Officer: username=officer / password=officer123")
    print("   Citizen: username=citizen / password=citizen123")
    print("\n⚠️  IMPORTANT: Change these passwords in production!")



def create_categories(db: Session):
    """Create default issue categories"""
    
    # Check if categories already exist
    existing_categories = db.query(Category).count()
    if existing_categories > 0:
        print(f"\n✓ Database already has {existing_categories} categories. Skipping category creation.")
        return
    
    categories_to_create = [
        {
            "name": "Potholes",
            "description": "Road potholes and surface damage",
            "icon_name": "pothole",
            "color_hex": "#E53E3E"
        },
        {
            "name": "Street Lights",
            "description": "Non-functional or damaged street lights",
            "icon_name": "lightbulb",
            "color_hex": "#F6E05E"
        },
        {
            "name": "Garbage",
            "description": "Garbage collection and littering issues",
            "icon_name": "trash",
            "color_hex": "#48BB78"
        },
        {
            "name": "Water Supply",
            "description": "Water leaks and supply issues",
            "icon_name": "water",
            "color_hex": "#4299E1"
        },
        {
            "name": "Drainage",
            "description": "Blocked drains and sewage issues",
            "icon_name": "drain",
            "color_hex": "#9F7AEA"
        },
        {
            "name": "Public Property",
            "description": "Damaged public property and infrastructure",
            "icon_name": "building",
            "color_hex": "#ED8936"
        },
        {
            "name": "Traffic",
            "description": "Traffic signals and road signage issues",
            "icon_name": "traffic",
            "color_hex": "#FC8181"
        },
        {
            "name": "Parks",
            "description": "Park maintenance and landscaping",
            "icon_name": "tree",
            "color_hex": "#68D391"
        },
        {
            "name": "Other",
            "description": "Other civic issues",
            "icon_name": "dots",
            "color_hex": "#A0AEC0"
        }
    ]
    
    for category_data in categories_to_create:
        category = Category(
            id=uuid.uuid4(),
            **category_data
        )
        db.add(category)
        print(f"✓ Created category: {category.name}")
    
    db.commit()
    print("\n✅ Categories created successfully!")


def seed_database():
    """Main function to seed the database"""
    print("🌱 Starting database seeding...\n")
    
    # Initialize database tables
    print("📋 Initializing database tables...")
    init_db()
    print("✓ Tables initialized\n")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create initial users
        print("👥 Creating initial users...")
        create_initial_users(db)
        
        # Create categories
        print("\n📂 Creating categories...")
        create_categories(db)
        
        print("\n✅ Database seeding completed successfully!")
        print("\n🚀 You can now start the application and login with the test credentials.")
        
    except Exception as e:
        print(f"\n❌ Error during database seeding: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

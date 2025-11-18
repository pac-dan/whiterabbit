"""Create an admin user for the application"""
import os
import sys
from dotenv import load_dotenv
from getpass import getpass

# Load environment variables
load_dotenv()

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models.user import User

def create_admin_user():
    """Create an admin user interactively"""
    app = create_app()
    
    with app.app_context():
        print("=" * 70)
        print("CREATE ADMIN USER")
        print("=" * 70)
        
        # Get user input
        print("\nEnter admin user details:\n")
        
        email = input("Email: ").strip()
        if not email:
            print("[ERROR] Email is required!")
            return
        
        name = input("Full Name: ").strip()
        if not name:
            print("[ERROR] Name is required!")
            return
        
        phone = input("Phone (optional): ").strip()
        
        password = getpass("Password: ")
        if not password:
            print("[ERROR] Password is required!")
            return
        
        confirm_password = getpass("Confirm Password: ")
        
        if password != confirm_password:
            print("[ERROR] Passwords don't match!")
            return
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            print(f"\n[ERROR] User with email '{email}' already exists!")
            make_admin = input("Make this user an admin? (y/n): ").strip().lower()
            if make_admin == 'y':
                existing_user.is_admin = True
                db.session.commit()
                print(f"\n[SUCCESS] '{name}' is now an admin!")
            return
        
        # Create admin user
        admin = User(
            email=email,
            name=name,
            phone=phone if phone else None,
            is_admin=True,
            is_active=True
        )
        admin.set_password(password)
        
        db.session.add(admin)
        db.session.commit()
        
        print("\n" + "=" * 70)
        print("[SUCCESS] Admin user created successfully!")
        print("=" * 70)
        print(f"\nAdmin Details:")
        print(f"  Email: {admin.email}")
        print(f"  Name: {admin.name}")
        print(f"  Phone: {admin.phone if admin.phone else 'N/A'}")
        print(f"  Admin: Yes")
        print(f"  Active: Yes")
        print("\n" + "=" * 70)
        print("You can now login at: http://localhost:5000/auth/login")
        print("=" * 70)

if __name__ == '__main__':
    create_admin_user()


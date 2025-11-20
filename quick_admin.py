"""Quick script to create/recreate admin user"""
from app import create_app, db
from app.models.user import User

def create_admin():
    app = create_app()
    
    with app.app_context():
        # Check if admin already exists
        existing_admin = User.query.filter_by(email='admin@momentumclips.com').first()
        
        if existing_admin:
            print("Admin user already exists!")
            print(f"Email: {existing_admin.email}")
            print("If you forgot the password, delete the user from database first.")
            return
        
        # Create new admin user
        admin = User(
            email='admin@momentumclips.com',
            name='Admin User',
            is_admin=True
        )
        admin.set_password('Admin123!')
        
        db.session.add(admin)
        db.session.commit()
        
        print("=" * 70)
        print("[SUCCESS] Admin user created!")
        print("=" * 70)
        print(f"\nLogin Credentials:")
        print(f"  Email: admin@momentumclips.com")
        print(f"  Password: Admin123!")
        print("\nLogin URL: http://127.0.0.1:5000/login")
        print("=" * 70)

if __name__ == '__main__':
    create_admin()


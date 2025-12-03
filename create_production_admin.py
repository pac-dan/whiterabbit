"""Create admin user for production deployment"""
from app import create_app, db
from app.models.user import User
import os

def create_admin():
    app = create_app()
    
    with app.app_context():
        # Admin credentials - set via environment or defaults
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@momentumclips.com')
        admin_name = os.getenv('ADMIN_NAME', 'Admin User')
        admin_password = os.getenv('ADMIN_PASSWORD', 'ChangeMe123!')
        
        print("=" * 70)
        print("CREATING ADMIN USER")
        print("=" * 70)
        
        # Check if admin already exists
        existing_admin = User.query.filter_by(email=admin_email).first()
        
        if existing_admin:
            print(f"\n❌ User with email '{admin_email}' already exists!")
            print(f"   Name: {existing_admin.name}")
            print(f"   Is Admin: {existing_admin.is_admin}")
            
            if not existing_admin.is_admin:
                # Promote to admin
                existing_admin.is_admin = True
                db.session.commit()
                print(f"\n✅ User promoted to admin!")
            return
        
        # Create new admin user
        admin = User(
            email=admin_email,
            name=admin_name,
            is_admin=True
        )
        admin.set_password(admin_password)
        
        db.session.add(admin)
        db.session.commit()
        
        print("\n" + "=" * 70)
        print("✅ [SUCCESS] Admin user created!")
        print("=" * 70)
        print(f"\nLogin at: https://www.momentumclips.com/login")
        print(f"Email: {admin_email}")
        print(f"Password: {admin_password}")
        print("\n⚠️  SECURITY: Change password immediately after first login!")
        print("=" * 70)
        
        # Print all users for verification
        all_users = User.query.all()
        print(f"\nTotal users in database: {len(all_users)}")
        for user in all_users:
            print(f"  - {user.email} (Admin: {user.is_admin})")
        print("=" * 70)

if __name__ == '__main__':
    try:
        create_admin()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()


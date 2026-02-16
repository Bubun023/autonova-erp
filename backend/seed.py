"""
Seed script to populate initial data for AutoNova ERP
"""
from app import create_app
from models import db, Role, User


def seed_database():
    """Seed the database with initial roles and admin user"""
    app = create_app()
    
    with app.app_context():
        print("Starting database seeding...")
        
        # Create roles
        roles_data = [
            {'name': 'admin', 'description': 'System administrator with full access'},
            {'name': 'manager', 'description': 'Manager with elevated permissions'},
            {'name': 'receptionist', 'description': 'Front desk staff for customer management'},
            {'name': 'technician', 'description': 'Technical staff for service operations'},
            {'name': 'accountant', 'description': 'Financial and accounting staff'}
        ]
        
        print("\nCreating roles...")
        for role_data in roles_data:
            existing_role = Role.query.filter_by(name=role_data['name']).first()
            if not existing_role:
                role = Role(**role_data)
                db.session.add(role)
                print(f"  ✓ Created role: {role_data['name']}")
            else:
                print(f"  - Role already exists: {role_data['name']}")
        
        db.session.commit()
        
        # Create default admin user
        print("\nCreating default admin user...")
        admin_role = Role.query.filter_by(name='admin').first()
        
        existing_admin = User.query.filter_by(username='admin').first()
        if not existing_admin:
            admin_user = User(
                username='admin',
                email='admin@autonova.com',
                first_name='Admin',
                last_name='User',
                role_id=admin_role.id
            )
            admin_user.set_password('admin123')
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("  ✓ Created admin user:")
            print("    Username: admin")
            print("    Password: admin123")
            print("    Email: admin@autonova.com")
        else:
            print("  - Admin user already exists")
        
        print("\n✅ Database seeding completed successfully!")
        print("\nYou can now login with:")
        print("  Username: admin")
        print("  Password: admin123")


if __name__ == '__main__':
    seed_database()

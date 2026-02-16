"""
Seed script to populate initial data
"""
from app import create_app
from models import db, Role, User

def seed_database():
    """Seed the database with initial data"""
    app = create_app()
    
    with app.app_context():
        print("Starting database seeding...")
        
        # Create roles
        roles_data = [
            {'name': 'admin', 'description': 'System administrator with full access'},
            {'name': 'manager', 'description': 'Manager with most permissions'},
            {'name': 'receptionist', 'description': 'Front desk staff handling customers'},
            {'name': 'technician', 'description': 'Technician performing vehicle services'},
            {'name': 'accountant', 'description': 'Financial staff handling accounting'}
        ]
        
        for role_data in roles_data:
            # Check if role already exists
            existing_role = Role.query.filter_by(name=role_data['name']).first()
            if not existing_role:
                role = Role(**role_data)
                db.session.add(role)
                print(f"Created role: {role_data['name']}")
            else:
                print(f"Role already exists: {role_data['name']}")
        
        db.session.commit()
        
        # Create default admin user
        admin_username = 'admin'
        existing_admin = User.query.filter_by(username=admin_username).first()
        
        if not existing_admin:
            admin_role = Role.query.filter_by(name='admin').first()
            
            admin_user = User(
                username='admin',
                email='admin@autonova.com',
                first_name='System',
                last_name='Administrator',
                role_id=admin_role.id
            )
            admin_user.set_password('admin123')
            
            db.session.add(admin_user)
            db.session.commit()
            
            print(f"\nDefault admin user created:")
            print(f"  Username: admin")
            print(f"  Password: admin123")
            print(f"  Email: admin@autonova.com")
        else:
            print(f"\nAdmin user already exists: {admin_username}")
        
        print("\nDatabase seeding completed successfully!")


if __name__ == '__main__':
    seed_database()

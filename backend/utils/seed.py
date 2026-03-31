"""
Terra Pravah - Database Seeding
================================
Seed sample data for development and testing.
"""

from datetime import datetime
from backend.models.models import db, User, Project, Team


def seed_database():
    """
    Seed the database with sample data.
    
    This function creates:
    - Sample admin users
    - Sample teams
    - Sample projects
    """
    
    # Create sample users if they don't exist
    admin = User.query.filter_by(email='admin@terrapravah.com').first()
    if not admin:
        admin = User(
            email='admin@terrapravah.com',
            first_name='Admin',
            last_name='User',
            subscription_plan='enterprise',
            email_verified=True
        )
        admin.set_password('AdminPassword123')
        db.session.add(admin)
        db.session.commit()
        print("✓ Created admin user")
    
    # Create sample user
    user = User.query.filter_by(email='user@terrapravah.com').first()
    if not user:
        user = User(
            email='user@terrapravah.com',
            first_name='Sample',
            last_name='User',
            subscription_plan='free',
            email_verified=True
        )
        user.set_password('UserPassword123')
        db.session.add(user)
        db.session.commit()
        print("✓ Created sample user")
    
    # Create sample team
    team = Team.query.filter_by(name='Demo Team').first()
    if not team:
        team = Team(
            name='Demo Team',
            slug='demo-team',
            description='Sample team for demonstration',
            owner_id=admin.id if admin else user.id
        )
        db.session.add(team)
        db.session.commit()
        print("✓ Created demo team")
    
    print("✅ Database seeding complete!")

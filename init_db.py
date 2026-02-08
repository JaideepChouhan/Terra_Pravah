"""Initialize the database."""
from backend.app import create_app
from backend.models.models import db

app = create_app()
with app.app_context():
    db.create_all()
    print("Database tables created successfully!")

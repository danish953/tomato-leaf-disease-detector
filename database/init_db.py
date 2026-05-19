from app import create_app
from database.extensions import db


app = create_app()

with app.app_context():
    db.create_all()
    print("Database initialized successfully.")

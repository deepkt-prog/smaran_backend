from app.database import SessionLocal
from app import models

db = SessionLocal()
users = db.query(models.User).all()

print(f"Total users: {len(users)}")
for u in users:
    print(f"ID: {u.id}, Email: {u.email}, Name: '{u.full_name}'")

db.close()

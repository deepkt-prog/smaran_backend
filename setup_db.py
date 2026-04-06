from sqlalchemy import create_engine
import os

# Import your Base and models
from app.database import Base, SQLALCHEMY_DATABASE_URL
import app.models

if __name__ == "__main__":
    current_db = os.environ.get("DATABASE_URL", "sqlite:///./smaran.db")
    print(f"Initializing database at: {current_db}")
    
    # Ensure Postgres connection works properly
    if current_db.startswith("postgres://"):
        current_db = current_db.replace("postgres://", "postgresql://", 1)
        
    engine = create_engine(current_db)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

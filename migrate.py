from sqlalchemy import create_engine, text
from app.database import SQLALCHEMY_DATABASE_URL

def migrate():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    with engine.connect() as conn:
        print("Starting Migration...")
        
        # 1. Create tables if not exist (SQLite doesn't support IF NOT EXISTS in CREATE TABLE easily via SQLAlchemy's create_all combined with existing tables without metadata reflection, but we can try manual SQL for new tables or just use raw SQL).
        # Actually easiest way is to try running CREATE TABLE and ignoring "already exists" errors.
        
        # Create families table
        try:
            conn.execute(text("""
            CREATE TABLE families (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR,
                invite_code VARCHAR,
                created_at DATETIME DEFAULT (CURRENT_TIMESTAMP)
            );
            """))
            conn.execute(text("CREATE UNIQUE INDEX ix_families_invite_code ON families (invite_code);"))
            conn.execute(text("CREATE INDEX ix_families_id ON families (id);"))
            print("Created families table.")
        except Exception as e:
            print(f"Skipping families creation (likely exists): {e}")

        # Create event_memories table
        try:
            conn.execute(text("""
            CREATE TABLE event_memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER,
                media_type VARCHAR,
                media_url VARCHAR,
                caption VARCHAR,
                created_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
                FOREIGN KEY(event_id) REFERENCES events(id)
            );
            """))
            conn.execute(text("CREATE INDEX ix_event_memories_id ON event_memories (id);"))
            print("Created event_memories table.")
        except Exception as e:
            print(f"Skipping event_memories creation: {e}")

        # 2. Alter existing tables (Add columns)
        
        # Add family_id to users
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN family_id INTEGER REFERENCES families(id);"))
            print("Added family_id to users.")
        except Exception as e:
            print(f"Skipping adding family_id to users: {e}")

        # Add suggested_action to events
        try:
            conn.execute(text("ALTER TABLE events ADD COLUMN suggested_action VARCHAR;"))
            print("Added suggested_action to events.")
        except Exception as e:
            print(f"Skipping adding suggested_action to events: {e}")

        print("Migration Completed.")

if __name__ == "__main__":
    migrate()

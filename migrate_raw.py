import sqlite3

def migrate():
    conn = sqlite3.connect("./smaran.db")
    cursor = conn.cursor()
    print("Starting Migration (sqlite3)...")
    
    # Families
    try:
        cursor.execute("""
        CREATE TABLE families (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR,
            invite_code VARCHAR,
            created_at DATETIME DEFAULT (CURRENT_TIMESTAMP)
        );
        """)
        cursor.execute("CREATE UNIQUE INDEX ix_families_invite_code ON families (invite_code);")
        cursor.execute("CREATE INDEX ix_families_id ON families (id);")
        print("Created families table.")
    except Exception as e:
        print(f"Skipping families: {e}")

    # Memories
    try:
        cursor.execute("""
        CREATE TABLE event_memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            media_type VARCHAR,
            media_url VARCHAR,
            caption VARCHAR,
            created_at DATETIME DEFAULT (CURRENT_TIMESTAMP),
            FOREIGN KEY(event_id) REFERENCES events(id)
        );
        """)
        cursor.execute("CREATE INDEX ix_event_memories_id ON event_memories (id);")
        print("Created event_memories table.")
    except Exception as e:
        print(f"Skipping memories: {e}")

    # Columns
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN family_id INTEGER REFERENCES families(id);")
        print("Added family_id.")
    except Exception as e:
        print(f"Skipping family_id: {e}")

    try:
        cursor.execute("ALTER TABLE events ADD COLUMN suggested_action VARCHAR;")
        print("Added suggested_action.")
    except Exception as e:
        print(f"Skipping suggested_action: {e}")

    conn.commit()
    conn.close()
    print("Done.")

if __name__ == "__main__":
    migrate()

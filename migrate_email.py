import sqlite3

# Connect to the SQLite database
# Adjust the path if your database is located elsewhere
db_path = "smaran.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Migrating database for Email Verification...")

# Add columns to users table
columns_to_add = [
    ("is_email_verified", "BOOLEAN DEFAULT 0"),
    ("email_notifications_enabled", "BOOLEAN DEFAULT 0"),
    ("otp_code", "VARCHAR"),
    ("otp_created_at", "DATETIME")
]

for col_name, col_type in columns_to_add:
    try:
        cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
        print(f"[SUCCESS] Added {col_name} to users")
    except sqlite3.OperationalError as e:
        print(f"[INFO] users.{col_name} might already exist: {e}")

conn.commit()
conn.close()
print("Migration complete.")

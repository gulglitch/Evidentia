import sqlite3

conn = sqlite3.connect('database/evidentia.db')
cursor = conn.cursor()

# Check if table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='activity_log'")
result = cursor.fetchone()
print(f"Table exists: {result}")

# Check columns
cursor.execute("PRAGMA table_info(activity_log)")
print("\nColumns:")
for col in cursor.fetchall():
    print(f"  {col[1]} ({col[2]})")

# Check recent activities
cursor.execute("SELECT * FROM activity_log ORDER BY timestamp DESC LIMIT 5")
print("\nRecent activities:")
for row in cursor.fetchall():
    print(f"  ID: {row[0]}, Case: {row[1]}, Action: {row[3]}, Details: {row[4]}")

conn.close()

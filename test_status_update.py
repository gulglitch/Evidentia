"""Test script to verify status update activity logging"""
import sqlite3
from datetime import datetime

# Connect to database
conn = sqlite3.connect('database/evidentia.db')
cursor = conn.cursor()

# Get the most recent activity logs
print("=== Recent Activity Logs (Last 10) ===")
cursor.execute("""
    SELECT 
        id, 
        case_id, 
        user_id, 
        action, 
        details, 
        timestamp 
    FROM activity_log 
    ORDER BY timestamp DESC 
    LIMIT 10
""")

for row in cursor.fetchall():
    print(f"\nID: {row[0]}")
    print(f"  Case ID: {row[1]}")
    print(f"  User ID: {row[2]}")
    print(f"  Action: {row[3]}")
    print(f"  Details: {row[4]}")
    print(f"  Time: {row[5]}")

# Check for status update activities specifically
print("\n\n=== Status Update Activities ===")
cursor.execute("""
    SELECT 
        id, 
        case_id, 
        action, 
        details, 
        timestamp 
    FROM activity_log 
    WHERE action LIKE '%Status%'
    ORDER BY timestamp DESC 
    LIMIT 5
""")

rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f"\nID: {row[0]}, Case: {row[1]}")
        print(f"  Action: {row[2]}")
        print(f"  Details: {row[3]}")
        print(f"  Time: {row[4]}")
else:
    print("No status update activities found!")

# Check for risk level update activities
print("\n\n=== Risk Level Update Activities ===")
cursor.execute("""
    SELECT 
        id, 
        case_id, 
        action, 
        details, 
        timestamp 
    FROM activity_log 
    WHERE action LIKE '%Risk%'
    ORDER BY timestamp DESC 
    LIMIT 5
""")

rows = cursor.fetchall()
if rows:
    for row in rows:
        print(f"\nID: {row[0]}, Case: {row[1]}")
        print(f"  Action: {row[2]}")
        print(f"  Details: {row[3]}")
        print(f"  Time: {row[4]}")
else:
    print("No risk level update activities found!")

conn.close()
print("\n=== Test Complete ===")

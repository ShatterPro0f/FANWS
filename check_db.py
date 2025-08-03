import sqlite3
import os

# Check template_collections.db
db_path = 'metadata/template_collections.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"Tables in {db_path}: {tables}")

    # Check template_collections table structure if it exists
    try:
        cursor.execute("PRAGMA table_info(template_collections)")
        columns = cursor.fetchall()
        print(f"template_collections columns: {columns}")
    except Exception as e:
        print(f"Error checking template_collections: {e}")

    conn.close()
else:
    print(f"Database {db_path} does not exist")

# Check other databases
for db_name in ['template_recommendations.db', 'template_versions.db']:
    db_path = f'metadata/{db_name}'
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Tables in {db_name}: {tables}")
        conn.close()

#!/usr/bin/env python3
"""
Check the exact schema of all metadata databases
"""

import sqlite3
from pathlib import Path

def check_all_schemas():
    metadata_dir = Path("metadata")

    for db_file in ["template_collections.db", "template_recommendations.db", "template_versions.db"]:
        db_path = metadata_dir / db_file
        if db_path.exists():
            print(f"\n{'='*50}")
            print(f"Database: {db_file}")
            print('='*50)

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()

            for table_name in tables:
                table_name = table_name[0]
                print(f"\nTable: {table_name}")
                print("-" * 30)

                # Get column info
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()

                for col in columns:
                    print(f"  {col[1]} ({col[2]}) {'PRIMARY KEY' if col[5] else ''}")

            conn.close()

if __name__ == "__main__":
    check_all_schemas()

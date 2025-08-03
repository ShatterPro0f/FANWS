#!/usr/bin/env python3
"""
FANWS Application Backup Script
Creates comprehensive backups of the entire FANWS application
"""

import os
import shutil
import zipfile
import datetime
import json
import sys
from pathlib import Path

class FANWSBackup:
    def __init__(self, source_dir=None, backup_dir=None):
        self.source_dir = Path(source_dir) if source_dir else Path(__file__).parent
        self.backup_dir = Path(backup_dir) if backup_dir else self.source_dir.parent / "FANWS_Backups"
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    def create_backup_directory(self):
        """Create backup directory if it doesn't exist"""
        self.backup_dir.mkdir(exist_ok=True)
        print(f"📁 Backup directory: {self.backup_dir}")

    def get_backup_info(self):
        """Generate backup metadata"""
        return {
            "backup_date": datetime.datetime.now().isoformat(),
            "source_directory": str(self.source_dir),
            "backup_type": "full_application_backup",
            "files_included": self.get_file_count(),
            "version": self.get_app_version()
        }

    def get_file_count(self):
        """Count files in source directory"""
        count = 0
        for root, dirs, files in os.walk(self.source_dir):
            # Skip certain directories
            dirs[:] = [d for d in dirs if not d.startswith(('.git', '__pycache__', '.vscode'))]
            count += len(files)
        return count

    def get_app_version(self):
        """Try to determine app version from various sources"""
        version_sources = [
            self.source_dir / "version.txt",
            self.source_dir / "src" / "__init__.py",
            self.source_dir / "setup.py"
        ]

        for source in version_sources:
            if source.exists():
                try:
                    content = source.read_text()
                    # Simple version extraction (can be enhanced)
                    if "version" in content.lower():
                        return f"found_in_{source.name}"
                except:
                    pass
        return "unknown"

    def create_zip_backup(self):
        """Create a ZIP backup of the entire application"""
        backup_name = f"FANWS_Backup_{self.timestamp}.zip"
        backup_path = self.backup_dir / backup_name

        print(f"🗜️  Creating ZIP backup: {backup_name}")

        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.source_dir):
                # Skip certain directories
                dirs[:] = [d for d in dirs if not d.startswith(('.git', '__pycache__', '.vscode', 'node_modules'))]

                for file in files:
                    file_path = Path(root) / file
                    # Skip certain file types
                    if file_path.suffix not in ['.pyc', '.pyo', '.log'] and not file.startswith('.'):
                        arc_path = file_path.relative_to(self.source_dir)
                        zipf.write(file_path, arc_path)

        print(f"✅ ZIP backup created: {backup_path}")
        return backup_path

    def create_folder_backup(self):
        """Create a folder backup (mirror copy)"""
        backup_name = f"FANWS_Backup_{self.timestamp}"
        backup_path = self.backup_dir / backup_name

        print(f"📂 Creating folder backup: {backup_name}")

        # Copy entire directory structure
        shutil.copytree(
            self.source_dir,
            backup_path,
            ignore=shutil.ignore_patterns(
                '__pycache__', '*.pyc', '*.pyo', '.git*', '.vscode',
                '*.log', 'node_modules', '.DS_Store'
            )
        )

        print(f"✅ Folder backup created: {backup_path}")
        return backup_path

    def create_database_backup(self):
        """Backup database files separately"""
        db_files = []
        for db_file in self.source_dir.glob("*.db"):
            if db_file.exists():
                backup_db_path = self.backup_dir / f"{db_file.stem}_backup_{self.timestamp}.db"
                shutil.copy2(db_file, backup_db_path)
                db_files.append(backup_db_path)
                print(f"💾 Database backup: {backup_db_path}")

        return db_files

    def save_backup_manifest(self, backup_path):
        """Save backup information"""
        manifest_path = backup_path.parent / f"backup_manifest_{self.timestamp}.json"
        manifest_data = self.get_backup_info()
        manifest_data["backup_path"] = str(backup_path)

        with open(manifest_path, 'w') as f:
            json.dump(manifest_data, f, indent=2)

        print(f"📋 Backup manifest saved: {manifest_path}")
        return manifest_path

    def perform_full_backup(self, backup_type="both"):
        """Perform complete backup operation"""
        print("🚀 Starting FANWS Application Backup...")
        print(f"📍 Source: {self.source_dir}")
        print("=" * 50)

        self.create_backup_directory()

        backup_paths = []

        # Create ZIP backup
        if backup_type in ["zip", "both"]:
            zip_path = self.create_zip_backup()
            backup_paths.append(zip_path)
            self.save_backup_manifest(zip_path)

        # Create folder backup
        if backup_type in ["folder", "both"]:
            folder_path = self.create_folder_backup()
            backup_paths.append(folder_path)
            self.save_backup_manifest(folder_path)

        # Backup databases
        db_backups = self.create_database_backup()
        backup_paths.extend(db_backups)

        print("\n" + "=" * 50)
        print("✅ Backup completed successfully!")
        print(f"📁 Backup location: {self.backup_dir}")
        print(f"📊 Total backups created: {len(backup_paths)}")

        return backup_paths

    def list_existing_backups(self):
        """List all existing backups"""
        if not self.backup_dir.exists():
            print("❌ No backup directory found.")
            return []

        backups = []
        for item in self.backup_dir.iterdir():
            if item.name.startswith("FANWS_Backup_"):
                stat = item.stat()
                backups.append({
                    "name": item.name,
                    "path": item,
                    "size": stat.st_size,
                    "modified": datetime.datetime.fromtimestamp(stat.st_mtime)
                })

        if backups:
            print("📋 Existing backups:")
            for backup in sorted(backups, key=lambda x: x["modified"], reverse=True):
                size_mb = backup["size"] / (1024 * 1024)
                print(f"   📦 {backup['name']} ({size_mb:.1f} MB) - {backup['modified'].strftime('%Y-%m-%d %H:%M')}")
        else:
            print("❌ No existing backups found.")

        return backups

def main():
    """Main backup function"""
    import argparse

    parser = argparse.ArgumentParser(description="FANWS Application Backup Tool")
    parser.add_argument("--type", choices=["zip", "folder", "both"], default="both",
                       help="Type of backup to create")
    parser.add_argument("--source", help="Source directory (default: current directory)")
    parser.add_argument("--dest", help="Destination directory (default: ../FANWS_Backups)")
    parser.add_argument("--list", action="store_true", help="List existing backups")

    args = parser.parse_args()

    backup_tool = FANWSBackup(args.source, args.dest)

    if args.list:
        backup_tool.list_existing_backups()
    else:
        backup_tool.perform_full_backup(args.type)

if __name__ == "__main__":
    main()

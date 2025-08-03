#!/usr/bin/env python3
"""
FANWS Directory Comprehensive Cleanup Script
============================================

This script identifies and removes unnecessary files while preserving:
1. Core application files
2. Essential documentation
3. Testing files referenced in the comprehensive testing guide
4. Configuration and data files
5. User content and templates

The script categorizes files and provides detailed reporting before removal.
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
import sys


class FANWSDirectoryCleanup:
    def __init__(self, base_path):
        self.base_path = Path(base_path)
        self.cleanup_report = {
            "timestamp": datetime.now().isoformat(),
            "base_path": str(self.base_path),
            "analysis": {},
            "actions": {
                "preserved": [],
                "removed": [],
                "errors": []
            },
            "summary": {}
        }

        # Essential files and directories to ALWAYS preserve
        self.essential_files = {
            # Core application
            "fanws.py",
            "requirements.txt",
            "README.md",
            "FANWS.code-workspace",
            ".gitignore",

            # Configuration
            "config",
            "metadata",

            # Core source code
            "src",

            # Data and user content
            "projects",
            "templates",
            "resources",
            "plugins",
            "analytics.db",
            "fanws.db",
            "fanws.db-shm",
            "fanws.db-wal",

            # Testing files referenced in comprehensive testing guide
            "quick_test_runner.py",
            "fanws_state_tester.py",
            "user_testing_suite.py",
            "error_tracking_system.py",
            "testing_orchestrator.py",

            # Essential documentation
            "COMPREHENSIVE_TESTING_GUIDE.md",
            "COMPREHENSIVE_TESTING_SUMMARY.md",
            "BACKUP_GUIDE.md",

            # Essential scripts
            "backup_fanws.py",
            "backup_fanws.ps1"
        }

        # Files that are definitely safe to remove
        self.removable_files = {
            # Temporary and generated files
            "*.tmp", "*.temp", "*.log",

            # Action verification and implementation test files
            "action2_verification.py",
            "action2_verification_results.json",
            "action3_implementation_test.py",

            # Redundant planning documents
            "COMPLETE_FIX_IMPLEMENTATION_PLAN.md",
            "COMPLETION_ACTION_PLAN.md",
            "COMPREHENSIVE_FEATURE_INTEGRATION_PLAN.md",
            "COMPREHENSIVE_IMPROVEMENT_PLAN.md",
            "FILECACHE_TTLSECONDS_FIX_COMPLETE.md",

            # Previous cleanup artifacts
            "directory_cleanup.py",
            "directory_cleanup_report.json",

            # Test reports (can be regenerated)
            "quick_test_report.json",
            "*_report.json",
            "*_results.json",

            # Other test files not in guide
            "comprehensive_ui_test.py",
            "check_db_schema.py",

            # Python cache
            "__pycache__",
            "*.pyc",
            ".pytest_cache"
        }

        # Directories that should be preserved but cleaned of temp files
        self.preserve_but_clean = {
            "logs",
            "docs",
            "analytics_data",
            "scripts"
        }

    def scan_directory(self):
        """Scan the directory and categorize all files and folders."""
        print("🔍 Scanning FANWS directory...")

        all_items = []
        for item in self.base_path.rglob("*"):
            if item.is_file():
                all_items.append(item)

        # Categorize files
        essential = []
        removable = []
        questionable = []

        for item in all_items:
            relative_path = item.relative_to(self.base_path)
            item_name = item.name

            # Check if essential
            if self._is_essential(relative_path, item_name):
                essential.append(str(relative_path))
            # Check if removable
            elif self._is_removable(relative_path, item_name):
                removable.append(str(relative_path))
            else:
                questionable.append(str(relative_path))

        self.cleanup_report["analysis"] = {
            "total_files": len(all_items),
            "essential_files": len(essential),
            "removable_files": len(removable),
            "questionable_files": len(questionable)
        }

        self.cleanup_report["file_categories"] = {
            "essential": essential,
            "removable": removable,
            "questionable": questionable
        }

        return essential, removable, questionable

    def _is_essential(self, relative_path, item_name):
        """Check if a file/directory is essential and should be preserved."""
        path_str = str(relative_path)

        # Check exact matches
        if item_name in self.essential_files or path_str in self.essential_files:
            return True

        # Check if in essential directories
        essential_dirs = ["src/", "config/", "projects/", "templates/", "resources/", "plugins/", "metadata/"]
        if any(path_str.startswith(dir_name) for dir_name in essential_dirs):
            return True

        # Preserve __init__.py files
        if item_name == "__init__.py":
            return True

        # Preserve any .py files in root src directory
        if str(relative_path).startswith("src/") and item_name.endswith(".py"):
            return True

        return False

    def _is_removable(self, relative_path, item_name):
        """Check if a file/directory can be safely removed."""
        path_str = str(relative_path)

        # Check exact matches for removable files
        for pattern in self.removable_files:
            if pattern.startswith("*") and pattern.endswith("*"):
                # Contains pattern
                if pattern[1:-1] in item_name:
                    return True
            elif pattern.startswith("*"):
                # Ends with pattern
                if item_name.endswith(pattern[1:]):
                    return True
            elif pattern.endswith("*"):
                # Starts with pattern
                if item_name.startswith(pattern[:-1]):
                    return True
            else:
                # Exact match
                if item_name == pattern or path_str == pattern:
                    return True

        # Remove cache directories
        if "__pycache__" in path_str or ".pytest_cache" in path_str:
            return True

        # Remove log files in logs directory
        if path_str.startswith("logs/") and (item_name.endswith(".log") or item_name.endswith(".txt")):
            return True

        return False

    def display_cleanup_plan(self, essential, removable, questionable):
        """Display the cleanup plan for user review."""
        print("\n" + "="*80)
        print("📋 FANWS DIRECTORY CLEANUP PLAN")
        print("="*80)

        print(f"\n✅ ESSENTIAL FILES TO PRESERVE ({len(essential)} files):")
        for item in sorted(essential)[:10]:  # Show first 10
            print(f"   📄 {item}")
        if len(essential) > 10:
            print(f"   ... and {len(essential) - 10} more essential files")

        print(f"\n🗑️  FILES TO REMOVE ({len(removable)} files):")
        for item in sorted(removable):
            print(f"   ❌ {item}")

        if questionable:
            print(f"\n❓ QUESTIONABLE FILES (need review) ({len(questionable)} files):")
            for item in sorted(questionable):
                print(f"   ⚠️  {item}")

    def perform_cleanup(self, removable_files, auto_confirm=False):
        """Perform the actual cleanup operation."""
        if not auto_confirm:
            print(f"\n⚠️  About to remove {len(removable_files)} files/directories.")
            response = input("Do you want to proceed? (yes/no): ").lower().strip()
            if response not in ['yes', 'y']:
                print("❌ Cleanup cancelled by user.")
                return False

        print("\n🧹 Starting cleanup...")
        removed_count = 0
        error_count = 0

        for file_path in removable_files:
            full_path = self.base_path / file_path
            try:
                if full_path.exists():
                    if full_path.is_file():
                        full_path.unlink()
                        print(f"   ✅ Removed file: {file_path}")
                    elif full_path.is_dir():
                        shutil.rmtree(full_path)
                        print(f"   ✅ Removed directory: {file_path}")

                    self.cleanup_report["actions"]["removed"].append(str(file_path))
                    removed_count += 1
                else:
                    print(f"   ⚠️  Already removed: {file_path}")

            except Exception as e:
                error_msg = f"Error removing {file_path}: {str(e)}"
                print(f"   ❌ {error_msg}")
                self.cleanup_report["actions"]["errors"].append(error_msg)
                error_count += 1

        # Remove empty directories
        self._remove_empty_dirs()

        self.cleanup_report["summary"] = {
            "files_removed": removed_count,
            "errors": error_count,
            "cleanup_successful": error_count == 0
        }

        print(f"\n✅ Cleanup completed!")
        print(f"   📊 Files removed: {removed_count}")
        print(f"   ❌ Errors: {error_count}")

        return True

    def _remove_empty_dirs(self):
        """Remove empty directories after file cleanup."""
        for root, dirs, files in os.walk(self.base_path, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                try:
                    if dir_path.exists() and not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        rel_path = dir_path.relative_to(self.base_path)
                        print(f"   ✅ Removed empty directory: {rel_path}")
                        self.cleanup_report["actions"]["removed"].append(f"{rel_path}/ (empty)")
                except OSError:
                    pass  # Directory not empty or permission error

    def save_report(self):
        """Save the cleanup report."""
        report_file = self.base_path / f"cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.cleanup_report, f, indent=2, ensure_ascii=False)

        print(f"\n📄 Cleanup report saved: {report_file.name}")
        return report_file

    def run_comprehensive_cleanup(self, auto_confirm=False):
        """Run the complete cleanup process."""
        print("🚀 Starting FANWS Comprehensive Directory Cleanup")
        print(f"📁 Target directory: {self.base_path}")

        # Scan directory
        essential, removable, questionable = self.scan_directory()

        # Display plan
        self.display_cleanup_plan(essential, removable, questionable)

        # Handle questionable files
        if questionable:
            print(f"\n⚠️  Found {len(questionable)} questionable files that need manual review.")
            print("These files will be preserved for now. Review them manually if needed.")
            for item in questionable:
                self.cleanup_report["actions"]["preserved"].append(f"{item} (questionable)")

        # Perform cleanup
        if removable:
            success = self.perform_cleanup(removable, auto_confirm)
            if not success:
                return False
        else:
            print("\n✨ No files need to be removed. Directory is already clean!")

        # Save report
        self.save_report()

        print("\n🎉 FANWS directory cleanup completed successfully!")
        print("\nPreserved essential components:")
        print("  ✅ Core application (fanws.py, src/)")
        print("  ✅ Testing framework (all referenced test files)")
        print("  ✅ Documentation (essential guides)")
        print("  ✅ Configuration and data")
        print("  ✅ User projects and templates")

        return True


def main():
    """Main execution function."""
    # Get the directory containing this script
    script_dir = Path(__file__).parent.absolute()

    print("FANWS Directory Comprehensive Cleanup Tool")
    print("==========================================")

    # Initialize cleanup
    cleanup = FANWSDirectoryCleanup(script_dir)

    # Check for auto-confirm flag
    auto_confirm = "--auto-confirm" in sys.argv
    if auto_confirm:
        print("🤖 Auto-confirm mode enabled")

    # Run cleanup
    try:
        success = cleanup.run_comprehensive_cleanup(auto_confirm)
        if success:
            print("\n✅ All operations completed successfully!")
            return 0
        else:
            print("\n❌ Cleanup was cancelled or failed.")
            return 1

    except Exception as e:
        print(f"\n💥 Unexpected error during cleanup: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)

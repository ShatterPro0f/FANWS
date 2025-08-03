"""
FANWS Testing Integration
Automatically instruments FANWS with user testing monitoring
"""

import sys
import os
import time
import traceback
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from user_testing_monitor import start_user_testing_monitor, get_user_monitor, log_user_action

class FANWSTestingWrapper:
    """Wrapper to integrate testing monitoring with FANWS."""

    def __init__(self):
        self.monitor = None
        self.original_modules = {}

    def start_testing_session(self, session_id: str = None):
        """Start a new testing session."""
        print("🚀 Starting FANWS User Testing Session")
        print("=" * 50)

        self.monitor = start_user_testing_monitor(session_id)
        self.monitor.set_test_phase("initialization")

        # Instrument key modules
        self.instrument_fanws_modules()

        print("✅ Testing monitor active")
        print("📋 Follow the USER_TESTING_GUIDE.md for systematic testing")
        print("🔍 All actions and errors will be automatically logged")
        print("=" * 50)

        return self.monitor

    def instrument_fanws_modules(self):
        """Instrument FANWS modules with monitoring."""
        try:
            # Import and instrument core modules
            self.instrument_memory_manager()
            self.instrument_file_operations()
            self.instrument_project_manager()
            self.instrument_ui_components()

        except Exception as e:
            if self.monitor:
                self.monitor.log_error("instrumentation", "FANWSTestingWrapper",
                                     f"Failed to instrument modules: {e}", "medium",
                                     "Module instrumentation", traceback.format_exc())

    def instrument_memory_manager(self):
        """Instrument memory manager components."""
        try:
            from src.memory_manager import FileCache, ProjectFileCache

            # Instrument FileCache
            original_filecache_get = FileCache.get
            original_filecache_set = FileCache.set
            original_filecache_update = FileCache.update

            @log_user_action("FileCache", "cache_operation")
            def monitored_filecache_get(self, key):
                return original_filecache_get(self, key)

            @log_user_action("FileCache", "cache_operation")
            def monitored_filecache_set(self, key, value):
                return original_filecache_set(self, key, value)

            @log_user_action("FileCache", "cache_operation")
            def monitored_filecache_update(self, key, value):
                return original_filecache_update(self, key, value)

            FileCache.get = monitored_filecache_get
            FileCache.set = monitored_filecache_set
            FileCache.update = monitored_filecache_update

            # Instrument ProjectFileCache
            original_projectcache_get = ProjectFileCache.get
            original_projectcache_update = ProjectFileCache.update

            @log_user_action("ProjectFileCache", "file_operation")
            def monitored_projectcache_get(self, filename):
                return original_projectcache_get(self, filename)

            @log_user_action("ProjectFileCache", "file_operation")
            def monitored_projectcache_update(self, filename, content):
                return original_projectcache_update(self, filename, content)

            ProjectFileCache.get = monitored_projectcache_get
            ProjectFileCache.update = monitored_projectcache_update

            if self.monitor:
                self.monitor.log_action("system", "instrumentation", "MemoryManager",
                                       "Successfully instrumented memory manager components")

        except Exception as e:
            if self.monitor:
                self.monitor.log_error("instrumentation", "MemoryManager",
                                     f"Failed to instrument memory manager: {e}", "low")

    def instrument_file_operations(self):
        """Instrument file operations."""
        try:
            from src import file_operations

            # Instrument key file functions
            if hasattr(file_operations, 'read_file'):
                original_read_file = file_operations.read_file

                @log_user_action("FileOperations", "file_io")
                def monitored_read_file(filepath, encoding='utf-8'):
                    return original_read_file(filepath, encoding)

                file_operations.read_file = monitored_read_file

            if hasattr(file_operations, 'save_to_file'):
                original_save_to_file = file_operations.save_to_file

                @log_user_action("FileOperations", "file_io")
                def monitored_save_to_file(filepath, content, encoding='utf-8'):
                    return original_save_to_file(filepath, content, encoding)

                file_operations.save_to_file = monitored_save_to_file

            if self.monitor:
                self.monitor.log_action("system", "instrumentation", "FileOperations",
                                       "Successfully instrumented file operations")

        except Exception as e:
            if self.monitor:
                self.monitor.log_error("instrumentation", "FileOperations",
                                     f"Failed to instrument file operations: {e}", "low")

    def instrument_project_manager(self):
        """Instrument project management components."""
        try:
            # Use the existing PerProjectConfigManager instead of project_manager
            from src.per_project_config_manager import PerProjectConfigManager

            # Instrument PerProjectConfigManager methods
            original_initialize = PerProjectConfigManager.initialize_project_config
            original_save_config = PerProjectConfigManager.save_config
            original_load_config = PerProjectConfigManager.load_config

            @log_user_action("PerProjectConfigManager", "project_operation")
            def monitored_initialize(self):
                return original_initialize(self)

            @log_user_action("PerProjectConfigManager", "project_operation")
            def monitored_save_config(self):
                return original_save_config(self)

            @log_user_action("PerProjectConfigManager", "project_operation")
            def monitored_load_config(self):
                return original_load_config(self)

            PerProjectConfigManager.initialize_project_config = monitored_initialize
            PerProjectConfigManager.save_config = monitored_save_config
            PerProjectConfigManager.load_config = monitored_load_config

            if self.monitor:
                self.monitor.log_action("system", "instrumentation", "PerProjectConfigManager",
                                       "Successfully instrumented per-project config manager")

        except Exception as e:
            if self.monitor:
                self.monitor.log_error("instrumentation", "PerProjectConfigManager",
                                     f"Failed to instrument per-project config manager: {e}", "low")

    def instrument_ui_components(self):
        """Instrument UI components if available."""
        try:
            # Try to instrument UI components
            # This will depend on the specific UI framework used

            if self.monitor:
                self.monitor.log_action("system", "instrumentation", "UIComponents",
                                       "UI monitoring enabled")

        except Exception as e:
            if self.monitor:
                self.monitor.log_error("instrumentation", "UIComponents",
                                     f"Failed to instrument UI components: {e}", "low")

# Global testing wrapper instance
_testing_wrapper = None

def start_fanws_testing(session_id: str = None):
    """Start FANWS with testing monitoring enabled."""
    global _testing_wrapper

    _testing_wrapper = FANWSTestingWrapper()
    monitor = _testing_wrapper.start_testing_session(session_id)

    return monitor

def set_testing_phase(phase: str):
    """Set the current testing phase."""
    monitor = get_user_monitor()
    if monitor:
        monitor.set_test_phase(phase)

def log_test_action(action_type: str, component: str, details: str, success: bool = True):
    """Manually log a test action."""
    monitor = get_user_monitor()
    if monitor:
        monitor.log_action(action_type, "manual_test", component, details, success)

def log_test_error(component: str, error_message: str, severity: str = "medium"):
    """Manually log a test error."""
    monitor = get_user_monitor()
    if monitor:
        monitor.log_error("user_reported", component, error_message, severity)

def get_testing_status():
    """Get current testing status."""
    monitor = get_user_monitor()
    if monitor:
        return {
            'session_id': monitor.session_id,
            'current_phase': monitor.current_test_phase,
            'actions_logged': len(monitor.actions_log),
            'errors_logged': len(monitor.errors_log),
            'fixes_needed': len(monitor.fixes_needed)
        }
    return None

if __name__ == "__main__":
    # Interactive testing session startup
    print("🧪 FANWS Interactive Testing Session")
    print("=" * 40)

    session_id = input("Enter session ID (or press Enter for auto-generated): ").strip()
    if not session_id:
        session_id = f"interactive_{int(time.time())}"

    monitor = start_fanws_testing(session_id)

    print(f"\n✅ Testing session '{session_id}' started")
    print("\nAvailable commands:")
    print("  set_phase <phase_name>  - Set testing phase")
    print("  log_action <component> <details>  - Log test action")
    print("  log_error <component> <error>     - Log test error")
    print("  status                  - Show testing status")
    print("  help                    - Show this help")
    print("  quit                    - End testing session")

    print("\n📋 Now launch FANWS and start systematic testing!")
    print("   python fanws.py")
    print("\n🔍 All actions will be automatically monitored.")

    # Simple command interface for manual interaction
    while True:
        try:
            command = input("\nTesting> ").strip().lower()

            if command == "quit":
                break
            elif command == "status":
                status = get_testing_status()
                if status:
                    print(f"Session: {status['session_id']}")
                    print(f"Phase: {status['current_phase']}")
                    print(f"Actions: {status['actions_logged']}")
                    print(f"Errors: {status['errors_logged']}")
                    print(f"Fixes Needed: {status['fixes_needed']}")
            elif command.startswith("set_phase "):
                phase = command[10:]
                set_testing_phase(phase)
                print(f"Testing phase set to: {phase}")
            elif command.startswith("log_action "):
                parts = command[11:].split(" ", 1)
                if len(parts) == 2:
                    component, details = parts
                    log_test_action("manual", component, details)
                    print("Action logged")
            elif command.startswith("log_error "):
                parts = command[10:].split(" ", 1)
                if len(parts) == 2:
                    component, error = parts
                    log_test_error(component, error)
                    print("Error logged")
            elif command == "help":
                print("Available commands:")
                print("  set_phase <phase_name>  - Set testing phase")
                print("  log_action <component> <details>  - Log test action")
                print("  log_error <component> <error>     - Log test error")
                print("  status                  - Show testing status")
                print("  help                    - Show this help")
                print("  quit                    - End testing session")
            else:
                print("Unknown command. Type 'help' for available commands.")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

    print("\n🔚 Ending testing session...")
    if monitor:
        monitor.stop_monitoring()
    print("✅ Testing session completed. Check user_testing_logs/ for reports.")

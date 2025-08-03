"""
Main Window for FANWS
Contains the primary application window and UI setup logic
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStatusBar,
    QMessageBox, QApplication, QTextEdit, QPushButton, QProgressBar,
    QLabel, QLineEdit, QSpinBox, QGroupBox, QComboBox, QDoubleSpinBox,
    QCheckBox, QFormLayout, QSplitter, QScrollArea, QInputDialog,
    QDialog, QListWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QFileDialog, QTabWidget
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

# Memory monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logging.warning("⚠ psutil not available - memory monitoring disabled")

from ..core.error_handling_system import ErrorHandler, create_styled_message_box
from ..core.error_handling_system import get_cache_manager, ProjectFileCache
from ..core.error_handling_system import get_project_list, validate_project_name, initialize_project_files
from ..core.performance_monitor import PerformanceMonitor
from . import UIComponents

try:
    from ..core.error_handling_system import get_async_manager, BackgroundTaskManager, ProgressTracker
    from ..plugins.plugin_workflow_integration import AsyncWorkflowOperations
    from ..core.error_handling_system import AsyncProgressDialog
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False

try:
    from ..plugins.plugin_management_ui import MainWindow, DesignSystem, Components, Animations, LayoutManager
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    MainWindow = None
    DesignSystem = None
    Components = None
    Animations = None
    LayoutManager = None


class FANWSMainWindow(QMainWindow):
    """Main application window for FANWS"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fiction AI Novel Writing Suite (FANWS)")
        self.resize(1600, 1000)  # Increased size to better accommodate 1/4 sidebar

        # Initialize basic attributes early to prevent AttributeError
        self.current_directory = os.path.dirname(os.path.abspath(__file__))
        self.current_project = None
        self.file_cache = None
        self.performance_monitor = None
        self.gui_enabled = False  # Initialize early, will be set to True in init_gui_system if successful

        # Initialize memory monitoring
        self.memory_warning_threshold = 80  # Warn at 80% memory usage
        self.memory_monitor_timer = None
        self.setup_memory_monitoring()

        # Initialize GUI system
        self.init_gui_system()

        # Initialize status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready", 5000)

        # Initialize performance monitoring
        if hasattr(self, 'performance_monitor') and self.performance_monitor is None:
            self.performance_monitor = PerformanceMonitor()
            self.performance_monitor.start_monitoring()

        # Initialize core UI components
        self.setup_ui_components()

        # Initialize project and file management attributes
        self.config = None
        self.project_manager = None

        # Initialize workflow attributes
        self.novel_workflow = None
        self.workflow_dialog = None
        self.collaborative_manager = None
        self.collaborative_dialog = None

        # Workflow control state
        self.workflow_active = False
        self.current_workflow_step = None
        self.workflow_timer = None

        # Initialize worker attribute
        self.worker = None

        # Setup UI after basic initialization
        self.setup_main_ui()

    def setup_memory_monitoring(self):
        """Setup periodic memory monitoring"""
        if PSUTIL_AVAILABLE:
            self.memory_monitor_timer = QTimer(self)
            self.memory_monitor_timer.timeout.connect(self.check_memory_usage)
            self.memory_monitor_timer.start(30000)  # Check every 30 seconds
            logging.info("Memory monitoring enabled")
        else:
            logging.warning("Memory monitoring disabled - psutil not available")

    def check_memory_usage(self):
        """Check current memory usage and warn if exceeding threshold"""
        if not PSUTIL_AVAILABLE:
            return

        try:
            # Get system memory info
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Get current process memory usage
            process = psutil.Process()
            process_memory_mb = process.memory_info().rss / 1024 / 1024

            # Update status bar with memory info
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(
                    f"Memory: {memory_percent:.1f}% | Process: {process_memory_mb:.1f}MB",
                    5000
                )

            # Show warning if memory usage is high
            if memory_percent > self.memory_warning_threshold:
                self.show_memory_warning(memory_percent, process_memory_mb)

        except Exception as e:
            logging.error(f"Error checking memory usage: {e}")

    def show_memory_warning(self, system_percent: float, process_mb: float):
        """Show memory usage warning"""
        message = (
            f"High memory usage detected!\n\n"
            f"System Memory: {system_percent:.1f}%\n"
            f"FANWS Process: {process_mb:.1f}MB\n\n"
            f"Consider:\n"
            f"• Saving your work\n"
            f"• Closing unused projects\n"
            f"• Clearing caches\n"
            f"• Restarting the application"
        )

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Memory Usage Warning")
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def init_gui_system(self):
        """Initialize modern GUI system."""
        if GUI_AVAILABLE:
            try:
                self.modern_design = DesignSystem()
                self.modern_components = Components()
                self.modern_animations = Animations()
                self.modern_layout = LayoutManager()
                self.gui_enabled = True
                print("✓ Modern GUI system initialized")
            except Exception as e:
                print(f"⚠ Failed to initialize modern GUI: {e}")
                self.gui_enabled = False
        else:
            self.gui_enabled = False

    def setup_ui_components(self):
        """Setup all UI components"""
        # Pre-create all tab widgets to avoid deleted C++ object errors
        self.story_tab = QTextEdit()
        self.config_tab = QTextEdit()
        self.characters_tab = QTextEdit()
        self.world_tab = QTextEdit()
        self.summaries_tab = QTextEdit()
        self.drafts_tab = QTextEdit()
        self.drafts_tab_ref = self.drafts_tab  # Extra reference to prevent GC
        self.readability_tab = QTextEdit()
        self.readability_tab_ref = self.readability_tab  # Extra reference to prevent GC
        self.synonyms_tab = QTextEdit()
        self.synonyms_tab_ref = self.synonyms_tab
        self.log_tab = QTextEdit()
        self.log_tab_ref = self.log_tab
        self.log_tab.setReadOnly(True)

        # Add additional text widgets used in UI components
        self.preview_text = QTextEdit()
        self.preview_text.setPlaceholderText("Story preview will appear here...")
        self.writing_area = QTextEdit()
        self.writing_area.setPlaceholderText("Your current draft will appear here when writing begins...")

        # Add progress widgets with modern styling
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Overall Progress: %p%")

        self.chapter_progress_label = QLabel("Current: Chapter 1, Section 1")
        self.chapter_progress_label.setStyleSheet("color: #666; margin: 10px 0;")

        # Add UI status labels
        self.progress_label = QLabel("Progress: 0%")
        self.status_label = QLabel("Status: Ready")
        self.word_count_label = QLabel("Word Count: 0")
        self.wordsapi_label = QLabel("WordsAPI Calls: 0/2500")

        # Create project selector to prevent C++ object deletion
        self.project_selector = QComboBox()
        self.project_selector.addItem("Select a project")

        # Defensive: keep references to all tabs to prevent garbage collection
        self._tab_refs = [
            self.story_tab, self.config_tab, self.characters_tab, self.world_tab,
            self.summaries_tab, self.drafts_tab, self.readability_tab, self.synonyms_tab, self.log_tab,
            self.drafts_tab_ref, self.readability_tab_ref, self.synonyms_tab_ref, self.log_tab_ref,
            self.preview_text, self.writing_area, self.progress_bar, self.chapter_progress_label,
            self.progress_label, self.status_label, self.word_count_label, self.wordsapi_label,
            self.project_selector  # Add project selector to prevent deletion
        ]

    def setup_main_ui(self):
        """Setup the main UI after components are initialized"""
        # Use UIComponents to build and assign all widgets as attributes
        self.ui = UIComponents(self)

        if self.gui_enabled:
            self.ui.modern_design = self.modern_design
            self.ui.modern_components = self.modern_components
            self.ui.modern_animations = self.modern_animations
            print("✓ Modern components passed to UI system")

        # Only call create_ui() once per window instance
        self.ui.create_ui()

        # Add missing widgets that are referenced in the main application
        self.ui.add_missing_widgets()

        # Populate project list after UI is created
        projects = get_project_list()
        self.project_selector.addItems(projects)

        # Also refresh the project selector to ensure consistency
        if hasattr(self.ui, '_refresh_project_selector'):
            self.ui._refresh_project_selector()

        # Always start with Project section regardless of available projects
        self.ui._show_project_content()

    def setup_signals(self):
        """Connect signals to slots - to be implemented by subclasses"""
        pass

    def setup_event_handlers(self):
        """Setup event handlers - to be implemented by subclasses"""
        pass

    def show_info_message(self, title, message):
        """Show an info message to the user"""
        try:
            msg_box = create_styled_message_box(title, message, QMessageBox.Information)
            msg_box.exec_()
        except Exception as e:
            logging.error(f"Failed to show info message: {e}")
            # Fallback to basic message box
            QMessageBox.information(self, title, message)

    def show_error_message(self, title, message):
        """Show an error message to the user"""
        try:
            msg_box = create_styled_message_box(title, message, QMessageBox.Critical)
            msg_box.exec_()
        except Exception as e:
            logging.error(f"Failed to show error message: {e}")
            # Fallback to basic message box
            QMessageBox.critical(self, title, message)

    def __getattr__(self, name):
        """Fallback to UIComponents attributes if not found in self"""
        # Prevent recursion by checking for specific problematic attributes
        if name in ['ui', '__dict__']:
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

        # Fallback to UIComponents attributes if not found in self, but avoid recursion
        if hasattr(self, 'ui_components') and hasattr(self.ui_components, name):
            return getattr(self.ui_components, name)
        elif hasattr(self, 'ui') and hasattr(self.ui, name):
            return getattr(self.ui, name)

        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        self.status_bar.showMessage("Ready", 5000)

        # Initialize performance monitoring
        self.init_performance_monitoring()

        # Initialize async operations
        self.init_async_operations()

        # Initialize other systems
        self.init_plugin_system()
        self.init_database_system()
        # self.init_multi_provider_ai_system()  # Temporarily disabled due to recursion

        # Setup event handlers (after UI components are created)
        # Note: This will be called after init_gui_system in the child class

    def __getattr__(self, name):
        """Fallback to UIComponents attributes if not found in self"""
        # Prevent recursion by checking for specific problematic attributes
        if name in ['ui', '__dict__']:
            raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")

        # Use __dict__ directly to avoid triggering __getattr__ recursively
        ui = object.__getattribute__(self, '__dict__').get('ui', None)
        if ui and hasattr(ui, name):
            return getattr(ui, name)
        raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")

    def init_gui_system(self):
        """Initialize the GUI system"""
        try:
            # Create and setup UI components
            print("Creating UIComponents...")
            self.ui = UIComponents(self)
            print("UIComponents created, calling create_ui...")
            self.ui.create_ui()
            print("create_ui completed...")

            # Set central widget
            if hasattr(self.ui, 'central_widget'):
                print("Setting central widget...")
                self.setCentralWidget(self.ui.central_widget)
                print("Central widget set.")

            logging.info("GUI system initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize GUI system: {e}")
            import traceback
            print(f"GUI Error: {traceback.format_exc()}")
            # self.show_error_message("GUI Initialization Error", f"Failed to initialize GUI: {e}")

    def init_performance_monitoring(self):
        """Initialize performance monitoring"""
        try:
            from ..core.performance_monitor import PerformanceMonitor
            self.performance_monitor = PerformanceMonitor()
            self.performance_monitor.start_monitoring()
            logging.info("Performance monitoring initialized")
        except ImportError:
            logging.warning("Performance monitoring not available")
            self.performance_monitor = None
        except Exception as e:
            logging.error(f"Failed to initialize performance monitoring: {e}")
            self.performance_monitor = None

    def init_async_operations(self):
        """Initialize async operations"""
        if not ASYNC_AVAILABLE:
            logging.warning("Async operations not available")
            self.async_manager = None
            self.async_progress_tracker = None
            self.async_workflow_manager = None
            self.background_tasks = []
            self.task_analytics = {
                'total_tasks': 0,
                'completed_tasks': 0,
                'failed_tasks': 0,
                'avg_duration': 0,
                'task_history': []
            }
            return

        try:
            # Initialize async operations manager
            self.async_manager = get_async_manager()
            if self.performance_monitor:
                self.async_manager.set_performance_monitor(self.performance_monitor)

            # Initialize async progress tracker
            self.async_progress_tracker = ProgressTracker()
            self.async_progress_tracker.setParent(self)

            # Initialize async workflow manager (will be set up when project is loaded)
            self.async_workflow_manager = None

            # Initialize async UI components
            self.async_workflow_panel = None
            self.async_task_monitor = None
            self.async_progress_widget = None
            self.async_status_indicator = None

            # Async operation state
            self.async_operations_active = False
            self.current_async_task_id = None

            # Initialize background task management
            self.background_tasks = []
            self.task_analytics = {
                'total_tasks': 0,
                'completed_tasks': 0,
                'failed_tasks': 0,
                'avg_duration': 0,
                'task_history': []
            }

            # Initialize task queue management
            self.init_task_queue_manager()

            # Initialize recovery system
            self.init_recovery_system()

            # Initialize async system
            self.init_async_system()

            logging.info("Async operations framework initialized")

        except Exception as e:
            logging.error(f"Failed to initialize async operations: {e}")
            self.async_manager = None
            self.async_progress_tracker = None
            self.async_workflow_manager = None
            self.background_tasks = []
            self.task_analytics = {
                'total_tasks': 0,
                'completed_tasks': 0,
                'failed_tasks': 0,
                'avg_duration': 0,
                'task_history': []
            }

    def init_plugin_system(self):
        """Initialize plugin system"""
        try:
            from ..plugins.plugin_system import get_plugin_manager
            self.plugin_manager = get_plugin_manager()
            logging.info("Plugin system initialized")
        except ImportError:
            logging.warning("Plugin system not available")
            self.plugin_manager = None
        except Exception as e:
            logging.error(f"Failed to initialize plugin system: {e}")
            self.plugin_manager = None

    def init_database_system(self):
        """Initialize database system"""
        try:
            from ..database.database_manager import get_database_manager
            self.database_manager = get_database_manager()
            logging.info("Database system initialized")
        except ImportError:
            logging.warning("Database system not available")
            self.database_manager = None
        except Exception as e:
            logging.error(f"Failed to initialize database system: {e}")
            self.database_manager = None

    def init_multi_provider_ai_system(self):
        """Initialize multi-provider AI system"""
        try:
            from ..ai.ai_provider_abstraction import get_ai_provider_manager
            self.ai_provider_manager = get_ai_provider_manager()
            logging.info("Multi-provider AI system initialized")
        except ImportError:
            logging.warning("Multi-provider AI system not available")
            self.ai_provider_manager = None
        except Exception as e:
            logging.error(f"Failed to initialize AI system: {e}")
            self.ai_provider_manager = None

    def init_task_queue_manager(self):
        """Initialize task queue management"""
        try:
            # Initialize task queue components
            self.task_queue = []
            self.task_workers = []
            self.max_concurrent_tasks = 3
            logging.info("Task queue manager initialized")
        except Exception as e:
            logging.error(f"Failed to initialize task queue manager: {e}")

    def init_recovery_system(self):
        """Initialize recovery system"""
        try:
            # Initialize recovery components
            self.recovery_enabled = True
            self.auto_save_interval = 300  # 5 minutes
            self.setup_auto_save()
            logging.info("Recovery system initialized")
        except Exception as e:
            logging.error(f"Failed to initialize recovery system: {e}")

    def init_async_system(self):
        """Initialize async system components"""
        try:
            # Initialize async system
            self.async_event_loop = None
            self.async_tasks = {}
            logging.info("Async system initialized")
        except Exception as e:
            logging.error(f"Failed to initialize async system: {e}")

    def setup_auto_save(self):
        """Setup automatic saving"""
        if hasattr(self, 'auto_save_interval') and self.auto_save_interval > 0:
            self.auto_save_timer = QTimer(self)
            self.auto_save_timer.timeout.connect(self.auto_save)
            self.auto_save_timer.start(self.auto_save_interval * 1000)  # Convert to milliseconds

    def auto_save(self):
        """Perform automatic save"""
        try:
            if self.current_project and self.file_cache:
                # Save current work
                self.save_current_work()
                self.status_bar.showMessage("Auto-saved", 2000)
        except Exception as e:
            logging.error(f"Auto-save failed: {e}")

    def save_current_work(self):
        """Save current work in progress"""
        # This would be implemented to save current editor contents
        pass

    def setup_event_handlers(self):
        """Setup event handlers"""
        try:
            # Connect UI signals
            if hasattr(self.ui, 'setup_connections'):
                self.ui.setup_connections(self)
            logging.info("Event handlers setup complete")
        except Exception as e:
            logging.error(f"Failed to setup event handlers: {e}")

    def show_error_message(self, title: str, message: str):
        """Show error message to user"""
        QMessageBox.critical(self, title, message)

    def show_info_message(self, title: str, message: str):
        """Show info message to user"""
        QMessageBox.information(self, title, message)

    def show_warning_message(self, title: str, message: str):
        """Show warning message to user"""
        QMessageBox.warning(self, title, message)

    def closeEvent(self, event):
        """Handle application close event"""
        try:
            # Save any unsaved work
            if self.current_project:
                self.save_current_work()

            # Stop monitoring systems
            if self.performance_monitor:
                self.performance_monitor.stop_monitoring()

            # Clean up async operations
            if self.async_manager:
                self.async_manager.cleanup()

            event.accept()
        except Exception as e:
            logging.error(f"Error during application shutdown: {e}")
            event.accept()

    # Draft management methods
    def populate_draft_versions(self, chapter: int, section: int):
        """Populate the draft version selector with available versions for the given chapter and section"""
        if not hasattr(self, 'file_cache') or not self.file_cache:
            return

        try:
            from ..ai.ai_provider_abstraction import DraftManager
            draft_manager = DraftManager(self.file_cache, self.current_project)
            versions = draft_manager.get_draft_versions(chapter, section)

            if hasattr(self, 'draft_version_selector'):
                self.draft_version_selector.clear()
                self.draft_version_selector.addItems([str(v) for v in versions])
                if versions:
                    self.draft_version_selector.setCurrentIndex(0)
                    self.load_draft_version(chapter, section, versions[0])
        except Exception as e:
            logging.error(f"Failed to populate draft versions: {e}")

    def connect_draft_version_selector(self, chapter: int, section: int):
        """Connect the draft version selector to load the selected draft version"""
        if not hasattr(self, 'draft_version_selector'):
            return

        def on_version_changed(idx):
            version_text = self.draft_version_selector.currentText()
            if version_text:
                try:
                    version = int(version_text)
                    self.load_draft_version(chapter, section, version)
                except ValueError:
                    logging.error(f"Invalid version format: {version_text}")

        self.draft_version_selector.currentIndexChanged.connect(on_version_changed)

    def load_draft_version(self, chapter: int, section: int, version: int):
        """Load the selected draft version into the drafts tab"""
        if not hasattr(self, 'file_cache') or not self.file_cache:
            return

        try:
            from ..ai.ai_provider_abstraction import DraftManager
            draft_manager = DraftManager(self.file_cache, self.current_project)
            content = draft_manager.load_draft(chapter, section, version)

            if hasattr(self, 'drafts_tab'):
                self.drafts_tab.setText(content if content else "(No content found for this draft version)")
        except Exception as e:
            logging.error(f"Failed to load draft version: {e}")
            if hasattr(self, 'drafts_tab'):
                self.drafts_tab.setText(f"Error loading draft: {e}")


def create_main_window() -> FANWSMainWindow:
    """Factory function to create the main window"""
    return FANWSMainWindow()

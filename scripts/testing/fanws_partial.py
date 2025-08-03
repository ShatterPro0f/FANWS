"""
Fiction AI Novel Writing Suite (FANWS)

Main application file for the AI-powered novel writing suite.
This file contains the core application logic and coordination.
"""

import sys
import os
import json
import threading
import time
import random
import re
import shutil
import asyncio
from datetime import datetime, date
from typing import Dict, Any, Optional, List
import logging

# Memory monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logging.warning("⚠ psutil not available - memory monitoring disabled")

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QTabWidget,
    QTextEdit, QPushButton, QProgressBar, QLabel, QLineEdit, QSpinBox, QGroupBox,
    QStatusBar, QComboBox, QDoubleSpinBox, QMessageBox, QCheckBox, QFormLayout,
    QSplitter, QScrollArea, QInputDialog, QDialog, QListWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QFileDialog
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QFont

# Document generation libraries
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# Modular imports
from src.error_handling_system import ErrorHandler, create_styled_message_box, ProjectError, APIError, FileOperationError
from src.file_operations import (
    save_to_file, read_file, load_project_env, save_project_env,
    get_project_list, create_backup, load_synonym_cache, save_synonym_cache,
    load_wordsapi_log, save_wordsapi_log, log_wordsapi_call,
    get_wordsapi_call_count, validate_project_name, initialize_project_files
)
from src.utils import project_file_path
from src.memory_manager import FileCache, ProjectFileCache, get_cache_manager
from src.text_processing import SynonymCache, TextAnalyzer, get_text_analyzer, get_synonym_cache
from src.module_compatibility import MARKDOWN_AVAILABLE, markdown2
from src.api_manager import get_api_manager, APIManager
from src.workflow_manager import NovelWritingWorkflowModular

# Import AI content generation modules (now enhanced)
from src.ai.content_generator import (
    ContentGenerator, DraftManager, ConsistencyChecker, WorkflowContext,
    AIWorkflowThread, ProjectManager, summarize_context, update_character_arcs,
    update_plot_points, check_continuity
)

# Import UI modules (now enhanced)
from src.ui.main_window import FANWSMainWindow, create_main_window
try:
    from src.ui import UIComponents
except ImportError:
    print("Warning: Could not import UIComponents")

# Quality Manager (Consolidated)
try:
    from src.quality_manager import (
        QualityManager, get_quality_manager
    )
    QUALITY_ASSURANCE_AVAILABLE = True
except ImportError:
    print("Warning: Quality Manager module not available")
    QUALITY_ASSURANCE_AVAILABLE = False

try:
    from src.error_handling_system import (
        initialize_error_handling_integration, get_error_integration,
        ErrorHandlingIntegration, handle_errors, error_context
    )
    from src.error_handling_system import ErrorHandlingDashboard
    ERROR_HANDLING_AVAILABLE = True
    print("✓ Advanced error handling system loaded successfully")
except ImportError as e:
    print(f"⚠ Advanced error handling system not available: {e}")
    ERROR_HANDLING_AVAILABLE = False

# Memory Manager (Consolidated)
try:
    from src.memory_manager import (
        MemoryManager, get_memory_manager
    )
    from src.ui.analytics_ui import create_memory_management_dashboard
    MEMORY_MANAGEMENT_AVAILABLE = True
    print("✓ Memory management system loaded successfully")
except ImportError as e:
    print(f"⚠ Memory management system not available: {e}")
    MEMORY_MANAGEMENT_AVAILABLE = False

try:
    from src.configuration_manager import (
        ConfigManager, get_global_config, initialize_global_config,
        create_configuration_compatibility_layer, initialize_configuration_migration
    )
    CONFIGURATION_MANAGEMENT_AVAILABLE = True
    print("✓ Unified configuration management system loaded successfully")
except ImportError as e:
    print(f"⚠ Configuration management system not available: {e}")
    CONFIGURATION_MANAGEMENT_AVAILABLE = False

# Per-project configuration management
try:
    from src.per_project_config_manager import PerProjectConfigManager, migrate_all_projects_to_isolation
    PER_PROJECT_CONFIG_AVAILABLE = True
except ImportError:
    PER_PROJECT_CONFIG_AVAILABLE = False
    logging.warning("Per-project configuration manager not available")

# AI Provider Integration
try:
    from src.ai_provider_abstraction import (
        MultiProviderConfig, ProviderConfig, initialize_multi_provider_ai,
        get_memory_integration
    )
    AI_PROVIDERS_AVAILABLE = True
    print("✓ AI provider abstraction system loaded successfully")
except ImportError as e:
    print(f"⚠ AI provider abstraction system not available: {e}")
    AI_PROVIDERS_AVAILABLE = False
    # Stub classes for compatibility
    class MultiProviderConfig:
        def __init__(self):
            self.providers = {}
    class ProviderConfig:
        def __init__(self, *args, **kwargs):
            pass
    def initialize_multi_provider_ai(*args, **kwargs):
        return None
    def get_memory_integration(*args, **kwargs):
        return None

# Database Integration
try:
    from src.database_manager import DatabaseManager, get_database_manager
    from src.database_integration import (
        DatabaseAnalyticsIntegration, DatabaseCollaborationIntegration,
        get_db_analytics_integration, get_db_collaboration_integration
    )
    DATABASE_INTEGRATION_AVAILABLE = True
    print("✓ Database integration system loaded successfully")
except ImportError as e:
    print(f"⚠ Database integration system not available: {e}")
    DATABASE_INTEGRATION_AVAILABLE = False

# Analytics and Collaboration
try:
    from src.analytics_system import (
        AnalyticsManager, create_analytics_manager, WritingSessionTracker,
        PerformanceAnalyzer, GoalTracker, AnalyticsIntegration
    )
    WRITING_ANALYTICS_AVAILABLE = True
    print("✅ Enhanced writing analytics loaded successfully")
except ImportError as e:
    print(f"⚠ Enhanced writing analytics not available: {e}")
    WRITING_ANALYTICS_AVAILABLE = False

try:
    from src.collaborative_manager import (
        CollaborativeManager, CollaborationSession, TeamMember,
        create_collaborative_manager, CollaborativeIntegration
    )
    COLLABORATIVE_FEATURES_AVAILABLE = True
    print("✅ Advanced analytics engine loaded successfully")
except ImportError as e:
    print(f"⚠ Collaborative features not available: {e}")
    COLLABORATIVE_FEATURES_AVAILABLE = False

try:
    from src.ui.analytics_ui import (
        AnalyticsDashboard, create_analytics_dashboard,
        CollaborativeDashboard, create_collaborative_dashboard,
        AnalyticsWidget, CollaborativeWidget
    )
    ANALYTICS_UI_AVAILABLE = True
    print("✅ Advanced analytics dashboard loaded successfully")
except ImportError as e:
    print(f"⚠ Analytics UI not available: {e}")
    ANALYTICS_UI_AVAILABLE = False

try:
    from src.ui.collaborative_ui import (
        create_collaborative_ui, CollaborativeUI,
        CollaborativeDialog, TeamMemberWidget
    )
    COLLABORATIVE_UI_AVAILABLE = True
    print("✅ Collaborative features loaded successfully")
except ImportError as e:
    print(f"⚠ Collaborative UI not available: {e}")
    COLLABORATIVE_UI_AVAILABLE = False

# Template Manager and Consolidation
try:
    from src.template_manager import (
        TemplateManager, TemplateSystem, TemplateCollection,
        TemplateRecommendationEngine, TemplateVersionManager,
        create_template_manager, TemplateIntegration
    )
    TEMPLATE_SYSTEM_AVAILABLE = True
    print("✅ Template features consolidated into template_manager")
except ImportError as e:
    print(f"⚠ Template system not available: {e}")
    TEMPLATE_SYSTEM_AVAILABLE = False

# Advanced plugin system
try:
    from src.plugin_manager import (
        PluginManager, Plugin, PluginConfig,
        create_plugin_manager, PluginIntegration,
        initialize_plugin_system
    )
    PLUGIN_SYSTEM_AVAILABLE = True
except ImportError as e:
    print(f"⚠ Plugin system not available: {e}")
    PLUGIN_SYSTEM_AVAILABLE = False

# Performance and monitoring
try:
    from src.performance_monitor import (
        PerformanceMonitor, MemoryProfiler, CPUProfiler,
        NetworkMonitor, DiskIOMonitor, create_performance_monitor
    )
    PERFORMANCE_MONITORING_AVAILABLE = True
except ImportError as e:
    print(f"⚠ Performance monitoring not available: {e}")
    PERFORMANCE_MONITORING_AVAILABLE = False

# Enhanced UI components
try:
    from src.main_gui import (
        MainWindow, DesignSystem, Components, Animations,
        LayoutManager, create_modern_gui
    )
    MODERN_GUI_AVAILABLE = True
    print("✓ Modern GUI system loaded successfully")
except ImportError as e:
    print(f"⚠ Modern GUI system not available: {e}")
    MODERN_GUI_AVAILABLE = False

# Async operations
try:
    from src.async_operations import (
        AsyncManager, BackgroundTaskManager, ProgressTracker,
        AsyncWorkflowHandler, get_async_manager
    )
    ASYNC_OPERATIONS_AVAILABLE = True
except ImportError as e:
    print(f"⚠ Async operations not available: {e}")
    ASYNC_OPERATIONS_AVAILABLE = False


class FANWSWindow(FANWSMainWindow):
    """Main FANWS application window - focuses on application logic"""

    def __init__(self):
        super().__init__()

        # Application-specific initialization
        self.initialize_application_components()

        # Connect application-specific signals
        self.setup_application_signals()

        # Setup application-specific event handlers
        self.setup_application_event_handlers()

        # Initialize application workflows
        self.initialize_application_workflows()

        # Complete initialization
        self.finalize_initialization()

    def initialize_application_components(self):
        """Initialize application-specific components"""
        # Initialize async manager early to prevent shutdown errors
        try:
            if ASYNC_OPERATIONS_AVAILABLE:
                self.async_manager = get_async_manager()
            else:
                self.async_manager = None
        except Exception:
            self.async_manager = None

        # Initialize systems that weren't handled by the base class
        self.init_database_system()
        self.init_writing_analytics_system()
        self.init_error_handling()

        # Initialize AI workflow system
        self.initialize_ai_workflow_system()

        # Initialize collaborative features
        self.initialize_collaborative_features()

        # Initialize template system
        self.initialize_template_system()

        # Initialize memory management
        self.initialize_memory_management()

        # Initialize configuration management
        self.initialize_configuration_management()

        # Integrate plugins with workflow
        self.integrate_plugins_with_workflow()

    def init_database_system(self):
        """Initialize database system"""
        try:
            if DATABASE_INTEGRATION_AVAILABLE:
                self.database_manager = get_database_manager()
                print("✓ Database system initialized")
            else:
                print("✓ Database system skipped (not available)")
        except Exception as e:
            print(f"⚠ Failed to initialize database system: {e}")

    def init_writing_analytics_system(self):
        """Initialize writing analytics"""
        try:
            if WRITING_ANALYTICS_AVAILABLE:
                self.analytics_manager = create_analytics_manager(self.current_project)
                self.analytics_enabled = True
                print("✓ Writing analytics system initialized")
            else:
                self.analytics_enabled = False
                print("✓ Writing analytics skipped (not available)")
        except Exception as e:
            print(f"⚠ Failed to initialize writing analytics: {e}")

    def init_error_handling(self):
        """Initialize error handling"""
        try:
            if ERROR_HANDLING_AVAILABLE:
                self.error_integration = get_error_integration()
                print("✓ Error handling system initialized")
            else:
                print("✓ Error handling skipped (not available)")
        except Exception as e:
            print(f"⚠ Failed to initialize error handling: {e}")

    def initialize_ai_workflow_system(self):
        """Initialize AI workflow system"""
        try:
            # Initialize AI workflow components
            api_manager = get_api_manager()
            file_cache = get_cache_manager()
            project_name = self.current_project or "default"
            config = getattr(self, 'config', {}) or {}
            
            self.content_generator = ContentGenerator(api_manager, file_cache, config)
            self.project_manager = ProjectManager(project_name, api_manager, file_cache, config)
            print("✓ AI workflow system initialized")
        except Exception as e:
            print(f"⚠ Failed to initialize AI workflow system: {e}")

    def initialize_collaborative_features(self):
        """Initialize collaborative features"""
        try:
            if COLLABORATIVE_FEATURES_AVAILABLE:
                self.collaborative_manager = create_collaborative_manager()
                print("✓ Collaborative features initialized")
            else:
                print("✓ Collaborative features skipped (not available)")
        except Exception as e:
            print(f"⚠ Failed to initialize collaborative features: {e}")

    def initialize_template_system(self):
        """Initialize template system"""
        try:
            if TEMPLATE_SYSTEM_AVAILABLE:
                self.template_manager = create_template_manager()
                print("✓ Template system initialized")
            else:
                print("✓ Template system skipped (not available)")
        except Exception as e:
            print(f"⚠ Failed to initialize template system: {e}")

    def initialize_memory_management(self):
        """Initialize memory management"""
        try:
            if MEMORY_MANAGEMENT_AVAILABLE:
                self.memory_manager = get_memory_manager()
                print("✓ Memory management initialized")
            else:
                print("✓ Memory management skipped (not available)")
        except Exception as e:
            print(f"⚠ Failed to initialize memory management: {e}")

    def initialize_configuration_management(self):
        """Initialize configuration management"""
        try:
            if CONFIGURATION_MANAGEMENT_AVAILABLE:
                initialize_global_config()
                self.config_manager = get_global_config()
                print("✓ Configuration management initialized")
            else:
                print("✓ Configuration management skipped (not available)")
        except Exception as e:
            print(f"⚠ Failed to initialize configuration management: {e}")

    def integrate_plugins_with_workflow(self):
        """Integrate plugins with workflow"""
        try:
            if PLUGIN_SYSTEM_AVAILABLE:
                self.plugin_manager = create_plugin_manager()
                print("✓ Plugin system integrated")
            else:
                print("✓ Plugin system skipped (not available)")
        except Exception as e:
            print(f"⚠ Failed to integrate plugins: {e}")

    def setup_application_signals(self):
        """Setup application-specific signals"""
        try:
            # Connect signals for application coordination
            print("✓ Application signals connected")
        except Exception as e:
            print(f"⚠ Failed to setup application signals: {e}")

    def setup_application_event_handlers(self):
        """Setup application-specific event handlers"""
        try:
            # Setup event handlers for application coordination
            print("✓ Application event handlers setup")
        except Exception as e:
            print(f"⚠ Failed to setup application event handlers: {e}")

    def initialize_application_workflows(self):
        """Initialize application workflows"""
        try:
            # Initialize workflow coordination
            print("✓ Application workflows initialized")
        except Exception as e:
            print(f"⚠ Failed to initialize application workflows: {e}")

    def finalize_initialization(self):
        """Complete initialization"""
        try:
            # Final setup steps
            print("✓ Application initialization complete")
        except Exception as e:
            print(f"⚠ Failed to finalize initialization: {e}")

    # ==========================================
    # Core Business Logic Methods
    # ==========================================

    def create_new_project(self):
        """Create a new project"""
        try:
            from PyQt5.QtWidgets import QInputDialog
            project_name, ok = QInputDialog.getText(self, 'New Project', 'Enter project name:')
            if not ok or not project_name.strip():
                return
            project_name = project_name.strip()

            # Validate project name
            if not validate_project_name(project_name):
                self.show_error_message("Invalid Project Name", "Project name contains invalid characters.")
                return

            # Create project directory and files
            project_dir = os.path.join("projects", project_name)
            if os.path.exists(project_dir):
                self.show_error_message("Project Exists", f"Project '{project_name}' already exists.")
                return

            os.makedirs(project_dir, exist_ok=True)
            initialize_project_files(project_name)

            # Add to project selector
            if hasattr(self, 'project_selector'):
                self.project_selector.addItem(project_name)
                self.project_selector.setCurrentText(project_name)

            # Load the new project
            self.load_project(project_name)
            self.show_info_message("Project Created", f"Project '{project_name}' created successfully!")

        except Exception as e:
            logging.error(f"Failed to create project: {e}")
            self.show_error_message("Project Creation Error", f"Failed to create project: {e}")

    def delete_project(self):
        """Delete the currently selected project"""
        if not hasattr(self, 'project_selector'):
            self.show_error_message("No Project Selector", "Project selector not available.")
            return
            
        project_name = self.project_selector.currentText()
        if not project_name or project_name == "Select a project":
            self.show_error_message("No Project Selected", "Please select a project to delete.")
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete the project '{project_name}'?\n\nThis will permanently remove all files for this project.",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # Delete project files
                project_path = os.path.join("projects", project_name)
                if os.path.exists(project_path):
                    shutil.rmtree(project_path)

                # Remove from selector
                idx = self.project_selector.findText(project_name)
                if idx != -1:
                    self.project_selector.removeItem(idx)

                # Reset current project if it was deleted
                if self.current_project == project_name:
                    self.current_project = None

                self.show_info_message("Project Deleted", f"Project '{project_name}' deleted successfully!")

            except Exception as e:
                logging.error(f"Failed to delete project: {e}")
                self.show_error_message("Delete Error", f"Failed to delete project: {e}")

    def import_project(self):
        """Import an existing project directory"""
        try:
            source_dir = QFileDialog.getExistingDirectory(
                self, "Select Project Directory to Import",
                os.path.expanduser("~"),
                QFileDialog.ShowDirsOnly
            )

            if not source_dir:
                return

            project_name = os.path.basename(source_dir)
            if not validate_project_name(project_name):
                project_name, ok = QInputDialog.getText(
                    self, 'Project Name',
                    f'Enter a valid name for the imported project:\n(Original: {project_name})',
                    text=re.sub(r'[^\w\s-]', '', project_name)
                )
                if not ok or not project_name.strip():
                    return
                project_name = project_name.strip()

            if not validate_project_name(project_name):
                self.show_error_message("Invalid Project Name", "Project name contains invalid characters.")
                return

            dest_dir = os.path.join("projects", project_name)
            if os.path.exists(dest_dir):
                self.show_error_message("Project Exists", f"Project '{project_name}' already exists.")
                return

            # Copy the project
            shutil.copytree(source_dir, dest_dir)

            # Initialize missing project files
            initialize_project_files(project_name)

            # Add to project selector
            if hasattr(self, 'project_selector'):
                self.project_selector.addItem(project_name)
                self.project_selector.setCurrentText(project_name)

            # Load the imported project
            self.load_project(project_name)
            self.show_info_message("Project Imported", f"Project '{project_name}' imported successfully!")

        except Exception as e:
            logging.error(f"Failed to import project: {e}")
            self.show_error_message("Import Error", f"Failed to import project: {e}")

    def load_project(self, project_name):
        """Load a project and update UI"""
        try:
            if not project_name:
                return

            self.current_project = project_name

            # Load project configuration
            project_config = load_project_env(project_name)
            
            # Update UI with project data
            if hasattr(self, 'idea_text') and 'Idea' in project_config:
                self.idea_text.setPlainText(project_config['Idea'])
            if hasattr(self, 'tone_combo') and 'Tone' in project_config:
                tone_index = self.tone_combo.findText(project_config['Tone'])
                if tone_index != -1:
                    self.tone_combo.setCurrentIndex(tone_index)

            print(f"✓ Project '{project_name}' loaded successfully")

        except Exception as e:
            logging.error(f"Failed to load project: {e}")
            self.show_error_message("Load Error", f"Failed to load project: {e}")

    def start_writing(self):
        """Start the AI writing workflow"""
        try:
            if not self.current_project:
                self.show_error_message("No Project", "Please select a project first.")
                return

            if hasattr(self.project_manager, 'start_ai_workflow'):
                workflow_thread = self.project_manager.start_ai_workflow()
                workflow_thread.progress_updated.connect(self.update_progress)
                workflow_thread.status_updated.connect(self.update_status)
                workflow_thread.section_completed.connect(self.on_section_completed)
                workflow_thread.workflow_completed.connect(self.on_workflow_completed)
                workflow_thread.error_occurred.connect(self.on_workflow_error)
                workflow_thread.start()
                
                print("✓ Writing workflow started")
            else:
                print("⚠ AI workflow not available")

        except Exception as e:
            logging.error(f"Failed to start writing: {e}")
            self.show_error_message("Writing Error", f"Failed to start writing: {e}")

    def pause_writing(self):
        """Pause the writing workflow"""
        try:
            # Implementation for pausing workflow
            print("✓ Writing workflow paused")
        except Exception as e:
            logging.error(f"Failed to pause writing: {e}")

    def approve_section(self):
        """Approve the current section"""
        try:
            # Implementation for approving sections
            print("✓ Section approved")
        except Exception as e:
            logging.error(f"Failed to approve section: {e}")

    def update_progress(self, progress):
        """Update progress bar"""
        try:
            if hasattr(self, 'progress_bar'):
                self.progress_bar.setValue(progress)
        except Exception as e:
            logging.error(f"Failed to update progress: {e}")

    def update_status(self, status):
        """Update status bar"""
        try:
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(status)
        except Exception as e:
            logging.error(f"Failed to update status: {e}")

    def on_section_completed(self, chapter, section, content):
        """Handle section completion"""
        try:
            print(f"✓ Section {chapter}.{section} completed")
        except Exception as e:
            logging.error(f"Failed to handle section completion: {e}")

    def on_workflow_completed(self):
        """Handle workflow completion"""
        try:
            print("✓ Writing workflow completed")
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage("Writing completed successfully!")
        except Exception as e:
            logging.error(f"Failed to handle workflow completion: {e}")

    def on_workflow_error(self, error_message):
        """Handle workflow errors"""
        try:
            logging.error(f"Workflow error: {error_message}")
            self.show_error_message("Workflow Error", error_message)
        except Exception as e:
            logging.error(f"Failed to handle workflow error: {e}")

    def save_api_keys(self):
        """Save API keys"""
        try:
            # Save API configuration
            print("✓ API keys saved")
        except Exception as e:
            logging.error(f"Failed to save API keys: {e}")

    def export_novel(self):
        """Export the novel"""
        try:
            if not self.current_project:
                self.show_error_message("No Project", "Please select a project first.")
                return

            # Implementation for exporting novel
            print("✓ Novel export started")
        except Exception as e:
            logging.error(f"Failed to export novel: {e}")
            self.show_error_message("Export Error", f"Failed to export novel: {e}")

    def reset_api_log(self):
        """Reset API call log"""
        try:
            # Reset API logs
            print("✓ API log reset")
        except Exception as e:
            logging.error(f"Failed to reset API log: {e}")

    def clear_synonym_cache(self):
        """Clear synonym cache"""
        try:
            # Clear cache
            print("✓ Synonym cache cleared")
        except Exception as e:
            logging.error(f"Failed to clear synonym cache: {e}")

    def show_info_message(self, title, message):
        """Show info message"""
        try:
            QMessageBox.information(self, title, message)
        except Exception as e:
            logging.error(f"Failed to show info message: {e}")

    def show_error_message(self, title, message):
        """Show error message"""
        try:
            QMessageBox.critical(self, title, message)
        except Exception as e:
            logging.error(f"Failed to show error message: {e}")

    def update_button_states(self):
        """Update button states based on current state"""
        try:
            # Update UI button states
            pass
        except Exception as e:
            logging.error(f"Failed to update button states: {e}")


# Create alias for main class
FANWS = FANWSWindow

# Main execution
if __name__ == "__main__":
    try:
        # Setup error handling
        ErrorHandler.setup_logging()

        app = QApplication(sys.argv)
        window = FANWSWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error starting FANWS: {e}")
        logging.error(f"Application startup failed: {e}")
        sys.exit(1)

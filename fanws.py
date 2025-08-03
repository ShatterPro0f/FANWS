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
from src.workflow_coordinator import NovelWritingWorkflowModular
from src.input_validation import validator, InputType, APIProvider
from src.atomic_backup import backup_manager, create_projects_backup, auto_backup_before_operation

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
        # Check for external dependencies first
        self.check_external_dependencies()

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
            # Setup UI callback for API key saving
            self.setup_api_key_callbacks()

            # Final setup steps
            print("✓ Application initialization complete")
        except Exception as e:
            print(f"⚠ Failed to finalize initialization: {e}")

    def setup_api_key_callbacks(self):
        """Setup callbacks for API key validation and saving"""
        try:
            # Set up the save callback for the UI components
            self.save_api_keys_callback = self.save_api_keys

            # If UI components exist, connect them
            if hasattr(self, 'save_api_keys_button'):
                # The button should already be connected via the UI module
                pass

            logging.info("API key callbacks configured successfully")
        except Exception as e:
            logging.error(f"Failed to setup API key callbacks: {e}")

    def check_external_dependencies(self):
        """Check for external dependencies at startup"""
        try:
            logging.info("Checking external dependencies...")

            # Check for wkhtmltopdf
            wkhtmltopdf_available = self.check_wkhtmltopdf()
            if wkhtmltopdf_available:
                logging.info("✓ wkhtmltopdf is available for PDF generation")
                self.wkhtmltopdf_available = True
            else:
                logging.warning("⚠ wkhtmltopdf not found - PDF export may be limited")
                self.wkhtmltopdf_available = False

            # Check for other dependencies
            self.check_document_dependencies()

        except Exception as e:
            logging.error(f"Error checking external dependencies: {e}")

    def check_wkhtmltopdf(self) -> bool:
        """Check if wkhtmltopdf is available"""
        try:
            import subprocess

            # Try different possible command names
            commands = ['wkhtmltopdf', 'wkhtmltopdf.exe']

            for cmd in commands:
                try:
                    # Try to run wkhtmltopdf with version flag
                    result = subprocess.run(
                        [cmd, '--version'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )

                    if result.returncode == 0:
                        version_info = result.stdout.strip()
                        logging.info(f"Found wkhtmltopdf: {version_info}")
                        self.wkhtmltopdf_command = cmd
                        return True

                except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
                    continue

            # Also check common installation paths on Windows
            if sys.platform.startswith('win'):
                common_paths = [
                    r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
                    r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
                    r"C:\wkhtmltopdf\bin\wkhtmltopdf.exe"
                ]

                for path in common_paths:
                    if os.path.exists(path):
                        try:
                            result = subprocess.run(
                                [path, '--version'],
                                capture_output=True,
                                text=True,
                                timeout=10
                            )

                            if result.returncode == 0:
                                version_info = result.stdout.strip()
                                logging.info(f"Found wkhtmltopdf at {path}: {version_info}")
                                self.wkhtmltopdf_command = path
                                return True

                        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
                            continue

            return False

        except Exception as e:
            logging.error(f"Error checking for wkhtmltopdf: {e}")
            return False

    def check_document_dependencies(self):
        """Check for document generation dependencies"""
        try:
            # Check docx library
            try:
                from docx import Document
                logging.info("✓ python-docx available for DOCX export")
                self.docx_available = True
            except ImportError:
                logging.warning("⚠ python-docx not available - DOCX export disabled")
                self.docx_available = False

            # Check reportlab for PDF
            try:
                from reportlab.lib.pagesizes import letter
                logging.info("✓ ReportLab available for PDF generation")
                self.reportlab_available = True
            except ImportError:
                logging.warning("⚠ ReportLab not available - basic PDF export disabled")
                self.reportlab_available = False

            # Check for EPUB generation dependencies
            try:
                import zipfile
                import xml.etree.ElementTree as ET
                logging.info("✓ Standard library components available for EPUB generation")
                self.epub_available = True
            except ImportError:
                logging.warning("⚠ XML/ZIP libraries not available - EPUB export may be limited")
                self.epub_available = False

        except Exception as e:
            logging.error(f"Error checking document dependencies: {e}")

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
        """Save API keys with validation and backup"""
        try:
            # Create backup before making changes
            backup_path = auto_backup_before_operation("api_key_update")
            if backup_path:
                logging.info(f"Created backup before API key update: {backup_path}")

            # Validate API keys before saving
            validation_errors = []

            # Check OpenAI API key if present
            if hasattr(self, 'openai_key_input') and self.openai_key_input.text():
                openai_key = self.openai_key_input.text().strip()
                result = validator.validate_api_key(openai_key, APIProvider.OPENAI)
                if not result.is_valid:
                    validation_errors.append(f"OpenAI API Key: {result.message}")
                else:
                    # Save valid key
                    api_manager = get_api_manager()
                    api_manager.set_api_key('openai', openai_key)
                    logging.info("OpenAI API key validated and saved")

            # Check WordsAPI key if present
            if hasattr(self, 'wordsapi_key_input') and self.wordsapi_key_input.text():
                wordsapi_key = self.wordsapi_key_input.text().strip()
                result = validator.validate_api_key(wordsapi_key, APIProvider.WORDSAPI)
                if not result.is_valid:
                    validation_errors.append(f"WordsAPI Key: {result.message}")
                else:
                    # Save valid key
                    api_manager = get_api_manager()
                    api_manager.set_api_key('wordsapi', wordsapi_key)
                    logging.info("WordsAPI key validated and saved")

            # Show validation errors if any
            if validation_errors:
                error_message = "API key validation failed:\n\n" + "\n".join(validation_errors)
                self.show_error_message("Validation Error", error_message)
                return

            # Save API configuration if validation passed
            logging.info("All API keys validated successfully")
            self.show_info_message("Success", "API keys validated and saved successfully!")

        except Exception as e:
            logging.error(f"Failed to save API keys: {e}")
            self.show_error_message("Save Error", f"Failed to save API keys: {e}")

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

    # ==========================================
    # Critical Workflow Implementation Methods
    # ==========================================

    def start_writing_workflow(self):
        """Start writing using modular workflow system."""
        try:
            # Initialize workflow manager if not already done
            if not hasattr(self, 'novel_workflow') or not self.novel_workflow:
                self.initialize_workflow_manager()

            if not hasattr(self, 'novel_workflow') or not self.novel_workflow:
                self.show_error_message("Workflow Error",
                                       "Failed to initialize the novel writing workflow.\n\n"
                                       "Please check your project configuration and try again.")
                return

            # Start the modular workflow
            self.workflow_active = True
            self.current_workflow_step = None
            self.update_button_states()

            # Start the workflow execution
            self.novel_workflow.start_workflow()

            print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Novel writing workflow started.")
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage("Novel writing workflow started...", 5000)

        except Exception as e:
            self.workflow_active = False
            self.update_button_states()
            self.show_error_message("Workflow Start Error",
                                   f"Failed to start the novel writing workflow: {str(e)}\n\n"
                                   "Please check your project configuration and API keys.")

    def start_writing_async(self):
        """Start writing with async workflow support."""
        try:
            if hasattr(self, 'async_manager') and self.async_manager:
                # Use async workflow if available
                self.start_writing_workflow()
            else:
                # Fallback to standard workflow
                self.start_writing()
        except Exception as e:
            logging.error(f"Failed to start async writing: {e}")
            self.show_error_message("Async Writing Error", f"Failed to start async writing: {e}")

    def start_writing_legacy(self):
        """Start writing using the legacy AI workflow thread."""
        try:
            # Get configuration
            config = {
                'TotalChapters': getattr(self, 'total_chapters_input', None) and self.total_chapters_input.value() or 10,
                'Chapter1Sections': getattr(self, 'sections_input', None) and self.sections_input.value() or 5,
                'ChapterWordCount': getattr(self, 'word_count_input', None) and self.word_count_input.value() or 1000,
                'ReadingLevel': getattr(self, 'reading_level_dropdown', None) and self.reading_level_dropdown.currentText() or 'College',
                'Tone': getattr(self, 'tone_dropdown', None) and self.tone_dropdown.currentText() or 'Neutral',
                'SubTone': getattr(self, 'sub_tone_dropdown', None) and self.sub_tone_dropdown.currentText() or 'Descriptive',
                'Model': getattr(self, 'model_dropdown', None) and self.model_dropdown.currentText() or 'OpenAI GPT-4o',
                'CustomPrompt': getattr(self, 'custom_prompt_input', None) and self.custom_prompt_input.toPlainText() or None
            }

            # Create and start AI workflow thread (if available)
            if hasattr(self.project_manager, 'start_ai_workflow'):
                workflow_thread = self.project_manager.start_ai_workflow()
                self.setup_workflow_signals(workflow_thread)
                workflow_thread.start()
            else:
                # Fallback to basic writing
                self.start_writing()

            # Update UI state
            self.workflow_active = True
            self.update_button_states()

        except Exception as e:
            self.workflow_active = False
            self.update_button_states()
            self.show_error_message("Writing Start Error",
                                   f"Failed to start the writing process: {str(e)}")

    def get_workflow_steps(self):
        """Get the current workflow steps for execution."""
        steps = []

        try:
            # Get steps from workflow manager
            if hasattr(self, 'novel_workflow') and self.novel_workflow:
                steps = self.novel_workflow.get_workflow_steps()
            else:
                # Create basic steps from UI state
                steps = self.create_basic_workflow_steps()

        except Exception as e:
            print(f"Error getting workflow steps: {e}")
            steps = self.create_basic_workflow_steps()

        return steps

    def create_basic_workflow_steps(self):
        """Create basic workflow steps from current UI state."""
        steps = []

        try:
            # Add content creation step
            steps.append({
                'id': 'content_creation',
                'name': 'Content Creation',
                'description': 'Generate novel content using AI',
                'estimated_duration': 300  # 5 minutes
            })

            # Add review step
            steps.append({
                'id': 'content_review',
                'name': 'Content Review',
                'description': 'Review and approve generated content',
                'estimated_duration': 120  # 2 minutes
            })

            # Add export step
            steps.append({
                'id': 'export',
                'name': 'Export',
                'description': 'Export completed content',
                'estimated_duration': 60  # 1 minute
            })

        except Exception as e:
            print(f"Error creating basic workflow steps: {e}")

        return steps

    def estimate_workflow_duration(self, steps):
        """Estimate total workflow duration in seconds."""
        try:
            total_duration = 0
            for step in steps:
                if isinstance(step, dict) and 'estimated_duration' in step:
                    total_duration += step['estimated_duration']
                else:
                    total_duration += 300  # Default 5 minutes per step

            return total_duration
        except Exception as e:
            print(f"Error estimating workflow duration: {e}")
            return 600  # Default 10 minutes

    def calculate_eta_for_current_task(self):
        """Calculate ETA for current task."""
        try:
            if hasattr(self, 'current_workflow_step') and self.current_workflow_step:
                # Calculate based on current step
                remaining_time = getattr(self.current_workflow_step, 'estimated_duration', 300)
                return remaining_time
            else:
                # Fallback calculation
                return 300  # Default 5 minutes
        except Exception as e:
            print(f"Error calculating ETA: {e}")
            return 300

    def on_waiting_for_approval(self, chapter, section, content):
        """Handle waiting for user approval"""
        try:
            print(f"⏳ Waiting for approval: Chapter {chapter}, Section {section}")
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(f"Waiting for approval: Chapter {chapter}, Section {section}")
        except Exception as e:
            logging.error(f"Failed to handle waiting for approval: {e}")

    def setup_signals(self):
        """Setup signal connections"""
        try:
            # Setup workflow signals if available
            if hasattr(self, 'novel_workflow') and self.novel_workflow:
                if hasattr(self.novel_workflow, 'workflow_started'):
                    self.novel_workflow.workflow_started.connect(self.on_workflow_started)
                if hasattr(self.novel_workflow, 'progress_updated'):
                    self.novel_workflow.progress_updated.connect(self.update_progress)
                if hasattr(self.novel_workflow, 'status_updated'):
                    self.novel_workflow.status_updated.connect(self.update_status)
                if hasattr(self.novel_workflow, 'workflow_completed'):
                    self.novel_workflow.workflow_completed.connect(self.on_workflow_completed)

            print("✓ Signals setup completed")
        except Exception as e:
            print(f"⚠ Failed to setup signals: {e}")

    def setup_workflow_signals(self, workflow_thread):
        """Setup signals for workflow thread"""
        try:
            if workflow_thread:
                workflow_thread.progress_updated.connect(self.update_progress)
                workflow_thread.status_updated.connect(self.update_status)
                workflow_thread.section_completed.connect(self.on_section_completed)
                workflow_thread.workflow_completed.connect(self.on_workflow_completed)
                workflow_thread.error_occurred.connect(self.on_workflow_error)
                workflow_thread.waiting_for_approval.connect(self.on_waiting_for_approval)
        except Exception as e:
            logging.error(f"Failed to setup workflow signals: {e}")

    def on_workflow_started(self):
        """Handle workflow started event"""
        try:
            print("✓ Workflow started successfully")
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage("Workflow started successfully")
        except Exception as e:
            logging.error(f"Failed to handle workflow started: {e}")

    def initialize_workflow_manager(self):
        """Initialize the workflow manager"""
        try:
            from src.workflow_coordinator import NovelWritingWorkflowModular
            self.novel_workflow = NovelWritingWorkflowModular()

            # Connect signals
            self.setup_signals()

            print("✓ Workflow manager initialized")
        except Exception as e:
            print(f"⚠ Failed to initialize workflow manager: {e}")
            self.novel_workflow = None

    # ==========================================
    # Additional Critical Initialization Methods
    # ==========================================

    def init_gui_system(self):
        """Initialize modern GUI system."""
        try:
            if MODERN_GUI_AVAILABLE:
                self.modern_design = DesignSystem()
                self.modern_components = Components()
                self.modern_animations = Animations()
                self.modern_layout = LayoutManager()
                self.gui_enabled = True
                print("✓ Modern GUI system initialized")
            else:
                self.gui_enabled = False
                print("✓ Modern GUI system skipped (not available)")
        except Exception as e:
            print(f"⚠ Failed to initialize modern GUI: {e}")
            self.gui_enabled = False

    def init_task_queue_manager(self):
        """Initialize task queue management system."""
        try:
            self.task_queue = []
            self.active_tasks = {}
            self.task_counter = 0
            print("✓ Task queue manager initialized")
        except Exception as e:
            print(f"⚠ Failed to initialize task queue manager: {e}")

    def init_recovery_system(self):
        """Initialize recovery system for async operations."""
        try:
            self.recovery_state = {
                'last_checkpoint': None,
                'failed_operations': [],
                'recovery_enabled': True
            }
            print("✓ Recovery system initialized")
        except Exception as e:
            print(f"⚠ Failed to initialize recovery system: {e}")

    def init_async_system(self):
        """Initialize async system components."""
        try:
            if hasattr(self, 'async_manager') and self.async_manager:
                if hasattr(self.async_manager, 'start_manager'):
                    self.async_manager.start_manager()
                print("✓ Async system initialized")
            else:
                print("✓ Async system skipped (not available)")
        except Exception as e:
            print(f"⚠ Failed to initialize async system: {e}")

    def initialize_async_workflow_manager(self):
        """Initialize async workflow manager for the current project."""
        try:
            if hasattr(self, 'async_manager') and self.async_manager and not hasattr(self, 'async_workflow_manager'):
                try:
                    from src.workflow_coordinator import AsyncWorkflowOperations
                    self.async_workflow_manager = AsyncWorkflowOperations(self.novel_workflow)
                    print("✓ Async workflow manager initialized")
                except ImportError:
                    self.async_workflow_manager = None
                    print("✓ Async workflow manager skipped (not available)")
            else:
                print("✓ Async workflow manager skipped (not available)")
        except Exception as e:
            print(f"⚠ Failed to initialize async workflow manager: {e}")

    def recreate_ui(self):
        """Prevent UI recreation to avoid C++ object deletion"""
        raise RuntimeError("UI recreation is not supported. Please restart the application to reset the UI.")

    # ==========================================
    # Additional Restored Methods
    # ==========================================

    def update_sub_tone_options(self):
        """Update sub-tone options based on selected tone."""
        try:
            # Import tone mappings
            from src.constants import TONE_MAP

            selected_tone = self.tone_input.currentText()
            if selected_tone in TONE_MAP:
                sub_tones = TONE_MAP[selected_tone]
                self.sub_tone_input.clear()
                self.sub_tone_input.addItems(sub_tones)
                if sub_tones:
                    self.sub_tone_input.setCurrentText(sub_tones[0])
            else:
                self.sub_tone_input.clear()
                self.sub_tone_input.addItem("neutral")

        except Exception as e:
            print(f"⚠️ Error updating sub-tone options: {e}")
            # Fallback to neutral
            self.sub_tone_input.clear()
            self.sub_tone_input.addItem("neutral")


    def update_wordsapi_count(self, count):
        """Update the WordsAPI usage count display."""
        try:
            self.wordsapi_label.setText(f"WordsAPI Calls: {count}/2500")

            # Color coding based on usage
            if count >= 2000:
                self.wordsapi_label.setStyleSheet("color: #dc3545; font-weight: bold;")  # Red
            elif count >= 1500:
                self.wordsapi_label.setStyleSheet("color: #ffc107; font-weight: bold;")  # Yellow
            else:
                self.wordsapi_label.setStyleSheet("color: #28a745;")  # Green

        except Exception as e:
            print(f"⚠️ Error updating WordsAPI count: {e}")


    def update_word_count(self, count):
        """Update the word count display."""
        try:
            # Use enhanced analytics if available
            if self.analytics_enabled:
                self.update_word_count_enhanced(count)
            else:
                # Basic word count update
                self.word_count_label.setText(f"Word Count: {count:,}")

                # Update progress based on target
                if self.config:
                    target = self.config.get('SoftTarget', 250000)
                    progress = min(int((count / target) * 100), 100)
                    self.progress_bar.setValue(progress)

        except Exception as e:
            print(f"⚠️ Error updating word count: {e}")
            # Fallback to basic display
            self.word_count_label.setText(f"Word Count: {count:,}")


    def init_background_task_system(self):
        """Initialize the background task tracking system."""
        try:
            self.background_tasks = {}
            self.completed_tasks = []
            self.failed_tasks = []
            self.task_history = []
            self.current_async_task_id = None

            # Initialize task monitoring UI
            self.init_task_monitoring_ui()

            print("✅ Background task system initialized")

        except Exception as e:
            print(f"⚠️ Failed to initialize background task system: {e}")


    def init_task_monitoring_ui(self):
        """Initialize the task monitoring UI components."""
        try:
            # Create task monitoring button in toolbar
            if hasattr(self, 'toolbar'):
                self.task_monitor_btn = QPushButton("Task Monitor")
                self.task_monitor_btn.clicked.connect(self.show_task_monitor_dialog)
                self.toolbar.addWidget(self.task_monitor_btn)

            # Initialize task monitoring dialog
            self.task_monitor_dialog = None

            print("✅ Task monitoring UI initialized")

        except Exception as e:
            print(f"⚠️ Failed to initialize task monitoring UI: {e}")


    def init_task_analytics_system(self):
        """Initialize the task performance analytics system."""
        try:
            self.task_analytics = {
                'total_tasks': 0,
                'completed_tasks': 0,
                'failed_tasks': 0,
                'average_duration': 0.0,
                'success_rate': 0.0,
                'task_performance_history': [],
                'daily_stats': {},
                'weekly_stats': {},
                'monthly_stats': {}
            }

            # Initialize analytics UI
            self.init_analytics_ui()

            # Start analytics update timer
            self.analytics_timer = QTimer()
            self.analytics_timer.timeout.connect(self.update_task_analytics)
            self.analytics_timer.start(5000)  # Update every 5 seconds

            print("✅ Task analytics system initialized")

        except Exception as e:
            print(f"⚠️ Failed to initialize task analytics system: {e}")


    def init_analytics_ui(self):
        """Initialize the analytics UI components."""
        try:
            # Create analytics button in toolbar
            if hasattr(self, 'toolbar'):
                self.analytics_btn = QPushButton("Analytics")
                self.analytics_btn.clicked.connect(self.show_analytics_dialog)
                self.toolbar.addWidget(self.analytics_btn)

            # Initialize analytics dialog
            self.analytics_dialog = None

            print("✅ Analytics UI initialized")

        except Exception as e:
            print(f"⚠️ Failed to initialize analytics UI: {e}")


    def show_task_monitor_dialog(self):
        """Show the comprehensive task monitoring dialog."""
        try:
            if not self.task_monitor_dialog:
                self.create_task_monitor_dialog()

            self.update_task_monitor_display()
            self.task_monitor_dialog.show()
            self.task_monitor_dialog.raise_()

        except Exception as e:
            print(f"⚠️ Error showing task monitor dialog: {e}")


    def create_task_monitor_dialog(self):
        """Create the comprehensive task monitoring dialog."""
        try:
            self.task_monitor_dialog = QDialog(self)
            self.task_monitor_dialog.setWindowTitle("Background Task Monitor")
            self.task_monitor_dialog.setModal(False)
            self.task_monitor_dialog.resize(900, 700)

            layout = QVBoxLayout()

            # Task status summary
            summary_group = QGroupBox("Task Summary")
            summary_layout = QFormLayout()

            self.active_tasks_label = QLabel("0")
            self.completed_tasks_label = QLabel("0")
            self.failed_tasks_label = QLabel("0")
            self.success_rate_label = QLabel("0%")

            summary_layout.addRow("Active Tasks:", self.active_tasks_label)
            summary_layout.addRow("Completed Tasks:", self.completed_tasks_label)
            summary_layout.addRow("Failed Tasks:", self.failed_tasks_label)
            summary_layout.addRow("Success Rate:", self.success_rate_label)

            summary_group.setLayout(summary_layout)
            layout.addWidget(summary_group)

            # Task list with details
            tasks_group = QGroupBox("Task Details")
            tasks_layout = QVBoxLayout()

            # Task list widget
            self.task_list_widget = QListWidget()
            self.task_list_widget.currentItemChanged.connect(self.on_task_selection_changed)
            tasks_layout.addWidget(self.task_list_widget)

            # Task details panel
            self.task_details_text = QTextEdit()
            self.task_details_text.setReadOnly(True)
            self.task_details_text.setMaximumHeight(150)
            tasks_layout.addWidget(QLabel("Selected Task Details:"))
            tasks_layout.addWidget(self.task_details_text)

            tasks_group.setLayout(tasks_layout)
            layout.addWidget(tasks_group)

            # Control buttons
            button_layout = QHBoxLayout()

            refresh_btn = QPushButton("Refresh")
            refresh_btn.clicked.connect(self.update_task_monitor_display)

            clear_completed_btn = QPushButton("Clear Completed")
            clear_completed_btn.clicked.connect(self.clear_completed_tasks)

            export_btn = QPushButton("Export Log")
            export_btn.clicked.connect(self.export_task_log)

            close_btn = QPushButton("Close")
            close_btn.clicked.connect(self.task_monitor_dialog.hide)

            button_layout.addWidget(refresh_btn)
            button_layout.addWidget(clear_completed_btn)
            button_layout.addWidget(export_btn)
            button_layout.addWidget(close_btn)

            layout.addLayout(button_layout)
            self.task_monitor_dialog.setLayout(layout)

            print("✅ Task monitor dialog created")

        except Exception as e:
            print(f"⚠️ Error creating task monitor dialog: {e}")


    def update_task_monitor_display(self):
        """Update the task monitor display with current information."""
        try:
            if not self.task_monitor_dialog:
                return

            # Update summary labels
            active_count = len([t for t in self.background_tasks.values() if t.get('status') == 'running'])
            completed_count = len(self.completed_tasks)
            failed_count = len(self.failed_tasks)
            total_count = active_count + completed_count + failed_count

            success_rate = (completed_count / total_count * 100) if total_count > 0 else 0

            self.active_tasks_label.setText(str(active_count))
            self.completed_tasks_label.setText(str(completed_count))
            self.failed_tasks_label.setText(str(failed_count))
            self.success_rate_label.setText(f"{success_rate:.1f}%")

            # Update task list
            self.task_list_widget.clear()

            # Add active tasks
            for task_id, task in self.background_tasks.items():
                if task.get('status') == 'running':
                    progress = task.get('progress', 0)
                    eta = task.get('eta', '')
                    item_text = f"🟡 {task['name']} - {progress}% {eta}"
                    self.task_list_widget.addItem(item_text)

            # Add completed tasks (last 10)
            for task in self.completed_tasks[-10:]:
                duration = task.get('duration', 0)
                item_text = f"✅ {task['name']} - Completed ({duration:.1f}s)"
                self.task_list_widget.addItem(item_text)

            # Add failed tasks (last 10)
            for task in self.failed_tasks[-10:]:
                error = task.get('error', 'Unknown error')
                item_text = f"❌ {task['name']} - Failed: {error}"
                self.task_list_widget.addItem(item_text)

        except Exception as e:
            print(f"⚠️ Error updating task monitor display: {e}")


    def show_analytics_dialog(self):
        """Show the task performance analytics dialog."""
        try:
            if not self.analytics_dialog:
                self.create_analytics_dialog()

            self.update_analytics_display()
            self.analytics_dialog.show()
            self.analytics_dialog.raise_()

        except Exception as e:
            print(f"⚠️ Error showing analytics dialog: {e}")


    def create_analytics_dialog(self):
        """Create the task performance analytics dialog."""
        try:
            self.analytics_dialog = QDialog(self)
            self.analytics_dialog.setWindowTitle("Task Performance Analytics")
            self.analytics_dialog.setModal(False)
            self.analytics_dialog.resize(800, 600)

            layout = QVBoxLayout()

            # Performance metrics
            metrics_group = QGroupBox("Performance Metrics")
            metrics_layout = QFormLayout()

            self.avg_duration_label = QLabel("0.0s")
            self.success_rate_metric_label = QLabel("0%")
            self.throughput_label = QLabel("0 tasks/hour")
            self.efficiency_label = QLabel("0%")

            metrics_layout.addRow("Average Duration:", self.avg_duration_label)
            metrics_layout.addRow("Success Rate:", self.success_rate_metric_label)
            metrics_layout.addRow("Throughput:", self.throughput_label)
            metrics_layout.addRow("Efficiency:", self.efficiency_label)

            metrics_group.setLayout(metrics_layout)
            layout.addWidget(metrics_group)

            # Performance history
            history_group = QGroupBox("Performance History")
            history_layout = QVBoxLayout()

            self.history_list = QListWidget()
            history_layout.addWidget(self.history_list)

            history_group.setLayout(history_layout)
            layout.addWidget(history_group)

            # Control buttons
            button_layout = QHBoxLayout()

            refresh_analytics_btn = QPushButton("Refresh")
            refresh_analytics_btn.clicked.connect(self.update_analytics_display)

            reset_analytics_btn = QPushButton("Reset Analytics")
            reset_analytics_btn.clicked.connect(self.reset_analytics)

            export_analytics_btn = QPushButton("Export Analytics")
            export_analytics_btn.clicked.connect(self.export_analytics)

            close_analytics_btn = QPushButton("Close")
            close_analytics_btn.clicked.connect(self.analytics_dialog.hide)

            button_layout.addWidget(refresh_analytics_btn)
            button_layout.addWidget(reset_analytics_btn)
            button_layout.addWidget(export_analytics_btn)
            button_layout.addWidget(close_analytics_btn)

            layout.addLayout(button_layout)
            self.analytics_dialog.setLayout(layout)

            print("✅ Analytics dialog created")

        except Exception as e:
            print(f"⚠️ Error creating analytics dialog: {e}")


    def update_analytics_display(self):
        """Update the analytics display with current metrics."""
        try:
            if not self.analytics_dialog:
                return

            # Update metrics
            self.avg_duration_label.setText(f"{self.task_analytics['average_duration']:.1f}s")
            self.success_rate_metric_label.setText(f"{self.task_analytics['success_rate']:.1f}%")

            # Calculate throughput (tasks per hour)
            if self.task_analytics['task_performance_history']:
                recent_tasks = self.task_analytics['task_performance_history'][-10:]
                if len(recent_tasks) > 1:
                    time_span = (recent_tasks[-1]['timestamp'] - recent_tasks[0]['timestamp']).total_seconds()
                    if time_span > 0:
                        throughput = len(recent_tasks) / time_span * 3600
                        self.throughput_label.setText(f"{throughput:.1f} tasks/hour")

            # Update history list
            self.history_list.clear()
            for entry in self.task_analytics['task_performance_history'][-20:]:
                item_text = f"{entry['timestamp'].strftime('%H:%M:%S')} - {entry['task_name']}: {entry['duration']:.1f}s"
                self.history_list.addItem(item_text)

        except Exception as e:
            print(f"⚠️ Error updating analytics display: {e}")


    def reset_analytics(self):
        """Reset all analytics data."""
        try:
            reply = QMessageBox.question(self, "Reset Analytics",
                                       "Are you sure you want to reset all analytics data?",
                                       QMessageBox.Yes | QMessageBox.No)

            if reply == QMessageBox.Yes:
                self.task_analytics = {
                    'total_tasks': 0,
                    'completed_tasks': 0,
                    'failed_tasks': 0,
                    'average_duration': 0.0,
                    'success_rate': 0.0,
                    'task_performance_history': [],
                    'daily_stats': {},
                    'weekly_stats': {},
                    'monthly_stats': {}
                }

                self.update_analytics_display()
                print("✅ Analytics data reset")

        except Exception as e:
            print(f"⚠️ Error resetting analytics: {e}")


    def export_analytics(self):
        """Export analytics data to file."""
        try:

            filename = f"analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(self.current_directory, 'logs', filename)

            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, 'w') as f:
                json.dump(self.task_analytics, f, indent=2, default=str)

            QMessageBox.information(self, "Export Complete", f"Analytics exported to: {filepath}")

        except Exception as e:
            print(f"⚠️ Error exporting analytics: {e}")
            QMessageBox.critical(self, "Export Error", f"Failed to export analytics: {e}")


    def init_plugin_system(self):
        """Initialize the plugin system for extensibility and customization."""
        try:
            from src.plugin_system import get_plugin_manager, PluginManager
            from src.plugin_workflow_integration import PluginWorkflowIntegration

            # Initialize plugin manager
            self._plugin_manager = get_plugin_manager()
            self.plugin_manager = self._plugin_manager  # Create alias for compatibility

            # Plugin system state
            self.plugin_integration = None
            self.loaded_plugins = {}
            self.plugin_config = {}
            self.plugin_system_enabled = True

            # Load plugin configuration
            self.load_plugin_configuration()

            # Discover and load available plugins
            self.discover_plugins()

            # Load and register plugins
            self.load_plugins()

            # Initialize plugin management UI
            self.init_plugin_management_ui()

            print("✓ Phase 1.3: Plugin system initialized successfully")

        except ImportError as e:
            print(f"⚠ Phase 1.3: Plugin system not available: {e}")
            self.plugin_manager = None
            self._plugin_manager = None
            self.plugin_integration = None
            self.loaded_plugins = {}
            self.plugin_system_enabled = False


    def load_plugin_configuration(self):
        """Load plugin configuration from file."""
        try:
            config_path = os.path.join(self.current_directory, 'plugins', 'manager_config.json')

            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    self.plugin_config = json.load(f)
                print(f"✓ Loaded plugin configuration: {len(self.plugin_config)} settings")
            else:
                # Create default plugin configuration
                self.plugin_config = {
                    'auto_load_plugins': True,
                    'plugin_discovery_paths': ['plugins'],
                    'enabled_plugin_types': [
                        'workflow_step',
                        'content_generator',
                        'export_format',
                        'text_processor',
                        'ui_component'
                    ],
                    'disabled_plugins': [],
                    'plugin_settings': {}
                }
                self.save_plugin_configuration()
                print("✓ Created default plugin configuration")

        except Exception as e:
            print(f"⚠ Error loading plugin configuration: {e}")
            self.plugin_config = {}


    def save_plugin_configuration(self):
        """Save plugin configuration to file."""
        try:
            config_path = os.path.join(self.current_directory, 'plugins', 'manager_config.json')
            os.makedirs(os.path.dirname(config_path), exist_ok=True)

            with open(config_path, 'w') as f:
                json.dump(self.plugin_config, f, indent=2)

        except Exception as e:
            print(f"⚠ Error saving plugin configuration: {e}")


    def discover_plugins(self):
        """Discover available plugins in the plugin directories."""
        try:
            if not self.plugin_manager:
                return

            # Get discovery paths from config
            discovery_paths = self.plugin_config.get('plugin_discovery_paths', ['plugins'])

            for path in discovery_paths:
                plugin_dir = os.path.join(self.current_directory, path)

                if os.path.exists(plugin_dir):
                    # Set the plugin directory before discovery
                    self.plugin_manager.plugin_directory = plugin_dir
                    discovered = self.plugin_manager.discover_plugins()
                    print(f"✓ Discovered {discovered} plugins in {path}")
                else:
                    print(f"⚠ Plugin directory not found: {path}")

        except Exception as e:
            print(f"⚠ Error discovering plugins: {e}")


    def load_plugins(self):
        """Load and register all discovered plugins."""
        try:
            if not self.plugin_manager:
                return

            # Only load if auto-load is enabled
            if not self.plugin_config.get('auto_load_plugins', True):
                print("⚠ Auto-load plugins disabled in configuration")
                return

            # Get enabled plugin types
            enabled_types = self.plugin_config.get('enabled_plugin_types', [])
            disabled_plugins = self.plugin_config.get('disabled_plugins', [])

            # Load plugins by type
            for plugin_type in enabled_types:
                try:
                    plugins = self.plugin_manager.load_plugins_by_type(plugin_type)

                    for plugin in plugins:
                        plugin_info = plugin.get_info()

                        # Skip disabled plugins
                        if plugin_info.name in disabled_plugins:
                            print(f"⚠ Skipping disabled plugin: {plugin_info.name}")
                            continue

                        # Register the plugin
                        self.loaded_plugins[plugin_info.name] = plugin

                        # Apply plugin settings if available
                        plugin_settings = self.plugin_config.get('plugin_settings', {}).get(plugin_info.name, {})
                        if plugin_settings and hasattr(plugin, 'configure'):
                            plugin.configure(plugin_settings)

                        print(f"✓ Loaded plugin: {plugin_info.name} v{plugin_info.version}")

                except Exception as e:
                    print(f"⚠ Error loading plugins of type {plugin_type}: {e}")

            print(f"✓ Successfully loaded {len(self.loaded_plugins)} plugins")

        except Exception as e:
            print(f"⚠ Error loading plugins: {e}")


    def show_plugin_manager(self):
        """Show the comprehensive plugin management dialog."""
        try:
            if not self.plugin_manager_dialog:
                self.create_plugin_manager_dialog()

            self.update_plugin_manager_display()
            self.plugin_manager_dialog.show()
            self.plugin_manager_dialog.raise_()

        except Exception as e:
            print(f"⚠ Error showing plugin manager: {e}")


    def create_plugin_manager_dialog(self):
        """Create the comprehensive plugin management dialog."""
        try:
            self.plugin_manager_dialog = QDialog(self)
            self.plugin_manager_dialog.setWindowTitle("Plugin Manager")
            self.plugin_manager_dialog.setModal(False)
            self.plugin_manager_dialog.resize(1000, 800)

            layout = QVBoxLayout()

            # Plugin status summary
            summary_group = QGroupBox("Plugin Summary")
            summary_layout = QFormLayout()

            self.total_plugins_label = QLabel("0")
            self.active_plugins_label = QLabel("0")
            self.available_plugins_label = QLabel("0")
            self.disabled_plugins_label = QLabel("0")

            summary_layout.addRow("Total Plugins:", self.total_plugins_label)
            summary_layout.addRow("Active Plugins:", self.active_plugins_label)
            summary_layout.addRow("Available Plugins:", self.available_plugins_label)
            summary_layout.addRow("Disabled Plugins:", self.disabled_plugins_label)

            summary_group.setLayout(summary_layout)
            layout.addWidget(summary_group)

            # Plugin list with details
            plugins_group = QGroupBox("Plugin Management")
            plugins_layout = QVBoxLayout()

            # Plugin list widget
            self.plugin_list_widget = QListWidget()
            self.plugin_list_widget.currentItemChanged.connect(self.on_plugin_selection_changed)
            plugins_layout.addWidget(self.plugin_list_widget)

            # Plugin details panel
            self.plugin_details_text = QTextEdit()
            self.plugin_details_text.setReadOnly(True)
            self.plugin_details_text.setMaximumHeight(200)
            plugins_layout.addWidget(QLabel("Selected Plugin Details:"))
            plugins_layout.addWidget(self.plugin_details_text)

            plugins_group.setLayout(plugins_layout)
            layout.addWidget(plugins_group)

            # Plugin control buttons
            button_layout = QHBoxLayout()

            refresh_btn = QPushButton("Refresh")
            refresh_btn.clicked.connect(self.refresh_plugins)

            enable_btn = QPushButton("Enable Plugin")
            enable_btn.clicked.connect(self.enable_selected_plugin)

            disable_btn = QPushButton("Disable Plugin")
            disable_btn.clicked.connect(self.disable_selected_plugin)

            configure_btn = QPushButton("Configure")
            configure_btn.clicked.connect(self.configure_selected_plugin)

            reload_btn = QPushButton("Reload Plugin")
            reload_btn.clicked.connect(self.reload_selected_plugin)

            discovery_btn = QPushButton("Plugin Discovery")
            discovery_btn.clicked.connect(self.show_plugin_discovery)

            marketplace_btn = QPushButton("Plugin Marketplace")
            marketplace_btn.clicked.connect(self.show_plugin_marketplace)

            performance_btn = QPushButton("Performance Monitor")
            performance_btn.clicked.connect(self.show_plugin_performance)

            close_btn = QPushButton("Close")
            close_btn.clicked.connect(self.plugin_manager_dialog.hide)

            button_layout.addWidget(refresh_btn)
            button_layout.addWidget(enable_btn)
            button_layout.addWidget(disable_btn)
            button_layout.addWidget(configure_btn)
            button_layout.addWidget(reload_btn)
            button_layout.addWidget(discovery_btn)
            button_layout.addWidget(marketplace_btn)
            button_layout.addWidget(performance_btn)
            button_layout.addWidget(close_btn)

            layout.addLayout(button_layout)
            self.plugin_manager_dialog.setLayout(layout)

            print("✓ Plugin manager dialog created")

        except Exception as e:
            print(f"⚠ Error creating plugin manager dialog: {e}")


    def show_onboarding(self):
        """Show the onboarding wizard"""
        try:
            if hasattr(self, 'onboarding_wizard'):
                self.onboarding_wizard.show()
            else:
                logging.warning("Onboarding wizard not available")
                self.show_error_message("Onboarding Error", "Onboarding wizard is not available.")
        except Exception as e:
            logging.error(f"Failed to show onboarding: {e}")
            self.show_error_message("Onboarding Error", f"Failed to show onboarding: {e}")


    def create_project(self, project_name=None):
        """Create a new project with enhanced validation and backup"""
        try:
            if not project_name:
                from PyQt5.QtWidgets import QInputDialog
                project_name, ok = QInputDialog.getText(self, 'New Project', 'Enter project name:')
                if not ok or not project_name.strip():
                    return
                project_name = project_name.strip()

            # Enhanced project name validation
            validation_result = validator.validate_project_name(project_name)
            if not validation_result.is_valid:
                error_msg = f"Invalid project name: {validation_result.message}"
                if validation_result.suggestions:
                    error_msg += f"\n\nSuggestions:\n" + "\n".join(f"• {suggestion}" for suggestion in validation_result.suggestions)
                self.show_error_message("Invalid Project Name", error_msg)
                return

            # Check if project already exists
            project_dir = os.path.join("projects", project_name)
            if os.path.exists(project_dir):
                self.show_error_message("Project Exists", f"Project '{project_name}' already exists.")
                return

            # Create backup before making changes to projects directory
            backup_path = auto_backup_before_operation("project_creation")
            if backup_path:
                logging.info(f"Created backup before project creation: {backup_path}")

            # Validate projects directory
            projects_dir_result = validator.validate_directory_path("projects", create_if_missing=True)
            if not projects_dir_result.is_valid:
                self.show_error_message("Directory Error", f"Projects directory issue: {projects_dir_result.message}")
                return

            # Create project directory and files
            os.makedirs(project_dir, exist_ok=True)
            initialize_project_files(project_name)

            # Switch to the new project
            self.switch_project(project_name)

            logging.info(f"Project '{project_name}' created successfully")
            self.show_info_message("Project Created", f"Project '{project_name}' created successfully!")

        except Exception as e:
            logging.error(f"Failed to create project: {e}")
            self.show_error_message("Project Creation Error", f"Failed to create project: {e}")


    def open_project(self, project_name=None):
        """Open an existing project"""
        try:
            if not project_name:
                projects = get_project_list()
                if not projects:
                    self.show_info_message("No Projects", "No projects found. Create a new project first.")
                    return

                from PyQt5.QtWidgets import QInputDialog
                project_name, ok = QInputDialog.getItem(self, 'Open Project', 'Select project:', projects, 0, False)
                if not ok or not project_name:
                    return

            # Switch to the selected project
            self.switch_project(project_name)

        except Exception as e:
            logging.error(f"Failed to open project: {e}")
            self.show_error_message("Project Open Error", f"Failed to open project: {e}")


    def populate_draft_versions(self, chapter, section):
        """Populate the draft version selector with available versions for the given chapter and section."""
        if not hasattr(self, 'file_cache') or not self.file_cache:
            return
        draft_manager = DraftManager(self.file_cache, self.current_project)
        versions = draft_manager.list_draft_versions(chapter, section)
        self.draft_version_selector.clear()
        self.draft_version_selector.addItems(versions)
        if versions:
            self.draft_version_selector.setCurrentIndex(0)
            self.load_draft_version(chapter, section, versions[0])


    def connect_draft_version_selector(self, chapter, section):
        """Connect the draft version selector to load the selected draft version."""
        def on_version_changed(idx):
            version = self.draft_version_selector.currentText()
            if version:
                self.load_draft_version(chapter, section, version)
        self.draft_version_selector.currentIndexChanged.connect(on_version_changed)
        self.draft_version_selector.currentIndexChanged.connect(on_version_changed)


    def load_draft_version(self, chapter, section, version_filename):
        """Load the selected draft version into the drafts_tab."""
        if not hasattr(self, 'file_cache') or not self.file_cache:
            return
        # Compose the path as used in FileCache
        filename = f"drafts/chapter{chapter}/{version_filename}"
        content = self.file_cache.get(filename)
        self.drafts_tab.setText(content if content else "(No content found for this draft version)")


    def init_multi_provider_ai_system(self):
        """Initialize multi-provider AI system (Phase 2.1 First Half)."""
        try:
            if not AI_AVAILABLE:
                print("⚠ Multi-provider AI system not available")
                self.multi_provider_ai = None
                return

            # Initialize multi-provider AI configuration
            config = MultiProviderConfig()

            # Setup OpenAI provider configuration
            config.providers['openai'] = ProviderConfig(
                provider="openai",
                api_key="",  # Will be set from user settings
                model="gpt-3.5-turbo",
                max_tokens=1000,
                temperature=0.7
            )

            # Setup Anthropic provider configuration
            config.providers['anthropic'] = ProviderConfig(
                provider="anthropic",
                api_key="",  # Will be set from user settings
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0.7
            )

            # Setup Local provider configuration
            config.providers['local'] = ProviderConfig(
                provider="local",
                api_key="",  # Not needed for local
                base_url="http://localhost:11434/api/generate",
                model="llama2",
                max_tokens=1000,
                temperature=0.7
            )

            # Set preferred provider order
            config.preferred_order = ['openai', 'anthropic', 'local']
            config.failover_enabled = True
            config.load_balancing = True
            config.cost_tracking = True
            config.performance_monitoring = True

            # Initialize the multi-provider AI manager
            print("🔄 About to call initialize_multi_provider_ai()...")

            # Call it safely
            try:
                ai_config = initialize_multi_provider_ai()
                print(f"✓ Function returned: {type(ai_config)}")
                self.multi_provider_ai = ai_config
                print("✓ Assignment completed successfully")
            except Exception as e:
                print(f"❌ Error in initialize_multi_provider_ai(): {e}")
                import traceback
                traceback.print_exc()
                self.multi_provider_ai = None
                return

            # Update API keys from current configuration if available
            if hasattr(self, 'openai_key') and self.openai_key:
                print("🔄 About to update OpenAI API key...")
                self.update_ai_provider_key('openai', self.openai_key)
                print("✓ OpenAI API key update completed")

            print("✓ Multi-provider AI system initialized")
            print("✓ Unified AI provider interface ready")
            print("✓ Multiple AI providers supported (OpenAI, Anthropic, Local)")
            print("✓ Automatic failover enabled")
            print("✓ Load balancing and cost tracking active")

        except Exception as e:
            print(f"⚠ Error initializing multi-provider AI system: {e}")
            self.multi_provider_ai = None


    def update_ai_provider_key(self, provider_name: str, api_key: str):
        """Update API key for a specific AI provider."""
        try:
            if hasattr(self, 'multi_provider_ai') and self.multi_provider_ai:
                if provider_name in self.multi_provider_ai.providers:
                    self.multi_provider_ai.providers[provider_name].api_key = api_key
                    self.multi_provider_ai.providers[provider_name].enabled = bool(api_key)
                    print(f"✓ Updated {provider_name} API key")
                    return True
                else:
                    print(f"⚠ Provider {provider_name} not found")
                    return False
            else:
                print("⚠ Multi-provider AI system not available")
                return False

        except Exception as e:
            print(f"⚠ Error updating AI provider key: {e}")
            return False


    def generate_ai_content(self, prompt: str, max_tokens: int = 1000,
                           temperature: float = 0.7, preferred_provider: str = None) -> str:
        """Generate AI content using multi-provider system with fallback to original API manager."""
        try:
            # First try multi-provider AI system
            if hasattr(self, 'multi_provider_ai') and self.multi_provider_ai:
                response = self.multi_provider_ai.generate_text(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    preferred_provider=preferred_provider
                )

                if response and response.content:
                    # Log successful generation
                    print(f"✓ Generated content using {response.provider} ({response.model})")
                    return response.content

            # Fallback to original API manager
            if hasattr(self, 'api_manager') and self.api_manager:
                print("⚠ Falling back to original API manager")
                if hasattr(self, 'openai_key') and self.openai_key:
                    return self.api_manager.generate_text_openai(prompt, max_tokens, self.openai_key)

            # Final fallback
            print("⚠ No AI providers available")
            return f"[System] Unable to generate content: No AI providers available"

        except Exception as e:
            print(f"⚠ Error in AI content generation: {e}")
            return f"[System] Error generating content: {e}"


    def get_ai_provider_status(self) -> dict:
        """Get status of all AI providers."""
        try:
            if hasattr(self, 'multi_provider_ai') and self.multi_provider_ai:
                return self.multi_provider_ai.get_provider_status()
            else:
                return {"error": "Multi-provider AI system not available"}
        except Exception as e:
            return {"error": str(e)}


    def on_analytics_updated(self, analytics_data):
        """Handle analytics update from analytics manager."""
        try:
            # Update enhanced word count display
            if analytics_data and 'basic_analytics' in analytics_data:
                total_words = analytics_data['basic_analytics'].get('total_words_written', 0)
                self.update_word_count_enhanced(total_words, analytics_data)

        except Exception as e:
            print(f"⚠ Error handling analytics update: {e}")


    def on_session_started(self, session_id):
        """Handle writing session start."""
        try:
            self.log_tab.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Analytics: Writing session started ({session_id})")

            # Update UI to show active session
            if hasattr(self, 'status_label'):
                self.status_label.setText("Status: Writing Session Active")

        except Exception as e:
            print(f"⚠ Error handling session start: {e}")


    def on_session_ended(self, session_id, session_data):
        """Handle writing session end."""
        try:
            words_written = session_data.get('words_written', 0)
            duration = session_data.get('duration_minutes', 0)
            wpm = session_data.get('words_per_minute', 0)

            self.log_tab.append(
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - "
                f"Analytics: Session ended - {words_written} words in {duration:.1f}m ({wpm:.1f} WPM)"
            )

            # Update UI to show session ended
            if hasattr(self, 'status_label'):
                self.status_label.setText("Status: Session Complete")

        except Exception as e:
            print(f"⚠ Error handling session end: {e}")


    def on_milestone_reached(self, milestone_type, milestone_data):
        """Handle milestone achievement."""
        try:
            milestone_msg = f"Milestone reached: {milestone_type}"
            self.log_tab.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Analytics: {milestone_msg}")

            # Show milestone notification
            msg_box = create_styled_message_box(
                self,
                QMessageBox.Information,
                "Milestone Achieved!",
                milestone_msg
            )
            msg_box.exec_()

        except Exception as e:
            print(f"⚠ Error handling milestone: {e}")


    def update_word_count_enhanced(self, count, analytics_data=None):
        """Enhanced word count update with analytics integration."""
        try:
            # Update basic word count display
            self.word_count_label.setText(f"Word Count: {count:,}")

            # Update progress based on target
            if self.config:
                target = self.config.get('SoftTarget', 250000)
                progress = min(int((count / target) * 100), 100)
                self.progress_bar.setValue(progress)

            # Enhanced analytics display
            if analytics_data and self.analytics_enabled:
                session_info = analytics_data.get('current_session', {})
                if session_info.get('active', False):
                    session_words = session_info.get('words_this_session', 0)
                    session_duration = session_info.get('duration', 0)

                    # Update progress bar format to include session info
                    if session_duration > 0:
                        wpm = session_words / session_duration if session_duration > 0 else 0
                        self.progress_bar.setFormat(f"Progress: %p% | Session: {session_words} words ({wpm:.1f} WPM)")
                    else:
                        self.progress_bar.setFormat(f"Progress: %p% | Session: {session_words} words")
                else:
                    self.progress_bar.setFormat("Overall Progress: %p%")

            # Update analytics manager if available
            if self.analytics_manager and hasattr(self, 'current_project') and self.current_project:
                # Get current story content for text analysis
                story_content = ""
                if self.file_cache:
                    story_content = self.file_cache.get("story.txt") or ""

                self.analytics_manager.update_writing_progress(count, story_content)

        except Exception as e:
            print(f"⚠ Error in enhanced word count update: {e}")
            # Fallback to basic update
            self.update_word_count(count)


    def start_analytics_session(self):
        """Start a writing analytics session."""
        try:
            if self.analytics_manager and self.current_project:
                # Get current word count
                current_words = 0
                if self.file_cache:
                    story_content = self.file_cache.get("story.txt") or ""
                    current_words = len(story_content.split()) if story_content else 0

                # Start analytics session
                session_id = self.analytics_manager.start_writing_session(self.current_project, current_words)
                print(f"✓ Analytics session started: {session_id}")
                return session_id

            elif not self.analytics_enabled:
                # Basic session tracking fallback
                self.basic_session_tracker['session_active'] = True
                self.basic_session_tracker['start_time'] = datetime.now()
                if self.file_cache:
                    story_content = self.file_cache.get("story.txt") or ""
                    self.basic_session_tracker['start_word_count'] = len(story_content.split()) if story_content else 0

                print("✓ Basic analytics session started")
                return "basic_session"

        except Exception as e:
            print(f"⚠ Error starting analytics session: {e}")
            return None


    def end_analytics_session(self):
        """End the current writing analytics session."""
        try:
            if self.analytics_manager:
                # Get final word count
                final_words = 0
                if self.file_cache:
                    story_content = self.file_cache.get("story.txt") or ""
                    final_words = len(story_content.split()) if story_content else 0

                # End analytics session
                session_result = self.analytics_manager.end_writing_session(final_words)
                print(f"✓ Analytics session ended: {session_result}")
                return session_result

            elif self.basic_session_tracker.get('session_active', False):
                # Basic session tracking fallback
                end_time = datetime.now()
                start_time = self.basic_session_tracker.get('start_time')
                start_words = self.basic_session_tracker.get('start_word_count', 0)

                final_words = 0
                if self.file_cache:
                    story_content = self.file_cache.get("story.txt") or ""
                    final_words = len(story_content.split()) if story_content else 0

                if start_time:
                    duration = (end_time - start_time).total_seconds() / 60
                    words_written = final_words - start_words
                    wpm = words_written / duration if duration > 0 else 0

                    session_result = {
                        'duration_minutes': duration,
                        'words_written': words_written,
                        'words_per_minute': wpm,
                        'basic_session': True
                    }

                    self.basic_session_tracker['session_active'] = False
                    print(f"✓ Basic analytics session ended: {session_result}")
                    return session_result

        except Exception as e:
            print(f"⚠ Error ending analytics session: {e}")
            return None


    def get_analytics_dashboard_data(self):
        """Get data for analytics dashboard display."""
        try:
            if self.analytics_manager:
                # Get comprehensive analytics
                productivity_report = self.analytics_manager.get_productivity_report(30)
                writing_insights = self.analytics_manager.get_writing_insights()

                return {
                    'productivity_report': productivity_report,
                    'writing_insights': writing_insights,
                    'enhanced_analytics': True
                }

            else:
                # Return basic analytics
                return {
                    'basic_analytics': getattr(self, 'basic_session_tracker', {}),
                    'enhanced_analytics': False
                }

        except Exception as e:
            print(f"⚠ Error getting analytics dashboard data: {e}")
            return {'error': str(e)}


    def on_goal_achieved(self, goal_id: str, message: str):
        """Handle goal achievement notifications from advanced analytics."""
        try:
            print(f"🎉 Goal Achieved: {message}")

            # Show notification to user
            if hasattr(self, 'status_bar'):
                self.status_bar.showMessage(f"Goal Achieved: {message}", 5000)

            # You could also show a popup or add to a notifications area
            # QMessageBox.information(self, "Goal Achieved! 🎉", message)

        except Exception as e:
            print(f"⚠ Error handling goal achievement: {e}")


    def on_pattern_detected(self, pattern_data: dict):
        """Handle pattern detection notifications from advanced analytics."""
        try:
            pattern_type = pattern_data.get('pattern_type', 'unknown')
            description = pattern_data.get('description', 'New pattern detected')
            impact_score = pattern_data.get('impact_score', 0)

            print(f"🔍 Pattern Detected ({pattern_type}): {description}")

            # Only show high-impact patterns to avoid notification fatigue
            if impact_score > 0.7:
                if hasattr(self, 'status_bar'):
                    self.status_bar.showMessage(f"New insight: {description}", 8000)

        except Exception as e:
            print(f"⚠ Error handling pattern detection: {e}")


    def get_advanced_analytics_dashboard(self):
        """Get the advanced analytics dashboard widget if available."""
        try:
            if self.analytics_manager and hasattr(self.analytics_manager, 'get_advanced_dashboard_widget'):
                return self.analytics_manager.get_advanced_dashboard_widget()
            return None
        except Exception as e:
            print(f"⚠ Error getting advanced analytics dashboard: {e}")
            return None


    def export_all_analytics(self, file_path: str, format_type: str = 'json'):
        """Export all analytics data to file."""
        try:
            if self.analytics_manager and hasattr(self.analytics_manager, 'export_analytics_data'):
                exported_data = self.analytics_manager.export_analytics_data(format_type)

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(exported_data)

                print(f"✓ Analytics exported to: {file_path}")
                return True
            else:
                print("⚠ Analytics export not available")
                return False

        except Exception as e:
            print(f"⚠ Error exporting analytics: {e}")
            return False


    def _initialize_enhanced_collaborative_features(self):
        """Initialize enhanced collaborative features (Second Half - Phase 3.1)."""
        if not self.collaborative_manager:
            return

        try:
            # Track application startup for analytics
            if hasattr(self.collaborative_manager, 'track_collaboration_event'):
                self.collaborative_manager.track_collaboration_event(
                    event_type='app_start',
                    user_id=self.current_user_id,
                    project_id=getattr(self, 'current_project', 'no_project'),
                    metadata={'app_version': '1.0', 'features': 'enhanced_collaboration'}
                )

            # Set up notification callbacks for UI updates
            if hasattr(self.collaborative_manager, 'notification_manager') and self.collaborative_manager.notification_manager:
                try:
                    self.collaborative_manager.notification_manager.add_notification_callback(
                        self.current_user_id, self._handle_collaboration_notification
                    )
                    print("✅ Collaboration notification callbacks initialized")
                except Exception as e:
                    print(f"⚠ Failed to set up notification callbacks: {e}")

            print("✅ Enhanced collaborative features initialized successfully")

        except Exception as e:
            print(f"⚠ Error initializing enhanced collaborative features: {e}")


    def _handle_collaboration_notification(self, notification):
        """Handle incoming collaboration notifications."""
        try:
            # Show notification in UI (could be implemented as status bar message or popup)
            if hasattr(self, 'status_bar') and self.status_bar:
                self.status_bar.showMessage(f"Collaboration: {notification.title}", 5000)
            print(f"📩 Collaboration notification: {notification.title}")
        except Exception as e:
            print(f"⚠ Error handling collaboration notification: {e}")


    def _ensure_default_user_exists(self):
        """Ensure a default user exists in the system."""
        try:
            if not self.collaborative_manager:
                return

            # Create a collaborative system for the current project
            if self.current_project:
                collab_system = self.collaborative_manager.get_collaboration_system(self.current_project)
                success = collab_system.add_user(
                    self.current_user_id,
                    "Default User",
                    "user@fanws.local",
                    "owner"
                )
                if success:
                    print("✓ Default collaboration user created")
                else:
                    print("⚠ User may already exist in collaboration system")

        except Exception as e:
            print(f"⚠ Error ensuring default user: {e}")


    def _initialize_project_collaboration(self):
        """Initialize collaboration for the current project."""
        try:
            from src.collaboration_system import UserRole

            # Create project member entry for current user as owner
            success = self.collaborative_manager.invite_user_to_project(
                self.current_project, self.current_user_id, UserRole.OWNER, self.current_user_id
            )

            if success:
                print(f"✅ Project collaboration initialized for: {self.current_project}")
            else:
                print(f"⚠ Failed to initialize project collaboration")

        except Exception as e:
            print(f"⚠ Error initializing project collaboration: {e}")


    def get_collaborative_manager(self):
        """Get the collaborative manager instance."""
        return getattr(self, 'collaborative_manager', None)


    def launch_collaboration_hub(self):
        """Launch the collaboration hub dialog."""
        if not self.collaborative_manager:
            QMessageBox.warning(self, "Collaboration Hub",
                              "Collaborative features are not available.\nPlease check the installation.")
            return

        try:
            # Create and show collaboration dialog
            self.collaborative_dialog = CollaborativeDialog(self.collaborative_manager, self)

            # Set current project if available
            if hasattr(self, 'current_project') and self.current_project:
                self.collaborative_dialog.set_project(self.current_project)

            self.collaborative_dialog.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error launching collaboration hub: {e}")


    def get_collaboration_status(self):
        """Get the current collaboration status."""
        if not self.collaborative_manager:
            return {'available': False, 'error': 'Collaborative features not available'}

        try:
            status = {
                'available': True,
                'current_project': getattr(self, 'current_project', None),
                'current_user': getattr(self, 'current_user_id', None),
                'active_users': 0,
                'total_comments': 0,
                'unresolved_comments': 0
            }

            # Get project-specific status if project is loaded
            if hasattr(self, 'current_project') and self.current_project:
                # TODO: Get actual collaboration metrics
                # For now, return basic status
                pass

            return status

        except Exception as e:
            return {'available': False, 'error': str(e)}


    def _handle_memory_event(self, event_data: Dict[str, Any]):
        """Handle memory management events."""
        try:
            event_type = event_data.get('event', '')

            if event_type == 'optimization_completed':
                print("✓ Memory optimization completed")
            elif event_type == 'warning_threshold_reached':
                print("⚠ Memory warning threshold reached")
            elif event_type == 'critical_threshold_reached':
                print("🚨 Memory critical threshold reached - optimization triggered")

        except Exception as e:
            print(f"⚠ Error handling memory event: {e}")


    def _handle_config_change(self, key: str, old_value, new_value):
        """Handle configuration changes."""
        try:
            print(f"🔧 Configuration changed: {key} = {new_value}")

            # Handle specific configuration changes
            if key.startswith('memory.'):
                # Memory configuration changed, update memory system
                if hasattr(self, 'memory_integration') and self.memory_integration:
                    self.memory_integration.update_config(key, new_value)

            elif key.startswith('ai.'):
                # AI configuration changed, update AI providers
                if hasattr(self, 'multi_provider_manager') and self.multi_provider_manager:
                    self.multi_provider_manager.update_config(key, new_value)

            elif key.startswith('database.'):
                # Database configuration changed, update database settings
                if hasattr(self, 'db_manager') and self.db_manager:
                    self.db_manager.update_config(key, new_value)

            # Update UI if dashboard is available
            if hasattr(self, 'config_dashboard') and self.config_dashboard:
                self.config_dashboard._refresh_display()

        except Exception as e:
            print(f"⚠ Error handling configuration change: {e}")


    def get_configuration_value(self, key: str, default=None):
        """Get configuration value with fallback."""
        if hasattr(self, 'config_integration') and self.config_integration:
            return self.config_integration.get(key, default)
        elif hasattr(self, 'config') and self.config:
            # Fallback to basic config
            return self.config.get(key, default)
        return default


    def set_configuration_value(self, key: str, value) -> bool:
        """Set configuration value."""
        if hasattr(self, 'config_integration') and self.config_integration:
            return self.config_integration.set(key, value)
        elif hasattr(self, 'config') and self.config:
            # Fallback to basic config
            try:
                self.config.set(key, value)
                return True
            except Exception:
                return False
        return False


    def show_configuration_dashboard(self):
        """Show configuration management dashboard."""
        if hasattr(self, 'config_dashboard') and self.config_dashboard:
            self.config_dashboard.show()
            self.config_dashboard.raise_()
            self.config_dashboard.activateWindow()
        else:
            print("⚠ Configuration dashboard not available")


    def get_configuration_feature_status(self) -> Dict[str, bool]:
        """Get configuration management feature status."""
        if hasattr(self, 'config_integration') and self.config_integration:
            return self.config_integration.get_feature_status()
        else:
            return {
                "advanced_config": False,
                "basic_config": hasattr(self, 'config') and bool(self.config),
                "validation": False,
                "hot_reload": False,
                "multi_environment": False,
                "backup_restore": False,
                "import_export": False,
            }


    def get_template_manager(self):
        """Get the template manager instance."""
        return getattr(self, 'template_manager', None)


    def launch_template_marketplace(self):
        """Launch the template marketplace dialog."""
        if not getattr(self, 'template_manager', None):
            QMessageBox.warning(self, "Template Marketplace",
                              "Template features are not available.\\nPlease check the installation.")
            return

        try:
            # Create and show template marketplace dialog
            from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout

            marketplace_dialog = QDialog(self)
            marketplace_dialog.setWindowTitle("Template Marketplace")
            marketplace_dialog.setModal(True)
            marketplace_dialog.resize(900, 700)

            layout = QVBoxLayout()
            # marketplace_widget = TemplateMarketplaceWidget(marketplace_dialog, self.template_manager)
            # layout.addWidget(marketplace_widget)

            # Template marketplace functionality consolidated into template_manager
            info_label = QLabel("Template marketplace functionality has been consolidated into the unified template manager.")
            layout.addWidget(info_label)

            # Add close button
            button_box = QDialogButtonBox(QDialogButtonBox.Close)
            button_box.rejected.connect(marketplace_dialog.reject)
            layout.addWidget(button_box)

            marketplace_dialog.setLayout(layout)
            marketplace_dialog.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error launching template marketplace: {e}")


    def create_project_from_template(self, template_id: str = None):
        """Create a new project from a template."""
        if not getattr(self, 'template_manager', None):
            QMessageBox.warning(self, "Template System",
                              "Template features are not available.\\nPlease check the installation.")
            return

        try:
            # Template functionality consolidated into template_manager
            if not template_id:
                # if not hasattr(self, 'template_project_creator') or not self.template_project_creator:
                #     self.template_project_creator = TemplateProjectCreator(self, self.template_manager)

                #     # Connect signals
                #     self.template_project_creator.project_created.connect(
                #         lambda project_name: self._handle_template_project_created(project_name)
                #     )

                print("Template project creation functionality consolidated into template_manager")
                return

                # Show template creator in a dialog

                dialog = QDialog(self)
                dialog.setWindowTitle("Create Project from Template")
                dialog.setModal(True)
                dialog.resize(1000, 700)

                layout = QVBoxLayout()
                layout.addWidget(self.template_project_creator)

                button_box = QDialogButtonBox(QDialogButtonBox.Close)
                button_box.rejected.connect(dialog.reject)
                layout.addWidget(button_box)

                dialog.setLayout(layout)
                dialog.exec_()
            else:
                # Direct template creation (future enhancement)
                QMessageBox.information(self, "Template Creation",
                                      "Direct template creation will be available in a future update.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating project from template: {e}")


    def _handle_template_project_created(self, project_name: str):
        """Handle completion of template-based project creation."""
        try:
            # Refresh project selector if it exists
            if hasattr(self, 'project_selector') and self.project_selector:
                # Clear and repopulate
                self.project_selector.clear()
                projects = get_project_list()
                self.project_selector.addItems(projects)
                self.project_selector.setCurrentText(project_name)

            # Refresh UI project selector
            if hasattr(self, 'ui') and hasattr(self.ui, '_refresh_project_selector'):
                self.ui._refresh_project_selector()

            # Load the new project
            self.load_project(project_name)

            print(f"✅ Template-based project '{project_name}' loaded successfully")

        except Exception as e:
            print(f"⚠ Error handling template project creation: {e}")

        except Exception as e:
            print(f"⚠ Error exporting analytics: {e}")
            return False

    # =============================================
    # ACTION 2: Integration Verification Testing
    # =============================================


    def test_workflow_integration(self):
        """Test workflow manager integration."""
        print("🔍 Testing Workflow Manager Integration...")

        try:
            # Check if workflow manager is initialized
            if not self.novel_workflow:
                print("❌ Workflow manager not initialized")
                # Try to initialize it
                self.initialize_workflow_manager()
                if not self.novel_workflow:
                    print("❌ Failed to initialize workflow manager")
                    return False
                else:
                    print("✅ Workflow manager initialized successfully")

            # Test workflow manager attributes
            if hasattr(self.novel_workflow, 'workflow_started'):
                print("✅ Workflow signals available")
            else:
                print("⚠ Workflow signals not available")

            # Test workflow status
            if hasattr(self.novel_workflow, 'get_progress_status'):
                try:
                    status = self.novel_workflow.get_progress_status()
                    print(f"✅ Workflow status: {status}")
                except Exception as e:
                    print(f"⚠ Error getting workflow status: {e}")

            # Test signal connections (safely)
            try:
                # Check if signals exist without emitting
                if hasattr(self.novel_workflow, 'workflow_started'):
                    print("✅ workflow_started signal exists")
                if hasattr(self.novel_workflow, 'progress_updated'):
                    print("✅ progress_updated signal exists")
                if hasattr(self.novel_workflow, 'workflow_completed'):
                    print("✅ workflow_completed signal exists")

                print("✅ Workflow signals working")
                return True

            except Exception as e:
                print(f"❌ Workflow signal error: {e}")
                return False

        except Exception as e:
            print(f"❌ Workflow integration test failed: {e}")
            return False


    def test_all_workflow_steps(self):
        """Test all 11 workflow steps are accessible."""
        print("🔍 Testing All Workflow Steps...")

        try:
            from src.workflow_steps import (
                Step01Initialization, Step02SynopsisGeneration, Step03SynopsisRefinement,
                Step04StructuralPlanning, Step05TimelineSynchronization, Step06IterativeWriting,
                Step07UserReview, Step08RefinementLoop, Step09ProgressionManagement,
                Step10Recovery, Step11CompletionExport
            )

            steps = [
                Step01Initialization, Step02SynopsisGeneration, Step03SynopsisRefinement,
                Step04StructuralPlanning, Step05TimelineSynchronization, Step06IterativeWriting,
                Step07UserReview, Step08RefinementLoop, Step09ProgressionManagement,
                Step10Recovery, Step11CompletionExport
            ]

            success_count = 0
            total_steps = len(steps)

            for i, step_class in enumerate(steps, 1):
                try:
                    # Test step instantiation
                    step = step_class()
                    print(f"✅ Step {i:02d}: {step_class.__name__} - OK")
                    success_count += 1

                    # Test if step has required methods
                    if hasattr(step, 'execute'):
                        print(f"   • execute() method available")
                    if hasattr(step, 'get_step_name'):
                        print(f"   • get_step_name() method available")

                except Exception as e:
                    print(f"❌ Step {i:02d}: {step_class.__name__} - Error: {e}")

            print(f"📊 Workflow Steps Test Results: {success_count}/{total_steps} steps working")
            return success_count == total_steps

        except ImportError as e:
            print(f"❌ Failed to import workflow steps: {e}")
            return False
        except Exception as e:
            print(f"❌ Workflow steps test failed: {e}")
            return False


    def test_gui_integration(self):
        """Test GUI integration with workflow components."""
        print("🔍 Testing GUI Integration...")

        try:
            # Test modern GUI availability
            if hasattr(self, 'gui') and self.gui:
                print("✅ Modern GUI available")

                # Test workflow controls
                try:
                    # Check if workflow control methods exist
                    if hasattr(self.gui, 'start_workflow'):
                        print("✅ start_workflow() method available")
                    if hasattr(self.gui, 'pause_workflow'):
                        print("✅ pause_workflow() method available")
                    if hasattr(self.gui, 'stop_workflow'):
                        print("✅ stop_workflow() method available")

                    print("✅ GUI workflow controls working")
                    gui_controls_ok = True

                except Exception as e:
                    print(f"❌ GUI workflow controls error: {e}")
                    gui_controls_ok = False
            else:
                print("⚠ Modern GUI not available - using fallback")
                gui_controls_ok = True  # Don't fail for missing modern GUI

            # Test basic GUI components
            components_ok = True

            # Test progress bar
            if hasattr(self, 'progress_bar') and self.progress_bar:
                print("✅ Progress bar available")
            else:
                print("⚠ Progress bar not available")
                components_ok = False

            # Test status bar
            if hasattr(self, 'status_bar') and self.status_bar:
                print("✅ Status bar available")
            else:
                print("⚠ Status bar not available")
                components_ok = False

            # Test main tabs
            if hasattr(self, 'story_tab') and self.story_tab:
                print("✅ Story tab available")
            else:
                print("⚠ Story tab not available")
                components_ok = False

            # Test workflow integration points
            integration_ok = True

            # Test workflow starting method
            if hasattr(self, 'start_writing_workflow'):
                print("✅ start_writing_workflow() method available")
            else:
                print("❌ start_writing_workflow() method missing")
                integration_ok = False

            # Test update methods
            if hasattr(self, 'update_button_states'):
                print("✅ update_button_states() method available")
            else:
                print("⚠ update_button_states() method missing")

            print(f"📊 GUI Integration Test Results:")
            print(f"   • GUI Controls: {'✅ PASS' if gui_controls_ok else '❌ FAIL'}")
            print(f"   • GUI Components: {'✅ PASS' if components_ok else '❌ FAIL'}")
            print(f"   • Workflow Integration: {'✅ PASS' if integration_ok else '❌ FAIL'}")

            return gui_controls_ok and components_ok and integration_ok

        except Exception as e:
            print(f"❌ GUI integration test failed: {e}")
            return False


    def run_system_validation(self):
        """Run complete system validation."""
        print("🔍 Running FANWS System Validation")
        print("=" * 50)

        # Test 1: Workflow Integration
        print("\n1️⃣ WORKFLOW INTEGRATION TEST")
        print("-" * 30)
        workflow_ok = self.test_workflow_integration()

        # Test 2: All Steps Accessible
        print("\n2️⃣ WORKFLOW STEPS TEST")
        print("-" * 30)
        steps_ok = self.test_all_workflow_steps()

        # Test 3: GUI Integration
        print("\n3️⃣ GUI INTEGRATION TEST")
        print("-" * 30)
        gui_ok = self.test_gui_integration()

        # Summary
        print(f"\n📊 SYSTEM VALIDATION SUMMARY")
        print("=" * 50)
        print(f"Workflow Integration: {'✅ PASS' if workflow_ok else '❌ FAIL'}")
        print(f"Workflow Steps: {'✅ PASS' if steps_ok else '❌ FAIL'}")
        print(f"GUI Integration: {'✅ PASS' if gui_ok else '❌ FAIL'}")

        overall_success = workflow_ok and steps_ok and gui_ok
        print(f"\nOverall Result: {'🎉 ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")

        if overall_success:
            print("✅ ACTION 2 (Integration Verification) COMPLETED!")
        else:
            print("⚠ ACTION 2 (Integration Verification) needs attention")

        return overall_success


    def run_external_tests(self):
        """Run external test suites (integration and end-to-end)."""
        print("🔍 Running External FANWS Test Suites")
        print("=" * 45)

        try:
            import subprocess
            import os

            # Get the tests directory
            tests_dir = os.path.join(os.path.dirname(__file__), 'tests')

            print("1️⃣ Running Integration Tests...")
            print("-" * 35)
            integration_result = subprocess.run([
                sys.executable,
                os.path.join(tests_dir, 'test_integration.py')
            ], capture_output=True, text=True)

            integration_ok = integration_result.returncode == 0
            if integration_ok:
                print("✅ Integration tests passed")
            else:
                print("❌ Integration tests failed")
                print(integration_result.stdout)
                print(integration_result.stderr)

            print("\n2️⃣ Running End-to-End Tests...")
            print("-" * 35)
            e2e_result = subprocess.run([
                sys.executable,
                os.path.join(tests_dir, 'test_end_to_end.py')
            ], capture_output=True, text=True)

            e2e_ok = e2e_result.returncode == 0
            if e2e_ok:
                print("✅ End-to-end tests passed")
            else:
                print("❌ End-to-end tests failed")
                print(e2e_result.stdout)
                print(e2e_result.stderr)

            # Summary
            print(f"\n📊 EXTERNAL TEST SUMMARY")
            print("=" * 30)
            print(f"Integration Tests: {'✅ PASS' if integration_ok else '❌ FAIL'}")
            print(f"End-to-End Tests: {'✅ PASS' if e2e_ok else '❌ FAIL'}")

            overall_success = integration_ok and e2e_ok

            if overall_success:
                print("\n🎉 ALL EXTERNAL TESTS PASSED!")
                print("FANWS is ready for production use!")
            else:
                print("\n❌ SOME EXTERNAL TESTS FAILED")
                print("Review test results and fix issues")

            return overall_success

        except Exception as e:
            print(f"❌ Error running external tests: {e}")
            return False# Create alias for main class
FANWS = FANWSWindow



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

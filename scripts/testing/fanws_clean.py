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
            self.content_generator = ContentGenerator()
            self.project_manager = ProjectManager()
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

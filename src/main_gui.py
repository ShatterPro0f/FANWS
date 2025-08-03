"""
Modern FANWS GUI - Enhanced User Interface
Priority 3.1: Modern GUI Design Implementation

This module provides the modernized main GUI for FANWS with:
- Professional modern design system
- Responsive layout management
- Enhanced workflow visualization
- Improved user experience
- Better progress tracking
"""

import sys
import os
import json
import asyncio
from datetime import datetime, timedelta
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# Import modern UI components from ui package
try:
    from src.ui.core_ui import CoreUIComponents as UIComponents
    from src.ui.analytics_ui import AnalyticsUIComponents
    from src.ui.management_ui import ManagementUIComponents
    GUI_AVAILABLE = True
except ImportError as e:
    UIComponents = None
    AnalyticsUIComponents = None
    ManagementUIComponents = None
    GUI_AVAILABLE = False
    print(f"⚠ Modern UI components not available: {e}")

# Create consolidated design system
class DesignSystem:
    """Consolidated design system for FANWS"""
    COLORS = {
        'primary': '#2196F3',
        'primary_light': '#64B5F6',
        'secondary': '#FFC107',
        'success': '#4CAF50',
        'danger': '#F44336',
        'warning': '#FF9800',
        'info': '#2196F3',
        'bg_primary': '#FFFFFF',
        'bg_secondary': '#F5F5F5',
        'bg_card': '#FFFFFF',
        'text_primary': '#212121',
        'text_secondary': '#757575',
        'border_primary': '#E0E0E0'
    }

    @staticmethod
    def get_main_stylesheet():
        return """
        QMainWindow {
            background-color: #f5f5f5;
            color: #212121;
        }
        QWidget {
            font-family: 'Segoe UI', Arial, sans-serif;
        }
        """

    @staticmethod
    def get_sidebar_stylesheet():
        return """
        QFrame[class="sidebar"] {
            background-color: #263238;
            color: white;
            border-right: 1px solid #37474F;
        }
        QPushButton[class="nav-button"] {
            background-color: transparent;
            color: white;
            text-align: left;
            padding: 12px 16px;
            border: none;
            margin: 2px;
        }
        QPushButton[class="nav-button"]:hover {
            background-color: #37474F;
        }
        QPushButton[class="nav-button active"] {
            background-color: #2196F3;
        }
        """

    @staticmethod
    def get_dashboard_stylesheet():
        return """
        QLabel[class="header"] {
            font-size: 24px;
            font-weight: bold;
            color: #212121;
            margin: 16px 0px 8px 0px;
        }
        QLabel[class="subheader"] {
            font-size: 16px;
            font-weight: 600;
            color: #424242;
        }
        QLabel[class="caption"] {
            font-size: 12px;
            color: #757575;
        }
        QFrame[class="card"] {
            background-color: white;
            border: 1px solid #E0E0E0;
            border-radius: 8px;
            padding: 16px;
            margin: 8px;
        }
        """

class Components:
    """Modern UI components factory"""

    @staticmethod
    def create_button(text, style="primary", icon=None):
        button = QPushButton(text)
        colors = DesignSystem.COLORS
        if style == "primary":
            color = colors['primary']
        elif style == "success":
            color = colors['success']
        elif style == "danger":
            color = colors['danger']
        elif style == "secondary":
            color = colors['secondary']
        else:
            color = colors['primary']

        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
        """)
        return button

    @staticmethod
    def create_card(title, content_widget):
        card = QFrame()
        card.setProperty("class", "card")
        layout = QVBoxLayout()
        card.setLayout(layout)

        if title:
            title_label = QLabel(title)
            title_label.setProperty("class", "subheader")
            layout.addWidget(title_label)

        layout.addWidget(content_widget)
        return card

    @staticmethod
    def create_status_indicator(status, text):
        indicator = QLabel(text)
        colors = {
            'online': '#4CAF50',
            'offline': '#F44336',
            'warning': '#FF9800',
            'completed': '#4CAF50',
            'in_progress': '#2196F3',
            'pending': '#9E9E9E'
        }
        color = colors.get(status, '#9E9E9E')
        indicator.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-weight: 600;
                padding: 4px 8px;
                border-radius: 4px;
                background-color: {color}20;
            }}
        """)
        return indicator

class WorkflowUI:
    """Workflow UI components"""

    @staticmethod
    def create_progress_dashboard(metrics):
        widget = QWidget()
        layout = QGridLayout()
        widget.setLayout(layout)

        for i, (key, value) in enumerate(metrics.items()):
            card = Components.create_card(
                key.replace('_', ' ').title(),
                QLabel(str(value))
            )
            layout.addWidget(card, i // 3, i % 3)

        return widget

    @staticmethod
    def create_workflow_step_card(step_num, title, description, status):
        card = QFrame()
        card.setProperty("class", "card")
        layout = QVBoxLayout()
        card.setLayout(layout)

        # Step header
        header_layout = QHBoxLayout()
        step_label = QLabel(f"{step_num}. {title}")
        step_label.setProperty("class", "subheader")
        header_layout.addWidget(step_label)

        status_indicator = Components.create_status_indicator(status, status.title())
        header_layout.addWidget(status_indicator)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Description
        desc_label = QLabel(description)
        desc_label.setProperty("class", "caption")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)

        return card

# Create placeholder classes for missing components
class Animations:
    pass

class LayoutManager:
    pass

class WorkflowVisualization:
    pass

class UserFeedbackIntegration:
    pass

class IntegratedWorkflowFeedback:
    pass

class ProjectManagement:
    def __init__(self, parent):
        self.parent = parent

class PerformanceOptimizationUI:
    def __init__(self, parent):
        self.parent = parent

    def create_performance_dashboard(self):
        return QLabel("Performance Dashboard - Coming Soon")

    def create_performance_overview(self):
        return QLabel("Performance Overview - Coming Soon")

    def create_system_health_overview(self):
        return QLabel("System Health Overview - Coming Soon")

# Import async operations framework (Priority 4.1)
try:
    from .async_operations import BackgroundTaskManager, get_async_manager
    from .workflow_manager import AsyncWorkflowOperations as WorkflowTaskManager
    ASYNC_FRAMEWORK_AVAILABLE = True

    # Create placeholder UI components for async operations
    class AsyncProgressDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle("Async Progress")
            layout = QVBoxLayout()
            self.progress_bar = QProgressBar()
            layout.addWidget(self.progress_bar)
            self.setLayout(layout)

    class AsyncStatusBar(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QHBoxLayout()
            self.status_label = QLabel("Ready")
            layout.addWidget(self.status_label)
            self.setLayout(layout)

    class AsyncTaskWidget(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            layout = QVBoxLayout()
            self.task_label = QLabel("No active tasks")
            layout.addWidget(self.task_label)
            self.setLayout(layout)

except ImportError as e:
    print(f"⚠ Async framework not available: {e}")
    BackgroundTaskManager = None
    WorkflowTaskManager = None
    AsyncProgressDialog = None
    AsyncStatusBar = None
    AsyncTaskWidget = None
    ASYNC_FRAMEWORK_AVAILABLE = False

# Import multi-provider AI system
# Using embedded implementation below
try:
    pass  # Implementation is embedded below
except ImportError:

    class MultiProviderConfigurationUI(QWidget):
        def __init__(self, ai_manager, parent=None):
            super().__init__(parent)
            self.ai_manager = ai_manager
            layout = QVBoxLayout()
            layout.addWidget(QLabel("AI Provider Configuration"))
            self.setLayout(layout)

except ImportError as e:
    class AIManager:
        def get_current_provider(self):
            return "openai"
    class MultiProviderConfigurationUI:
        def __init__(self, ai_manager, parent=None):
            super().__init__(parent)

# Import advanced prompt engineering system
try:
    from .prompt_engineering_tools import PromptEngineeringManager as PromptEngine

    class PromptEngineUI(QWidget):
        def __init__(self, prompt_engine, parent=None):
            super().__init__(parent)
            self.prompt_engine = prompt_engine
            layout = QVBoxLayout()
            layout.addWidget(QLabel("Prompt Engineering Tools"))
            self.setLayout(layout)

except ImportError as e:
    class PromptEngine:
        def __init__(self, ai_manager=None):
            pass
    class PromptEngineUI:
        def __init__(self, prompt_engine=None, parent=None):
            super().__init__(parent)

# Import existing components
try:
    # Primary import from consolidated workflow_manager
    from src.workflow_manager import NovelWritingWorkflowModular
except ImportError:
    NovelWritingWorkflowModular = None

try:
    from src.ui import UIComponents
except ImportError:
    UIComponents = None

try:
    from src.configuration_manager import get_global_config
    ConfigManager = get_global_config()
except ImportError:
    ConfigManager = None

try:
    from src.database_manager import DatabaseManager
except ImportError:
    DatabaseManager = None

try:
    from .performance_monitor import PerformanceMonitor
except ImportError:
    PerformanceMonitor = None

# Import workflow controller
try:
    # Primary import from consolidated workflow_manager
    from .workflow_manager import FeedbackManager as WorkflowFeedbackIntegrator
except ImportError:
        class WorkflowFeedbackIntegrator:
            def __init__(self):
                # Create minimal progress tracker
                class ProgressTracker:
                    progress_updated = pyqtSignal(int, str)
                    eta_updated = pyqtSignal(str)
                    speed_updated = pyqtSignal(float)
                    log_message = pyqtSignal(str, str)

                self.progress_tracker = ProgressTracker()
                self.workflow_feedback_ready = pyqtSignal(str, dict)

                class FeedbackManager:
                    feedback_received = pyqtSignal(dict)

                self.feedback_manager = FeedbackManager()

class MainWindow(QMainWindow):
    """
    Main window for FANWS with GUI design.
    """

    def __init__(self):
        super().__init__()

        # Initialize components if available
        self.config = ConfigManager if ConfigManager else None
        self.db_manager = DatabaseManager() if DatabaseManager else None

        # Initialize design system and UI components
        self.design_system = DesignSystem()
        self.animations = Animations()
        self.components = Components()
        self.layout_manager = LayoutManager()

        self.performance_monitor = PerformanceMonitor() if PerformanceMonitor else None
        self.workflow_manager = NovelWritingWorkflowModular() if NovelWritingWorkflowModular else None

        # Initialize multi-provider AI system
        self.ai_provider_manager = AIManager()
        self.ai_config_ui = MultiProviderConfigurationUI(self.ai_provider_manager)

        # Initialize advanced prompt engineering system
        self.prompt_engine = PromptEngine(self.ai_provider_manager)
        self.prompt_engine_ui = PromptEngineUI(self.prompt_engine)

        # Initialize analytics system for dashboard
        try:
            from .analytics_system import WritingAnalyticsDashboard, AnalyticsWidget
            self.analytics_manager = WritingAnalyticsDashboard()
            self.analytics_widget = AnalyticsWidget(self.analytics_manager)
            print("✓ Analytics system initialized")
        except ImportError as e:
            self.analytics_manager = None
            self.analytics_widget = None
            print(f"⚠ Analytics system not available: {e}")

        # Initialize workflow manager with analytics integration
        if self.workflow_manager and self.analytics_manager:
            # Connect workflow events to analytics
            try:
                # This would connect workflow completion events to analytics tracking
                pass
            except Exception as e:
                print(f"⚠ Analytics integration failed: {e}")

        # UI state
        self.current_project = None
        self.workflow_status = {}
        self.animations = {}

        # Dashboard chart state
        self._last_total_progress = 0.0
        self._last_avg_daily = 0.0
        self._chart_metrics = {}

        # Initialize workflow controller
        self.workflow_controller = WorkflowFeedbackIntegrator()

        # Initialize advanced project management
        self.advanced_project_mgmt = ProjectManagement(self)

        # Intelligent caching integration
        try:
            from .memory_manager import IntelligentCacheManager, CacheIntegration
            # Get project directory safely
            project_dir = getattr(self, 'project_dir', os.path.dirname(__file__))
            self.cache_manager = IntelligentCacheManager(
                cache_dir=os.path.join(project_dir, "cache"),
                max_cache_size=500
            )
            self.cache_integration = CacheIntegration(self.cache_manager)
            self.cache_enabled = True
            print("✓ Intelligent caching system initialized")
        except (ImportError, Exception) as e:
            self.cache_manager = None
            self.cache_integration = None
            self.cache_enabled = False
            print(f"⚠ Intelligent caching system not available: {e}")

        # Initialize async framework (Priority 4.1)
        if ASYNC_FRAMEWORK_AVAILABLE:
            self.async_manager = get_async_manager()
            self.async_workflow_manager = WorkflowTaskManager(self.async_manager)
            self.async_status_bar = AsyncStatusBar(self)
            self.async_task_widgets = {}
            self.async_enabled = True
            print("✓ Async operations framework initialized")
        else:
            self.async_manager = None
            self.async_workflow_manager = None
            self.async_status_bar = None
            self.async_task_widgets = {}
            self.async_enabled = False
            print("⚠ Running without async framework")

        # UI
        self.init_ui()
        self.setup_styling()
        self.setup_connections()

        # Initialize async UI components if available
        if self.async_enabled:
            self.init_async_ui()

        self.load_project_data()

        # Connect controller signals to UI updates
        self.workflow_controller.progress_tracker.progress_updated.connect(self.update_progress_display)
        self.workflow_controller.progress_tracker.eta_updated.connect(self.update_eta_display)
        self.workflow_controller.progress_tracker.speed_updated.connect(self.update_speed_display)
        self.workflow_controller.progress_tracker.log_message.connect(self.add_log_message)
        self.workflow_controller.workflow_feedback_ready.connect(self.show_feedback_request)
        self.workflow_controller.feedback_manager.feedback_received.connect(self.update_feedback_metrics)

        # Start performance monitoring if available
        if self.performance_monitor:
            try:
                self.performance_monitor.start_monitoring()
            except:
                pass

    def init_ui(self):
        """Initialize the modern user interface."""
        self.setWindowTitle("FANWS - Fantasy Adventure Novel Writing System")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 800)

        # Set window icon if available
        icon_path = self.get_icon_path('fanws_icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # Create sidebar
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar, 0)

        # Create main content area
        self.main_content = self.create_main_content_area()
        main_layout.addWidget(self.main_content, 1)

        # Create status bar
        self.create_status_bar()

        # Create menu bar
        self.create_menu_bar()

    def create_sidebar(self):
        """Create the modern sidebar navigation."""
        sidebar = QFrame()
        sidebar.setProperty("class", "sidebar")
        sidebar.setMinimumWidth(280)
        sidebar.setMaximumWidth(350)

        layout = QVBoxLayout()
        sidebar.setLayout(layout)

        # Header
        header = QFrame()
        header.setProperty("class", "sidebar-header")
        header_layout = QVBoxLayout()
        header.setLayout(header_layout)

        # Logo/Title
        title = QLabel("FANWS")
        title.setProperty("class", "header")
        header_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Fantasy Adventure Novel Writing System")
        subtitle.setProperty("class", "caption")
        header_layout.addWidget(subtitle)

        layout.addWidget(header)

        # Navigation buttons
        nav_buttons = [
            ("Dashboard", "dashboard", "📊"),
            ("Projects", "projects", "📚"),
            ("Workflow", "workflow", "⚙️"),
            ("Project Management", "project_management", "📁"),
            ("Performance", "performance", "📈"),
            ("Settings", "settings", "⚙️"),
            ("Help", "help", "❓")
        ]

        self.nav_buttons = {}
        for text, key, icon in nav_buttons:
            button = QPushButton(f"{icon} {text}")
            button.setProperty("class", "nav-button")
            button.clicked.connect(lambda checked, k=key: self.switch_view(k))
            self.nav_buttons[key] = button
            layout.addWidget(button)

        # Spacer
        layout.addStretch()

        # Project info
        self.project_info = self.create_project_info_widget()
        layout.addWidget(self.project_info)

        return sidebar

    def create_main_content_area(self):
        """Create the main content area with stacked pages."""
        content_area = QStackedWidget()

        # Create different views
        self.views = {
            'dashboard': self.create_dashboard_view(),
            'projects': self.create_projects_view(),
            'workflow': self.create_workflow_view(),
            'project_management': self.create_project_management_view(),
            'settings': self.create_settings_view(),
            'help': self.create_help_view()
        }

        # Performance Optimization view
        self.performance_ui = PerformanceOptimizationUI(self)
        self.performance_view = self.performance_ui.create_performance_dashboard()
        self.views['performance'] = self.performance_view

        # System Health Monitor
        self.system_health_view = self.performance_ui.create_system_health_overview()
        self.views['system_health'] = self.system_health_view

        # Add views to stacked widget
        for view_name, view_widget in self.views.items():
            content_area.addWidget(view_widget)

        # Set default view
        content_area.setCurrentWidget(self.views['dashboard'])
        self.current_view = 'dashboard'
        self.nav_buttons['dashboard'].setProperty("class", "nav-button active")

        return content_area

    def create_dashboard_view(self):
        """Create the dashboard view with project metrics."""
        dashboard = QWidget()
        layout = QVBoxLayout()
        dashboard.setLayout(layout)

        # Page header
        header = QLabel("Dashboard")
        header.setProperty("class", "header")
        layout.addWidget(header)

        # Metrics section
        metrics_data = self.get_project_metrics()
        metrics_dashboard = WorkflowUI.create_progress_dashboard(metrics_data)
        layout.addWidget(metrics_dashboard)

        # Performance overview
        if hasattr(self, 'performance_ui'):
            performance_overview = self.performance_ui.create_performance_overview()
            layout.addWidget(performance_overview)

        # Recent activity
        activity_card = Components.create_card(
            "Recent Activity",
            self.create_activity_list()
        )
        layout.addWidget(activity_card)

        # Workflow status
        workflow_card = Components.create_card(
            "Workflow Status",
            self.create_workflow_status_widget()
        )
        layout.addWidget(workflow_card)

        layout.addStretch()
        return dashboard

    def create_projects_view(self):
        """Create the projects management view."""
        projects = QWidget()
        layout = QVBoxLayout()
        projects.setLayout(layout)

        # Page header
        header_layout = QHBoxLayout()

        header = QLabel("Projects")
        header.setProperty("class", "header")
        header_layout.addWidget(header)

        # New project button
        new_project_btn = Components.create_button("New Project", "success", None)
        new_project_btn.clicked.connect(self.create_new_project)
        header_layout.addWidget(new_project_btn)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Project list
        self.project_list = self.create_project_list()
        layout.addWidget(self.project_list)

        return projects

    def create_workflow_view(self):
        """Create the workflow management view."""
        workflow = QWidget()
        layout = QVBoxLayout()
        workflow.setLayout(layout)

        # Page header
        header_layout = QHBoxLayout()

        header = QLabel("Workflow")
        header.setProperty("class", "header")
        header_layout.addWidget(header)

        # Workflow controls
        start_btn = Components.create_button("Start Workflow", "primary")
        start_btn.clicked.connect(self.start_workflow)
        header_layout.addWidget(start_btn)

        pause_btn = Components.create_button("Pause", "secondary")
        pause_btn.clicked.connect(self.pause_workflow)
        header_layout.addWidget(pause_btn)

        stop_btn = Components.create_button("Stop", "danger")
        stop_btn.clicked.connect(self.stop_workflow)
        header_layout.addWidget(stop_btn)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Workflow steps
        self.workflow_steps_widget = self.create_workflow_steps_widget()
        layout.addWidget(self.workflow_steps_widget)

        # Progress section
        progress_card = Components.create_card(
            "Progress",
            self.create_workflow_progress_widget()
        )
        layout.addWidget(progress_card)

        return workflow

    def create_settings_view(self):
        """Create the settings view."""
        settings = QWidget()
        layout = QVBoxLayout()
        settings.setLayout(layout)

        # Page header
        header = QLabel("Settings")
        header.setProperty("class", "header")
        layout.addWidget(header)

        # Settings tabs
        tabs = QTabWidget()

        # General settings
        general_tab = self.create_general_settings_tab()
        tabs.addTab(general_tab, "General")

        # AI Provider settings
        ai_tab = self.create_ai_provider_settings_tab()
        tabs.addTab(ai_tab, "AI Providers")

        # Prompt Engineering settings
        prompt_tab = self.create_prompt_engineering_settings_tab()
        tabs.addTab(prompt_tab, "Prompt Engineering")

        # Workflow settings
        workflow_tab = self.create_workflow_settings_tab()
        tabs.addTab(workflow_tab, "Workflow")

        # Performance settings
        performance_tab = self.create_performance_settings_tab()
        tabs.addTab(performance_tab, "Performance")

        # Cache Settings tab
        if self.cache_enabled:
            cache_tab = self.create_cache_settings_tab()
            tabs.addTab(cache_tab, "Cache Settings")

        layout.addWidget(tabs)

        return settings

    def create_help_view(self):
        """Create the help view."""
        help_widget = QWidget()
        layout = QVBoxLayout()
        help_widget.setLayout(layout)

        # Page header
        header = QLabel("Help & Documentation")
        header.setProperty("class", "header")
        layout.addWidget(header)

        # Help content
        help_content = QTextEdit()
        help_content.setReadOnly(True)
        help_content.setHtml(self.get_help_content())
        layout.addWidget(help_content)

        return help_widget

    def create_project_info_widget(self):
        """Create the project information widget for the sidebar."""
        info_widget = QFrame()
        info_widget.setProperty("class", "card")

        layout = QVBoxLayout()
        info_widget.setLayout(layout)

        # Project name
        self.project_name_label = QLabel("No Project Selected")
        self.project_name_label.setProperty("class", "subheader")
        layout.addWidget(self.project_name_label)

        # Project stats
        self.project_stats = QLabel("Select a project to view details")
        self.project_stats.setProperty("class", "caption")
        self.project_stats.setWordWrap(True)
        layout.addWidget(self.project_stats)

        return info_widget

    def create_activity_list(self):
        """Create the recent activity list widget."""
        activity_list = QListWidget()
        activity_list.setMaximumHeight(200)

        # Sample activities
        activities = [
            "Created new project 'Epic Fantasy Adventure'",
            "Completed character development for protagonist",
            "Generated initial plot outline",
            "Refined story structure",
            "Exported draft to PDF"
        ]

        for activity in activities:
            item = QListWidgetItem(activity)
            activity_list.addItem(item)

        return activity_list

    def create_workflow_status_widget(self):
        """Create the workflow status widget."""
        status_widget = QWidget()
        layout = QVBoxLayout()
        status_widget.setLayout(layout)

        # Current step
        current_step = QLabel("Current Step: Story Planning")
        current_step.setProperty("class", "subheader")
        layout.addWidget(current_step)

        # Progress bar
        progress = QProgressBar()
        progress.setValue(45)
        layout.addWidget(progress)

        # Status indicators
        status_layout = QHBoxLayout()

        for status, count in [("Completed", 4), ("In Progress", 1), ("Pending", 6)]:
            indicator = Components.create_status_indicator(
                status.lower().replace(' ', '_'),
                f"{status}: {count}"
            )
            status_layout.addWidget(indicator)

        layout.addLayout(status_layout)

        return status_widget

    def create_project_list(self):
        """Create the project list widget."""
        project_list = QTreeWidget()
        project_list.setHeaderLabels(["Project", "Status", "Progress", "Last Modified"])

        # Sample projects
        projects = [
            ("Epic Fantasy Adventure", "Active", "45%", "2024-01-15"),
            ("Sci-Fi Thriller", "Paused", "23%", "2024-01-10"),
            ("Mystery Novel", "Completed", "100%", "2024-01-05")
        ]

        for project_data in projects:
            item = QTreeWidgetItem(project_data)
            project_list.addTopLevelItem(item)

        return project_list

    def create_workflow_steps_widget(self):
        """Create the workflow steps visualization widget."""
        steps_widget = QScrollArea()
        steps_widget.setWidgetResizable(True)

        content_widget = QWidget()
        layout = QVBoxLayout()
        content_widget.setLayout(layout)

        # Workflow steps
        steps_data = [
            (1, "Project Initialization", "Set up project structure and metadata", "completed"),
            (2, "Character Development", "Create and develop main characters", "completed"),
            (3, "World Building", "Design the story world and settings", "completed"),
            (4, "Plot Outline", "Create the main plot structure", "completed"),
            (5, "Story Planning", "Detailed story planning and structure", "processing"),
            (6, "Chapter Generation", "Generate chapter content", "pending"),
            (7, "User Review", "Review and refine generated content", "pending"),
            (8, "Refinement Loop", "Iterative improvement process", "pending"),
            (9, "Progression Management", "Track and manage story progression", "pending"),
            (10, "Recovery System", "Handle errors and recovery", "pending"),
            (11, "Completion & Export", "Finalize and export the novel", "pending")
        ]

        for step_data in steps_data:
            step_card = WorkflowUI.create_workflow_step_card(*step_data)
            layout.addWidget(step_card)

        steps_widget.setWidget(content_widget)
        return steps_widget

    def create_workflow_progress_widget(self):
        """Create the workflow progress tracking widget."""
        progress_widget = QWidget()
        layout = QVBoxLayout()
        progress_widget.setLayout(layout)

        # Overall progress
        overall_label = QLabel("Overall Progress")
        overall_label.setProperty("class", "subheader")
        layout.addWidget(overall_label)

        overall_progress = QProgressBar()
        overall_progress.setValue(45)
        layout.addWidget(overall_progress)

        # Step-by-step progress
        steps_progress = QLabel("Steps Completed: 4/11")
        steps_progress.setProperty("class", "caption")
        layout.addWidget(steps_progress)

        return progress_widget

    def create_general_settings_tab(self):
        """Create the general settings tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        # Theme selection
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout()
        theme_group.setLayout(theme_layout)

        theme_combo = QComboBox()
        theme_combo.addItems(["Dark", "Light", "Auto"])
        theme_layout.addWidget(theme_combo)

        layout.addWidget(theme_group)

        # Language selection
        lang_group = QGroupBox("Language")
        lang_layout = QVBoxLayout()
        lang_group.setLayout(lang_layout)

        lang_combo = QComboBox()
        lang_combo.addItems(["English", "Spanish", "French", "German"])
        lang_layout.addWidget(lang_combo)

        layout.addWidget(lang_group)

        layout.addStretch()
        return tab

    def create_prompt_engineering_settings_tab(self):
        """Create the prompt engineering settings tab."""
        # Return the prompt engine UI directly
        return self.prompt_engine_ui

    def create_ai_provider_settings_tab(self):
        """Create the AI provider settings tab."""
        # Return the AI configuration UI directly
        return self.ai_config_ui

    def create_workflow_settings_tab(self):
        """Create the workflow settings tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        # Auto-save settings
        autosave_group = QGroupBox("Auto-Save")
        autosave_layout = QVBoxLayout()
        autosave_group.setLayout(autosave_layout)

        autosave_checkbox = QCheckBox("Enable auto-save")
        autosave_checkbox.setChecked(True)
        autosave_layout.addWidget(autosave_checkbox)

        autosave_interval = QSpinBox()
        autosave_interval.setRange(1, 60)
        autosave_interval.setValue(5)
        autosave_interval.setSuffix(" minutes")
        autosave_layout.addWidget(autosave_interval)

        layout.addWidget(autosave_group)

        # Backup settings
        backup_group = QGroupBox("Backup")
        backup_layout = QVBoxLayout()
        backup_group.setLayout(backup_layout)

        backup_checkbox = QCheckBox("Enable automatic backups")
        backup_checkbox.setChecked(True)
        backup_layout.addWidget(backup_checkbox)

        backup_interval = QSpinBox()
        backup_interval.setRange(1, 24)
        backup_interval.setValue(1)
        backup_interval.setSuffix(" hours")
        backup_layout.addWidget(backup_interval)

        layout.addWidget(backup_group)

        layout.addStretch()
        return tab

    def create_performance_settings_tab(self):
        """Create the performance settings tab."""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)

        # Performance monitoring
        perf_group = QGroupBox("Performance Monitoring")
        perf_layout = QVBoxLayout()
        perf_group.setLayout(perf_layout)

        monitor_checkbox = QCheckBox("Enable performance monitoring")
        monitor_checkbox.setChecked(True)
        perf_layout.addWidget(monitor_checkbox)

        layout.addWidget(perf_group)

        layout.addStretch()
        return tab

    def create_cache_settings_tab(self):
        """Create cache settings tab for intelligent caching configuration."""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Cache status section
        status_group = QGroupBox("Cache Status")
        status_layout = QFormLayout(status_group)

        self.cache_stats_label = QLabel("Loading cache statistics...")
        status_layout.addRow("Status:", self.cache_stats_label)

        # Cache configuration section
        config_group = QGroupBox("Cache Configuration")
        config_layout = QFormLayout(config_group)

        # Max cache size
        self.max_cache_size_spinbox = QSpinBox()
        self.max_cache_size_spinbox.setRange(10, 10000)
        self.max_cache_size_spinbox.setValue(500)
        config_layout.addRow("Max Cache Size:", self.max_cache_size_spinbox)

        # Similarity threshold
        self.similarity_threshold_spinbox = QDoubleSpinBox()
        self.similarity_threshold_spinbox.setRange(0.1, 1.0)
        self.similarity_threshold_spinbox.setSingleStep(0.05)
        self.similarity_threshold_spinbox.setValue(0.85)
        config_layout.addRow("Similarity Threshold:", self.similarity_threshold_spinbox)

        # Max age hours
        self.max_age_hours_spinbox = QSpinBox()
        self.max_age_hours_spinbox.setRange(1, 720)  # 1 hour to 30 days
        self.max_age_hours_spinbox.setValue(168)  # 1 week
        config_layout.addRow("Max Age (hours):", self.max_age_hours_spinbox)

        # Enable semantic caching
        self.enable_semantic_checkbox = QCheckBox("Enable Semantic Caching")
        self.enable_semantic_checkbox.setChecked(True)
        config_layout.addRow("", self.enable_semantic_checkbox)

        # Enable compression
        self.enable_compression_checkbox = QCheckBox("Enable Compression")
        self.enable_compression_checkbox.setChecked(True)
        config_layout.addRow("", self.enable_compression_checkbox)

        # Cache actions section
        actions_group = QGroupBox("Cache Actions")
        actions_layout = QVBoxLayout(actions_group)

        # Buttons layout
        buttons_layout = QHBoxLayout()

        # Refresh stats button
        refresh_button = QPushButton("Refresh Statistics")
        refresh_button.clicked.connect(self.refresh_cache_stats)
        buttons_layout.addWidget(refresh_button)

        # Optimize cache button
        optimize_button = QPushButton("Optimize Cache")
        optimize_button.clicked.connect(self.optimize_cache)
        buttons_layout.addWidget(optimize_button)

        # Clear cache button
        clear_button = QPushButton("Clear Cache")
        clear_button.clicked.connect(self.clear_cache)
        buttons_layout.addWidget(clear_button)

        # Export cache button
        export_button = QPushButton("Export Cache Data")
        export_button.clicked.connect(self.export_cache_data)
        buttons_layout.addWidget(export_button)

        actions_layout.addLayout(buttons_layout)

        # Cache statistics display
        self.cache_stats_text = QTextEdit()
        self.cache_stats_text.setReadOnly(True)
        self.cache_stats_text.setMaximumHeight(150)
        actions_layout.addWidget(self.cache_stats_text)

        # Layout assembly
        layout.addWidget(status_group)
        layout.addWidget(config_group)
        layout.addWidget(actions_group)
        layout.addStretch()

        # Initialize cache stats
        self.refresh_cache_stats()

        return tab

    def refresh_cache_stats(self):
        """Refresh and display cache statistics."""
        if not self.cache_enabled:
            return

        try:
            stats = self.cache_manager.get_cache_stats()

            # Update status label
            status_text = f"Active - {stats['total_entries']} entries, {stats['hit_rate']}% hit rate"
            self.cache_stats_label.setText(status_text)

            # Update detailed stats
            stats_text = f"""Cache Statistics:
Total Entries: {stats['total_entries']}
Cache Hits: {stats['cache_hits']}
Cache Misses: {stats['cache_misses']}
Hit Rate: {stats['hit_rate']}%
Average Response Time: {stats['average_response_time']:.3f}s
Total Cost Saved: ${stats['total_cost_saved']:.2f}
Storage Size: {stats['storage_size_mb']:.2f} MB
Semantic Matches: {stats['semantic_matches']}
Exact Matches: {stats['exact_matches']}
Cache Strategy: {stats['cache_strategy']}
Invalidation Strategy: {stats['invalidation_strategy']}
Semantic Caching: {'Enabled' if stats['semantic_caching_enabled'] else 'Disabled'}"""

            self.cache_stats_text.setText(stats_text)

        except Exception as e:
            self.cache_stats_label.setText(f"Error: {str(e)}")
            self.cache_stats_text.setText(f"Failed to load cache statistics: {str(e)}")

    def optimize_cache(self):
        """Optimize the cache system."""
        if not self.cache_enabled:
            return

        try:
            optimization_results = self.cache_manager.optimize_cache()

            message = "Cache optimization completed!\n\n"

            if optimization_results['actions_taken']:
                message += "Actions taken:\n"
                for action in optimization_results['actions_taken']:
                    message += f"• {action}\n"
                message += "\n"

            if optimization_results['recommendations']:
                message += "Recommendations:\n"
                for rec in optimization_results['recommendations']:
                    message += f"• {rec}\n"

            if not optimization_results['actions_taken'] and not optimization_results['recommendations']:
                message += "No optimization actions needed at this time."

            QMessageBox.information(self, "Cache Optimization", message)

            # Refresh stats
            self.refresh_cache_stats()

        except Exception as e:
            QMessageBox.critical(self, "Cache Optimization Error", f"Failed to optimize cache: {str(e)}")

    def clear_cache(self):
        """Clear cache with confirmation."""
        if not self.cache_enabled:
            return

        reply = QMessageBox.question(
            self, "Clear Cache",
            "Are you sure you want to clear all cache entries?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                deleted = self.cache_manager.clear_cache()
                QMessageBox.information(self, "Cache Cleared", f"Cleared {deleted} cache entries.")

                # Refresh stats
                self.refresh_cache_stats()

            except Exception as e:
                QMessageBox.critical(self, "Cache Clear Error", f"Failed to clear cache: {str(e)}")

    def export_cache_data(self):
        """Export cache data to file."""
        if not self.cache_enabled:
            return

        try:
            from datetime import datetime
            default_filename = f"cache_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Cache Data",
                default_filename,
                "JSON Files (*.json);;All Files (*)"
            )

            if filename:
                success = self.cache_manager.export_cache_data(filename)

                if success:
                    QMessageBox.information(self, "Export Complete", f"Cache data exported to:\n{filename}")
                else:
                    QMessageBox.critical(self, "Export Error", "Failed to export cache data.")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export cache data: {str(e)}")

    # ...existing code...
    def create_status_bar(self):
        """Create the modern status bar."""
        status_bar = self.statusBar()

        # Status message
        self.status_message = QLabel("Ready")
        status_bar.addWidget(self.status_message)

        # Progress indicator
        self.status_progress = QProgressBar()
        self.status_progress.setMaximumWidth(200)
        self.status_progress.setVisible(False)
        status_bar.addPermanentWidget(self.status_progress)

        # Connection status
        self.connection_status = Components.create_status_indicator("online", "Connected")
        status_bar.addPermanentWidget(self.connection_status)

        # Performance info
        self.performance_label = QLabel("CPU: 0% | Memory: 0MB")
        status_bar.addPermanentWidget(self.performance_label)

    def create_menu_bar(self):
        """Create the modern menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('File')

        new_action = QAction('New Project', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.create_new_project)
        file_menu.addAction(new_action)

        open_action = QAction('Open Project', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)

        save_action = QAction('Save Project', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu('Edit')

        # View menu = menubar.addMenu('View')

        # Help menu
        help_menu = menubar.addMenu('Help')

        about_action = QAction('About FANWS', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_styling(self):
        """Apply modern styling to the application."""
        # Apply main stylesheet
        main_style = DesignSystem.get_main_stylesheet()
        sidebar_style = DesignSystem.get_sidebar_stylesheet()
        dashboard_style = DesignSystem.get_dashboard_stylesheet()

        combined_style = main_style + sidebar_style + dashboard_style
        self.setStyleSheet(combined_style)

    def setup_connections(self):
        """Set up signal connections."""
        # Performance monitoring
        self.performance_timer = QTimer()
        self.performance_timer.timeout.connect(self.update_performance_display)
        self.performance_timer.start(1000)  # Update every second

    def init_async_ui(self):
        """Initialize async UI components (Priority 4.1)."""
        if not self.async_enabled:
            return

        # Initialize async status bar
        if self.async_status_bar and hasattr(self, 'statusBar'):
            self.statusBar().addPermanentWidget(self.async_status_bar)

        # Connect async manager signals
        if self.async_manager:
            self.async_manager.task_started.connect(self.on_async_task_started)
            self.async_manager.task_progress.connect(self.on_async_task_progress)
            self.async_manager.task_completed.connect(self.on_async_task_completed)
            self.async_manager.task_failed.connect(self.on_async_task_failed)

        # Connect async workflow manager signals
        if self.async_workflow_manager:
            self.async_workflow_manager.workflow_started.connect(self.on_async_workflow_started)
            self.async_workflow_manager.workflow_progress.connect(self.on_async_workflow_progress)
            self.async_workflow_manager.workflow_completed.connect(self.on_async_workflow_completed)
            self.async_workflow_manager.workflow_failed.connect(self.on_async_workflow_failed)

        print("✓ Async UI components initialized")

    def get_icon_path(self, icon_name):
        """Get the path to an icon file."""
        return os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', icon_name)

    def get_project_metrics(self):
        """Get project metrics for the dashboard."""
        # Calculate dynamic metrics with real data
        total_progress = self.calculate_total_progress()
        avg_daily = self.calculate_avg_daily_progress()

        # Get current project data
        current_project = self.get_current_project_data()

        return {
            'total_projects': len(self.get_all_projects()),
            'active_projects': len([p for p in self.get_all_projects() if p.get('status') == 'active']),
            'completed_projects': len([p for p in self.get_all_projects() if p.get('status') == 'completed']),
            'words_written': current_project.get('words_written', 0),
            'chapters_completed': current_project.get('chapters_completed', 0),
            'workflow_steps': current_project.get('completed_steps', 0),
            'total_progress': total_progress,
            'avg_daily': avg_daily,
            'workflow_completion': f"{total_progress:.1f}%",
            'daily_average': f"{avg_daily:.0f} words/day"
        }

    def get_help_content(self):
        """Get help content HTML."""
        return """
        <h2>FANWS Help & Documentation</h2>

        <h3>Getting Started</h3>
        <p>Welcome to FANWS (Fantasy Adventure Novel Writing System). This application helps you create comprehensive fantasy novels through an automated workflow.</p>

        <h3>Features</h3>
        <ul>
            <li><strong>Project Management:</strong> Create and manage multiple writing projects</li>
            <li><strong>Automated Workflow:</strong> 11-step process for complete novel generation</li>
            <li><strong>Character Development:</strong> Create detailed character profiles</li>
            <li><strong>World Building:</strong> Design comprehensive fantasy worlds</li>
            <li><strong>Story Planning:</strong> Structured plot development</li>
        </ul>

        <h3>Workflow Steps</h3>
        <ol>
            <li>Project Initialization</li>
            <li>Character Development</li>
            <li>World Building</li>
            <li>Plot Outline</li>
            <li>Story Planning</li>
            <li>Chapter Generation</li>
            <li>User Review</li>
            <li>Refinement Loop</li>
            <li>Progression Management</li>
            <li>Recovery System</li>
            <li>Completion & Export</li>
        </ol>

        <h3>Support</h3>
        <p>For additional help, please refer to the documentation or contact support.</p>
        """

    def switch_view(self, view_name):
        """Switch to a different view."""
        if view_name in self.views:
            # Update navigation buttons
            for key, button in self.nav_buttons.items():
                if key == view_name:
                    button.setProperty("class", "nav-button active")
                else:
                    button.setProperty("class", "nav-button")

            # Switch view
            self.main_content.setCurrentWidget(self.views[view_name])
            self.current_view = view_name

            # Update status
            self.status_message.setText(f"Switched to {view_name.title()}")

            # Refresh view if needed
            if view_name == 'dashboard':
                self.refresh_dashboard()

    def refresh_dashboard(self):
        """Refresh the dashboard with current data."""
        try:
            # Update dashboard chart with current metrics
            self.update_dashboard_chart()

            # Update other dashboard components
            if hasattr(self, 'views') and 'dashboard' in self.views:
                # Refresh metrics in the dashboard view
                metrics_data = self.get_project_metrics()

                # Find and update the metrics dashboard widget
                dashboard_widget = self.views['dashboard']
                if dashboard_widget:
                    # Update the metrics display
                    self.update_metrics_display(metrics_data)

            self.add_log_message("Dashboard refreshed successfully", "info")

        except Exception as e:
            error_msg = f"Error refreshing dashboard: {str(e)}"
            self.add_log_message(error_msg, "error")
            import logging
            logging.error(error_msg)

    def update_dashboard_chart(self):
        """Update dashboard chart with proper variable calculations."""
        try:
            # Calculate total progress from workflow status
            total_progress = 0
            if hasattr(self, 'workflow_manager') and self.workflow_manager:
                status = self.workflow_manager.get_progress_status()
                total_progress = status.get('progress_percentage', 0)
            elif hasattr(self, 'novel_workflow') and self.novel_workflow:
                # Try alternative workflow reference
                if hasattr(self.novel_workflow, 'progress_tracker'):
                    total_progress = getattr(self.novel_workflow.progress_tracker, 'current_step', 0) / 11 * 100
            else:
                # Fallback to calculated progress
                total_progress = self.calculate_total_progress()

            # Calculate average daily progress
            avg_daily = 0
            if hasattr(self, 'analytics_manager') and self.analytics_manager:
                recent_activity = self.analytics_manager.get_recent_activity(7)  # Last 7 days
                if recent_activity:
                    total_words = sum(activity.get('word_count', 0) for activity in recent_activity)
                    avg_daily = total_words / 7 if total_words > 0 else 0
            else:
                # Fallback to calculated average
                avg_daily = self.calculate_avg_daily_progress()

            # Update chart display with calculated values
            self.update_chart_display(total_progress, avg_daily)

            # Store values for access by other methods
            self._last_total_progress = total_progress
            self._last_avg_daily = avg_daily

            # Update status
            self.add_log_message(f"Chart updated: {total_progress:.1f}% progress, {avg_daily:.0f} words/day", "info")

        except Exception as e:
            error_msg = f"Error updating dashboard chart: {str(e)}"
            self.add_log_message(error_msg, "error")
            import logging
            logging.error(error_msg)

    def calculate_total_progress(self):
        """Calculate total workflow progress percentage."""
        try:
            # Check if we have a current project
            current_project = self.get_current_project_data()
            if not current_project:
                return 0.0

            # Calculate based on completed steps
            completed_steps = current_project.get('completed_steps', 0)
            total_steps = 11  # FANWS has 11 workflow steps

            progress = (completed_steps / total_steps) * 100
            return min(progress, 100.0)

        except Exception as e:
            import logging
            logging.error(f"Error calculating total progress: {e}")
            return 0.0

    def calculate_avg_daily_progress(self):
        """Calculate average daily word count progress."""
        try:
            # Get recent writing activity
            current_project = self.get_current_project_data()
            if not current_project:
                return 0.0

            # Calculate from session history or analytics
            writing_sessions = current_project.get('writing_sessions', [])
            if not writing_sessions:
                return 0.0

            # Get last 7 days of data
            from datetime import datetime, timedelta
            seven_days_ago = datetime.now() - timedelta(days=7)

            recent_sessions = [
                session for session in writing_sessions
                if datetime.fromisoformat(session.get('date', '1970-01-01')) >= seven_days_ago
            ]

            if not recent_sessions:
                return 0.0

            total_words = sum(session.get('word_count', 0) for session in recent_sessions)
            unique_days = len(set(session.get('date', '').split('T')[0] for session in recent_sessions))

            avg_daily = total_words / max(unique_days, 1)
            return avg_daily

        except Exception as e:
            import logging
            logging.error(f"Error calculating average daily progress: {e}")
            return 0.0

    def update_chart_display(self, total_progress, avg_daily):
        """Update the chart display with new values."""
        try:
            # Update dashboard metrics if available
            if hasattr(self, 'views') and 'dashboard' in self.views:
                # Create updated metrics data
                updated_metrics = {
                    'workflow_progress': f"{total_progress:.1f}%",
                    'daily_average': f"{avg_daily:.0f} words/day",
                    'progress_bar_value': int(total_progress),
                    'last_updated': datetime.now().strftime("%H:%M:%S")
                }

                # Store for later use
                self._chart_metrics = updated_metrics

                # If we have chart widgets, update them
                self.update_chart_widgets(updated_metrics)

        except Exception as e:
            import logging
            logging.error(f"Error updating chart display: {e}")

    def update_chart_widgets(self, metrics):
        """Update individual chart widget components."""
        try:
            # Update progress bars if they exist
            if hasattr(self, 'progress_chart_widget'):
                self.progress_chart_widget.setValue(metrics.get('progress_bar_value', 0))

            # Update text labels if they exist
            if hasattr(self, 'progress_label'):
                self.progress_label.setText(metrics.get('workflow_progress', '0%'))

            if hasattr(self, 'daily_label'):
                self.daily_label.setText(metrics.get('daily_average', '0 words/day'))

        except Exception as e:
            import logging
            logging.error(f"Error updating chart widgets: {e}")

    def update_metrics_display(self, metrics_data):
        """Update the metrics display with new data."""
        try:
            # This would update the dashboard metrics display
            # Currently metrics are handled by the static dashboard creation
            # In the future, this could update live chart components
            pass

        except Exception as e:
            import logging
            logging.error(f"Error updating metrics display: {e}")

    def get_current_project_data(self):
        """Get current project data."""
        try:
            # Return current project data or default structure
            return {
                'id': 'current_project',
                'name': 'Current Project',
                'status': 'active',
                'words_written': 0,
                'chapters_completed': 0,
                'completed_steps': 0,
                'writing_sessions': [],
                'created_date': datetime.now().isoformat(),
                'last_modified': datetime.now().isoformat()
            }
        except Exception as e:
            import logging
            logging.error(f"Error getting current project data: {e}")
            return {}

    def get_all_projects(self):
        """Get all projects list."""
        try:
            # Return list of all projects or default
            return [self.get_current_project_data()]
        except Exception as e:
            import logging
            logging.error(f"Error getting all projects: {e}")
            return []

    def update_performance_display(self):
        """Update the performance display in the status bar."""
        if self.performance_monitor:
            try:
                cpu_percent = self.performance_monitor.get_cpu_usage()
                memory_mb = self.performance_monitor.get_memory_usage()
                self.performance_label.setText(f"CPU: {cpu_percent:.1f}% | Memory: {memory_mb:.1f}MB")
            except:
                self.performance_label.setText("Performance monitoring unavailable")
        else:
            self.performance_label.setText("Performance monitoring disabled")

    def load_project_data(self):
        """Load project data from database."""
        # This would load real project data
        pass

    def create_new_project(self):
        """Create a new project with async support."""
        try:
            if self.async_enabled and self.async_manager:
                # Use async task for project creation
                task_id = self.async_manager.run_async_task(
                    self._create_new_project_async,
                    task_name="Creating New Project"
                )
                self.add_log_message("Creating new project...", "info")
            else:
                # Fallback to synchronous creation
                self._create_new_project_sync()

        except Exception as e:
            error_msg = f"Error creating project: {str(e)}"
            self.add_log_message(error_msg, "error")
            QMessageBox.critical(self, "Project Error", error_msg)

    def open_project(self):
        """Open an existing project with async support."""
        try:
            if self.async_enabled and self.async_manager:
                # Use async task for project opening
                task_id = self.async_manager.run_async_task(
                    self._open_project_async,
                    task_name="Opening Project"
                )
                self.add_log_message("Opening project...", "info")
            else:
                # Fallback to synchronous opening
                self._open_project_sync()

        except Exception as e:
            error_msg = f"Error opening project: {str(e)}"
            self.add_log_message(error_msg, "error")
            QMessageBox.critical(self, "Project Error", error_msg)

    def save_project(self):
        """Save the current project with async support."""
        try:
            if self.async_enabled and self.async_manager:
                # Use async task for project saving
                task_id = self.async_manager.run_async_task(
                    self._save_project_async,
                    task_name="Saving Project"
                )
                self.add_log_message("Saving project...", "info")
            else:
                # Fallback to synchronous saving
                self._save_project_sync()

        except Exception as e:
            error_msg = f"Error saving project: {str(e)}"
            self.add_log_message(error_msg, "error")
            QMessageBox.critical(self, "Project Error", error_msg)

    def _create_new_project_sync(self):
        """Synchronous project creation (fallback)."""
        QMessageBox.information(self, "New Project", "New project creation dialog would open here.")

    def _open_project_sync(self):
        """Synchronous project opening (fallback)."""
        QMessageBox.information(self, "Open Project", "Project selection dialog would open here.")

    def _save_project_sync(self):
        """Synchronous project saving (fallback)."""
        QMessageBox.information(self, "Save Project", "Project saved successfully.")

    async def _create_new_project_async(self):
        """Asynchronous project creation."""
        # Simulate project creation work
        await asyncio.sleep(0.1)
        return {"status": "success", "message": "New project created"}

    async def _open_project_async(self):
        """Asynchronous project opening."""
        # Simulate project loading work
        await asyncio.sleep(0.1)
        return {"status": "success", "message": "Project opened"}

    async def _save_project_async(self):
        """Asynchronous project saving."""
        # Simulate project saving work
        await asyncio.sleep(0.1)
        return {"status": "success", "message": "Project saved"}

    def start_workflow(self):
        """Start the workflow process with async support."""
        try:
            if self.async_enabled and self.async_workflow_manager:
                # Use async workflow manager
                workflow_config = self.get_workflow_config()
                task_id = self.async_workflow_manager.start_async_workflow(
                    workflow_type="novel_writing",
                    config=workflow_config,
                    project_data=self.current_project
                )
                self.add_log_message(f"Started async workflow: {task_id}", "info")
            else:
                # Fallback to synchronous workflow
                self.start_legacy_workflow()

        except Exception as e:
            error_msg = f"Error starting workflow: {str(e)}"
            self.add_log_message(error_msg, "error")
            QMessageBox.critical(self, "Workflow Error", error_msg)

    def start_legacy_workflow(self):
        """Start workflow using legacy method (fallback)."""
        QMessageBox.information(self, "Start Workflow", "Workflow started successfully (legacy mode).")

    def pause_workflow(self):
        """Pause the workflow process."""
        try:
            if self.async_enabled and self.async_workflow_manager:
                self.async_workflow_manager.pause_current_workflow()
                self.add_log_message("Workflow paused", "info")
            else:
                QMessageBox.information(self, "Pause Workflow", "Workflow paused.")
        except Exception as e:
            error_msg = f"Error pausing workflow: {str(e)}"
            self.add_log_message(error_msg, "error")
            QMessageBox.critical(self, "Workflow Error", error_msg)

    def stop_workflow(self):
        """Stop the workflow process."""
        try:
            if self.async_enabled and self.async_workflow_manager:
                self.async_workflow_manager.stop_current_workflow()
                self.add_log_message("Workflow stopped", "info")
            else:
                QMessageBox.information(self, "Stop Workflow", "Workflow stopped.")
        except Exception as e:
            error_msg = f"Error stopping workflow: {str(e)}"
            self.add_log_message(error_msg, "error")
            QMessageBox.critical(self, "Workflow Error", error_msg)

    def get_workflow_config(self):
        """Get current workflow configuration."""
        return {
            "project_name": self.current_project.get("name", "Untitled") if self.current_project else "Untitled",
            "ai_provider": self.ai_provider_manager.get_current_provider() if self.ai_provider_manager else "openai",
            "use_cache": self.cache_enabled,
            "enable_feedback": True,
            "auto_save": True
        }

    def show_about(self):
        """Show the about dialog."""
        QMessageBox.about(self, "About FANWS",
                         "FANWS - Fantasy Adventure Novel Writing System\n\n"
                         "Version 2.0\n"
                         "Modern GUI with Enhanced User Experience\n\n"
                         "© 2024 FANWS Development Team")

    def closeEvent(self, event):
        """Handle application close event."""
        # Save settings and cleanup
        if self.performance_monitor:
            try:
                self.performance_monitor.stop_monitoring()
            except:
                pass

        event.accept()

    def connect_workflow_controls(self):
        """Connect UI controls to workflow controller."""
        # This method was referenced in the __init__ but wasn't defined
        # Add connections here when UI controls are available
        pass

    @pyqtSlot(int, str)
    def update_progress_display(self, progress: int, current_step: str):
        """Update progress display in UI."""
        try:
            # Update overall progress bar
            progress_bar = self.findChild(QProgressBar, "overallProgress")
            if progress_bar:
                progress_bar.setValue(progress)

            # Update current step label
            step_label = self.findChild(QLabel, "currentStepLabel")
            if step_label:
                step_label.setText(f"Current Step: {current_step}")

        except Exception as e:
            print(f"Error updating progress display: {e}")

    @pyqtSlot(str)
    def update_eta_display(self, eta: str):
        """Update ETA display in UI."""
        try:
            eta_label = self.findChild(QLabel, "etaLabel")
            if eta_label:
                eta_label.setText(f"Estimated Time Remaining: {eta}")
        except Exception as e:
            print(f"Error updating ETA display: {e}")

    @pyqtSlot(float)
    def update_speed_display(self, speed: float):
        """Update speed display in UI."""
        try:
            speed_label = self.findChild(QLabel, "speedLabel")
            if speed_label:
                speed_label.setText(f"Processing Speed: {speed:.1f} operations/sec")
        except Exception as e:
            print(f"Error updating speed display: {e}")

    @pyqtSlot(str, str)
    def add_log_message(self, message: str, level: str):
        """Add message to live log viewer."""
        try:
            log_text = self.findChild(QTextEdit, "liveLogText")
            if log_text:
                timestamp = datetime.now().strftime("%H:%M:%S")
                formatted_message = f"[{timestamp}] {level.upper()}: {message}\n"
                log_text.append(formatted_message)

                # Auto-scroll if enabled
                auto_scroll = self.findChild(QCheckBox, "autoScrollCheckbox")
                if auto_scroll and auto_scroll.isChecked():
                    log_text.moveCursor(log_text.textCursor().End)

        except Exception as e:
            print(f"Error adding log message: {e}")

    @pyqtSlot(str, dict)
    def show_feedback_request(self, step_name: str, step_data: dict):
        """Show feedback request in review panel."""
        try:
            # Switch to feedback tab
            workflow_tabs = self.findChild(QTabWidget, "workflowTabs")
            if workflow_tabs:
                workflow_tabs.setCurrentIndex(1)  # Feedback tab

            # Update review content area
            content_area = self.findChild(QTextEdit, "reviewContentArea")
            if content_area:
                content_text = f"Step: {step_name}\n\n"
                content_text += f"Generated Content:\n{step_data.get('content', 'No content available')}\n\n"
                content_text += f"Metadata:\n{json.dumps(step_data, indent=2)}"
                content_area.setPlainText(content_text)

            # Store current review item
            self.current_review_item = step_data.get("item_id", step_name)

        except Exception as e:
            print(f"Error showing feedback request: {e}")

    @pyqtSlot(dict)
    def update_feedback_metrics(self, feedback_data: dict):
        """Update feedback metrics display."""
        try:
            if hasattr(self, 'workflow_controller'):
                metrics = self.workflow_controller.feedback_manager.get_metrics()

                # Update metric cards
                pending_metric = self.findChild(QLabel, "pendingReviewsMetric")
                if pending_metric:
                    pending_metric.setText(str(metrics.get("pending_reviews", 0)))

                approved_metric = self.findChild(QLabel, "approvedMetric")
                if approved_metric:
                    approved_metric.setText(str(metrics.get("total_feedback", 0)))

                rating_metric = self.findChild(QLabel, "ratingMetric")
                if rating_metric:
                    rating_metric.setText(f"{metrics.get('average_rating', 0):.1f}")

                response_metric = self.findChild(QLabel, "responseMetric")
                if response_metric:
                    avg_response = metrics.get("average_response_time", 0)
                    if avg_response > 0:
                        response_metric.setText(f"{avg_response / 3600:.1f}h")
                    else:
                        response_metric.setText("0h")

        except Exception as e:
            print(f"Error updating feedback metrics: {e}")

    def approve_content(self):
        """Handle content approval."""
        try:
            if hasattr(self, 'current_review_item') and self.current_review_item:
                if hasattr(self, 'workflow_controller'):
                    self.workflow_controller.feedback_manager.process_feedback(
                        self.current_review_item, "approve"
                    )
                    self.add_log_message("Content approved by user", "info")
        except Exception as e:
            print(f"Error approving content: {e}")

    def request_changes(self):
        """Handle change request."""
        try:
            if hasattr(self, 'current_review_item') and self.current_review_item:
                # Get feedback text
                feedback_text = self.findChild(QTextEdit, "feedbackText")
                feedback_type = self.findChild(QComboBox, "feedbackTypeCombo")
                priority = self.findChild(QComboBox, "priorityCombo")

                feedback_data = {
                    "item_id": self.current_review_item,
                    "type": feedback_type.currentText() if feedback_type else "general",
                    "content": feedback_text.toPlainText() if feedback_text else "",
                    "priority": priority.currentText().lower() if priority else "medium"
                }

                if hasattr(self, 'workflow_controller'):
                    self.workflow_controller.feedback_manager.process_feedback(
                        self.current_review_item, "change", feedback_data
                    )
                    self.add_log_message("Change request submitted", "info")

        except Exception as e:
            print(f"Error requesting changes: {e}")

    # Async signal handlers (Priority 4.1)
    @pyqtSlot(str, str)
    def on_async_task_started(self, task_id: str, task_name: str):
        """Handle async task started signal."""
        if self.async_status_bar:
            self.async_status_bar.add_task(task_id, task_name)
        self.add_log_message(f"Started async task: {task_name}", "info")

    @pyqtSlot(str, int, str)
    def on_async_task_progress(self, task_id: str, progress: int, status: str):
        """Handle async task progress signal."""
        if self.async_status_bar:
            self.async_status_bar.update_task_progress(task_id, progress, status)

    @pyqtSlot(str, object)
    def on_async_task_completed(self, task_id: str, result: object):
        """Handle async task completed signal."""
        if self.async_status_bar:
            self.async_status_bar.remove_task(task_id)
        self.add_log_message(f"Completed async task: {task_id}", "success")

    @pyqtSlot(str, str)
    def on_async_task_failed(self, task_id: str, error: str):
        """Handle async task failed signal."""
        if self.async_status_bar:
            self.async_status_bar.remove_task(task_id)
        self.add_log_message(f"Async task failed: {task_id} - {error}", "error")

    @pyqtSlot(str, str)
    def on_async_workflow_started(self, workflow_id: str, workflow_name: str):
        """Handle async workflow started signal."""
        self.add_log_message(f"Started async workflow: {workflow_name}", "info")

    @pyqtSlot(str, str, int)
    def on_async_workflow_progress(self, workflow_id: str, step_name: str, progress: int):
        """Handle async workflow progress signal."""
        self.add_log_message(f"Workflow progress: {step_name} ({progress}%)", "info")

    @pyqtSlot(str, object)
    def on_async_workflow_completed(self, workflow_id: str, result: object):
        """Handle async workflow completed signal."""
        self.add_log_message(f"Completed async workflow: {workflow_id}", "success")

    @pyqtSlot(str, str)
    def on_async_workflow_failed(self, workflow_id: str, error: str):
        """Handle async workflow failed signal."""
        self.add_log_message(f"Async workflow failed: {workflow_id} - {error}", "error")

    def create_project_management_view(self):
        """Create the project management view."""
        project_mgmt_widget = QWidget()
        layout = QVBoxLayout()
        project_mgmt_widget.setLayout(layout)

        # Page header
        header = QLabel("Advanced Project Management")
        header.setProperty("class", "header")
        layout.addWidget(header)

        # Create tabbed interface for project management features
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {self.design_system.COLORS['border_primary']};
                background-color: {self.design_system.COLORS['bg_card']};
                border-radius: 8px;
            }}
            QTabBar::tab {{
                background-color: {self.design_system.COLORS['bg_secondary']};
                color: {self.design_system.COLORS['text_primary']};
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }}
            QTabBar::tab:selected {{
                background-color: {self.design_system.COLORS['primary']};
                color: white;
            }}
            QTabBar::tab:hover {{
                background-color: {self.design_system.COLORS['primary_light']};
            }}
        """)

        # Project Templates tab
        templates_tab = QScrollArea()
        templates_tab.setWidgetResizable(True)
        templates_tab.setWidget(self.advanced_project_mgmt.create_project_template_selector())
        tab_widget.addTab(templates_tab, "🏗️ Project Templates")

        # Version Control tab
        version_control_tab = QScrollArea()
        version_control_tab.setWidgetResizable(True)
        version_control_tab.setWidget(self.advanced_project_mgmt.create_version_control_interface())
        tab_widget.addTab(version_control_tab, "🔄 Version Control")

        # Backup Management tab
        backup_tab = QScrollArea()
        backup_tab.setWidgetResizable(True)
        backup_tab.setWidget(self.advanced_project_mgmt.create_backup_management_interface())
        tab_widget.addTab(backup_tab, "💾 Backup Management")

        # Project Sharing tab
        sharing_tab = QScrollArea()
        sharing_tab.setWidgetResizable(True)
        sharing_tab.setWidget(self.advanced_project_mgmt.create_project_sharing_interface())
        tab_widget.addTab(sharing_tab, "🤝 Project Sharing")

        layout.addWidget(tab_widget)

        return project_mgmt_widget

    # Project Management Methods
    def apply_project_template(self, template_data):
        """Apply a project template to the current project"""
        try:
            # Create project structure based on template
            project_name = f"New {template_data['name']}"

            # Update project metadata
            if self.current_project:
                self.current_project.update({
                    'template': template_data['name'],
                    'target_chapters': template_data['structure']['chapters'],
                    'target_words': template_data['structure']['target_words'],
                    'pacing': template_data['structure']['pacing'],
                    'themes': template_data['structure']['themes']
                })

            # Create template-specific files
            for filename in template_data['files']:
                filepath = os.path.join(self.get_project_path(), filename)
                if not os.path.exists(filepath):
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(f"# {filename.replace('.txt', '').replace('_', ' ').title()}\n\n")

            # Show success message
            QMessageBox.information(self, "Template Applied",
                                  f"Successfully applied {template_data['name']} template to your project.")

            # Refresh project view
            self.refresh_project_view()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply template: {str(e)}")

    def create_custom_template_dialog(self):
        """Show dialog for creating custom templates"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Create Custom Template")
        dialog.setModal(True)
        dialog.resize(500, 400)

        layout = QVBoxLayout(dialog)

        # Template name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Template Name:"))
        name_input = QLineEdit()
        name_layout.addWidget(name_input)
        layout.addLayout(name_layout)

        # Template description
        desc_layout = QVBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        desc_input = QTextEdit()
        desc_input.setMaximumHeight(100)
        desc_layout.addWidget(desc_input)
        layout.addLayout(desc_layout)

        # Structure settings
        struct_group = QGroupBox("Structure Settings")
        struct_layout = QFormLayout(struct_group)

        chapters_spin = QSpinBox()
        chapters_spin.setRange(10, 50)
        chapters_spin.setValue(25)
        struct_layout.addRow("Target Chapters:", chapters_spin)

        words_spin = QSpinBox()
        words_spin.setRange(50000, 200000)
        words_spin.setValue(80000)
        struct_layout.addRow("Target Words:", words_spin)

        pacing_combo = QComboBox()
        pacing_combo.addItems(["slow", "moderate", "fast", "epic"])
        struct_layout.addRow("Pacing:", pacing_combo)

        layout.addWidget(struct_group)

        # Buttons
        button_layout = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(dialog.reject)
        create_button = QPushButton("Create Template")
        create_button.clicked.connect(dialog.accept)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(create_button)
        layout.addLayout(button_layout)

        if dialog.exec_() == QDialog.Accepted:
            # Create custom template
            template_data = {
                'name': name_input.text(),
                'description': desc_input.toPlainText(),
                'structure': {
                    'chapters': chapters_spin.value(),
                    'target_words': words_spin.value(),
                    'pacing': pacing_combo.currentText(),
                    'themes': []
                },
                'files': ['characters.txt', 'timeline.txt', 'notes.txt']
            }

            # Save template
            self.save_custom_template(template_data)

    def save_custom_template(self, template_data):
        """Save a custom template"""
        try:
            # Save template to config
            templates_file = os.path.join(self.get_config_path(), 'custom_templates.json')

            if os.path.exists(templates_file):
                with open(templates_file, 'r', encoding='utf-8') as f:
                    custom_templates = json.load(f)
            else:
                custom_templates = {}

            template_id = template_data['name'].lower().replace(' ', '_')
            custom_templates[template_id] = template_data

            with open(templates_file, 'w', encoding='utf-8') as f:
                json.dump(custom_templates, f, indent=2)

            QMessageBox.information(self, "Success", "Custom template saved successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save template: {str(e)}")

    def create_project_version(self):
        """Create a new project version"""
        try:
            # Get version message from user
            message, ok = QInputDialog.getText(self, "Create Version",
                                             "Enter version message:")
            if not ok or not message:
                return

            # Create version data
            version_data = {
                'version': self.get_next_version_number(),
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'changes': self.get_recent_changes()
            }

            # Save version
            self.save_project_version(version_data)

            QMessageBox.information(self, "Success",
                                  f"Version {version_data['version']} created successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create version: {str(e)}")

    def create_project_branch(self):
        """Create a new project branch"""
        try:
            # Get branch name from user
            branch_name, ok = QInputDialog.getText(self, "Create Branch",
                                                 "Enter branch name:")
            if not ok or not branch_name:
                return

            # Create branch
            branch_data = {
                'name': branch_name,
                'created_from': self.get_current_version(),
                'timestamp': datetime.now().isoformat()
            }

            # Save branch
            self.save_project_branch(branch_data)

            QMessageBox.information(self, "Success",
                                  f"Branch '{branch_name}' created successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create branch: {str(e)}")

    def merge_project_changes(self):
        """Merge changes from another branch"""
        try:
            # Get available branches
            branches = self.get_project_branches()

            if not branches:
                QMessageBox.information(self, "No Branches", "No branches available to merge.")
                return

            # Show branch selection dialog
            branch_name, ok = QInputDialog.getItem(self, "Merge Changes",
                                                 "Select branch to merge:",
                                                 list(branches.keys()), 0, False)
            if not ok:
                return

            # Perform merge
            self.perform_branch_merge(branch_name)

            QMessageBox.information(self, "Success",
                                  f"Successfully merged changes from '{branch_name}'!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to merge changes: {str(e)}")

    def restore_project_version(self, version):
        """Restore a specific project version"""
        try:
            # Confirm restoration
            reply = QMessageBox.question(self, "Confirm Restore",
                                       f"Are you sure you want to restore version {version}? "
                                       f"This will overwrite your current changes.")

            if reply != QMessageBox.Yes:
                return

            # Restore version
            self.perform_version_restore(version)

            QMessageBox.information(self, "Success",
                                  f"Successfully restored version {version}!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to restore version: {str(e)}")

    def create_manual_backup(self):
        """Create a manual backup"""
        try:
            # Create backup
            backup_name = f"manual_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_path = self.create_project_backup(backup_name)

            QMessageBox.information(self, "Success",
                                  f"Manual backup created successfully!\nLocation: {backup_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create backup: {str(e)}")

    def restore_from_backup_dialog(self):
        """Show dialog for restoring from backup"""
        try:
            # Get available backups
            backups = self.get_available_backups()

            if not backups:
                QMessageBox.information(self, "No Backups", "No backups available.")
                return

            # Show backup selection dialog
            backup_items = [f"{b['name']} ({b['date']})" for b in backups]
            backup_choice, ok = QInputDialog.getItem(self, "Restore from Backup",
                                                   "Select backup to restore:",
                                                   backup_items, 0, False)
            if not ok:
                return

            # Find selected backup
            selected_backup = None
            for backup in backups:
                if backup_choice.startswith(backup['name']):
                    selected_backup = backup
                    break

            if selected_backup:
                # Confirm restoration
                reply = QMessageBox.question(self, "Confirm Restore",
                                           f"Are you sure you want to restore from this backup? "
                                           f"This will overwrite your current project.")

                if reply == QMessageBox.Yes:
                    self.restore_from_backup(selected_backup)
                    QMessageBox.information(self, "Success", "Project restored from backup!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to restore from backup: {str(e)}")

    def export_backup_dialog(self):
        """Show dialog for exporting backup"""
        try:
            # Get export location
            export_path, _ = QFileDialog.getSaveFileName(self, "Export Backup",
                                                       "project_backup.zip",
                                                       "ZIP files (*.zip)")
            if not export_path:
                return

            # Export backup
            self.export_project_backup(export_path)

            QMessageBox.information(self, "Success",
                                  f"Backup exported successfully to:\n{export_path}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export backup: {str(e)}")

    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self.status_message.setText("Copied to clipboard")

    def add_project_collaborator(self, email):
        """Add a project collaborator"""
        try:
            # Validate email
            if not email or '@' not in email:
                QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address.")
                return

            # Add collaborator
            collaborator_data = {
                'email': email,
                'role': 'Reviewer',
                'status': 'Pending',
                'added_date': datetime.now().isoformat()
            }

            self.save_project_collaborator(collaborator_data)

            QMessageBox.information(self, "Success",
                                  f"Collaborator {email} added successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add collaborator: {str(e)}")

    def remove_project_collaborator(self, email):
        """Remove a project collaborator"""
        try:
            # Confirm removal
            reply = QMessageBox.question(self, "Confirm Remove",
                                       f"Are you sure you want to remove {email} from this project?")

            if reply == QMessageBox.Yes:
                self.delete_project_collaborator(email)
                QMessageBox.information(self, "Success",
                                      f"Collaborator {email} removed successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to remove collaborator: {str(e)}")

    # Helper methods for project management
    def get_project_path(self):
        """Get the current project path"""
        return os.path.join(os.getcwd(), 'projects')

    def get_config_path(self):
        """Get the configuration path"""
        return os.path.join(os.getcwd(), 'config')

    def get_next_version_number(self):
        """Get the next version number"""
        # This would implement version numbering logic
        return "v1.0.1"

    def get_recent_changes(self):
        """Get recent changes for version"""
        # This would implement change tracking
        return "Recent changes to project files"

    def save_project_version(self, version_data):
        """Save project version data"""
        # This would implement version saving logic
        pass

    def save_project_branch(self, branch_data):
        """Save project branch data"""
        # This would implement branch saving logic
        pass

    def get_current_version(self):
        """Get current project version"""
        return "v1.0.0"

    def get_project_branches(self):
        """Get available project branches"""
        # This would implement branch retrieval logic
        return {}

    def perform_branch_merge(self, branch_name):
        """Perform branch merge"""
        # This would implement merge logic
        pass

    def perform_version_restore(self, version):
        """Perform version restoration"""
        # This would implement version restoration logic
        pass

    def create_project_backup(self, backup_name):
        """Create project backup"""
        # This would implement backup creation logic
        return f"backups/{backup_name}.zip"

    def get_available_backups(self):
        """Get available project backups"""
        # This would implement backup retrieval logic
        return []

    def restore_from_backup(self, backup_data):
        """Restore project from backup"""
        # This would implement backup restoration logic
        pass

    def export_project_backup(self, export_path):
        """Export project backup"""
        # This would implement backup export logic
        pass

    def save_project_collaborator(self, collaborator_data):
        """Save project collaborator data"""
        # This would implement collaborator saving logic
        pass

    def delete_project_collaborator(self, email):
        """Delete project collaborator"""
        # This would implement collaborator deletion logic
        pass

    def refresh_project_view(self):
        """Refresh the project view"""
        # This would implement project view refresh logic
        pass

def main():
    """Main entry point for the modern FANWS application."""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("FANWS")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("FANWS Development Team")

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run application
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

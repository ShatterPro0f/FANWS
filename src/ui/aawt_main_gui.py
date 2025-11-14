"""
Main GUI Implementation for AAWT
Comprehensive graphical user interface with sidebar navigation, content views, and real-time analysis.
"""

import sys
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit,
    QLineEdit, QComboBox, QSpinBox, QCheckBox, QTabWidget, QScrollArea,
    QSplitter, QMessageBox, QProgressBar, QListWidget, QListWidgetItem,
    QDialog, QDialogButtonBox, QFormLayout, QGroupBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette

logger = logging.getLogger(__name__)


class MainGUI(QWidget):
    """Main GUI widget with sidebar navigation and content views."""
    
    def __init__(self, settings_manager, database_manager, api_manager,
                 text_analyzer, export_manager, file_operations, workflow_manager=None,
                 grammar_analyzer=None):
        """
        Initialize main GUI.
        
        Args:
            settings_manager: Settings manager instance
            database_manager: Database manager instance
            api_manager: API manager instance
            text_analyzer: Text analyzer instance
            export_manager: Export manager instance
            file_operations: File operations instance
            workflow_manager: Workflow manager instance (optional)
            grammar_analyzer: Grammar analyzer instance (optional)
        """
        super().__init__()
        
        self.settings = settings_manager
        self.database = database_manager
        self.api = api_manager
        self.analyzer = text_analyzer
        self.exporter = export_manager
        self.files = file_operations
        self.workflow = workflow_manager
        self.grammar = grammar_analyzer
        
        self.current_project = None
        self.current_session = None
        self.auto_save_timer = None
        self.analysis_timer = None
        
        self.init_ui()
        self.apply_theme()
        self.start_timers()
        
        logger.info("Main GUI initialized")
    
    def init_ui(self):
        """Initialize user interface."""
        main_layout = QHBoxLayout()
        
        # Create sidebar (1/4 width)
        sidebar = self.create_sidebar()
        
        # Create content area (3/4 width)
        self.content_stack = self.create_content_stack()
        
        # Use splitter for resizable layout
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(sidebar)
        splitter.addWidget(self.content_stack)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
    
    def create_sidebar(self) -> QWidget:
        """Create navigation sidebar."""
        sidebar = QWidget()
        layout = QVBoxLayout()
        
        # Navigation buttons
        nav_buttons = [
            ("Dashboard", self.show_dashboard),
            ("Projects", self.show_projects),
            ("Writing Editor", self.show_editor),
            ("Workflow", self.show_workflow),
            ("Analytics", self.show_analytics),
            ("Settings", self.show_settings),
            ("Help", self.show_help)
        ]
        
        self.nav_buttons = {}
        for name, handler in nav_buttons:
            btn = QPushButton(name)
            btn.setMinimumHeight(40)
            btn.clicked.connect(handler)
            layout.addWidget(btn)
            self.nav_buttons[name] = btn
        
        layout.addStretch()
        
        # Project info at bottom
        self.project_label = QLabel("No project loaded")
        self.project_label.setWordWrap(True)
        self.project_label.setStyleSheet("padding: 10px; background: #f0f0f0; border-radius: 5px;")
        layout.addWidget(self.project_label)
        
        sidebar.setLayout(layout)
        sidebar.setMaximumWidth(250)
        return sidebar
    
    def create_content_stack(self) -> QTabWidget:
        """Create stacked content area."""
        stack = QTabWidget()
        stack.setTabsClosable(False)
        stack.setMovable(False)
        
        # Dashboard view
        self.dashboard_widget = self.create_dashboard()
        stack.addTab(self.dashboard_widget, "Dashboard")
        
        # Projects view
        self.projects_widget = self.create_projects_view()
        stack.addTab(self.projects_widget, "Projects")
        
        # Editor view
        self.editor_widget = self.create_editor()
        stack.addTab(self.editor_widget, "Editor")
        
        # Workflow view
        self.workflow_widget = self.create_workflow_view()
        stack.addTab(self.workflow_widget, "Workflow")
        
        # Analytics view
        self.analytics_widget = self.create_analytics()
        stack.addTab(self.analytics_widget, "Analytics")
        
        # Settings view
        self.settings_widget = self.create_settings()
        stack.addTab(self.settings_widget, "Settings")
        
        # Help view
        self.help_widget = self.create_help()
        stack.addTab(self.help_widget, "Help")
        
        return stack
    
    def create_dashboard(self) -> QWidget:
        """Create dashboard view."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Progress section
        progress_group = QGroupBox("Project Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        progress_layout.addWidget(self.progress_bar)
        
        self.word_count_label = QLabel("Word Count: 0 / 0")
        self.word_count_label.setStyleSheet("font-size: 14px; padding: 5px;")
        progress_layout.addWidget(self.word_count_label)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Recent activity
        activity_group = QGroupBox("Recent Activity")
        activity_layout = QVBoxLayout()
        
        self.activity_list = QListWidget()
        activity_layout.addWidget(self.activity_list)
        
        activity_group.setLayout(activity_layout)
        layout.addWidget(activity_group)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def create_projects_view(self) -> QWidget:
        """Create projects management view."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Title and buttons
        header = QHBoxLayout()
        title = QLabel("Projects")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()
        
        new_btn = QPushButton("New Project")
        new_btn.clicked.connect(self.create_new_project)
        header.addWidget(new_btn)
        
        load_btn = QPushButton("Load Project")
        load_btn.clicked.connect(self.load_project)
        header.addWidget(load_btn)
        
        delete_btn = QPushButton("Delete Project")
        delete_btn.clicked.connect(self.delete_project)
        header.addWidget(delete_btn)
        
        layout.addLayout(header)
        
        # Project list
        self.project_list = QListWidget()
        self.project_list.itemDoubleClicked.connect(self.on_project_double_click)
        layout.addWidget(self.project_list)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh List")
        refresh_btn.clicked.connect(self.refresh_project_list)
        layout.addWidget(refresh_btn)
        
        widget.setLayout(layout)
        return widget
    
    def create_editor(self) -> QWidget:
        """Create writing editor view."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Editor toolbar
        toolbar = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_current_project)
        toolbar.addWidget(save_btn)
        
        analyze_btn = QPushButton("Analyze Text")
        analyze_btn.clicked.connect(self.analyze_current_text)
        toolbar.addWidget(analyze_btn)
        
        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self.export_current_project)
        toolbar.addWidget(export_btn)
        
        toolbar.addStretch()
        
        # Word count display
        self.editor_word_count = QLabel("Words: 0")
        self.editor_word_count.setStyleSheet("font-weight: bold; padding: 5px;")
        toolbar.addWidget(self.editor_word_count)
        
        layout.addLayout(toolbar)
        
        # Text editor
        self.text_editor = QTextEdit()
        self.text_editor.setFont(QFont(
            self.settings.get('ui.font_family', 'Arial'),
            self.settings.get('ui.font_size', 11)
        ))
        self.text_editor.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.text_editor)
        
        # Analysis panel
        self.analysis_panel = QLabel("Text analysis will appear here")
        self.analysis_panel.setWordWrap(True)
        self.analysis_panel.setStyleSheet("background: #f9f9f9; padding: 10px; border: 1px solid #ddd;")
        self.analysis_panel.setMaximumHeight(150)
        layout.addWidget(self.analysis_panel)
        
        widget.setLayout(layout)
        return widget
    
    def create_workflow_view(self) -> QWidget:
        """Create automated workflow view."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        if self.workflow:
            # Import the automated novel GUI
            from .automated_novel_gui import AutomatedNovelGUI
            workflow_gui = AutomatedNovelGUI(self.workflow)
            layout.addWidget(workflow_gui)
        else:
            # Show message if workflow not available
            label = QLabel("Automated Workflow feature not available.\nWorkflow manager not initialized.")
            label.setStyleSheet("font-size: 16px; padding: 20px;")
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)
        
        widget.setLayout(layout)
        return widget
    
    def create_analytics(self) -> QWidget:
        """Create analytics view."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Analytics")
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Tabs for different analytics
        tabs = QTabWidget()
        
        # Text Analysis Tab
        text_tab = self.create_text_analysis_tab()
        tabs.addTab(text_tab, "Text Analysis")
        
        # API Usage Tab
        api_tab = self.create_api_usage_tab()
        tabs.addTab(api_tab, "API Usage")
        
        # Session Stats Tab
        session_tab = self.create_session_stats_tab()
        tabs.addTab(session_tab, "Session Stats")
        
        layout.addWidget(tabs)
        widget.setLayout(layout)
        return widget
    
    def create_text_analysis_tab(self) -> QWidget:
        """Create text analysis tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Analysis results
        self.analysis_text = QTextEdit()
        self.analysis_text.setReadOnly(True)
        layout.addWidget(self.analysis_text)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Analysis")
        refresh_btn.clicked.connect(self.refresh_text_analysis)
        layout.addWidget(refresh_btn)
        
        widget.setLayout(layout)
        return widget
    
    def create_api_usage_tab(self) -> QWidget:
        """Create API usage statistics tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Stats display
        self.api_stats_text = QTextEdit()
        self.api_stats_text.setReadOnly(True)
        layout.addWidget(self.api_stats_text)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Stats")
        refresh_btn.clicked.connect(self.refresh_api_stats)
        layout.addWidget(refresh_btn)
        
        widget.setLayout(layout)
        return widget
    
    def create_session_stats_tab(self) -> QWidget:
        """Create session statistics tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.session_stats_text = QTextEdit()
        self.session_stats_text.setReadOnly(True)
        layout.addWidget(self.session_stats_text)
        
        refresh_btn = QPushButton("Refresh Stats")
        refresh_btn.clicked.connect(self.refresh_session_stats)
        layout.addWidget(refresh_btn)
        
        widget.setLayout(layout)
        return widget
    
    def create_settings(self) -> QWidget:
        """Create settings view."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Settings tabs
        tabs = QTabWidget()
        
        # General settings
        general_tab = self.create_general_settings()
        tabs.addTab(general_tab, "General")
        
        # API settings
        api_tab = self.create_api_settings()
        tabs.addTab(api_tab, "API Keys")
        
        # Writing settings
        writing_tab = self.create_writing_settings()
        tabs.addTab(writing_tab, "Writing")
        
        # Theme settings
        theme_tab = self.create_theme_settings()
        tabs.addTab(theme_tab, "Theme")
        
        layout.addWidget(tabs)
        
        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)
        
        widget.setLayout(layout)
        return widget
    
    def create_general_settings(self) -> QWidget:
        """Create general settings tab."""
        widget = QWidget()
        layout = QFormLayout()
        
        # Auto-save interval
        self.autosave_spin = QSpinBox()
        self.autosave_spin.setMinimum(30)
        self.autosave_spin.setMaximum(3600)
        self.autosave_spin.setValue(self.settings.get('writing.auto_save_interval', 60))
        self.autosave_spin.setSuffix(" seconds")
        layout.addRow("Auto-save interval:", self.autosave_spin)
        
        # Font family
        self.font_family_combo = QComboBox()
        self.font_family_combo.addItems(['Arial', 'Times New Roman', 'Courier New', 'Calibri', 'Georgia'])
        self.font_family_combo.setCurrentText(self.settings.get('ui.font_family', 'Arial'))
        layout.addRow("Font family:", self.font_family_combo)
        
        # Font size
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setMinimum(8)
        self.font_size_spin.setMaximum(24)
        self.font_size_spin.setValue(self.settings.get('ui.font_size', 11))
        layout.addRow("Font size:", self.font_size_spin)
        
        widget.setLayout(layout)
        return widget
    
    def create_api_settings(self) -> QWidget:
        """Create API settings tab."""
        widget = QWidget()
        layout = QFormLayout()
        
        # OpenAI
        openai_group = QGroupBox("OpenAI")
        openai_layout = QVBoxLayout()
        
        self.openai_key_input = QLineEdit()
        self.openai_key_input.setEchoMode(QLineEdit.Password)
        self.openai_key_input.setText(self.settings.get('api.openai_key', ''))
        self.openai_key_input.setPlaceholderText("Enter OpenAI API key")
        openai_layout.addWidget(self.openai_key_input)
        
        openai_test_btn = QPushButton("Test Connection")
        openai_test_btn.clicked.connect(lambda: self.test_api_connection('openai'))
        openai_layout.addWidget(openai_test_btn)
        
        openai_group.setLayout(openai_layout)
        layout.addRow(openai_group)
        
        # Anthropic
        anthropic_group = QGroupBox("Anthropic (Claude)")
        anthropic_layout = QVBoxLayout()
        
        self.anthropic_key_input = QLineEdit()
        self.anthropic_key_input.setEchoMode(QLineEdit.Password)
        self.anthropic_key_input.setText(self.settings.get('api.anthropic_key', ''))
        self.anthropic_key_input.setPlaceholderText("Enter Anthropic API key")
        anthropic_layout.addWidget(self.anthropic_key_input)
        
        anthropic_test_btn = QPushButton("Test Connection")
        anthropic_test_btn.clicked.connect(lambda: self.test_api_connection('anthropic'))
        anthropic_layout.addWidget(anthropic_test_btn)
        
        anthropic_group.setLayout(anthropic_layout)
        layout.addRow(anthropic_group)
        
        # Google
        google_group = QGroupBox("Google (Gemini)")
        google_layout = QVBoxLayout()
        
        self.google_key_input = QLineEdit()
        self.google_key_input.setEchoMode(QLineEdit.Password)
        self.google_key_input.setText(self.settings.get('api.google_key', ''))
        self.google_key_input.setPlaceholderText("Enter Google API key")
        google_layout.addWidget(self.google_key_input)
        
        google_test_btn = QPushButton("Test Connection")
        google_test_btn.clicked.connect(lambda: self.test_api_connection('google'))
        google_layout.addWidget(google_test_btn)
        
        google_group.setLayout(google_layout)
        layout.addRow(google_group)
        
        # Ollama
        ollama_group = QGroupBox("Ollama (Local LLM)")
        ollama_layout = QVBoxLayout()
        
        ollama_info = QLabel("Ollama runs locally and doesn't require an API key.")
        ollama_info.setWordWrap(True)
        ollama_layout.addWidget(ollama_info)
        
        self.ollama_url_input = QLineEdit()
        self.ollama_url_input.setText(self.settings.get('api.ollama_url', 'http://localhost:11434'))
        self.ollama_url_input.setPlaceholderText("Ollama server URL")
        ollama_layout.addWidget(self.ollama_url_input)
        
        ollama_test_btn = QPushButton("Test Connection")
        ollama_test_btn.clicked.connect(lambda: self.test_api_connection('ollama'))
        ollama_layout.addWidget(ollama_test_btn)
        
        ollama_group.setLayout(ollama_layout)
        layout.addRow(ollama_group)
        
        # Default provider
        self.default_provider_combo = QComboBox()
        self.default_provider_combo.addItems(['openai', 'anthropic', 'google', 'ollama'])
        self.default_provider_combo.setCurrentText(self.settings.get('api.default_provider', 'openai'))
        layout.addRow("Default provider:", self.default_provider_combo)
        
        widget.setLayout(layout)
        return widget
    
    def create_writing_settings(self) -> QWidget:
        """Create writing settings tab."""
        widget = QWidget()
        layout = QFormLayout()
        
        # Default tone
        self.tone_combo = QComboBox()
        self.tone_combo.addItems(['Formal', 'Professional', 'Conversational', 'Creative', 'Academic'])
        self.tone_combo.setCurrentText(self.settings.get('writing.default_tone', 'Professional'))
        layout.addRow("Default tone:", self.tone_combo)
        
        # Default POV
        self.pov_combo = QComboBox()
        self.pov_combo.addItems(['First', 'Second', 'Third Limited', 'Omniscient'])
        self.pov_combo.setCurrentText(self.settings.get('writing.default_pov', 'Third Limited'))
        layout.addRow("Default POV:", self.pov_combo)
        
        # Default genre
        self.genre_combo = QComboBox()
        self.genre_combo.addItems(['Fiction', 'Fantasy', 'Science Fiction', 'Mystery', 'Romance', 'Horror'])
        self.genre_combo.setCurrentText(self.settings.get('writing.default_genre', 'Fiction'))
        layout.addRow("Default genre:", self.genre_combo)
        
        # Daily word goal
        self.daily_goal_spin = QSpinBox()
        self.daily_goal_spin.setMinimum(0)
        self.daily_goal_spin.setMaximum(100000)
        self.daily_goal_spin.setValue(self.settings.get('writing.daily_word_goal', 1000))
        layout.addRow("Daily word goal:", self.daily_goal_spin)
        
        # Enable features
        self.spell_check_box = QCheckBox()
        self.spell_check_box.setChecked(self.settings.get('writing.enable_spell_check', True))
        layout.addRow("Enable spell check:", self.spell_check_box)
        
        self.grammar_check_box = QCheckBox()
        self.grammar_check_box.setChecked(self.settings.get('writing.enable_grammar_check', True))
        layout.addRow("Enable grammar check:", self.grammar_check_box)
        
        widget.setLayout(layout)
        return widget
    
    def create_theme_settings(self) -> QWidget:
        """Create theme settings tab."""
        widget = QWidget()
        layout = QFormLayout()
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['light', 'dark'])
        self.theme_combo.setCurrentText(self.settings.get('ui.theme', 'light'))
        self.theme_combo.currentTextChanged.connect(self.apply_theme)
        layout.addRow("Theme:", self.theme_combo)
        
        # Primary color
        self.primary_color_input = QLineEdit()
        self.primary_color_input.setText(self.settings.get('ui.primary_color', '#2196F3'))
        layout.addRow("Primary color:", self.primary_color_input)
        
        widget.setLayout(layout)
        return widget
    
    def create_help(self) -> QWidget:
        """Create help view."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Help & Documentation")
        title.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        help_text = QTextEdit()
        help_text.setReadOnly(True)
        help_text.setHtml("""
        <h2>Welcome to AAWT (AI-Assisted Writing Tool)</h2>
        
        <h3>Getting Started</h3>
        <ol>
            <li><b>Create a Project:</b> Go to Projects > New Project</li>
            <li><b>Configure API Keys:</b> Go to Settings > API Keys to add your AI provider keys</li>
            <li><b>Start Writing:</b> Use the Editor tab to write your content</li>
            <li><b>Analyze Text:</b> Click "Analyze Text" to get readability and grammar insights</li>
            <li><b>Export:</b> Export your project in multiple formats (TXT, MD, DOCX, PDF, EPUB, JSON)</li>
        </ol>
        
        <h3>Features</h3>
        <ul>
            <li><b>Multi-Project Management:</b> Create and manage multiple writing projects</li>
            <li><b>Real-Time Analysis:</b> Get instant feedback on word count, readability, and style</li>
            <li><b>AI Integration:</b> Use OpenAI, Anthropic, Google, or Ollama for AI assistance</li>
            <li><b>Export Options:</b> Export to TXT, MD, DOCX, PDF, EPUB, and JSON formats</li>
            <li><b>Auto-Save:</b> Your work is automatically saved at regular intervals</li>
            <li><b>Analytics:</b> Track your writing progress and API usage</li>
        </ul>
        
        <h3>API Providers</h3>
        <ul>
            <li><b>OpenAI:</b> GPT-3.5, GPT-4 models</li>
            <li><b>Anthropic:</b> Claude models</li>
            <li><b>Google:</b> Gemini models</li>
            <li><b>Ollama:</b> Local LLMs (free, runs on your computer)</li>
        </ul>
        
        <h3>Keyboard Shortcuts</h3>
        <ul>
            <li><b>Ctrl+S:</b> Save current project</li>
            <li><b>Ctrl+N:</b> New project</li>
            <li><b>Ctrl+O:</b> Open project</li>
            <li><b>Ctrl+E:</b> Export project</li>
        </ul>
        
        <h3>Support</h3>
        <p>For more information, please refer to the README.md file.</p>
        """)
        layout.addWidget(help_text)
        
        widget.setLayout(layout)
        return widget
    
    # Navigation methods
    def show_dashboard(self):
        """Show dashboard view."""
        self.content_stack.setCurrentIndex(0)
        self.update_dashboard()
    
    def show_projects(self):
        """Show projects view."""
        self.content_stack.setCurrentIndex(1)
        self.refresh_project_list()
    
    def show_editor(self):
        """Show editor view."""
        self.content_stack.setCurrentIndex(2)
    
    def show_workflow(self):
        """Show workflow view."""
        self.content_stack.setCurrentIndex(3)
    
    def show_analytics(self):
        """Show analytics view."""
        self.content_stack.setCurrentIndex(4)
        self.refresh_text_analysis()
        self.refresh_api_stats()
    
    def show_settings(self):
        """Show settings view."""
        self.content_stack.setCurrentIndex(5)
    
    def show_help(self):
        """Show help view."""
        self.content_stack.setCurrentIndex(6)
    
    # Project management methods
    def create_new_project(self):
        """Create a new project."""
        dialog = QDialog(self)
        dialog.setWindowTitle("New Project")
        dialog.setModal(True)
        
        layout = QFormLayout()
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("Enter project name")
        layout.addRow("Project Name:", name_input)
        
        genre_combo = QComboBox()
        genre_combo.addItems(['Fiction', 'Fantasy', 'Science Fiction', 'Mystery', 'Romance', 'Horror', 'Non-Fiction'])
        layout.addRow("Genre:", genre_combo)
        
        target_spin = QSpinBox()
        target_spin.setMinimum(0)
        target_spin.setMaximum(1000000)
        target_spin.setValue(50000)
        layout.addRow("Target Words:", target_spin)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            name = name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Error", "Please enter a project name")
                return
            
            metadata = {
                'genre': genre_combo.currentText(),
                'target_audience': 'General',
                'created_by': 'user'
            }
            
            project_id = self.database.create_project(name, metadata)
            if project_id:
                # Create project structure
                self.files.create_project_structure(name)
                
                # Update project with target words
                self.database.update_project(project_id, target_words=target_spin.value())
                
                QMessageBox.information(self, "Success", f"Project '{name}' created successfully!")
                self.refresh_project_list()
                
                # Load the new project
                self.current_project = self.database.get_project(project_id)
                self.update_project_display()
            else:
                QMessageBox.critical(self, "Error", "Failed to create project. Project name may already exist.")
    
    def load_project(self):
        """Load selected project."""
        selected_items = self.project_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a project to load")
            return
        
        project_name = selected_items[0].text()
        project = self.database.get_project_by_name(project_name)
        
        if project:
            # Load content
            content = self.files.load_project_content(project_name)
            if content is None:
                content = ''
            
            self.current_project = project
            self.text_editor.setPlainText(content)
            self.update_project_display()
            
            # Start session
            self.current_session = self.database.start_session(project['id'])
            
            QMessageBox.information(self, "Success", f"Project '{project_name}' loaded successfully!")
            self.show_editor()
        else:
            QMessageBox.critical(self, "Error", "Failed to load project")
    
    def on_project_double_click(self, item):
        """Handle project double-click."""
        self.load_project()
    
    def delete_project(self):
        """Delete selected project."""
        selected_items = self.project_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a project to delete")
            return
        
        project_name = selected_items[0].text()
        
        reply = QMessageBox.question(
            self, 'Confirm Delete',
            f"Are you sure you want to delete project '{project_name}'?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            project = self.database.get_project_by_name(project_name)
            if project:
                # Delete from database
                self.database.delete_project(project['id'])
                
                # Delete files
                self.files.delete_project_files(project_name)
                
                QMessageBox.information(self, "Success", f"Project '{project_name}' deleted successfully!")
                self.refresh_project_list()
                
                # Clear current project if it was deleted
                if self.current_project and self.current_project['name'] == project_name:
                    self.current_project = None
                    self.text_editor.clear()
                    self.update_project_display()
    
    def refresh_project_list(self):
        """Refresh the project list."""
        self.project_list.clear()
        projects = self.database.list_projects()
        
        for project in projects:
            self.project_list.addItem(project['name'])
    
    def save_current_project(self):
        """Save current project."""
        if not self.current_project:
            QMessageBox.warning(self, "Warning", "No project loaded")
            return
        
        content = self.text_editor.toPlainText()
        
        # Save content to file
        self.files.save_project_content(self.current_project['name'], content)
        
        # Update word count in database
        analysis = self.analyzer.analyze_text(content)
        self.database.update_project(
            self.current_project['id'],
            word_count=analysis['word_count']
        )
        
        # Update current project data
        self.current_project['word_count'] = analysis['word_count']
        self.update_project_display()
        
        self.statusBar().showMessage("Project saved successfully", 3000)
    
    def export_current_project(self):
        """Export current project."""
        if not self.current_project:
            QMessageBox.warning(self, "Warning", "No project loaded")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Export Project")
        dialog.setModal(True)
        
        layout = QFormLayout()
        
        format_combo = QComboBox()
        formats = self.exporter.get_export_formats()
        format_combo.addItems([f['key'] for f in formats])
        layout.addRow("Format:", format_combo)
        
        metadata_check = QCheckBox()
        metadata_check.setChecked(True)
        layout.addRow("Include Metadata:", metadata_check)
        
        stats_check = QCheckBox()
        stats_check.setChecked(True)
        layout.addRow("Include Statistics:", stats_check)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        dialog.setLayout(layout)
        
        if dialog.exec_() == QDialog.Accepted:
            # Prepare project data
            project_data = self.current_project.copy()
            project_data['content'] = self.text_editor.toPlainText()
            
            # Export
            result = self.exporter.export_project(
                project_data,
                format_combo.currentText(),
                include_metadata=metadata_check.isChecked(),
                include_statistics=stats_check.isChecked()
            )
            
            if result.get('success'):
                QMessageBox.information(
                    self, "Success",
                    f"Project exported successfully to:\n{result['path']}"
                )
            else:
                QMessageBox.critical(
                    self, "Error",
                    f"Export failed:\n{result.get('error', 'Unknown error')}"
                )
    
    def analyze_current_text(self):
        """Analyze current text in editor."""
        if not self.text_editor.toPlainText():
            QMessageBox.warning(self, "Warning", "No text to analyze")
            return
        
        text = self.text_editor.toPlainText()
        analysis = self.analyzer.analyze_text(text)
        
        # Format analysis results
        results = []
        results.append(f"<h3>Text Analysis Results</h3>")
        results.append(f"<p><b>Word Count:</b> {analysis['word_count']}</p>")
        results.append(f"<p><b>Character Count:</b> {analysis['character_count']}</p>")
        results.append(f"<p><b>Sentence Count:</b> {analysis['sentence_count']}</p>")
        results.append(f"<p><b>Paragraph Count:</b> {analysis['paragraph_count']}</p>")
        results.append(f"<p><b>Average Words/Sentence:</b> {analysis['average_words_per_sentence']}</p>")
        results.append(f"<p><b>Readability Score:</b> {analysis['readability_score']} ({analysis['complexity_level']})</p>")
        results.append(f"<p><b>Grade Level:</b> {analysis['grade_level']}</p>")
        results.append(f"<p><b>Reading Time:</b> {analysis['reading_time_minutes']} minutes</p>")
        
        if analysis['repeated_words']:
            results.append(f"<h4>Repeated Words:</h4>")
            results.append("<ul>")
            for word, count in analysis['repeated_words'][:10]:
                results.append(f"<li>{word}: {count} times</li>")
            results.append("</ul>")
        
        if analysis['long_sentences']:
            results.append(f"<h4>Long Sentences (>{25} words):</h4>")
            results.append(f"<p>Found {len(analysis['long_sentences'])} long sentences</p>")
        
        self.analysis_panel.setText(''.join(results))
    
    def on_text_changed(self):
        """Handle text editor changes."""
        if self.text_editor.toPlainText():
            word_count = len(self.text_editor.toPlainText().split())
            self.editor_word_count.setText(f"Words: {word_count}")
    
    def update_project_display(self):
        """Update project information display."""
        if self.current_project:
            name = self.current_project['name']
            word_count = self.current_project.get('word_count', 0)
            target = self.current_project.get('target_words', 0)
            
            self.project_label.setText(
                f"<b>Current Project:</b><br>{name}<br>"
                f"<small>{word_count:,} / {target:,} words</small>"
            )
            
            # Update dashboard
            self.update_dashboard()
        else:
            self.project_label.setText("No project loaded")
    
    def update_dashboard(self):
        """Update dashboard with current project info."""
        if self.current_project:
            word_count = self.current_project.get('word_count', 0)
            target = self.current_project.get('target_words', 0)
            
            if target > 0:
                progress = int((word_count / target) * 100)
                self.progress_bar.setValue(progress)
                self.word_count_label.setText(f"Word Count: {word_count:,} / {target:,} ({progress}%)")
            else:
                self.progress_bar.setValue(0)
                self.word_count_label.setText(f"Word Count: {word_count:,} / No target set")
            
            # Update activity
            self.activity_list.clear()
            self.activity_list.addItem(f"Project loaded: {self.current_project['name']}")
            self.activity_list.addItem(f"Last modified: {self.current_project.get('last_modified', 'Unknown')}")
        else:
            self.progress_bar.setValue(0)
            self.word_count_label.setText("No project loaded")
    
    def refresh_text_analysis(self):
        """Refresh text analysis in analytics tab."""
        if not self.current_project or not self.text_editor.toPlainText():
            self.analysis_text.setPlainText("No text to analyze")
            return
        
        text = self.text_editor.toPlainText()
        analysis = self.analyzer.analyze_text(text)
        
        output = []
        output.append("=== TEXT ANALYSIS ===\n")
        output.append(f"Word Count: {analysis['word_count']}")
        output.append(f"Character Count: {analysis['character_count']}")
        output.append(f"Sentence Count: {analysis['sentence_count']}")
        output.append(f"Paragraph Count: {analysis['paragraph_count']}")
        output.append(f"Unique Words: {analysis['unique_words']}")
        output.append(f"Vocabulary Diversity: {analysis['vocabulary_diversity']}%")
        output.append(f"\nReadability Score: {analysis['readability_score']}")
        output.append(f"Complexity Level: {analysis['complexity_level']}")
        output.append(f"Grade Level: {analysis['grade_level']}")
        output.append(f"Reading Time: {analysis['reading_time_minutes']} minutes")
        
        if analysis['repeated_words']:
            output.append("\n=== REPEATED WORDS ===")
            for word, count in analysis['repeated_words'][:20]:
                output.append(f"{word}: {count} times")
        
        if analysis['long_sentences']:
            output.append(f"\n=== LONG SENTENCES ===")
            output.append(f"Found {len(analysis['long_sentences'])} sentences longer than 25 words")
        
        self.analysis_text.setPlainText('\n'.join(output))
    
    def refresh_api_stats(self):
        """Refresh API usage statistics."""
        stats = self.api.get_usage_stats(30)
        
        output = []
        output.append("=== API USAGE (Last 30 Days) ===\n")
        output.append(f"Total API Calls: {stats.get('total_calls', 0)}")
        output.append(f"Total Tokens: {stats.get('total_tokens', 0):,}")
        output.append(f"Total Cost: ${stats.get('total_cost', 0):.4f}")
        
        if stats.get('by_api'):
            output.append("\n=== By Provider ===")
            for api_stat in stats['by_api']:
                output.append(f"\n{api_stat['api_type'].upper()}:")
                output.append(f"  Calls: {api_stat['count']}")
                output.append(f"  Tokens: {api_stat.get('tokens', 0):,}")
                output.append(f"  Cost: ${api_stat.get('cost', 0):.4f}")
        
        self.api_stats_text.setPlainText('\n'.join(output))
    
    def refresh_session_stats(self):
        """Refresh session statistics."""
        if not self.current_project:
            self.session_stats_text.setPlainText("No project loaded")
            return
        
        stats = self.database.get_session_stats(self.current_project['id'], 30)
        
        output = []
        output.append("=== WRITING SESSIONS (Last 30 Days) ===\n")
        output.append(f"Total Sessions: {stats.get('total_sessions', 0)}")
        output.append(f"Total Words Written: {stats.get('total_words', 0):,}")
        output.append(f"Average Words/Session: {stats.get('avg_words', 0):.0f}")
        
        self.session_stats_text.setPlainText('\n'.join(output))
    
    def test_api_connection(self, provider: str):
        """Test API connection for a provider."""
        # Save current settings first
        self.save_api_settings()
        
        result = self.api.test_connection(provider)
        
        if result.get('success'):
            QMessageBox.information(
                self, "Success",
                f"{provider.upper()} connection successful!"
            )
        else:
            QMessageBox.critical(
                self, "Error",
                f"{provider.upper()} connection failed:\n{result.get('error', 'Unknown error')}"
            )
    
    def save_api_settings(self):
        """Save API settings temporarily (called before testing)."""
        self.settings.set('api.openai_key', self.openai_key_input.text())
        self.settings.set('api.anthropic_key', self.anthropic_key_input.text())
        self.settings.set('api.google_key', self.google_key_input.text())
        self.settings.set('api.ollama_url', self.ollama_url_input.text())
        self.settings.set('api.default_provider', self.default_provider_combo.currentText())
    
    def save_settings(self):
        """Save all settings."""
        # General
        self.settings.set('writing.auto_save_interval', self.autosave_spin.value())
        self.settings.set('ui.font_family', self.font_family_combo.currentText())
        self.settings.set('ui.font_size', self.font_size_spin.value())
        
        # API
        self.save_api_settings()
        
        # Writing
        self.settings.set('writing.default_tone', self.tone_combo.currentText())
        self.settings.set('writing.default_pov', self.pov_combo.currentText())
        self.settings.set('writing.default_genre', self.genre_combo.currentText())
        self.settings.set('writing.daily_word_goal', self.daily_goal_spin.value())
        self.settings.set('writing.enable_spell_check', self.spell_check_box.isChecked())
        self.settings.set('writing.enable_grammar_check', self.grammar_check_box.isChecked())
        
        # Theme
        self.settings.set('ui.theme', self.theme_combo.currentText())
        self.settings.set('ui.primary_color', self.primary_color_input.text())
        
        # Apply theme
        self.apply_theme()
        
        # Update font in editor
        self.text_editor.setFont(QFont(
            self.font_family_combo.currentText(),
            self.font_size_spin.value()
        ))
        
        QMessageBox.information(self, "Success", "Settings saved successfully!")
    
    def apply_theme(self):
        """Apply current theme to GUI."""
        theme = self.theme_combo.currentText() if hasattr(self, 'theme_combo') else self.settings.get('ui.theme', 'light')
        
        if theme == 'dark':
            # Dark theme
            self.setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #404040;
                    color: #ffffff;
                    border: 1px solid #555555;
                    padding: 8px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #505050;
                }
                QTextEdit, QLineEdit, QListWidget {
                    background-color: #353535;
                    color: #ffffff;
                    border: 1px solid #555555;
                }
                QTabWidget::pane {
                    border: 1px solid #555555;
                }
                QGroupBox {
                    border: 1px solid #555555;
                    margin-top: 10px;
                }
            """)
        else:
            # Light theme
            self.setStyleSheet("""
                QWidget {
                    background-color: #ffffff;
                    color: #000000;
                }
                QPushButton {
                    background-color: #f0f0f0;
                    color: #000000;
                    border: 1px solid #cccccc;
                    padding: 8px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
                QTextEdit, QLineEdit, QListWidget {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                }
                QTabWidget::pane {
                    border: 1px solid #cccccc;
                }
                QGroupBox {
                    border: 1px solid #cccccc;
                    margin-top: 10px;
                }
            """)
    
    def start_timers(self):
        """Start auto-save and analysis timers."""
        # Auto-save timer
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.auto_save)
        interval = self.settings.get('writing.auto_save_interval', 60) * 1000
        self.auto_save_timer.start(interval)
        
        # Analysis timer (update every 2 seconds)
        self.analysis_timer = QTimer()
        self.analysis_timer.timeout.connect(self.update_live_analysis)
        self.analysis_timer.start(2000)
    
    def auto_save(self):
        """Auto-save current project."""
        if self.current_project and self.text_editor.toPlainText():
            self.save_current_project()
    
    def update_live_analysis(self):
        """Update live analysis while typing."""
        if self.text_editor.toPlainText():
            # Just update word count for now
            word_count = len(self.text_editor.toPlainText().split())
            self.editor_word_count.setText(f"Words: {word_count}")
    
    def statusBar(self):
        """Get status bar (from main window)."""
        # This will be connected to the main window's status bar
        return self.window().statusBar() if self.window() else None
    
    def closeEvent(self, event):
        """Handle window close event."""
        # End current session
        if self.current_session:
            content = self.text_editor.toPlainText()
            word_count = len(content.split()) if content else 0
            self.database.end_session(self.current_session, word_count)
        
        # Unlock project
        if self.current_project:
            self.files.unlock_project(self.current_project['name'])
        
        event.accept()

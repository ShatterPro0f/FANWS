"""
Automated Novel Writing GUI for FANWS
Implements the specification from the problem statement for automated novel generation.

This module provides:
- Modern PyQt5 GUI with sidebar, central panel, and right panel
- Real-time progress tracking and visualization
- Step-by-step novel writing workflow
- Integration with AI tools and file management
"""

import os
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QPushButton, QLabel, QTextEdit, QProgressBar, QLineEdit,
    QSpinBox, QTabWidget, QTreeWidget, QTreeWidgetItem, QMessageBox,
    QStatusBar, QMenuBar, QAction, QFileDialog, QInputDialog,
    QFormLayout, QGroupBox, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QTextCharFormat, QColor, QSyntaxHighlighter

# Import workflow backend
try:
    from ..workflow.automated_novel_workflow import AutomatedNovelWorkflowThread
    WORKFLOW_AVAILABLE = True
except ImportError:
    WORKFLOW_AVAILABLE = False
    print("Warning: Automated novel workflow backend not available")


class LogHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for log files with color coding"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        
        # Info messages (white/default)
        info_format = QTextCharFormat()
        info_format.setForeground(QColor("#FFFFFF"))
        
        # Warning messages (yellow)
        warning_format = QTextCharFormat()
        warning_format.setForeground(QColor("#FFC107"))
        warning_format.setFontWeight(QFont.Bold)
        
        # Error messages (red)
        error_format = QTextCharFormat()
        error_format.setForeground(QColor("#F44336"))
        error_format.setFontWeight(QFont.Bold)
        
        self.highlighting_rules.append(("WARNING", warning_format))
        self.highlighting_rules.append(("ERROR", error_format))
        self.highlighting_rules.append(("FAILED", error_format))
        self.highlighting_rules.append(("SUCCESS", info_format))
    
    def highlightBlock(self, text):
        """Apply highlighting to a block of text"""
        for pattern, format in self.highlighting_rules:
            if pattern in text.upper():
                self.setFormat(0, len(text), format)
                return


class AutomatedNovelGUI(QMainWindow):
    """
    Main GUI for automated novel writing system.
    Implements the comprehensive workflow from the problem statement.
    """
    
    # Signals for workflow communication
    start_workflow_signal = pyqtSignal(dict)
    approve_signal = pyqtSignal()
    adjust_signal = pyqtSignal(str)
    pause_signal = pyqtSignal()
    resume_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize attributes
        self.current_project_dir = None
        self.current_step = "initialization"
        self.workflow_thread = None
        self.is_paused = False
        self.is_dark_theme = True  # Track current theme
        
        # Setup UI
        self.init_ui()
        self.apply_dark_theme()
        
    def init_ui(self):
        """Initialize the user interface following the specification"""
        self.setWindowTitle("FANWS - Automated Novel-Writing System")
        self.setGeometry(100, 100, 1600, 1000)
        self.setMinimumSize(1200, 800)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        
        # Left Sidebar (20%)
        self.sidebar = self.create_sidebar()
        splitter.addWidget(self.sidebar)
        
        # Central Panel (60%)
        self.central_panel = self.create_central_panel()
        splitter.addWidget(self.central_panel)
        
        # Right Panel (20%)
        self.right_panel = self.create_right_panel()
        splitter.addWidget(self.right_panel)
        
        # Set initial sizes (20%, 60%, 20%)
        total_width = 1600
        splitter.setSizes([int(total_width * 0.2), int(total_width * 0.6), int(total_width * 0.2)])
        
        main_layout.addWidget(splitter)
        
        # Bottom status bar
        self.create_status_bar()
        
    def create_menu_bar(self):
        """Create menu bar with File, View, and Help menus"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        export_action = QAction("Export Novel", self)
        export_action.triggered.connect(self.export_novel)
        file_menu.addAction(export_action)
        
        save_state_action = QAction("Save State", self)
        save_state_action.triggered.connect(self.save_state)
        file_menu.addAction(save_state_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        toggle_theme_action = QAction("Toggle Dark Mode", self)
        toggle_theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(toggle_theme_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        user_guide_action = QAction("User Guide", self)
        user_guide_action.triggered.connect(self.show_user_guide)
        help_menu.addAction(user_guide_action)
        
    def create_sidebar(self):
        """Create left sidebar with navigation buttons (20%)"""
        sidebar_widget = QFrame()
        sidebar_widget.setFrameShape(QFrame.StyledPanel)
        sidebar_widget.setMaximumWidth(320)
        
        layout = QVBoxLayout(sidebar_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Navigation buttons
        self.nav_buttons = {}
        nav_items = [
            ("Dashboard", self.show_dashboard),
            ("Story", self.show_story),
            ("Logs", self.show_logs),
            ("Config", self.show_config),
            ("Characters", self.show_characters),
            ("World", self.show_world),
            ("Summaries", self.show_summaries),
            ("Drafts", self.show_drafts)
        ]
        
        for name, callback in nav_items:
            btn = QPushButton(name)
            btn.setProperty("class", "nav-button")
            btn.setMinimumHeight(40)
            btn.clicked.connect(callback)
            layout.addWidget(btn)
            self.nav_buttons[name] = btn
        
        layout.addStretch()
        
        return sidebar_widget
    
    def create_central_panel(self):
        """Create central panel for dynamic content (60%)"""
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        # Tab widget for different views
        self.central_tabs = QTabWidget()
        self.central_tabs.setTabsClosable(False)
        
        # Initialization tab
        self.init_tab = self.create_initialization_tab()
        self.central_tabs.addTab(self.init_tab, "Initialization")
        
        # Planning tab (initially hidden)
        self.planning_tab = self.create_planning_tab()
        
        # Writing tab (initially hidden)
        self.writing_tab = self.create_writing_tab()
        
        layout.addWidget(self.central_tabs)
        
        return central_widget
    
    def create_initialization_tab(self):
        """Create initialization interface for user input"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Title
        title = QLabel("Initialize Novel Writing Project")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Novel Idea input
        self.idea_input = QTextEdit()
        self.idea_input.setPlaceholderText("Enter your novel idea (e.g., 'A hacker's rebellion in a dystopian city')")
        self.idea_input.setMaximumHeight(100)
        form_layout.addRow("Novel Idea:", self.idea_input)
        
        # Tone input
        self.tone_input = QLineEdit()
        self.tone_input.setPlaceholderText("Enter tone (e.g., 'dark and tense')")
        form_layout.addRow("Tone:", self.tone_input)
        
        # Soft Target Word Count
        self.target_input = QSpinBox()
        self.target_input.setRange(50000, 500000)
        self.target_input.setValue(250000)
        self.target_input.setSingleStep(10000)
        form_layout.addRow("Target Word Count:", self.target_input)
        
        layout.addLayout(form_layout)
        
        # Start button
        self.start_button = QPushButton("Start Novel Generation")
        self.start_button.setMinimumHeight(50)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.start_button.clicked.connect(self.start_novel_generation)
        layout.addWidget(self.start_button)
        
        layout.addStretch()
        
        return widget
    
    def create_planning_tab(self):
        """Create planning interface for synopsis, outline, characters, world"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Title
        title = QLabel("Planning Phase")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Content area
        self.planning_content = QTextEdit()
        self.planning_content.setReadOnly(True)
        layout.addWidget(self.planning_content)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.approve_planning_button = QPushButton("Approve")
        self.approve_planning_button.setMinimumHeight(40)
        self.approve_planning_button.clicked.connect(self.approve_current_step)
        button_layout.addWidget(self.approve_planning_button)
        
        self.adjust_planning_button = QPushButton("Adjust")
        self.adjust_planning_button.setMinimumHeight(40)
        self.adjust_planning_button.clicked.connect(self.adjust_current_step)
        button_layout.addWidget(self.adjust_planning_button)
        
        layout.addLayout(button_layout)
        
        return widget
    
    def create_writing_tab(self):
        """Create writing interface for section drafting and approval"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Title
        self.writing_title = QLabel("Writing Phase - Chapter 1, Section 1")
        self.writing_title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(self.writing_title)
        
        # Draft content
        self.draft_content = QTextEdit()
        self.draft_content.setReadOnly(True)
        layout.addWidget(self.draft_content)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.approve_section_button = QPushButton("Approve Section")
        self.approve_section_button.setMinimumHeight(40)
        self.approve_section_button.clicked.connect(self.approve_section)
        button_layout.addWidget(self.approve_section_button)
        
        self.adjust_section_button = QPushButton("Adjust Section")
        self.adjust_section_button.setMinimumHeight(40)
        self.adjust_section_button.clicked.connect(self.adjust_section)
        button_layout.addWidget(self.adjust_section_button)
        
        self.pause_button = QPushButton("Pause")
        self.pause_button.setMinimumHeight(40)
        self.pause_button.clicked.connect(self.pause_workflow)
        button_layout.addWidget(self.pause_button)
        
        layout.addLayout(button_layout)
        
        return widget
    
    def create_right_panel(self):
        """Create right panel for real-time dashboard (20%)"""
        right_widget = QWidget()
        right_widget.setMaximumWidth(320)
        layout = QVBoxLayout(right_widget)
        
        # Dashboard title
        title = QLabel("Dashboard")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Progress section
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.word_count_label = QLabel("Word Count: 0 / 250,000")
        progress_layout.addWidget(self.word_count_label)
        
        self.chapter_label = QLabel("Chapter: 0 / 0")
        progress_layout.addWidget(self.chapter_label)
        
        self.section_label = QLabel("Section: 0 / 0")
        progress_layout.addWidget(self.section_label)
        
        layout.addWidget(progress_group)
        
        # Mood meter section
        mood_group = QGroupBox("Mood & Pacing")
        mood_layout = QVBoxLayout(mood_group)
        
        self.mood_label = QLabel("Tension: 0%")
        mood_layout.addWidget(self.mood_label)
        
        self.pacing_label = QLabel("Pacing: Steady")
        mood_layout.addWidget(self.pacing_label)
        
        layout.addWidget(mood_group)
        
        # Notifications section
        notifications_group = QGroupBox("Notifications")
        notifications_layout = QVBoxLayout(notifications_group)
        
        self.notifications_list = QTextEdit()
        self.notifications_list.setReadOnly(True)
        self.notifications_list.setMaximumHeight(150)
        notifications_layout.addWidget(self.notifications_list)
        
        layout.addWidget(notifications_group)
        
        layout.addStretch()
        
        return right_widget
    
    def create_status_bar(self):
        """Create bottom status bar with controls"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # Status label
        self.status_label = QLabel("Status: Ready")
        status_bar.addWidget(self.status_label)
        
        status_bar.addPermanentWidget(QLabel("  |  "))
        
        # Resume button
        self.resume_button = QPushButton("Resume")
        self.resume_button.clicked.connect(self.resume_workflow)
        self.resume_button.setEnabled(False)
        status_bar.addPermanentWidget(self.resume_button)
        
        # Stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_workflow)
        self.stop_button.setEnabled(False)
        status_bar.addPermanentWidget(self.stop_button)
    
    # ============ Navigation Methods ============
    
    def show_dashboard(self):
        """Show dashboard view"""
        self.set_active_nav_button("Dashboard")
        # Dashboard is always visible in right panel
        QMessageBox.information(self, "Dashboard", "Dashboard is visible in the right panel.")
    
    def show_story(self):
        """Show story content"""
        self.set_active_nav_button("Story")
        self.update_central_panel_with_file("story.txt", "Story Content")
    
    def show_logs(self):
        """Show log content"""
        self.set_active_nav_button("Logs")
        self.update_central_panel_with_file("log.txt", "Logs", use_highlighter=True)
    
    def show_config(self):
        """Show config content"""
        self.set_active_nav_button("Config")
        self.update_central_panel_with_file("config.txt", "Configuration")
    
    def show_characters(self):
        """Show characters in structured view"""
        self.set_active_nav_button("Characters")
        self.update_central_panel_with_json("characters.txt", "Characters")
    
    def show_world(self):
        """Show world details in structured view"""
        self.set_active_nav_button("World")
        self.update_central_panel_with_json("world.txt", "World Building")
    
    def show_summaries(self):
        """Show summaries"""
        self.set_active_nav_button("Summaries")
        self.update_central_panel_with_file("summaries.txt", "Chapter Summaries")
    
    def show_drafts(self):
        """Show drafts tree view"""
        self.set_active_nav_button("Drafts")
        self.update_central_panel_with_drafts_tree()
    
    def set_active_nav_button(self, name):
        """Set active state for navigation button"""
        for btn_name, btn in self.nav_buttons.items():
            if btn_name == name:
                btn.setProperty("active", True)
            else:
                btn.setProperty("active", False)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
    
    def update_central_panel_with_file(self, filename, title, use_highlighter=False):
        """Update central panel to show file content"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        # Apply syntax highlighter if requested
        if use_highlighter:
            highlighter = LogHighlighter(text_edit.document())
        
        # Load file content
        if self.current_project_dir:
            filepath = os.path.join(self.current_project_dir, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    text_edit.setPlainText(content)
                except Exception as e:
                    text_edit.setPlainText(f"Error loading file: {str(e)}")
            else:
                text_edit.setPlainText(f"File not found: {filename}")
        else:
            text_edit.setPlainText("No project loaded.")
        
        layout.addWidget(text_edit)
        
        # Replace current central tab
        self.central_tabs.clear()
        self.central_tabs.addTab(widget, title)
    
    def update_central_panel_with_json(self, filename, title):
        """Update central panel to show JSON content in structured view"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        
        # Load and format JSON content
        if self.current_project_dir:
            filepath = os.path.join(self.current_project_dir, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    # Try to parse and pretty-print JSON
                    if content.strip():
                        try:
                            json_data = json.loads(content)
                            formatted = json.dumps(json_data, indent=2)
                            text_edit.setPlainText(formatted)
                        except json.JSONDecodeError:
                            text_edit.setPlainText(content)
                    else:
                        text_edit.setPlainText("(Empty file)")
                except Exception as e:
                    text_edit.setPlainText(f"Error loading file: {str(e)}")
            else:
                text_edit.setPlainText(f"File not found: {filename}")
        else:
            text_edit.setPlainText("No project loaded.")
        
        layout.addWidget(text_edit)
        
        # Replace current central tab
        self.central_tabs.clear()
        self.central_tabs.addTab(widget, title)
    
    def update_central_panel_with_drafts_tree(self):
        """Update central panel to show drafts in a tree view"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        title_label = QLabel("Draft Versions")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title_label)
        
        # Create tree widget
        tree = QTreeWidget()
        tree.setHeaderLabels(["Draft", "Size", "Modified"])
        tree.setColumnWidth(0, 300)
        
        # Load drafts from project directory
        if self.current_project_dir:
            drafts_dir = os.path.join(self.current_project_dir, "drafts")
            if os.path.exists(drafts_dir) and os.path.isdir(drafts_dir):
                try:
                    # List all chapter folders
                    chapters = sorted([d for d in os.listdir(drafts_dir) 
                                     if os.path.isdir(os.path.join(drafts_dir, d))])
                    
                    for chapter in chapters:
                        chapter_path = os.path.join(drafts_dir, chapter)
                        chapter_item = QTreeWidgetItem([chapter, "", ""])
                        
                        # List all draft files in chapter
                        drafts = sorted([f for f in os.listdir(chapter_path) 
                                       if os.path.isfile(os.path.join(chapter_path, f))])
                        
                        for draft in drafts:
                            draft_path = os.path.join(chapter_path, draft)
                            # Get file stats
                            stat = os.stat(draft_path)
                            size = f"{stat.st_size} bytes"
                            modified = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                            
                            draft_item = QTreeWidgetItem([draft, size, modified])
                            chapter_item.addChild(draft_item)
                        
                        tree.addTopLevelItem(chapter_item)
                        chapter_item.setExpanded(True)
                    
                    if not chapters:
                        info_item = QTreeWidgetItem(["No drafts found", "", ""])
                        tree.addTopLevelItem(info_item)
                        
                except Exception as e:
                    error_item = QTreeWidgetItem([f"Error loading drafts: {str(e)}", "", ""])
                    tree.addTopLevelItem(error_item)
            else:
                info_item = QTreeWidgetItem(["Drafts folder not found", "", ""])
                tree.addTopLevelItem(info_item)
        else:
            info_item = QTreeWidgetItem(["No project loaded", "", ""])
            tree.addTopLevelItem(info_item)
        
        layout.addWidget(tree)
        
        # Add text preview area
        preview_label = QLabel("Preview:")
        preview_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(preview_label)
        
        preview_text = QTextEdit()
        preview_text.setReadOnly(True)
        preview_text.setMaximumHeight(200)
        layout.addWidget(preview_text)
        
        # Connect tree selection to preview
        def on_selection_changed():
            items = tree.selectedItems()
            if items and items[0].parent():  # Only show preview for files, not folders
                chapter = items[0].parent().text(0)
                draft = items[0].text(0)
                draft_path = os.path.join(self.current_project_dir, "drafts", chapter, draft)
                if os.path.exists(draft_path):
                    try:
                        with open(draft_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        # Show first 500 characters
                        preview_text.setPlainText(content[:500] + ("..." if len(content) > 500 else ""))
                    except Exception as e:
                        preview_text.setPlainText(f"Error loading preview: {str(e)}")
        
        tree.itemSelectionChanged.connect(on_selection_changed)
        
        # Replace current central tab
        self.central_tabs.clear()
        self.central_tabs.addTab(widget, "Draft Versions")
    
    # ============ Workflow Methods ============
    
    def start_novel_generation(self):
        """Start the novel generation workflow"""
        # Get input values
        idea = self.idea_input.toPlainText().strip()
        tone = self.tone_input.text().strip()
        target = self.target_input.value()
        
        # Validate inputs
        if not idea:
            QMessageBox.warning(self, "Input Required", "Please enter a novel idea.")
            return
        if not tone:
            QMessageBox.warning(self, "Input Required", "Please enter a tone.")
            return
        
        # Create project directory
        project_name = f"novel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_project_dir = os.path.join(os.getcwd(), "projects", project_name)
        os.makedirs(self.current_project_dir, exist_ok=True)
        
        # Initialize files
        self.initialize_project_files(idea, tone, target)
        
        # Update UI
        self.status_label.setText("Status: Initializing...")
        self.add_notification("Project initialized")
        
        # Log to file
        self.log_message(f"System initialized. Idea: {idea}. Tone: {tone}. Target: {target}")
        
        # Switch to planning tab
        self.central_tabs.clear()
        self.central_tabs.addTab(self.planning_tab, "Planning")
        
        # Start background workflow thread if available
        if WORKFLOW_AVAILABLE:
            self.workflow_thread = AutomatedNovelWorkflowThread(
                self.current_project_dir,
                idea,
                tone,
                target
            )
            
            # Connect signals
            self.workflow_thread.log_update.connect(self.on_log_update)
            self.workflow_thread.new_synopsis.connect(self.on_new_synopsis)
            self.workflow_thread.new_outline.connect(self.on_new_outline)
            self.workflow_thread.new_characters.connect(self.on_new_characters)
            self.workflow_thread.new_world.connect(self.on_new_world)
            self.workflow_thread.new_draft.connect(self.on_new_draft)
            self.workflow_thread.progress_updated.connect(self.on_progress_updated)
            self.workflow_thread.status_updated.connect(self.on_status_updated)
            self.workflow_thread.error_signal.connect(self.on_error)
            self.workflow_thread.waiting_approval.connect(self.on_waiting_approval)
            self.workflow_thread.workflow_completed.connect(self.on_workflow_completed)
            
            # Connect GUI signals to workflow
            self.approve_signal.connect(self.workflow_thread.approve_current_step)
            self.adjust_signal.connect(self.workflow_thread.adjust_current_step)
            self.pause_signal.connect(self.workflow_thread.pause)
            self.resume_signal.connect(self.workflow_thread.resume)
            
            # Start workflow
            self.workflow_thread.start()
            self.stop_button.setEnabled(True)
            self.pause_button.setEnabled(True)
            
            self.add_notification("Workflow started - generating synopsis...")
        else:
            # Show demo message if workflow not available
            QMessageBox.information(
                self,
                "Workflow Started (Demo Mode)",
                f"Novel generation started!\n\nIdea: {idea}\nTone: {tone}\nTarget: {target:,} words\n\nProject: {project_name}\n\n(Full workflow backend coming soon)"
            )
    
    def initialize_project_files(self, idea, tone, target):
        """Initialize project files as specified"""
        if not self.current_project_dir:
            return
        
        # Create story.txt
        with open(os.path.join(self.current_project_dir, "story.txt"), 'w', encoding='utf-8') as f:
            f.write("")
        
        # Create log.txt
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(os.path.join(self.current_project_dir, "log.txt"), 'w', encoding='utf-8') as f:
            f.write(f"{timestamp} - System initialized.\n")
        
        # Create config.txt
        config_content = f"""Idea: {idea}
Tone: {tone}
SoftTarget: {target}
TotalChapters: 0
CurrentChapter: 0
CurrentSection: 0
Progress: 0%
ToolWeights: Sassbook:0.5,DeepL:0.5,Thesaurus:0.5,Grammarly:0.5
"""
        with open(os.path.join(self.current_project_dir, "config.txt"), 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        # Create context.txt
        with open(os.path.join(self.current_project_dir, "context.txt"), 'w', encoding='utf-8') as f:
            f.write(f"Novel started: {idea}. Initial tone: {tone}.\n")
        
        # Create empty JSON files
        for filename in ["characters.txt", "world.txt"]:
            with open(os.path.join(self.current_project_dir, filename), 'w', encoding='utf-8') as f:
                f.write("")
        
        # Create summaries.txt
        with open(os.path.join(self.current_project_dir, "summaries.txt"), 'w', encoding='utf-8') as f:
            f.write("")
        
        # Create weights.txt
        with open(os.path.join(self.current_project_dir, "weights.txt"), 'w', encoding='utf-8') as f:
            f.write("Sassbook AI,0.5;DeepL Write,0.5;Thesaurus API,0.5;Grammarly,0.5\n")
        
        # Create drafts directory
        os.makedirs(os.path.join(self.current_project_dir, "drafts"), exist_ok=True)
        
        # Create backup files
        for filename in ["buffer_backup.txt", "story_backup.txt", "log_backup.txt"]:
            with open(os.path.join(self.current_project_dir, filename), 'w', encoding='utf-8') as f:
                f.write("")
    
    def log_message(self, message):
        """Log a message to log.txt"""
        if not self.current_project_dir:
            return
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {message}\n"
        
        log_path = os.path.join(self.current_project_dir, "log.txt")
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def add_notification(self, message):
        """Add a notification to the notifications panel"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        current = self.notifications_list.toPlainText()
        new_text = f"[{timestamp}] {message}\n{current}"
        self.notifications_list.setPlainText(new_text)
    
    def approve_current_step(self):
        """Approve current planning step"""
        self.approve_signal.emit()
        self.add_notification("Step approved")
        # TODO: Implement step-specific logic
    
    def adjust_current_step(self):
        """Request adjustment to current planning step"""
        text, ok = QInputDialog.getMultiLineText(
            self,
            "Adjust Content",
            "Enter your feedback for adjustments:"
        )
        if ok and text:
            self.adjust_signal.emit(text)
            self.add_notification("Adjustment requested")
    
    def approve_section(self):
        """Approve current section"""
        self.approve_signal.emit()
        self.add_notification("Section approved")
    
    def adjust_section(self):
        """Request adjustment to current section"""
        text, ok = QInputDialog.getMultiLineText(
            self,
            "Adjust Section",
            "Enter your changes for this section:"
        )
        if ok and text:
            self.adjust_signal.emit(text)
            self.add_notification("Section adjustment requested")
    
    def pause_workflow(self):
        """Pause the workflow"""
        self.pause_signal.emit()
        self.is_paused = True
        self.status_label.setText("Status: Paused")
        self.resume_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.add_notification("Workflow paused")
    
    def resume_workflow(self):
        """Resume the workflow"""
        self.resume_signal.emit()
        self.is_paused = False
        self.status_label.setText("Status: Writing...")
        self.resume_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.add_notification("Workflow resumed")
    
    def stop_workflow(self):
        """Stop the workflow"""
        reply = QMessageBox.question(
            self,
            "Stop Workflow",
            "Are you sure you want to stop the workflow?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if self.workflow_thread:
                self.workflow_thread.stop()
            self.status_label.setText("Status: Stopped")
            self.stop_button.setEnabled(False)
            self.add_notification("Workflow stopped")
    
    # ============ Workflow Signal Handlers ============
    
    def on_log_update(self, message: str):
        """Handle log update from workflow"""
        # Display in notifications
        self.add_notification(message.split(" - ", 1)[-1])
    
    def on_new_synopsis(self, synopsis: str):
        """Handle new synopsis from workflow"""
        self.planning_content.setPlainText(synopsis)
        self.add_notification("Synopsis generated - please review")
    
    def on_new_outline(self, outline: str):
        """Handle new outline from workflow"""
        self.planning_content.setPlainText(outline)
        self.add_notification("Outline generated - please review")
    
    def on_new_characters(self, characters: str):
        """Handle new characters from workflow"""
        self.planning_content.setPlainText(characters)
        self.add_notification("Characters generated - please review")
    
    def on_new_world(self, world: str):
        """Handle new world details from workflow"""
        self.planning_content.setPlainText(world)
        self.add_notification("World details generated - please review")
    
    def on_new_draft(self, chapter: int, section: int, content: str):
        """Handle new section draft from workflow"""
        # Switch to writing tab if not already there
        if self.central_tabs.count() == 0 or self.central_tabs.tabText(0) != "Writing":
            self.central_tabs.clear()
            self.central_tabs.addTab(self.writing_tab, "Writing")
        
        # Update title and content
        self.writing_title.setText(f"Writing Phase - Chapter {chapter}, Section {section}")
        self.draft_content.setPlainText(content)
        
        # Update dashboard
        self.chapter_label.setText(f"Chapter: {chapter} / {self.workflow_thread.total_chapters if self.workflow_thread else 0}")
        self.section_label.setText(f"Section: {section} / {self.workflow_thread.sections_per_chapter if self.workflow_thread else 0}")
        
        self.add_notification(f"Chapter {chapter}, Section {section} drafted - please review")
    
    def on_progress_updated(self, progress: int):
        """Handle progress update from workflow"""
        self.progress_bar.setValue(progress)
        
        # Update word count (estimate based on progress)
        if self.workflow_thread:
            estimated_words = int((progress / 100) * self.workflow_thread.target_words)
            self.word_count_label.setText(
                f"Word Count: {estimated_words:,} / {self.workflow_thread.target_words:,}"
            )
    
    def on_status_updated(self, status: str):
        """Handle status update from workflow"""
        self.status_label.setText(f"Status: {status}")
    
    def on_error(self, error: str):
        """Handle error from workflow"""
        QMessageBox.critical(self, "Workflow Error", error)
        self.add_notification(f"ERROR: {error}")
    
    def on_waiting_approval(self, step_name: str):
        """Handle workflow waiting for approval"""
        self.add_notification(f"Waiting for approval: {step_name}")
    
    def on_workflow_completed(self):
        """Handle workflow completion"""
        self.status_label.setText("Status: Complete!")
        self.progress_bar.setValue(100)
        self.stop_button.setEnabled(False)
        self.pause_button.setEnabled(False)
        QMessageBox.information(
            self,
            "Workflow Complete",
            "Novel generation complete!\n\nYou can now export your novel via File > Export Novel."
        )
        self.add_notification("Workflow completed successfully!")
    
    # ============ Menu Actions ============
    
    def export_novel(self):
        """Export novel to various formats"""
        if not self.current_project_dir:
            QMessageBox.warning(self, "No Project", "No project loaded to export.")
            return
        
        story_path = os.path.join(self.current_project_dir, "story.txt")
        if not os.path.exists(story_path):
            QMessageBox.warning(self, "No Content", "No story content to export.")
            return
        
        # Get export filename
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Novel",
            "",
            "Word Document (*.docx);;PDF (*.pdf);;Text File (*.txt)"
        )
        
        if filename:
            try:
                with open(story_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if filename.endswith('.docx'):
                    from docx import Document
                    doc = Document()
                    doc.add_paragraph(content)
                    doc.save(filename)
                elif filename.endswith('.pdf'):
                    from reportlab.lib.pagesizes import letter
                    from reportlab.platypus import SimpleDocTemplate, Paragraph
                    from reportlab.lib.styles import getSampleStyleSheet
                    
                    doc = SimpleDocTemplate(filename, pagesize=letter)
                    styles = getSampleStyleSheet()
                    story_paragraphs = [Paragraph(line, styles['Normal']) for line in content.split('\n')]
                    doc.build(story_paragraphs)
                else:
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                QMessageBox.information(self, "Export Successful", f"Novel exported to: {filename}")
                self.log_message(f"Novel exported to: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Error exporting novel: {str(e)}")
    
    def save_state(self):
        """Save current state"""
        if self.current_project_dir:
            self.log_message("State saved manually")
            QMessageBox.information(self, "Save State", "Current state saved.")
        else:
            QMessageBox.warning(self, "No Project", "No project loaded to save.")
    
    def toggle_theme(self):
        """Toggle between dark and light themes"""
        self.is_dark_theme = not self.is_dark_theme
        if self.is_dark_theme:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
    
    def show_user_guide(self):
        """Show user guide"""
        guide_text = """
FANWS - Automated Novel-Writing System User Guide

1. Initialization:
   - Enter your novel idea
   - Specify the tone (e.g., "dark and tense")
   - Set target word count
   - Click "Start Novel Generation"

2. Planning Phase:
   - Review generated synopsis
   - Approve or adjust with feedback
   - Review outline, characters, world building
   - Approve each element

3. Writing Phase:
   - Review generated sections
   - Approve sections to move forward
   - Adjust sections with specific feedback
   - Pause/resume as needed

4. Navigation:
   - Use sidebar buttons to view different files
   - Dashboard shows real-time progress
   - Logs display system activity
   
5. Export:
   - File > Export Novel to save as DOCX, PDF, or TXT
        """
        QMessageBox.information(self, "User Guide", guide_text)
    
    def apply_light_theme(self):
        """Apply light theme styling"""
        light_stylesheet = """
        QMainWindow {
            background-color: #ffffff;
            color: #212121;
        }
        QWidget {
            background-color: #ffffff;
            color: #212121;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 11pt;
        }
        QFrame {
            background-color: #f5f5f5;
            border: 1px solid #e0e0e0;
        }
        QPushButton {
            background-color: #f5f5f5;
            color: #212121;
            border: 1px solid #bdbdbd;
            padding: 8px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #e0e0e0;
        }
        QPushButton:pressed {
            background-color: #d0d0d0;
        }
        QPushButton[class="nav-button"] {
            background-color: transparent;
            color: #212121;
            text-align: left;
            padding: 12px 16px;
            border: none;
            border-radius: 0px;
        }
        QPushButton[class="nav-button"]:hover {
            background-color: #e3f2fd;
        }
        QPushButton[active="true"] {
            background-color: #2196F3;
            color: white;
        }
        QTextEdit, QLineEdit, QSpinBox {
            background-color: #ffffff;
            color: #212121;
            border: 1px solid #bdbdbd;
            padding: 4px;
        }
        QLabel {
            background-color: transparent;
            color: #212121;
        }
        QGroupBox {
            border: 1px solid #bdbdbd;
            border-radius: 4px;
            margin-top: 8px;
            padding-top: 8px;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 3px;
        }
        QProgressBar {
            border: 1px solid #bdbdbd;
            border-radius: 4px;
            text-align: center;
            background-color: #f5f5f5;
        }
        QProgressBar::chunk {
            background-color: #2196F3;
        }
        QMenuBar {
            background-color: #f5f5f5;
            color: #212121;
        }
        QMenuBar::item:selected {
            background-color: #e0e0e0;
        }
        QMenu {
            background-color: #ffffff;
            color: #212121;
            border: 1px solid #bdbdbd;
        }
        QMenu::item:selected {
            background-color: #e0e0e0;
        }
        QStatusBar {
            background-color: #f5f5f5;
            color: #212121;
        }
        QTabWidget::pane {
            border: 1px solid #bdbdbd;
            background-color: #ffffff;
        }
        QTabBar::tab {
            background-color: #f5f5f5;
            color: #212121;
            padding: 8px 16px;
            border: 1px solid #bdbdbd;
        }
        QTabBar::tab:selected {
            background-color: #e0e0e0;
        }
        """
        self.setStyleSheet(light_stylesheet)
    
    def apply_dark_theme(self):
        """Apply dark theme styling"""
        dark_stylesheet = """
        QMainWindow {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
        QWidget {
            background-color: #1e1e1e;
            color: #e0e0e0;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 11pt;
        }
        QFrame {
            background-color: #252525;
            border: 1px solid #3d3d3d;
        }
        QPushButton {
            background-color: #3d3d3d;
            color: #e0e0e0;
            border: 1px solid #5d5d5d;
            padding: 8px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #4d4d4d;
        }
        QPushButton:pressed {
            background-color: #2d2d2d;
        }
        QPushButton[class="nav-button"] {
            background-color: transparent;
            color: white;
            text-align: left;
            padding: 12px 16px;
            border: none;
            border-radius: 0px;
        }
        QPushButton[class="nav-button"]:hover {
            background-color: #37474F;
        }
        QPushButton[active="true"] {
            background-color: #2196F3;
        }
        QTextEdit, QLineEdit, QSpinBox {
            background-color: #2d2d2d;
            color: #e0e0e0;
            border: 1px solid #3d3d3d;
            padding: 4px;
        }
        QLabel {
            background-color: transparent;
            color: #e0e0e0;
        }
        QGroupBox {
            border: 1px solid #3d3d3d;
            border-radius: 4px;
            margin-top: 8px;
            padding-top: 8px;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 3px;
        }
        QProgressBar {
            border: 1px solid #3d3d3d;
            border-radius: 4px;
            text-align: center;
            background-color: #2d2d2d;
        }
        QProgressBar::chunk {
            background-color: #2196F3;
        }
        QMenuBar {
            background-color: #252525;
            color: #e0e0e0;
        }
        QMenuBar::item:selected {
            background-color: #3d3d3d;
        }
        QMenu {
            background-color: #252525;
            color: #e0e0e0;
            border: 1px solid #3d3d3d;
        }
        QMenu::item:selected {
            background-color: #3d3d3d;
        }
        QStatusBar {
            background-color: #252525;
            color: #e0e0e0;
        }
        QTabWidget::pane {
            border: 1px solid #3d3d3d;
            background-color: #1e1e1e;
        }
        QTabBar::tab {
            background-color: #2d2d2d;
            color: #e0e0e0;
            padding: 8px 16px;
            border: 1px solid #3d3d3d;
        }
        QTabBar::tab:selected {
            background-color: #3d3d3d;
        }
        """
        self.setStyleSheet(dark_stylesheet)


def create_automated_novel_gui():
    """Factory function to create the automated novel GUI"""
    return AutomatedNovelGUI()


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = AutomatedNovelGUI()
    window.show()
    sys.exit(app.exec_())

"""
Main Window for AAWT
Container window with menu bar, status bar, and central widget.
"""

import sys
import logging
from PyQt5.QtWidgets import (
    QMainWindow, QAction, QMenu, QMenuBar, QStatusBar, QMessageBox,
    QApplication
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence, QIcon

from .aawt_main_gui import MainGUI

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self, settings_manager, database_manager, api_manager,
                 text_analyzer, export_manager, file_operations, workflow_manager=None,
                 grammar_analyzer=None):
        """
        Initialize main window.
        
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
        
        self.init_ui()
        self.create_menu_bar()
        self.create_status_bar()
        self.apply_settings()
        
        logger.info("Main window initialized")
    
    def init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle("AAWT - AI-Assisted Writing Tool")
        
        # Set window size from settings
        width = self.settings.get('ui.window.width', 1280)
        height = self.settings.get('ui.window.height', 800)
        self.resize(width, height)
        
        # Center window
        self.center_window()
        
        # Create central widget
        self.central_widget = MainGUI(
            self.settings,
            self.database,
            self.api,
            self.analyzer,
            self.exporter,
            self.files,
            self.workflow,
            self.grammar
        )
        self.setCentralWidget(self.central_widget)
    
    def center_window(self):
        """Center window on screen."""
        from PyQt5.QtWidgets import QDesktopWidget
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def create_menu_bar(self):
        """Create menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        new_action = QAction('&New Project', self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.central_widget.create_new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction('&Open Project', self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.central_widget.load_project)
        file_menu.addAction(open_action)
        
        save_action = QAction('&Save', self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.central_widget.save_current_project)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        export_action = QAction('&Export...', self)
        export_action.setShortcut('Ctrl+E')
        export_action.triggered.connect(self.central_widget.export_current_project)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('E&xit', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu('&Edit')
        
        undo_action = QAction('&Undo', self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(lambda: self.central_widget.text_editor.undo())
        edit_menu.addAction(undo_action)
        
        redo_action = QAction('&Redo', self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(lambda: self.central_widget.text_editor.redo())
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction('Cu&t', self)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(lambda: self.central_widget.text_editor.cut())
        edit_menu.addAction(cut_action)
        
        copy_action = QAction('&Copy', self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(lambda: self.central_widget.text_editor.copy())
        edit_menu.addAction(copy_action)
        
        paste_action = QAction('&Paste', self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(lambda: self.central_widget.text_editor.paste())
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        select_all_action = QAction('Select &All', self)
        select_all_action.setShortcut(QKeySequence.SelectAll)
        select_all_action.triggered.connect(lambda: self.central_widget.text_editor.selectAll())
        edit_menu.addAction(select_all_action)
        
        # View menu
        view_menu = menubar.addMenu('&View')
        
        dashboard_action = QAction('&Dashboard', self)
        dashboard_action.triggered.connect(self.central_widget.show_dashboard)
        view_menu.addAction(dashboard_action)
        
        projects_action = QAction('&Projects', self)
        projects_action.triggered.connect(self.central_widget.show_projects)
        view_menu.addAction(projects_action)
        
        editor_action = QAction('&Editor', self)
        editor_action.triggered.connect(self.central_widget.show_editor)
        view_menu.addAction(editor_action)
        
        analytics_action = QAction('&Analytics', self)
        analytics_action.triggered.connect(self.central_widget.show_analytics)
        view_menu.addAction(analytics_action)
        
        view_menu.addSeparator()
        
        settings_action = QAction('&Settings', self)
        settings_action.triggered.connect(self.central_widget.show_settings)
        view_menu.addAction(settings_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('&Tools')
        
        analyze_action = QAction('&Analyze Text', self)
        analyze_action.setShortcut('Ctrl+Alt+A')
        analyze_action.triggered.connect(self.central_widget.analyze_current_text)
        tools_menu.addAction(analyze_action)
        
        tools_menu.addSeparator()
        
        ai_assist_action = QAction('AI &Assistance...', self)
        ai_assist_action.setShortcut('Ctrl+Alt+I')
        ai_assist_action.triggered.connect(self.show_ai_assistant)
        tools_menu.addAction(ai_assist_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        help_action = QAction('&Help Documentation', self)
        help_action.setShortcut(QKeySequence.HelpContents)
        help_action.triggered.connect(self.central_widget.show_help)
        help_menu.addAction(help_action)
        
        help_menu.addSeparator()
        
        about_action = QAction('&About AAWT', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_status_bar(self):
        """Create status bar."""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage('Ready')
        
        # Performance metrics timer
        self.perf_timer = QTimer()
        self.perf_timer.timeout.connect(self.update_performance_metrics)
        self.perf_timer.start(2000)  # Update every 2 seconds
    
    def update_performance_metrics(self):
        """Update performance metrics in status bar."""
        try:
            import psutil
            
            # CPU and memory
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            memory_mb = memory.used / 1024 / 1024
            
            # Database stats
            db_stats = self.database.get_database_stats()
            cache_entries = db_stats.get('cache_entries', 0)
            
            status_text = f"CPU: {cpu_percent:.1f}% | Memory: {memory_mb:.0f}MB | Cache: {cache_entries} entries"
            self.status_bar.showMessage(status_text)
        except Exception as e:
            # If psutil not available, just show basic status
            self.status_bar.showMessage('Ready')
    
    def apply_settings(self):
        """Apply settings to window."""
        # Apply theme
        theme = self.settings.get('ui.theme', 'light')
        if theme == 'dark':
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2b2b2b;
                }
                QMenuBar {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QMenuBar::item:selected {
                    background-color: #404040;
                }
                QMenu {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QMenu::item:selected {
                    background-color: #404040;
                }
                QStatusBar {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #ffffff;
                }
            """)
    
    def show_ai_assistant(self):
        """Show AI assistance dialog."""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QPushButton, QComboBox, QLabel
        
        if not self.central_widget.current_project:
            QMessageBox.warning(self, "Warning", "Please load a project first")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("AI Assistant")
        dialog.setModal(True)
        dialog.resize(600, 400)
        
        layout = QVBoxLayout()
        
        # Provider selection
        provider_layout = QVBoxLayout()
        provider_label = QLabel("Select AI Provider:")
        provider_layout.addWidget(provider_label)
        
        provider_combo = QComboBox()
        providers = self.api.get_available_providers()
        provider_combo.addItems(providers)
        provider_combo.setCurrentText(self.settings.get('api.default_provider', 'openai'))
        provider_layout.addWidget(provider_combo)
        
        layout.addLayout(provider_layout)
        
        # Prompt input
        prompt_label = QLabel("Enter your prompt:")
        layout.addWidget(prompt_label)
        
        prompt_input = QTextEdit()
        prompt_input.setPlaceholderText("e.g., Continue this story, suggest improvements, etc.")
        prompt_input.setMaximumHeight(100)
        layout.addWidget(prompt_input)
        
        # Response display
        response_label = QLabel("Response:")
        layout.addWidget(response_label)
        
        response_display = QTextEdit()
        response_display.setReadOnly(True)
        layout.addWidget(response_display)
        
        # Buttons
        button_layout = QVBoxLayout()
        
        generate_btn = QPushButton("Generate")
        generate_btn.clicked.connect(lambda: self.generate_ai_response(
            prompt_input.toPlainText(),
            provider_combo.currentText(),
            response_display
        ))
        button_layout.addWidget(generate_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def generate_ai_response(self, prompt, provider, response_widget):
        """Generate AI response."""
        if not prompt.strip():
            QMessageBox.warning(self, "Warning", "Please enter a prompt")
            return
        
        response_widget.setPlainText("Generating response...")
        QApplication.processEvents()  # Update UI
        
        try:
            # Get context from current text
            current_text = self.central_widget.text_editor.toPlainText()
            if current_text:
                # Get last 500 characters as context
                context = current_text[-500:] if len(current_text) > 500 else current_text
                system_prompt = f"You are a writing assistant. Here's the context from the current document:\n\n{context}\n\nNow help with the following request:"
            else:
                system_prompt = "You are a writing assistant."
            
            result = self.api.call_ai(prompt, provider=provider, system_prompt=system_prompt)
            
            if result.get('success'):
                text = result.get('text', '')
                cost = result.get('cost', 0)
                
                response_text = f"{text}\n\n---\nCost: ${cost:.4f}"
                response_widget.setPlainText(response_text)
            else:
                error = result.get('error', 'Unknown error')
                response_widget.setPlainText(f"Error: {error}")
                QMessageBox.critical(self, "Error", f"Failed to generate response:\n{error}")
        except Exception as e:
            response_widget.setPlainText(f"Error: {str(e)}")
            QMessageBox.critical(self, "Error", f"An error occurred:\n{str(e)}")
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About AAWT",
            """<h2>AAWT - AI-Assisted Writing Tool</h2>
            <p><b>Version:</b> 2.0</p>
            <p><b>Description:</b> A comprehensive desktop application for writers with real-time analysis, 
            project management, AI integration, and multi-format export capabilities.</p>
            
            <p><b>Features:</b></p>
            <ul>
                <li>Multi-project management</li>
                <li>Real-time text analysis</li>
                <li>AI integration (OpenAI, Anthropic, Google, Ollama)</li>
                <li>Export to TXT, MD, DOCX, PDF, EPUB, JSON</li>
                <li>Auto-save and session tracking</li>
            </ul>
            
            <p><b>Built with:</b> Python, PyQt5, SQLite</p>
            <p>Copyright © 2024. All rights reserved.</p>
            """
        )
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Save window size
        self.settings.set('ui.window.width', self.width(), auto_save=False)
        self.settings.set('ui.window.height', self.height(), auto_save=False)
        self.settings.save()
        
        # Close database
        self.database.close()
        
        event.accept()

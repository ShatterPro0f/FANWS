"""
Consolidated UI Components with Categorized Sidebar
Implements tabbed sidebar with Projects, Templates, and Tools categories
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QFrame, QLabel,
    QPushButton, QScrollArea, QGroupBox, QFormLayout, QLineEdit,
    QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,
    QTreeWidget, QTreeWidgetItem, QStackedWidget, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon


class CategorizedSidebar(QWidget):
    """Sidebar with categorized tabs for better organization"""

    # Signals for navigation
    page_changed = pyqtSignal(str)  # Emits page ID when navigation changes

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.current_page = None
        self.init_ui()

    def init_ui(self):
        """Initialize the categorized sidebar UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Create tab widget for categories
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: white;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                padding: 8px 16px;
                margin: 2px;
                border-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #4CAF50;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #e0e0e0;
            }
        """)

        # Create category tabs
        self._create_projects_tab()
        self._create_templates_tab()
        self._create_tools_tab()

        layout.addWidget(self.tab_widget)

    def _create_projects_tab(self):
        """Create the Projects category tab"""
        projects_widget = QWidget()
        layout = QVBoxLayout(projects_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Project Management Section
        project_group = QGroupBox("Project Management")
        project_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        project_layout = QVBoxLayout(project_group)

        # Project management buttons
        self.switch_project_btn = QPushButton("Switch Project")
        self.switch_project_btn.setStyleSheet(self._get_button_style("#2196F3"))
        self.switch_project_btn.clicked.connect(lambda: self.page_changed.emit("switch_project"))

        self.create_project_btn = QPushButton("Create New Project")
        self.create_project_btn.setStyleSheet(self._get_button_style("#4CAF50"))
        self.create_project_btn.clicked.connect(lambda: self.page_changed.emit("create_project"))

        self.import_project_btn = QPushButton("Import Project")
        self.import_project_btn.setStyleSheet(self._get_button_style("#FF9800"))
        self.import_project_btn.clicked.connect(lambda: self.page_changed.emit("import_project"))

        self.delete_project_btn = QPushButton("Delete Project")
        self.delete_project_btn.setStyleSheet(self._get_button_style("#f44336"))
        self.delete_project_btn.clicked.connect(lambda: self.page_changed.emit("delete_project"))

        project_layout.addWidget(self.switch_project_btn)
        project_layout.addWidget(self.create_project_btn)
        project_layout.addWidget(self.import_project_btn)
        project_layout.addWidget(self.delete_project_btn)

        # Novel Settings Section
        novel_group = QGroupBox("Novel Settings")
        novel_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        novel_layout = QVBoxLayout(novel_group)

        self.novel_concept_btn = QPushButton("Novel Concept")
        self.novel_concept_btn.setStyleSheet(self._get_button_style("#9C27B0"))
        self.novel_concept_btn.clicked.connect(lambda: self.page_changed.emit("novel_concept"))

        self.tone_settings_btn = QPushButton("Tone & Style")
        self.tone_settings_btn.setStyleSheet(self._get_button_style("#9C27B0"))
        self.tone_settings_btn.clicked.connect(lambda: self.page_changed.emit("tone_settings"))

        self.structure_btn = QPushButton("Story Structure")
        self.structure_btn.setStyleSheet(self._get_button_style("#9C27B0"))
        self.structure_btn.clicked.connect(lambda: self.page_changed.emit("structure_settings"))

        novel_layout.addWidget(self.novel_concept_btn)
        novel_layout.addWidget(self.tone_settings_btn)
        novel_layout.addWidget(self.structure_btn)

        # Add groups to layout
        layout.addWidget(project_group)
        layout.addWidget(novel_group)
        layout.addStretch()  # Push content to top

        self.tab_widget.addTab(projects_widget, "Projects")

    def _create_templates_tab(self):
        """Create the Templates category tab"""
        templates_widget = QWidget()
        layout = QVBoxLayout(templates_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Template Categories
        categories = [
            ("Genre Templates", [
                ("Fantasy Adventure", "fantasy_template"),
                ("Sci-Fi Thriller", "scifi_template"),
                ("Romance Novel", "romance_template"),
                ("Mystery/Detective", "mystery_template"),
                ("Historical Fiction", "historical_template")
            ]),
            ("Structure Templates", [
                ("Three-Act Structure", "three_act_template"),
                ("Hero's Journey", "hero_journey_template"),
                ("Seven-Point Story", "seven_point_template"),
                ("Freytag's Pyramid", "freytag_template")
            ]),
            ("Character Templates", [
                ("Character Archetypes", "character_archetypes"),
                ("Relationship Dynamics", "relationship_templates"),
                ("Character Development", "character_development")
            ])
        ]

        for category_name, templates in categories:
            group = QGroupBox(category_name)
            group.setStyleSheet("QGroupBox { font-weight: bold; }")
            group_layout = QVBoxLayout(group)

            for template_name, template_id in templates:
                btn = QPushButton(template_name)
                btn.setStyleSheet(self._get_button_style("#795548"))
                btn.clicked.connect(lambda checked, tid=template_id: self.page_changed.emit(tid))
                group_layout.addWidget(btn)

            layout.addWidget(group)

        layout.addStretch()
        self.tab_widget.addTab(templates_widget, "Templates")

    def _create_tools_tab(self):
        """Create the Tools category tab"""
        tools_widget = QWidget()
        layout = QVBoxLayout(tools_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Dashboard Tools
        dashboard_group = QGroupBox("Dashboard & Analytics")
        dashboard_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        dashboard_layout = QVBoxLayout(dashboard_group)

        dashboard_tools = [
            ("Progress Dashboard", "progress_dashboard", "#4CAF50"),
            ("Writing Analytics", "writing_analytics", "#2196F3"),
            ("Performance Monitor", "performance_monitor", "#FF9800"),
            ("Synonyms & Language", "synonyms_tools", "#9C27B0")
        ]

        for tool_name, tool_id, color in dashboard_tools:
            btn = QPushButton(tool_name)
            btn.setStyleSheet(self._get_button_style(color))
            btn.clicked.connect(lambda checked, tid=tool_id: self.page_changed.emit(tid))
            dashboard_layout.addWidget(btn)

        # Writing Tools
        writing_group = QGroupBox("Writing Tools")
        writing_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        writing_layout = QVBoxLayout(writing_group)

        writing_tools = [
            ("Start Writing", "start_writing", "#4CAF50"),
            ("Draft Manager", "draft_manager", "#2196F3"),
            ("Export Options", "export_options", "#FF9800"),
            ("Backup & Recovery", "backup_tools", "#795548")
        ]

        for tool_name, tool_id, color in writing_tools:
            btn = QPushButton(tool_name)
            btn.setStyleSheet(self._get_button_style(color))
            btn.clicked.connect(lambda checked, tid=tool_id: self.page_changed.emit(tid))
            writing_layout.addWidget(btn)

        # Settings Tools
        settings_group = QGroupBox("Settings & Configuration")
        settings_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        settings_layout = QVBoxLayout(settings_group)

        settings_tools = [
            ("API Configuration", "api_settings", "#f44336"),
            ("Advanced Settings", "advanced_settings", "#607D8B"),
            ("Plugin Management", "plugin_management", "#9E9E9E")
        ]

        for tool_name, tool_id, color in settings_tools:
            btn = QPushButton(tool_name)
            btn.setStyleSheet(self._get_button_style(color))
            btn.clicked.connect(lambda checked, tid=tool_id: self.page_changed.emit(tid))
            settings_layout.addWidget(btn)

        layout.addWidget(dashboard_group)
        layout.addWidget(writing_group)
        layout.addWidget(settings_group)
        layout.addStretch()

        self.tab_widget.addTab(tools_widget, "Tools")

    def _get_button_style(self, color):
        """Get consistent button styling"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 10px;
                margin: 2px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(color, 0.3)};
            }}
            QPushButton:disabled {{
                background-color: #cccccc;
                color: #666666;
            }}
        """

    def _darken_color(self, hex_color, factor=0.2):
        """Darken a hex color by a factor"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(int(c * (1 - factor)) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    def set_current_page(self, page_id):
        """Set the current page and update UI accordingly"""
        self.current_page = page_id
        # Could add visual indicators here if needed


class ConsolidatedUIComponents:
    """Consolidated UI components with categorized sidebar"""

    def __init__(self, window=None):
        self.window = window
        self.sidebar = None
        self.content_area = None
        self.content_pages = {}

    def create_ui(self):
        """Create the consolidated UI with categorized sidebar"""
        if not self.window:
            return

        # Create main central widget and layout
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create categorized sidebar (1/4 width)
        self.sidebar = CategorizedSidebar(self.window)
        self.sidebar.setMaximumWidth(int(self.window.width() * 0.25))
        self.sidebar.setMinimumWidth(350)  # Slightly wider for tabs
        self.sidebar.setFrameStyle(QFrame.Box)
        self.sidebar.setStyleSheet("QFrame { border-right: 2px solid #cccccc; background-color: #f5f5f5; }")

        # Connect sidebar navigation
        self.sidebar.page_changed.connect(self._on_page_changed)

        # Create content area (3/4 width)
        self.content_area = QStackedWidget()
        self.content_area.setStyleSheet("""
            QStackedWidget {
                background-color: white;
                border: 1px solid #cccccc;
            }
        """)

        # Create content pages
        self._create_content_pages()

        # Add to main layout
        main_layout.addWidget(self.sidebar, 1)  # 1/4 width
        main_layout.addWidget(self.content_area, 3)  # 3/4 width

        # Set central widget
        self.window.setCentralWidget(central_widget)

        # Store references
        self.window._ui_central_widget = central_widget
        self.window._ui_sidebar = self.sidebar
        self.window._ui_content_area = self.content_area

        # Set default page
        self._on_page_changed("switch_project")

    def _create_content_pages(self):
        """Create all content pages for the application"""
        # Import necessary widgets first
        self._create_missing_widgets()

        # Define page creators
        page_creators = {
            "switch_project": self._create_switch_project_page,
            "create_project": self._create_create_project_page,
            "import_project": self._create_import_project_page,
            "delete_project": self._create_delete_project_page,
            "novel_concept": self._create_novel_concept_page,
            "tone_settings": self._create_tone_settings_page,
            "structure_settings": self._create_structure_settings_page,
            "progress_dashboard": self._create_progress_dashboard_page,
            "writing_analytics": self._create_writing_analytics_page,
            "performance_monitor": self._create_performance_monitor_page,
            "synonyms_tools": self._create_synonyms_tools_page,
            "start_writing": self._create_start_writing_page,
            "draft_manager": self._create_draft_manager_page,
            "export_options": self._create_export_options_page,
            "api_settings": self._create_api_settings_page,
            "advanced_settings": self._create_advanced_settings_page,
        }

        # Create pages
        for page_id, creator in page_creators.items():
            try:
                page_widget = creator()
                index = self.content_area.addWidget(page_widget)
                self.content_pages[page_id] = index
            except Exception as e:
                print(f"Warning: Could not create page {page_id}: {e}")
                # Create placeholder page
                placeholder = QLabel(f"Page '{page_id}' is under construction")
                placeholder.setAlignment(Qt.AlignCenter)
                placeholder.setStyleSheet("color: #666; font-size: 14px;")
                index = self.content_area.addWidget(placeholder)
                self.content_pages[page_id] = index

    def _on_page_changed(self, page_id):
        """Handle page navigation"""
        if page_id in self.content_pages:
            self.content_area.setCurrentIndex(self.content_pages[page_id])
            self.sidebar.set_current_page(page_id)

            # Trigger specific actions for certain pages
            if hasattr(self.window, '_on_page_changed'):
                self.window._on_page_changed(page_id)

    def _create_missing_widgets(self):
        """Create missing widgets that the main application expects"""
        # This method ensures compatibility with existing code
        # Create basic widgets that are referenced in the main application

        if not hasattr(self.window, 'project_selector'):
            from PyQt5.QtWidgets import QComboBox
            self.window.project_selector = QComboBox()

        if not hasattr(self.window, 'new_project_button'):
            self.window.new_project_button = QPushButton("Create Project")

        if not hasattr(self.window, 'import_project_button'):
            self.window.import_project_button = QPushButton("Import Project")

        if not hasattr(self.window, 'delete_project_button'):
            self.window.delete_project_button = QPushButton("Delete Project")

        # Add other essential widgets as needed
        essential_widgets = [
            'start_button', 'pause_button', 'approve_button', 'export_button',
            'reset_api_button', 'clear_cache_button', 'save_api_keys_button',
            'project_input', 'idea_input', 'tone_input', 'sub_tone_input',
            'reading_level_input', 'thesaurus_weight_input', 'target_input',
            'characters_seed_input', 'world_seed_input', 'themes_seed_input',
            'structure_seed_input', 'openai_key_input', 'wordsapi_key_input',
            'continuity_rules_input', 'theme_dropdown', 'use_default_settings'
        ]

        for widget_name in essential_widgets:
            if not hasattr(self.window, widget_name):
                # Create appropriate widget type based on name
                if 'button' in widget_name:
                    widget = QPushButton(widget_name.replace('_', ' ').title())
                elif 'input' in widget_name and 'seed' in widget_name:
                    widget = QTextEdit()
                elif 'input' in widget_name:
                    widget = QLineEdit()
                elif 'dropdown' in widget_name or widget_name in ['tone_input', 'sub_tone_input', 'reading_level_input', 'target_input']:
                    widget = QComboBox()
                elif 'weight' in widget_name:
                    widget = QDoubleSpinBox()
                    widget.setRange(0.0, 1.0)
                    widget.setSingleStep(0.1)
                    widget.setValue(0.5)
                elif 'settings' in widget_name:
                    widget = QCheckBox()
                else:
                    widget = QLineEdit()

                setattr(self.window, widget_name, widget)

    # Page creation methods - these will be implemented in the following sections
    def _create_switch_project_page(self):
        """Create switch project page"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Header
        header = QLabel("Switch Project")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin: 10px;")
        layout.addWidget(header)

        # Project selector
        group = QGroupBox("Select Project")
        form_layout = QFormLayout(group)
        form_layout.addRow("Current Project:", self.window.project_selector)
        layout.addWidget(group)

        layout.addStretch()
        return widget

    def _create_create_project_page(self):
        """Create new project page"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        header = QLabel("Create New Project")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin: 10px;")
        layout.addWidget(header)

        # Project creation form
        group = QGroupBox("Project Details")
        form_layout = QFormLayout(group)
        form_layout.addRow("Project Name:", self.window.project_input)
        form_layout.addRow("Novel Idea:", self.window.idea_input)
        form_layout.addRow(self.window.new_project_button)
        layout.addWidget(group)

        layout.addStretch()
        return widget

    def _create_import_project_page(self):
        """Create import project page"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        header = QLabel("Import Project")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin: 10px;")
        layout.addWidget(header)

        group = QGroupBox("Import Project from Folder")
        form_layout = QFormLayout(group)

        info_label = QLabel("Select a project folder to import into FANWS")
        info_label.setStyleSheet("color: #666; font-style: italic;")
        form_layout.addRow(info_label)

        form_layout.addRow("Project Folder:", self.window.import_project_button)
        layout.addWidget(group)

        layout.addStretch()
        return widget

    def _create_delete_project_page(self):
        """Create delete project page"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        header = QLabel("Delete Project")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin: 10px;")
        layout.addWidget(header)

        group = QGroupBox("Delete Project")
        form_layout = QFormLayout(group)

        warning_label = QLabel("⚠️ Warning: This action cannot be undone!")
        warning_label.setStyleSheet("color: red; font-weight: bold;")
        form_layout.addRow(warning_label)

        form_layout.addRow(self.window.delete_project_button)
        layout.addWidget(group)

        layout.addStretch()
        return widget

    def _create_novel_concept_page(self):
        """Create novel concept configuration page"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        header = QLabel("Novel Concept")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin: 10px;")
        layout.addWidget(header)

        # Concept details
        group = QGroupBox("Story Concept")
        form_layout = QFormLayout(group)
        form_layout.addRow("Main Idea:", self.window.idea_input)
        form_layout.addRow("Characters:", self.window.characters_seed_input)
        form_layout.addRow("World/Setting:", self.window.world_seed_input)
        form_layout.addRow("Themes:", self.window.themes_seed_input)
        form_layout.addRow("Structure:", self.window.structure_seed_input)
        layout.addWidget(group)

        layout.addStretch()
        return widget

    def _create_tone_settings_page(self):
        """Create tone and style settings page"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        header = QLabel("Tone & Style Settings")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin: 10px;")
        layout.addWidget(header)

        group = QGroupBox("Writing Style")
        form_layout = QFormLayout(group)
        form_layout.addRow("Primary Tone:", self.window.tone_input)
        form_layout.addRow("Sub-Tone:", self.window.sub_tone_input)
        form_layout.addRow("Reading Level:", self.window.reading_level_input)
        form_layout.addRow("Theme:", self.window.theme_dropdown)
        form_layout.addRow("Thesaurus Weight:", self.window.thesaurus_weight_input)
        layout.addWidget(group)

        layout.addStretch()
        return widget

    def _create_structure_settings_page(self):
        """Create story structure settings page"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        header = QLabel("Story Structure")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin: 10px;")
        layout.addWidget(header)

        group = QGroupBox("Structure Settings")
        form_layout = QFormLayout(group)
        form_layout.addRow("Target Word Count:", self.window.target_input)
        form_layout.addRow("Use Defaults:", self.window.use_default_settings)
        layout.addWidget(group)

        layout.addStretch()
        return widget

    # Placeholder methods for other pages
    def _create_progress_dashboard_page(self):
        return self._create_placeholder_page("Progress Dashboard")

    def _create_writing_analytics_page(self):
        return self._create_placeholder_page("Writing Analytics")

    def _create_performance_monitor_page(self):
        return self._create_placeholder_page("Performance Monitor")

    def _create_synonyms_tools_page(self):
        return self._create_placeholder_page("Synonyms & Language Tools")

    def _create_start_writing_page(self):
        return self._create_placeholder_page("Start Writing")

    def _create_draft_manager_page(self):
        return self._create_placeholder_page("Draft Manager")

    def _create_export_options_page(self):
        return self._create_placeholder_page("Export Options")

    def _create_api_settings_page(self):
        """Create API settings page"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        header = QLabel("API Configuration")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin: 10px;")
        layout.addWidget(header)

        group = QGroupBox("API Keys")
        form_layout = QFormLayout(group)
        form_layout.addRow("OpenAI API Key:", self.window.openai_key_input)
        form_layout.addRow("WordsAPI Key:", self.window.wordsapi_key_input)
        form_layout.addRow("Continuity Rules:", self.window.continuity_rules_input)
        form_layout.addRow(self.window.save_api_keys_button)
        layout.addWidget(group)

        layout.addStretch()
        return widget

    def _create_advanced_settings_page(self):
        return self._create_placeholder_page("Advanced Settings")

    def _create_placeholder_page(self, title):
        """Create a placeholder page"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        header = QLabel(title)
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #333; margin: 10px;")
        layout.addWidget(header)

        placeholder = QLabel(f"{title} functionality will be implemented here")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: #666; font-size: 14px; margin: 50px;")
        layout.addWidget(placeholder)

        layout.addStretch()
        return widget

    def add_missing_widgets(self):
        """Compatibility method for existing code"""
        pass  # Already handled in _create_missing_widgets

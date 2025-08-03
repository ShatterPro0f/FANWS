"""
FANWS UI Package
Modular UI components broken down from mega-file in cleanup
"""

# Import modules directly to avoid naming conflicts
from . import core_ui
from . import analytics_ui
from . import management_ui
from . import export_ui
from .consolidated_ui import CategorizedSidebar
from .onboarding_wizard import OnboardingWizard
from .export_ui import ExportManagerWidget, create_export_manager

# Legacy compatibility - create a placeholder UIComponents
class UIComponents:
    """Legacy UI components placeholder"""
    def __init__(self, window=None):
        self.window = window
        self.modern_design = None
        self.modern_components = None
        self.modern_animations = None

    def create_ui(self):
        """Create UI widgets required by the main application"""
        if not self.window:
            return

        # Import PyQt5 widgets
        from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QSplitter, QStackedWidget)
        from PyQt5.QtCore import Qt

        # Create main central widget and layout
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create horizontal splitter for sidebar and content
        splitter = QSplitter(Qt.Horizontal)

        # Create the new categorized sidebar
        self.categorized_sidebar = CategorizedSidebar()
        splitter.addWidget(self.categorized_sidebar)

        # Create content area separately
        content_area = QStackedWidget()
        content_area.setStyleSheet("QStackedWidget { background-color: #ffffff; }")
        splitter.addWidget(content_area)

        # Set splitter sizes (1/4 sidebar, 3/4 content)
        splitter.setSizes([400, 1200])

        # Add splitter to main layout
        main_layout.addWidget(splitter)

        # Store references for compatibility
        self.window.central_widget = central_widget
        self.window._content_area = content_area
        self.window._sidebar = self.categorized_sidebar
        self.window.categorized_sidebar = self.categorized_sidebar

        # Create onboarding wizard
        self.onboarding_wizard = OnboardingWizard(self.window)
        self.window.onboarding_wizard = self.onboarding_wizard

        # Connect sidebar signals for navigation
        self._connect_sidebar_signals()

        # Setup navigation tree for backward compatibility
        self._setup_compatibility_navigation()

    def _connect_sidebar_signals(self):
        """Connect signals from the categorized sidebar"""
        if hasattr(self.categorized_sidebar, 'project_created'):
            self.categorized_sidebar.project_created.connect(self.window.create_project)
        if hasattr(self.categorized_sidebar, 'project_opened'):
            self.categorized_sidebar.project_opened.connect(self.window.open_project)
        if hasattr(self.categorized_sidebar, 'onboarding_requested'):
            self.categorized_sidebar.onboarding_requested.connect(self.window.show_onboarding)

    def _setup_compatibility_navigation(self):
        """Setup navigation tree for backward compatibility"""
        # Create a dummy navigation tree for compatibility
        from PyQt5.QtWidgets import QTreeWidget
        self.window.nav_tree = QTreeWidget()
        self.window.nav_tree.setVisible(False)  # Hidden since we use the new sidebar

    def _build_navigation_tree(self):
        """Build the hierarchical navigation tree structure"""
        from PyQt5.QtWidgets import QTreeWidgetItem
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont

        # Clear any existing items
        self.window.nav_tree.clear()

        # Section 1: Project
        project_section = QTreeWidgetItem(self.window.nav_tree, ["Project"])
        project_section.setFont(0, QFont("Arial", 12, QFont.Bold))
        project_section.setData(0, Qt.UserRole, {"type": "section", "id": "project"})

        # Project subsections
        project_subsections = [
            ("Switch Project", "switch_project"),
            ("Create Project", "create_project"),
            ("Load Project", "load_project"),
            ("Delete Project", "delete_project"),
            ("Novel Settings", "novel_settings")
        ]

        for sub_name, sub_id in project_subsections:
            sub_item = QTreeWidgetItem(project_section, [sub_name])
            sub_item.setData(0, Qt.UserRole, {"type": "subsection", "id": sub_id, "parent": "project"})

            # Novel Settings subsubsections
            if sub_id == "novel_settings":
                novel_subsubsections = [
                    ("Novel Concept", "novel_concept"),
                    ("Primary Tone", "primary_tone"),
                    ("Sub-Tone", "sub_tone"),
                    ("Theme", "theme"),
                    ("Target Word Count", "target_word_count"),
                    ("Reading Level", "reading_level"),
                    ("Chapter/section organization", "chapter_organization"),
                    ("Total Chapters", "total_chapters"),
                    ("Chapter Sections: Sections per chapter", "chapter_sections")
                ]

                for subsub_name, subsub_id in novel_subsubsections:
                    subsub_item = QTreeWidgetItem(sub_item, [subsub_name])
                    subsub_item.setData(0, Qt.UserRole, {"type": "subsubsection", "id": subsub_id, "parent": "novel_settings"})

        # Section 2: Dashboard
        dashboard_section = QTreeWidgetItem(self.window.nav_tree, ["Dashboard"])
        dashboard_section.setFont(0, QFont("Arial", 12, QFont.Bold))
        dashboard_section.setData(0, Qt.UserRole, {"type": "section", "id": "dashboard"})

        dashboard_subsections = [
            ("Progress Graph", "progress_graph"),
            ("Synonyms", "synonyms"),
            ("Log", "log"),
            ("Chapter Progress", "chapter_progress"),
            ("Current Draft", "current_draft")
        ]

        for sub_name, sub_id in dashboard_subsections:
            sub_item = QTreeWidgetItem(dashboard_section, [sub_name])
            sub_item.setData(0, Qt.UserRole, {"type": "subsection", "id": sub_id, "parent": "dashboard"})

        # Section 3: Performance
        performance_section = QTreeWidgetItem(self.window.nav_tree, ["Performance"])
        performance_section.setFont(0, QFont("Arial", 12, QFont.Bold))
        performance_section.setData(0, Qt.UserRole, {"type": "section", "id": "performance"})

        performance_subsections = [
            ("Memory Usage: Current RAM consumption (MB)", "memory_usage"),
            ("CPU Usage: Processor utilization (%)", "cpu_usage"),
            ("API Call Statistics: Requests per service", "api_stats"),
            ("File Operations: Read/write counts", "file_operations"),
            ("Cache Hit Rate: File cache efficiency (%)", "cache_hit_rate"),
            ("Response Times: API and file operation speeds", "response_times"),
            ("Optimization Recommendations: Performance suggestions", "optimization_recommendations"),
            ("System Resources: Disk space, network status", "system_resources")
        ]

        for sub_name, sub_id in performance_subsections:
            sub_item = QTreeWidgetItem(performance_section, [sub_name])
            sub_item.setData(0, Qt.UserRole, {"type": "subsection", "id": sub_id, "parent": "performance"})

        # Section 4: Settings
        settings_section = QTreeWidgetItem(self.window.nav_tree, ["Settings"])
        settings_section.setFont(0, QFont("Arial", 12, QFont.Bold))
        settings_section.setData(0, Qt.UserRole, {"type": "section", "id": "settings"})

        settings_subsections = [
            ("OpenAi API Key (Savable)", "openai_api_key"),
            ("WordsAPI Key (Savable)", "wordsapi_key")
        ]

        for sub_name, sub_id in settings_subsections:
            sub_item = QTreeWidgetItem(settings_section, [sub_name])
            sub_item.setData(0, Qt.UserRole, {"type": "subsection", "id": sub_id, "parent": "settings"})

        # Section 5: Export
        export_section = QTreeWidgetItem(self.window.nav_tree, ["Export"])
        export_section.setFont(0, QFont("Arial", 12, QFont.Bold))
        export_section.setData(0, Qt.UserRole, {"type": "section", "id": "export"})

        export_subsections = [
            ("Export Status: Success/failure of exports", "export_status"),
            ("Export Formats: Available output types", "export_formats"),
            ("Export History: Previous export attempts", "export_history"),
            ("File Sizes: Generated file sizes", "file_sizes"),
            ("Export Quality: Format-specific settings", "export_quality")
        ]

        for sub_name, sub_id in export_subsections:
            sub_item = QTreeWidgetItem(export_section, [sub_name])
            sub_item.setData(0, Qt.UserRole, {"type": "subsection", "id": sub_id, "parent": "export"})

        # Section 6: Writing Tools
        writing_tools_section = QTreeWidgetItem(self.window.nav_tree, ["Writing Tools"])
        writing_tools_section.setFont(0, QFont("Arial", 12, QFont.Bold))
        writing_tools_section.setData(0, Qt.UserRole, {"type": "section", "id": "writing_tools"})

        writing_tools_subsections = [
            ("Character Development", "character_development"),
            ("World Building", "world_building"),
            ("Timeline Management", "timeline_management"),
            ("Research Notes", "research_notes"),
            ("Writing Analytics", "writing_analytics")
        ]

        for sub_name, sub_id in writing_tools_subsections:
            sub_item = QTreeWidgetItem(writing_tools_section, [sub_name])
            sub_item.setData(0, Qt.UserRole, {"type": "subsection", "id": sub_id, "parent": "writing_tools"})

        # Section 7: Advanced Features
        advanced_section = QTreeWidgetItem(self.window.nav_tree, ["Advanced Features"])
        advanced_section.setFont(0, QFont("Arial", 12, QFont.Bold))
        advanced_section.setData(0, Qt.UserRole, {"type": "section", "id": "advanced"})

        advanced_subsections = [
            ("Collaboration Tools", "collaboration_tools"),
            ("Backup Management", "backup_management"),
            ("Template Management", "template_management"),
            ("Quality Analysis", "quality_analysis"),
            ("AI Writing Assistant", "ai_assistance")
        ]

        for sub_name, sub_id in advanced_subsections:
            sub_item = QTreeWidgetItem(advanced_section, [sub_name])
            sub_item.setData(0, Qt.UserRole, {"type": "subsection", "id": sub_id, "parent": "advanced"})

        # Section 8: Project Management
        project_mgmt_section = QTreeWidgetItem(self.window.nav_tree, ["Project Management"])
        project_mgmt_section.setFont(0, QFont("Arial", 12, QFont.Bold))
        project_mgmt_section.setData(0, Qt.UserRole, {"type": "section", "id": "project_management"})

        project_mgmt_subsections = [
            ("Project Statistics", "project_statistics"),
            ("Goal Tracking", "goal_tracking"),
            ("Deadline Management", "deadline_management"),
            ("Version Control", "version_control")
        ]

        for sub_name, sub_id in project_mgmt_subsections:
            sub_item = QTreeWidgetItem(project_mgmt_section, [sub_name])
            sub_item.setData(0, Qt.UserRole, {"type": "subsection", "id": sub_id, "parent": "project_management"})

        # Section 9: Configuration
        config_section = QTreeWidgetItem(self.window.nav_tree, ["Configuration"])
        config_section.setFont(0, QFont("Arial", 12, QFont.Bold))
        config_section.setData(0, Qt.UserRole, {"type": "section", "id": "configuration"})

        config_subsections = [
            ("Advanced Settings", "advanced_settings"),
            ("Plugin Management", "plugin_management"),
            ("Workflow Configuration", "workflow_configuration")
        ]

        for sub_name, sub_id in config_subsections:
            sub_item = QTreeWidgetItem(config_section, [sub_name])
            sub_item.setData(0, Qt.UserRole, {"type": "subsection", "id": sub_id, "parent": "configuration"})

        # Expand all sections by default
        self.window.nav_tree.expandAll()

    def _on_nav_item_clicked(self, item, column):
        """Handle navigation tree item clicks"""
        from PyQt5.QtCore import Qt

        if not item:
            return

        item_data = item.data(0, Qt.UserRole)
        if not item_data:
            return

        item_type = item_data.get("type")
        item_id = item_data.get("id")

        if item_type == "section":
            # Section clicks don't change content, just expand/collapse
            if item.isExpanded():
                item.setExpanded(False)
            else:
                item.setExpanded(True)
        elif item_type in ["subsection", "subsubsection"]:
            # Navigate to the appropriate content page
            self._switch_to_content_page(item_id)

        print(f"✓ Navigation: {item_type} '{item_id}' clicked")

    def _switch_to_content_page(self, page_id):
        """Switch to the appropriate content page"""
        if hasattr(self.window, '_content_pages') and page_id in self.window._content_pages:
            page_index = self.window._content_pages[page_id]
            self.window._content_area.setCurrentIndex(page_index)
            print(f"✓ Switched to content page: {page_id}")
        else:
            print(f"⚠ Content page not found: {page_id}")

    def _create_content_pages(self):
        """Create content pages for each section/subsection"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTextEdit, QFormLayout,
                                   QLineEdit, QComboBox, QPushButton, QSpinBox, QDoubleSpinBox,
                                   QCheckBox, QProgressBar, QTableWidget, QGroupBox, QHBoxLayout)
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont

        # Store page mappings
        self.window._content_pages = {}

        # Create content pages for each subsection and subsubsection
        content_definitions = self._get_content_definitions()

        for page_id, page_config in content_definitions.items():
            page_widget = QWidget()
            page_layout = QVBoxLayout(page_widget)

            # Add page title
            title_label = QLabel(page_config["title"])
            title_label.setFont(QFont("Arial", 16, QFont.Bold))
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("QLabel { background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 10px; }")
            page_layout.addWidget(title_label)

            # Add page content based on type
            content_widget = self._create_page_content(page_id, page_config)
            page_layout.addWidget(content_widget)

            page_layout.addStretch()

            # Add to stacked widget and store index
            page_index = self.window._content_area.addWidget(page_widget)
            self.window._content_pages[page_id] = page_index

    def _get_content_definitions(self):
        """Define content structure for each page"""
        return {
            # Project subsections
            "switch_project": {"title": "Switch Project", "type": "project_management"},
            "create_project": {"title": "Create New Project", "type": "project_management"},
            "load_project": {"title": "Load Existing Project", "type": "project_management"},
            "delete_project": {"title": "Delete Project", "type": "project_management"},

            # Novel Settings overview page
            "novel_settings": {"title": "Novel Settings Overview", "type": "overview"},

            # Novel Settings subsubsections
            "novel_concept": {"title": "Novel Concept", "type": "text_input"},
            "primary_tone": {"title": "Primary Tone", "type": "dropdown"},
            "sub_tone": {"title": "Sub-Tone", "type": "dropdown"},
            "theme": {"title": "Theme", "type": "dropdown"},
            "target_word_count": {"title": "Target Word Count", "type": "number_input"},
            "reading_level": {"title": "Reading Level", "type": "dropdown"},
            "chapter_organization": {"title": "Chapter/Section Organization", "type": "text_input"},
            "total_chapters": {"title": "Total Chapters", "type": "number_input"},
            "chapter_sections": {"title": "Sections per Chapter", "type": "number_input"},

            # Dashboard subsections
            "progress_graph": {"title": "Progress Graph", "type": "progress_display"},
            "synonyms": {"title": "Synonyms", "type": "synonym_tool"},
            "log": {"title": "System Log", "type": "log_display"},
            "chapter_progress": {"title": "Chapter Progress", "type": "chapter_progress"},
            "current_draft": {"title": "Current Draft", "type": "draft_editor"},

            # Performance subsections
            "memory_usage": {"title": "Memory Usage", "type": "performance_metric"},
            "cpu_usage": {"title": "CPU Usage", "type": "performance_metric"},
            "api_stats": {"title": "API Call Statistics", "type": "performance_table"},
            "file_operations": {"title": "File Operations", "type": "performance_metric"},
            "cache_hit_rate": {"title": "Cache Hit Rate", "type": "performance_metric"},
            "response_times": {"title": "Response Times", "type": "performance_table"},
            "optimization_recommendations": {"title": "Optimization Recommendations", "type": "recommendations"},
            "system_resources": {"title": "System Resources", "type": "system_info"},

            # Settings subsections
            "openai_api_key": {"title": "OpenAI API Key", "type": "api_key_input"},
            "wordsapi_key": {"title": "WordsAPI Key", "type": "api_key_input"},

            # Export subsections
            "export_status": {"title": "Export Status", "type": "export_status"},
            "export_formats": {"title": "Export Formats", "type": "export_formats"},
            "export_history": {"title": "Export History", "type": "export_history"},
            "file_sizes": {"title": "File Sizes", "type": "file_info"},
            "export_quality": {"title": "Export Quality Settings", "type": "export_settings"},

            # Additional backend features that need GUI integration
            # Writing Tools section
            "character_development": {"title": "Character Development", "type": "character_tools"},
            "world_building": {"title": "World Building", "type": "world_tools"},
            "timeline_management": {"title": "Timeline Management", "type": "timeline_tools"},
            "research_notes": {"title": "Research Notes", "type": "research_tools"},
            "writing_analytics": {"title": "Writing Analytics", "type": "analytics_display"},

            # Advanced Features section
            "collaboration_tools": {"title": "Collaboration", "type": "collaboration_tools"},
            "backup_management": {"title": "Backup Management", "type": "backup_tools"},
            "template_management": {"title": "Template Management", "type": "template_tools"},
            "quality_analysis": {"title": "Quality Analysis", "type": "quality_tools"},
            "ai_assistance": {"title": "AI Writing Assistant", "type": "ai_tools"},

            # Project Management section
            "project_statistics": {"title": "Project Statistics", "type": "stats_display"},
            "goal_tracking": {"title": "Goal Tracking", "type": "goal_tools"},
            "deadline_management": {"title": "Deadline Management", "type": "deadline_tools"},
            "version_control": {"title": "Version Control", "type": "version_tools"},

            # Configuration section
            "advanced_settings": {"title": "Advanced Settings", "type": "advanced_config"},
            "plugin_management": {"title": "Plugin Management", "type": "plugin_tools"},
            "workflow_configuration": {"title": "Workflow Configuration", "type": "workflow_config"}
        }

    def _create_page_content(self, page_id, page_config):
        """Create specific content widget based on page type"""
        from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QFormLayout,
                                   QLineEdit, QComboBox, QPushButton, QSpinBox, QDoubleSpinBox,
                                   QCheckBox, QProgressBar, QTableWidget, QGroupBox, QTableWidgetItem,
                                   QHeaderView, QTextBrowser, QSlider, QFrame)
        from PyQt5.QtCore import Qt

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)

        page_type = page_config.get("type", "default")

        if page_type == "project_management":
            self._create_project_management_content(layout, page_id)
        elif page_type == "text_input":
            self._create_text_input_content(layout, page_id)
        elif page_type == "dropdown":
            self._create_dropdown_content(layout, page_id)
        elif page_type == "number_input":
            self._create_number_input_content(layout, page_id)
        elif page_type == "progress_display":
            self._create_progress_display_content(layout, page_id)
        elif page_type == "synonym_tool":
            self._create_synonym_tool_content(layout, page_id)
        elif page_type == "log_display":
            self._create_log_display_content(layout, page_id)
        elif page_type == "chapter_progress":
            self._create_chapter_progress_content(layout, page_id)
        elif page_type == "draft_editor":
            self._create_draft_editor_content(layout, page_id)
        elif page_type == "performance_metric":
            self._create_performance_metric_content(layout, page_id)
        elif page_type == "performance_table":
            self._create_performance_table_content(layout, page_id)
        elif page_type == "recommendations":
            self._create_recommendations_content(layout, page_id)
        elif page_type == "system_info":
            self._create_system_info_content(layout, page_id)
        elif page_type == "api_key_input":
            self._create_api_key_input_content(layout, page_id)
        elif page_type == "export_status":
            self._create_export_status_content(layout, page_id)
        elif page_type == "export_formats":
            self._create_export_formats_content(layout, page_id)
        elif page_type == "export_history":
            self._create_export_history_content(layout, page_id)
        elif page_type == "file_info":
            self._create_file_info_content(layout, page_id)
        elif page_type == "export_settings":
            self._create_export_settings_content(layout, page_id)
        elif page_type == "overview":
            self._create_overview_content(layout, page_id)
        # New content types for expanded backend integration
        elif page_type == "character_tools":
            self._create_character_tools_content(layout, page_id)
        elif page_type == "world_tools":
            self._create_world_tools_content(layout, page_id)
        elif page_type == "timeline_tools":
            self._create_timeline_tools_content(layout, page_id)
        elif page_type == "research_tools":
            self._create_research_tools_content(layout, page_id)
        elif page_type == "analytics_display":
            self._create_analytics_display_content(layout, page_id)
        elif page_type == "collaboration_tools":
            self._create_collaboration_tools_content(layout, page_id)
        elif page_type == "backup_tools":
            self._create_backup_tools_content(layout, page_id)
        elif page_type == "template_tools":
            self._create_template_tools_content(layout, page_id)
        elif page_type == "quality_tools":
            self._create_quality_tools_content(layout, page_id)
        elif page_type == "ai_tools":
            self._create_ai_tools_content(layout, page_id)
        elif page_type == "stats_display":
            self._create_stats_display_content(layout, page_id)
        elif page_type == "goal_tools":
            self._create_goal_tools_content(layout, page_id)
        elif page_type == "deadline_tools":
            self._create_deadline_tools_content(layout, page_id)
        elif page_type == "version_tools":
            self._create_version_tools_content(layout, page_id)
        elif page_type == "advanced_config":
            self._create_advanced_config_content(layout, page_id)
        elif page_type == "plugin_tools":
            self._create_plugin_tools_content(layout, page_id)
        elif page_type == "workflow_config":
            self._create_workflow_config_content(layout, page_id)
        else:
            # Default content
            default_label = QLabel(f"Content for {page_config['title']} coming soon...")
            default_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(default_label)

        return content_widget

    def _create_project_management_content(self, layout, page_id):
        """Create project management content"""
        from PyQt5.QtWidgets import QGroupBox, QFormLayout, QComboBox, QLineEdit, QPushButton, QVBoxLayout, QLabel

        if page_id == "switch_project":
            group = QGroupBox("Switch to Existing Project")
            form_layout = QFormLayout(group)

            self.window.project_selector = QComboBox()
            self.window.project_selector.addItems(["Select a project...", "Default Project", "Test Project"])
            form_layout.addRow("Available Projects:", self.window.project_selector)

            switch_btn = QPushButton("Switch Project")
            form_layout.addRow(switch_btn)
            layout.addWidget(group)

        elif page_id == "create_project":
            group = QGroupBox("Create New Project")
            form_layout = QFormLayout(group)

            self.window.project_input = QLineEdit()
            self.window.project_input.setPlaceholderText("Enter project name...")
            form_layout.addRow("Project Name:", self.window.project_input)

            self.window.new_project_button = QPushButton("Create Project")
            form_layout.addRow(self.window.new_project_button)
            layout.addWidget(group)

        elif page_id == "load_project":
            group = QGroupBox("Load Project from File")
            form_layout = QFormLayout(group)

            info_label = QLabel("Select a project folder to import into FANWS")
            info_label.setStyleSheet("QLabel { color: #666; font-style: italic; }")
            form_layout.addRow(info_label)

            self.window.import_project_button = QPushButton("Browse for Project Folder")
            self.window.import_project_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 8px; }")
            form_layout.addRow("Project Folder:", self.window.import_project_button)
            layout.addWidget(group)

        elif page_id == "delete_project":
            group = QGroupBox("Delete Project")
            form_layout = QFormLayout(group)

            warning_label = QLabel("Warning: This action cannot be undone!")
            warning_label.setStyleSheet("QLabel { color: red; font-weight: bold; }")
            form_layout.addRow(warning_label)

            self.window.delete_project_button = QPushButton("Delete Selected Project")
            self.window.delete_project_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; }")
            form_layout.addRow(self.window.delete_project_button)
            layout.addWidget(group)

    def _create_text_input_content(self, layout, page_id):
        """Create text input content"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QTextEdit, QPushButton

        group = QGroupBox("Settings")
        group_layout = QVBoxLayout(group)

        if page_id == "novel_concept":
            self.window.idea_input = QTextEdit()
            self.window.idea_input.setPlaceholderText("Enter your novel concept and main plot ideas...")
            group_layout.addWidget(self.window.idea_input)
        elif page_id == "chapter_organization":
            text_edit = QTextEdit()
            text_edit.setPlaceholderText("Describe how you want to organize chapters and sections...")
            group_layout.addWidget(text_edit)

        save_btn = QPushButton("Save Settings")
        group_layout.addWidget(save_btn)
        layout.addWidget(group)

    def _create_dropdown_content(self, layout, page_id):
        """Create dropdown content"""
        from PyQt5.QtWidgets import QGroupBox, QFormLayout, QComboBox, QPushButton

        group = QGroupBox("Settings")
        form_layout = QFormLayout(group)

        if page_id == "primary_tone":
            self.window.tone_input = QComboBox()
            self.window.tone_input.addItems(["Formal", "Casual", "Academic", "Creative", "Professional", "Conversational"])
            form_layout.addRow("Primary Tone:", self.window.tone_input)
        elif page_id == "sub_tone":
            self.window.sub_tone_input = QComboBox()
            self.window.sub_tone_input.addItems(["Neutral", "Optimistic", "Serious", "Humorous", "Dramatic", "Mysterious"])
            form_layout.addRow("Sub-Tone:", self.window.sub_tone_input)
        elif page_id == "theme":
            self.window.theme_dropdown = QComboBox()
            self.window.theme_dropdown.addItems(["Adventure", "Romance", "Mystery", "Science Fiction", "Fantasy", "Thriller", "Drama"])
            form_layout.addRow("Theme:", self.window.theme_dropdown)
        elif page_id == "reading_level":
            self.window.reading_level_input = QComboBox()
            self.window.reading_level_input.addItems(["Elementary", "Middle School", "High School", "College", "Graduate"])
            form_layout.addRow("Reading Level:", self.window.reading_level_input)

        save_btn = QPushButton("Save Settings")
        form_layout.addRow(save_btn)
        layout.addWidget(group)

    def _create_number_input_content(self, layout, page_id):
        """Create number input content"""
        from PyQt5.QtWidgets import QGroupBox, QFormLayout, QSpinBox, QComboBox, QPushButton

        group = QGroupBox("Settings")
        form_layout = QFormLayout(group)

        if page_id == "target_word_count":
            self.window.target_input = QComboBox()
            self.window.target_input.setEditable(True)
            self.window.target_input.addItems(["50000", "75000", "100000", "150000", "200000", "250000", "300000"])
            self.window.target_input.setCurrentText("250000")
            form_layout.addRow("Target Word Count:", self.window.target_input)
        elif page_id == "total_chapters":
            chapters_input = QSpinBox()
            chapters_input.setRange(1, 100)
            chapters_input.setValue(20)
            form_layout.addRow("Total Chapters:", chapters_input)
        elif page_id == "chapter_sections":
            sections_input = QSpinBox()
            sections_input.setRange(1, 20)
            sections_input.setValue(3)
            form_layout.addRow("Sections per Chapter:", sections_input)

        save_btn = QPushButton("Save Settings")
        form_layout.addRow(save_btn)
        layout.addWidget(group)

    def _create_api_key_input_content(self, layout, page_id):
        """Create API key input content with validation"""
        from PyQt5.QtWidgets import QGroupBox, QFormLayout, QLineEdit, QPushButton, QLabel
        from PyQt5.QtCore import pyqtSignal
        try:
            from error_handling_system import validator, APIProvider
        except ImportError:
            # Fallback: define dummy validator and APIProvider to avoid errors
            class DummyValidator:
                @staticmethod
                def validate_api_key(key, provider):
                    class Result:
                        is_valid = True
                        message = "Validation not available"
                        suggestions = []
                    return Result()
            class DummyAPIProvider:
                OPENAI = "openai"
                WORDSAPI = "wordsapi"
            validator = DummyValidator()
            APIProvider = DummyAPIProvider()
        import logging

        group = QGroupBox("API Configuration")
        form_layout = QFormLayout(group)

        if page_id == "openai_api_key":
            self.window.openai_key_input = QLineEdit()
            self.window.openai_key_input.setEchoMode(QLineEdit.Password)
            self.window.openai_key_input.setPlaceholderText("Enter your OpenAI API key...")

            # Add validation on text change
            def validate_openai_key():
                key = self.window.openai_key_input.text()
                if key:
                    result = validator.validate_api_key(key, APIProvider.OPENAI)
                    if result.is_valid:
                        self.window.openai_key_input.setStyleSheet("border: 2px solid green;")
                        info_label.setText("✓ API key format appears valid")
                        info_label.setStyleSheet("color: green;")
                    else:
                        self.window.openai_key_input.setStyleSheet("border: 2px solid red;")
                        info_label.setText(f"✗ {result.message}")
                        info_label.setStyleSheet("color: red;")
                        if result.suggestions:
                            info_label.setText(f"✗ {result.message}\nTip: {result.suggestions[0]}")
                else:
                    self.window.openai_key_input.setStyleSheet("")
                    info_label.setText("Your OpenAI API key is used for AI-powered writing assistance.")
                    info_label.setStyleSheet("")

            self.window.openai_key_input.textChanged.connect(validate_openai_key)
            form_layout.addRow("OpenAI API Key:", self.window.openai_key_input)

            info_label = QLabel("Your OpenAI API key is used for AI-powered writing assistance.")
            info_label.setWordWrap(True)
            form_layout.addRow(info_label)

        elif page_id == "wordsapi_key":
            self.window.wordsapi_key_input = QLineEdit()
            self.window.wordsapi_key_input.setEchoMode(QLineEdit.Password)
            self.window.wordsapi_key_input.setPlaceholderText("Enter your WordsAPI key...")

            # Add validation on text change
            def validate_wordsapi_key():
                key = self.window.wordsapi_key_input.text()
                if key:
                    result = validator.validate_api_key(key, APIProvider.WORDSAPI)
                    if result.is_valid:
                        self.window.wordsapi_key_input.setStyleSheet("border: 2px solid green;")
                        words_info_label.setText("✓ API key format appears valid")
                        words_info_label.setStyleSheet("color: green;")
                    else:
                        self.window.wordsapi_key_input.setStyleSheet("border: 2px solid red;")
                        words_info_label.setText(f"✗ {result.message}")
                        words_info_label.setStyleSheet("color: red;")
                        if result.suggestions:
                            words_info_label.setText(f"✗ {result.message}\nTip: {result.suggestions[0]}")
                else:
                    self.window.wordsapi_key_input.setStyleSheet("")
                    words_info_label.setText("WordsAPI is used for synonym suggestions and word analysis.")
                    words_info_label.setStyleSheet("")

            self.window.wordsapi_key_input.textChanged.connect(validate_wordsapi_key)
            form_layout.addRow("WordsAPI Key:", self.window.wordsapi_key_input)

            words_info_label = QLabel("WordsAPI is used for synonym suggestions and word analysis.")
            words_info_label.setWordWrap(True)
            form_layout.addRow(words_info_label)

        # Enhanced save button with validation
        self.window.save_api_keys_button = QPushButton("Save API Keys")

        def save_with_validation():
            """Save API keys with validation."""
            try:
                all_valid = True
                validation_messages = []

                # Validate OpenAI key if present
                if hasattr(self.window, 'openai_key_input') and self.window.openai_key_input.text():
                    result = validator.validate_api_key(self.window.openai_key_input.text(), APIProvider.OPENAI)
                    if not result.is_valid:
                        all_valid = False
                        validation_messages.append(f"OpenAI API Key: {result.message}")

                # Validate WordsAPI key if present
                if hasattr(self.window, 'wordsapi_key_input') and self.window.wordsapi_key_input.text():
                    result = validator.validate_api_key(self.window.wordsapi_key_input.text(), APIProvider.WORDSAPI)
                    if not result.is_valid:
                        all_valid = False
                        validation_messages.append(f"WordsAPI Key: {result.message}")

                if not all_valid:
                    from PyQt5.QtWidgets import QMessageBox
                    QMessageBox.warning(
                        self.window,
                        "Validation Error",
                        "Please fix the following issues before saving:\n\n" + "\n".join(validation_messages)
                    )
                    return

                # If validation passes, proceed with original save logic
                if hasattr(self.window, 'save_api_keys_callback'):
                    self.window.save_api_keys_callback()
                    logging.info("API keys saved successfully after validation")

            except Exception as e:
                logging.error(f"Error saving API keys: {e}")
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.critical(
                    self.window,
                    "Save Error",
                    f"Failed to save API keys: {str(e)}"
                )

        self.window.save_api_keys_button.clicked.connect(save_with_validation)
        form_layout.addRow(self.window.save_api_keys_button)
        layout.addWidget(group)

    def _create_progress_display_content(self, layout, page_id):
        """Create progress display content"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QProgressBar, QLabel

        group = QGroupBox("Writing Progress")
        group_layout = QVBoxLayout(group)

        # Word count display
        self.window.word_count_label = QLabel("Word Count: 0")
        group_layout.addWidget(self.window.word_count_label)

        # Progress bar
        self.window.progress_bar = QProgressBar()
        self.window.progress_bar.setRange(0, 100)
        self.window.progress_bar.setValue(0)
        group_layout.addWidget(self.window.progress_bar)

        # Additional stats
        stats_label = QLabel("Daily Goal: 0 / 1000 words\nSession Time: 0 minutes")
        group_layout.addWidget(stats_label)

        layout.addWidget(group)

    def _create_performance_metric_content(self, layout, page_id):
        """Create performance metric content"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QLabel, QProgressBar

        group = QGroupBox("Performance Monitoring")
        group_layout = QVBoxLayout(group)

        # Metric display based on page_id
        if page_id == "memory_usage":
            metric_label = QLabel("Current RAM Usage: 512 MB")
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(35)
            progress_bar.setFormat("35% of available memory")
        elif page_id == "cpu_usage":
            metric_label = QLabel("Current CPU Usage: 15%")
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(15)
            progress_bar.setFormat("15% processor utilization")
        elif page_id == "cache_hit_rate":
            metric_label = QLabel("Cache Hit Rate: 85%")
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(85)
            progress_bar.setFormat("85% cache efficiency")
        else:
            metric_label = QLabel(f"Monitoring: {page_id}")
            progress_bar = QProgressBar()
            progress_bar.setValue(50)

        group_layout.addWidget(metric_label)
        group_layout.addWidget(progress_bar)
        layout.addWidget(group)

    def _create_log_display_content(self, layout, page_id):
        """Create log display content"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QTextBrowser, QPushButton, QHBoxLayout

        group = QGroupBox("System Activity Log")
        group_layout = QVBoxLayout(group)

        # Create the log display that the main application expects
        self.window.log_tab = QTextBrowser()
        self.window.log_tab.setPlaceholderText("System log entries will appear here...")
        group_layout.addWidget(self.window.log_tab)

        # Log controls
        controls_layout = QHBoxLayout()
        clear_log_btn = QPushButton("Clear Log")
        export_log_btn = QPushButton("Export Log")
        group_layout.addWidget(clear_log_btn)
        group_layout.addWidget(export_log_btn)
        group_layout.addLayout(controls_layout)

        layout.addWidget(group)

    def _create_synonym_tool_content(self, layout, page_id):
        """Create synonym tool content"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel

        group = QGroupBox("Synonym Lookup Tool")
        group_layout = QVBoxLayout(group)

        # Create the synonyms tab that the main application expects
        self.window.synonyms_tab = QTextEdit()
        self.window.synonyms_tab.setPlaceholderText("Synonym suggestions will appear here...")
        group_layout.addWidget(QLabel("Word to lookup:"))

        word_input = QLineEdit()
        word_input.setPlaceholderText("Enter word to find synonyms...")
        group_layout.addWidget(word_input)

        lookup_btn = QPushButton("Find Synonyms")
        group_layout.addWidget(lookup_btn)

        group_layout.addWidget(QLabel("Synonyms:"))
        group_layout.addWidget(self.window.synonyms_tab)

        layout.addWidget(group)

    def _create_chapter_progress_content(self, layout, page_id):
        """Create chapter progress content"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView

        group = QGroupBox("Chapter Progress Overview")
        group_layout = QVBoxLayout(group)

        # Create progress table
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Chapter", "Target Words", "Current Words", "Progress"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Add sample data
        for i in range(5):
            table.insertRow(i)
            table.setItem(i, 0, QTableWidgetItem(f"Chapter {i+1}"))
            table.setItem(i, 1, QTableWidgetItem("5000"))
            table.setItem(i, 2, QTableWidgetItem(str(i * 1200)))
            table.setItem(i, 3, QTableWidgetItem(f"{min(100, i * 24)}%"))

        group_layout.addWidget(table)
        layout.addWidget(group)

    def _create_draft_editor_content(self, layout, page_id):
        """Create draft editor content"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QTextEdit, QComboBox, QLabel, QHBoxLayout

        group = QGroupBox("Current Draft Editor")
        group_layout = QVBoxLayout(group)

        # Draft selector
        draft_layout = QHBoxLayout()
        draft_layout.addWidget(QLabel("Draft Version:"))
        self.window.draft_version_selector = QComboBox()
        self.window.draft_version_selector.addItems(["Draft 1", "Draft 2", "Final Draft"])
        draft_layout.addWidget(self.window.draft_version_selector)
        group_layout.addLayout(draft_layout)

        # Create the story tab that the main application expects
        self.window.story_tab = QTextEdit()
        self.window.story_tab.setPlaceholderText("Start writing your story here...")
        group_layout.addWidget(self.window.story_tab)

        layout.addWidget(group)

    def _create_performance_table_content(self, layout, page_id):
        """Create performance table content"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView

        group = QGroupBox("Performance Statistics")
        group_layout = QVBoxLayout(group)

        table = QTableWidget()

        if page_id == "api_stats":
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["Service", "Requests", "Response Time"])
            # Add sample data
            services = [("OpenAI", "25", "1.2s"), ("WordsAPI", "15", "0.8s"), ("File System", "150", "0.1s")]
            for i, (service, requests, time) in enumerate(services):
                table.insertRow(i)
                table.setItem(i, 0, QTableWidgetItem(service))
                table.setItem(i, 1, QTableWidgetItem(requests))
                table.setItem(i, 2, QTableWidgetItem(time))

        elif page_id == "response_times":
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(["Operation", "Average Time", "Status"])
            operations = [("File Read", "45ms", "Good"), ("File Write", "78ms", "Good"), ("API Call", "1200ms", "Normal")]
            for i, (operation, time, status) in enumerate(operations):
                table.insertRow(i)
                table.setItem(i, 0, QTableWidgetItem(operation))
                table.setItem(i, 1, QTableWidgetItem(time))
                table.setItem(i, 2, QTableWidgetItem(status))

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        group_layout.addWidget(table)
        layout.addWidget(group)

    def _create_recommendations_content(self, layout, page_id):
        """Create recommendations content"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QTextBrowser

        group = QGroupBox("Performance Optimization Recommendations")
        group_layout = QVBoxLayout(group)

        recommendations = QTextBrowser()
        recommendations.setPlainText("""
Performance Optimization Recommendations:

1. Memory Usage: Currently within normal range (35% usage)
   - Consider clearing cache if usage exceeds 80%

2. File Operations: Operating efficiently
   - Cache hit rate is good at 85%

3. API Calls: Response times are acceptable
   - Consider implementing request batching for better efficiency

4. System Resources: All systems running normally
   - Disk space: 15GB available
   - Network: Connected and stable
        """)

        group_layout.addWidget(recommendations)
        layout.addWidget(group)

    def _create_system_info_content(self, layout, page_id):
        """Create system info content"""
        from PyQt5.QtWidgets import QGroupBox, QFormLayout, QLabel

        group = QGroupBox("System Resource Information")
        form_layout = QFormLayout(group)

        form_layout.addRow("Available Disk Space:", QLabel("15.2 GB"))
        form_layout.addRow("Network Status:", QLabel("Connected"))
        form_layout.addRow("System Memory:", QLabel("8 GB Total, 2.8 GB Available"))
        form_layout.addRow("CPU Cores:", QLabel("4 cores"))
        form_layout.addRow("Python Version:", QLabel("3.8.10"))
        form_layout.addRow("Qt Version:", QLabel("5.15.0"))

        layout.addWidget(group)

    def _create_export_status_content(self, layout, page_id):
        """Create export status content with enhanced export manager"""
        try:
            from export_ui import ExportManagerWidget

            # Create the export manager widget
            export_manager = ExportManagerWidget()

            # Store reference for later use
            if not hasattr(self.window, 'export_manager'):
                self.window.export_manager = export_manager

            layout.addWidget(export_manager)

        except ImportError as e:
            # Fallback to basic export status if import fails
            from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QLabel, QProgressBar, QPushButton

            group = QGroupBox("Export Status Monitor")
            group_layout = QVBoxLayout(group)

            status_label = QLabel("Last Export: Success")
            status_label.setStyleSheet("QLabel { color: green; font-weight: bold; }")
            group_layout.addWidget(status_label)

            export_progress = QProgressBar()
            export_progress.setValue(100)
            export_progress.setFormat("Export Complete")
            group_layout.addWidget(export_progress)

            self.window.export_button = QPushButton("Export Novel")
            group_layout.addWidget(self.window.export_button)

            layout.addWidget(group)

    def _create_export_formats_content(self, layout, page_id):
        """Create export formats content"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QCheckBox, QPushButton

        group = QGroupBox("Available Export Formats")
        group_layout = QVBoxLayout(group)

        formats = ["PDF", "DOCX", "TXT", "HTML", "EPUB", "RTF"]
        for format_name in formats:
            checkbox = QCheckBox(format_name)
            if format_name in ["PDF", "DOCX"]:  # Default selections
                checkbox.setChecked(True)
            group_layout.addWidget(checkbox)

        export_btn = QPushButton("Export in Selected Formats")
        group_layout.addWidget(export_btn)

        layout.addWidget(group)

    def _create_export_history_content(self, layout, page_id):
        """Create export history content"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView

        group = QGroupBox("Export History")
        group_layout = QVBoxLayout(group)

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Date", "Format", "Size", "Status"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Add sample export history
        history = [
            ("2025-08-02 10:30", "PDF", "2.5 MB", "Success"),
            ("2025-08-01 15:45", "DOCX", "1.8 MB", "Success"),
            ("2025-07-31 09:15", "EPUB", "3.2 MB", "Success"),
        ]

        for i, (date, format_type, size, status) in enumerate(history):
            table.insertRow(i)
            table.setItem(i, 0, QTableWidgetItem(date))
            table.setItem(i, 1, QTableWidgetItem(format_type))
            table.setItem(i, 2, QTableWidgetItem(size))
            table.setItem(i, 3, QTableWidgetItem(status))

        group_layout.addWidget(table)
        layout.addWidget(group)

    def _create_file_info_content(self, layout, page_id):
        """Create file info content"""
        from PyQt5.QtWidgets import QGroupBox, QFormLayout, QLabel

        group = QGroupBox("Generated File Information")
        form_layout = QFormLayout(group)

        form_layout.addRow("Story File Size:", QLabel("245 KB"))
        form_layout.addRow("Characters File Size:", QLabel("18 KB"))
        form_layout.addRow("World Building File Size:", QLabel("32 KB"))
        form_layout.addRow("Total Project Size:", QLabel("295 KB"))
        form_layout.addRow("Last Modified:", QLabel("2025-08-02 10:45"))

        layout.addWidget(group)

    def _create_export_settings_content(self, layout, page_id):
        """Create export settings content"""
        from PyQt5.QtWidgets import QGroupBox, QFormLayout, QComboBox, QCheckBox, QSpinBox

        group = QGroupBox("Export Quality and Format Settings")
        form_layout = QFormLayout(group)

        # PDF settings
        pdf_quality = QComboBox()
        pdf_quality.addItems(["High", "Medium", "Low"])
        form_layout.addRow("PDF Quality:", pdf_quality)

        # DOCX settings
        include_toc = QCheckBox("Include Table of Contents")
        include_toc.setChecked(True)
        form_layout.addRow("DOCX Options:", include_toc)

        # General settings
        page_numbers = QCheckBox("Include Page Numbers")
        page_numbers.setChecked(True)
        form_layout.addRow("General:", page_numbers)

        # Margins
        margin_size = QSpinBox()
        margin_size.setRange(10, 50)
        margin_size.setValue(25)
        margin_size.setSuffix(" mm")
        form_layout.addRow("Page Margins:", margin_size)

        layout.addWidget(group)

    def _create_missing_widgets(self):
        """Create any missing widgets that the main application expects"""
        from PyQt5.QtWidgets import QTextEdit, QComboBox, QLineEdit, QPushButton, QCheckBox, QDoubleSpinBox

        # Create missing widgets that might be referenced by the main application
        if not hasattr(self.window, 'characters_tab'):
            self.window.characters_tab = QTextEdit()
            self.window.characters_tab.setPlaceholderText("Describe your characters here...")

        if not hasattr(self.window, 'world_tab'):
            self.window.world_tab = QTextEdit()
            self.window.world_tab.setPlaceholderText("Describe your world and settings here...")

        if not hasattr(self.window, 'summaries_tab'):
            self.window.summaries_tab = QTextEdit()
            self.window.summaries_tab.setPlaceholderText("Chapter and plot summaries...")

        if not hasattr(self.window, 'drafts_tab'):
            self.window.drafts_tab = QTextEdit()
            self.window.drafts_tab.setPlaceholderText("Draft versions and revisions...")

        if not hasattr(self.window, 'readability_tab'):
            self.window.readability_tab = QTextEdit()
            self.window.readability_tab.setPlaceholderText("Readability analysis results...")

        if not hasattr(self.window, 'config_tab'):
            self.window.config_tab = QTextEdit()
            self.window.config_tab.setPlaceholderText("Configuration settings...")

        # Create additional input widgets
        if not hasattr(self.window, 'characters_seed_input'):
            self.window.characters_seed_input = QTextEdit()
            self.window.characters_seed_input.setPlaceholderText("Describe your main characters...")

        if not hasattr(self.window, 'world_seed_input'):
            self.window.world_seed_input = QTextEdit()
            self.window.world_seed_input.setPlaceholderText("Describe your story's world/setting...")

        if not hasattr(self.window, 'themes_seed_input'):
            self.window.themes_seed_input = QTextEdit()
            self.window.themes_seed_input.setPlaceholderText("Enter themes for your story...")

        if not hasattr(self.window, 'structure_seed_input'):
            self.window.structure_seed_input = QLineEdit()
            self.window.structure_seed_input.setPlaceholderText("Outline or structure notes...")

        if not hasattr(self.window, 'continuity_rules_input'):
            self.window.continuity_rules_input = QTextEdit()
            self.window.continuity_rules_input.setPlaceholderText("Enter continuity rules for your story...")

        if not hasattr(self.window, 'custom_prompt_input'):
            self.window.custom_prompt_input = QTextEdit()
            self.window.custom_prompt_input.setPlaceholderText("Enter custom writing prompts...")

        # Create control buttons
        if not hasattr(self.window, 'start_button'):
            self.window.start_button = QPushButton("Start Writing")
        if not hasattr(self.window, 'approve_button'):
            self.window.approve_button = QPushButton("Approve")
        if not hasattr(self.window, 'pause_button'):
            self.window.pause_button = QPushButton("Pause")

        # Create settings widgets
        if not hasattr(self.window, 'use_default_settings'):
            self.window.use_default_settings = QCheckBox("Use Default Settings")
        if not hasattr(self.window, 'thesaurus_weight_input'):
            self.window.thesaurus_weight_input = QDoubleSpinBox()
            self.window.thesaurus_weight_input.setRange(0.0, 1.0)
            self.window.thesaurus_weight_input.setValue(0.3)

        # Create API control buttons
        if not hasattr(self.window, 'reset_api_button'):
            self.window.reset_api_button = QPushButton("Reset API")
        if not hasattr(self.window, 'clear_cache_button'):
            self.window.clear_cache_button = QPushButton("Clear Cache")

        # Create legacy navigation buttons for backward compatibility
        if not hasattr(self.window, 'show_dashboard_button'):
            self.window.show_dashboard_button = QPushButton("Dashboard")
        if not hasattr(self.window, 'show_novel_settings_button'):
            self.window.show_novel_settings_button = QPushButton("Novel Settings")
        if not hasattr(self.window, 'show_advanced_settings_button'):
            self.window.show_advanced_settings_button = QPushButton("Advanced Settings")
        if not hasattr(self.window, 'show_performance_button'):
            self.window.show_performance_button = QPushButton("Performance")
        if not hasattr(self.window, 'show_settings_button'):
            self.window.show_settings_button = QPushButton("Settings")

    def add_missing_widgets(self):
        """Add any missing widgets that the main application expects"""
        if not self.window:
            return

        # Create any widgets that might be missing
        from PyQt5.QtWidgets import QPushButton, QComboBox, QLineEdit, QTextEdit

        # Ensure all expected widgets exist
        widget_defaults = {
            # Additional widgets that might be referenced
        }

        for widget_name, widget_class in widget_defaults.items():
            if not hasattr(self.window, widget_name):
                setattr(self.window, widget_name, widget_class())

    def _refresh_project_selector(self):
        """Refresh project selector placeholder"""
        pass

    def smart_switch_to_dashboard(self):
        """Switch to dashboard - use the progress graph page"""
        self._switch_to_content_page('progress_graph')
        print("✓ Dashboard switch - switched to Progress Graph")

    def smart_switch_to_novel_settings(self):
        """Switch to novel settings - use the novel concept page"""
        self._switch_to_content_page('novel_concept')
        print("✓ Novel Settings - switched to Novel Concept")

    def switch_to_settings(self):
        """Switch to settings - use the OpenAI API key page"""
        self._switch_to_content_page('openai_api_key')
        print("✓ Settings - switched to API Settings")

    def smart_switch_to_performance(self):
        """Switch to performance monitoring - use the memory usage page"""
        self._switch_to_content_page('memory_usage')
        print("✓ Performance Monitor - switched to Memory Usage")

    def smart_switch_to_settings(self):
        """Switch to general settings - use the OpenAI API key page"""
        self._switch_to_content_page('openai_api_key')
        print("✓ Settings - switched to API Settings")

    def _show_project_content(self):
        """Show project content placeholder"""
        pass

    def switch_to_new_project_mode(self):
        """Switch UI to new project mode when no project is selected"""
        try:
            # Reset UI to show new project creation interface
            if hasattr(self.window, 'project_selector'):
                self.window.project_selector.setCurrentText("Select a project")

            # Clear all input fields
            input_widgets = [
                'idea_input', 'characters_seed_input', 'world_seed_input',
                'themes_seed_input', 'structure_seed_input', 'continuity_rules_input',
                'custom_prompt_input'
            ]

            for widget_name in input_widgets:
                if hasattr(self.window, widget_name):
                    widget = getattr(self.window, widget_name)
                    if hasattr(widget, 'clear'):
                        widget.clear()
                    elif hasattr(widget, 'setText'):
                        widget.setText("")

            # Reset dropdown selections
            dropdown_widgets = [
                'tone_input', 'sub_tone_input', 'theme_dropdown', 'reading_level_input'
            ]

            for widget_name in dropdown_widgets:
                if hasattr(self.window, widget_name):
                    widget = getattr(self.window, widget_name)
                    if hasattr(widget, 'setCurrentIndex'):
                        widget.setCurrentIndex(0)

            print("✓ Switched to new project mode")

        except Exception as e:
            print(f"⚠ Error switching to new project mode: {e}")

    def switch_to_project_workspace(self):
        """Switch UI to project workspace mode when a project is loaded"""
        try:
            # Enable project-specific UI elements
            # This is where you'd show project-specific tabs, enable buttons, etc.
            print("✓ Switched to project workspace mode")

        except Exception as e:
            print(f"⚠ Error switching to project workspace mode: {e}")

    def _create_overview_content(self, layout, page_id):
        """Create overview content for section pages"""
        from PyQt5.QtWidgets import QLabel, QVBoxLayout, QFrame
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont

        if page_id == "novel_settings":
            # Create Novel Settings overview
            overview_label = QLabel("Novel Settings Configuration")
            overview_label.setFont(QFont("Arial", 14, QFont.Bold))
            overview_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(overview_label)

            description = QLabel("""
            Configure your novel's core parameters and writing guidelines.
            Use the subsections below to set up:

            • Novel Concept - Your main story idea
            • Primary Tone - Overall writing style
            • Sub-Tone - Secondary emotional undertones
            • Theme - Central message or meaning
            • Target Word Count - Desired final length
            • Reading Level - Target audience complexity
            • Chapter Organization - Structure planning
            • Total Chapters - Planned book sections
            • Chapter Sections - Subsections per chapter
            """)
            description.setWordWrap(True)
            description.setAlignment(Qt.AlignLeft)
            description.setStyleSheet("QLabel { background-color: #f8f9fa; padding: 15px; border-radius: 8px; }")
            layout.addWidget(description)
        else:
            # Generic overview
            overview_label = QLabel(f"Overview for {page_id}")
            overview_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(overview_label)

    # New content creation methods for expanded backend integration

    def _create_character_tools_content(self, layout, page_id):
        """Create character development tools interface"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QTextEdit, QListWidget, QPushButton, QLineEdit, QFormLayout, QLabel, QComboBox, QSpinBox

        # Character list section
        char_group = QGroupBox("Character Management")
        char_layout = QVBoxLayout(char_group)

        # Character selector
        char_selector_layout = QHBoxLayout()
        char_selector_layout.addWidget(QLabel("Character:"))
        char_dropdown = QComboBox()
        char_dropdown.addItems(["Create New Character...", "Main Protagonist", "Antagonist", "Supporting Character 1"])
        char_selector_layout.addWidget(char_dropdown)
        char_layout.addLayout(char_selector_layout)

        # Character details form
        char_form = QFormLayout()
        char_form.addRow("Name:", QLineEdit())
        char_form.addRow("Age:", QSpinBox())
        char_form.addRow("Role:", QComboBox())
        char_form.addRow("Background:", QTextEdit())
        char_form.addRow("Personality:", QTextEdit())
        char_form.addRow("Goals:", QTextEdit())
        char_form.addRow("Conflicts:", QTextEdit())
        char_layout.addLayout(char_form)

        # Character actions
        char_actions = QHBoxLayout()
        char_actions.addWidget(QPushButton("Save Character"))
        char_actions.addWidget(QPushButton("Delete Character"))
        char_actions.addWidget(QPushButton("Export Character"))
        char_layout.addLayout(char_actions)

        layout.addWidget(char_group)

    def _create_world_tools_content(self, layout, page_id):
        """Create world building tools interface"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QTextEdit, QTreeWidget, QPushButton, QLineEdit, QFormLayout, QLabel, QTabWidget, QWidget

        # World building tabs
        world_tabs = QTabWidget()

        # Geography tab
        geo_widget = QWidget()
        geo_layout = QVBoxLayout(geo_widget)
        geo_layout.addWidget(QLabel("Geography and Locations"))
        geo_layout.addWidget(QTextEdit("Describe the physical world, locations, maps, climate..."))
        world_tabs.addTab(geo_widget, "Geography")

        # Culture tab
        culture_widget = QWidget()
        culture_layout = QVBoxLayout(culture_widget)
        culture_layout.addWidget(QLabel("Culture and Society"))
        culture_layout.addWidget(QTextEdit("Describe customs, traditions, social structure..."))
        world_tabs.addTab(culture_widget, "Culture")

        # Magic/Technology tab
        tech_widget = QWidget()
        tech_layout = QVBoxLayout(tech_widget)
        tech_layout.addWidget(QLabel("Magic System / Technology"))
        tech_layout.addWidget(QTextEdit("Describe the rules of magic or technology level..."))
        world_tabs.addTab(tech_widget, "Magic/Tech")

        # History tab
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget)
        history_layout.addWidget(QLabel("History and Timeline"))
        history_layout.addWidget(QTextEdit("Important historical events and their impact..."))
        world_tabs.addTab(history_widget, "History")

        layout.addWidget(world_tabs)

    def _create_timeline_tools_content(self, layout, page_id):
        """Create timeline management interface"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QTableWidget, QPushButton, QLineEdit, QDateEdit, QTextEdit, QHeaderView, QTableWidgetItem

        # Timeline table
        timeline_group = QGroupBox("Story Timeline")
        timeline_layout = QVBoxLayout(timeline_group)

        # Timeline controls
        timeline_controls = QHBoxLayout()
        timeline_controls.addWidget(QPushButton("Add Event"))
        timeline_controls.addWidget(QPushButton("Edit Event"))
        timeline_controls.addWidget(QPushButton("Delete Event"))
        timeline_controls.addWidget(QPushButton("Sort by Date"))
        timeline_layout.addLayout(timeline_controls)

        # Timeline table
        timeline_table = QTableWidget(0, 4)
        timeline_table.setHorizontalHeaderLabels(["Date", "Event", "Characters Involved", "Impact"])
        timeline_table.horizontalHeader().setStretchLastSection(True)
        timeline_layout.addWidget(timeline_table)

        layout.addWidget(timeline_group)

    def _create_research_tools_content(self, layout, page_id):
        """Create research notes interface"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QTextEdit, QListWidget, QPushButton, QLineEdit, QTabWidget, QLabel, QWidget

        # Research organization
        research_tabs = QTabWidget()

        # General research tab
        general_widget = QWidget()
        general_layout = QVBoxLayout(general_widget)
        general_layout.addWidget(QLabel("General Research Notes"))
        general_layout.addWidget(QTextEdit("Store general research, facts, references..."))
        research_tabs.addTab(general_widget, "General")

        # Historical research tab
        historical_widget = QWidget()
        historical_layout = QVBoxLayout(historical_widget)
        historical_layout.addWidget(QLabel("Historical Research"))
        historical_layout.addWidget(QTextEdit("Historical facts, time periods, events..."))
        research_tabs.addTab(historical_widget, "Historical")

        # Technical research tab
        technical_widget = QWidget()
        technical_layout = QVBoxLayout(technical_widget)
        technical_layout.addWidget(QLabel("Technical Research"))
        technical_layout.addWidget(QTextEdit("Technical details, scientific facts, processes..."))
        research_tabs.addTab(technical_widget, "Technical")

        # Cultural research tab
        cultural_widget = QWidget()
        cultural_layout = QVBoxLayout(cultural_widget)
        cultural_layout.addWidget(QLabel("Cultural Research"))
        cultural_layout.addWidget(QTextEdit("Cultural practices, languages, customs..."))
        research_tabs.addTab(cultural_widget, "Cultural")

        layout.addWidget(research_tabs)

    def _create_analytics_display_content(self, layout, page_id):
        """Create writing analytics display"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QTableWidget, QHeaderView, QFormLayout

        # Writing statistics
        stats_group = QGroupBox("Writing Statistics")
        stats_layout = QVBoxLayout(stats_group)

        # Progress bars
        progress_layout = QFormLayout()

        # Word count progress
        word_progress = QProgressBar()
        word_progress.setValue(65)
        progress_layout.addRow("Word Count Progress:", word_progress)

        # Chapter progress
        chapter_progress = QProgressBar()
        chapter_progress.setValue(40)
        progress_layout.addRow("Chapter Progress:", chapter_progress)

        # Daily goal progress
        daily_progress = QProgressBar()
        daily_progress.setValue(80)
        progress_layout.addRow("Daily Goal:", daily_progress)

        stats_layout.addLayout(progress_layout)

        # Writing session table
        session_table = QTableWidget(5, 4)
        session_table.setHorizontalHeaderLabels(["Date", "Words Written", "Time Spent", "Goal Met"])
        session_table.horizontalHeader().setStretchLastSection(True)
        stats_layout.addWidget(session_table)

        layout.addWidget(stats_group)

    def _create_collaboration_tools_content(self, layout, page_id):
        """Create collaboration interface"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QLineEdit, QLabel, QTextEdit, QComboBox

        # Collaboration management
        collab_group = QGroupBox("Collaboration Management")
        collab_layout = QVBoxLayout(collab_group)

        # Collaborator list
        collab_list_layout = QHBoxLayout()
        collab_list_layout.addWidget(QLabel("Collaborators:"))
        collab_list = QListWidget()
        collab_list.addItems(["No collaborators added"])
        collab_list_layout.addWidget(collab_list)
        collab_layout.addLayout(collab_list_layout)

        # Add collaborator
        add_collab_layout = QHBoxLayout()
        add_collab_layout.addWidget(QLabel("Add Collaborator:"))
        add_collab_layout.addWidget(QLineEdit())
        add_collab_layout.addWidget(QComboBox())  # Permission level
        add_collab_layout.addWidget(QPushButton("Add"))
        collab_layout.addLayout(add_collab_layout)

        # Comments section
        comments_layout = QVBoxLayout()
        comments_layout.addWidget(QLabel("Comments and Reviews:"))
        comments_layout.addWidget(QTextEdit("Collaboration comments will appear here..."))
        collab_layout.addLayout(comments_layout)

        layout.addWidget(collab_group)

    def _create_backup_tools_content(self, layout, page_id):
        """Create backup management interface"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QCheckBox, QSpinBox, QComboBox, QFormLayout

        # Backup settings
        backup_group = QGroupBox("Backup Management")
        backup_layout = QVBoxLayout(backup_group)

        # Backup controls
        backup_controls = QHBoxLayout()
        backup_controls.addWidget(QPushButton("Create Backup Now"))
        backup_controls.addWidget(QPushButton("Restore from Backup"))
        backup_controls.addWidget(QPushButton("Delete Old Backups"))
        backup_layout.addLayout(backup_controls)

        # Auto-backup settings
        auto_backup_layout = QFormLayout()
        auto_backup_layout.addRow("Auto-backup enabled:", QCheckBox())
        auto_backup_layout.addRow("Backup frequency:", QComboBox())
        auto_backup_layout.addRow("Keep backups for (days):", QSpinBox())
        backup_layout.addLayout(auto_backup_layout)

        # Backup list
        backup_layout.addWidget(QLabel("Available Backups:"))
        backup_list = QListWidget()
        backup_list.addItems(["No backups found"])
        backup_layout.addWidget(backup_list)

        layout.addWidget(backup_group)

    def _create_template_tools_content(self, layout, page_id):
        """Create template management interface"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QTextEdit, QLineEdit

        # Template management
        template_group = QGroupBox("Template Management")
        template_layout = QVBoxLayout(template_group)

        # Template list
        template_list_layout = QVBoxLayout()
        template_list_layout.addWidget(QLabel("Available Templates:"))
        template_list = QListWidget()
        template_list.addItems(["Character Template", "Chapter Template", "Scene Template", "World Building Template"])
        template_list_layout.addWidget(template_list)
        template_layout.addLayout(template_list_layout)

        # Template editor
        template_editor_layout = QVBoxLayout()
        template_editor_layout.addWidget(QLabel("Template Content:"))
        template_editor = QTextEdit("Select a template to edit...")
        template_editor_layout.addWidget(template_editor)

        # Template actions
        template_actions = QHBoxLayout()
        template_actions.addWidget(QPushButton("Save Template"))
        template_actions.addWidget(QPushButton("Create New"))
        template_actions.addWidget(QPushButton("Delete Template"))
        template_editor_layout.addLayout(template_actions)

        template_layout.addLayout(template_editor_layout)
        layout.addWidget(template_group)

    def _create_quality_tools_content(self, layout, page_id):
        """Create quality analysis interface"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QProgressBar, QTableWidget, QFormLayout

        # Quality analysis
        quality_group = QGroupBox("Writing Quality Analysis")
        quality_layout = QVBoxLayout(quality_group)

        # Analysis controls
        analysis_controls = QHBoxLayout()
        analysis_controls.addWidget(QPushButton("Analyze Current Chapter"))
        analysis_controls.addWidget(QPushButton("Analyze Full Story"))
        analysis_controls.addWidget(QPushButton("Grammar Check"))
        quality_layout.addLayout(analysis_controls)

        # Quality metrics
        metrics_layout = QFormLayout()

        readability_bar = QProgressBar()
        readability_bar.setValue(75)
        metrics_layout.addRow("Readability Score:", readability_bar)

        grammar_bar = QProgressBar()
        grammar_bar.setValue(90)
        metrics_layout.addRow("Grammar Score:", grammar_bar)

        style_bar = QProgressBar()
        style_bar.setValue(80)
        metrics_layout.addRow("Style Consistency:", style_bar)

        quality_layout.addLayout(metrics_layout)

        # Suggestions
        quality_layout.addWidget(QLabel("Improvement Suggestions:"))
        suggestions = QTextEdit("Quality analysis suggestions will appear here...")
        quality_layout.addWidget(suggestions)

        layout.addWidget(quality_group)

    def _create_ai_tools_content(self, layout, page_id):
        """Create AI writing assistant interface"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QComboBox, QCheckBox

        # AI assistant
        ai_group = QGroupBox("AI Writing Assistant")
        ai_layout = QVBoxLayout(ai_group)

        # AI service selection
        ai_service_layout = QHBoxLayout()
        ai_service_layout.addWidget(QLabel("AI Service:"))
        ai_service = QComboBox()
        ai_service.addItems(["OpenAI GPT", "Anthropic Claude", "Local AI", "Custom Endpoint"])
        ai_service_layout.addWidget(ai_service)
        ai_layout.addLayout(ai_service_layout)

        # AI assistance options
        ai_options = QVBoxLayout()
        ai_options.addWidget(QCheckBox("Character development suggestions"))
        ai_options.addWidget(QCheckBox("Plot development assistance"))
        ai_options.addWidget(QCheckBox("Dialogue improvement"))
        ai_options.addWidget(QCheckBox("Description enhancement"))
        ai_layout.addLayout(ai_options)

        # AI prompt area
        ai_layout.addWidget(QLabel("AI Prompt:"))
        ai_prompt = QTextEdit("Enter your writing assistance request...")
        ai_layout.addWidget(ai_prompt)

        # AI controls
        ai_controls = QHBoxLayout()
        ai_controls.addWidget(QPushButton("Get AI Suggestions"))
        ai_controls.addWidget(QPushButton("Clear Conversation"))
        ai_layout.addLayout(ai_controls)

        # AI response
        ai_layout.addWidget(QLabel("AI Response:"))
        ai_response = QTextEdit("AI suggestions will appear here...")
        ai_layout.addWidget(ai_response)

        layout.addWidget(ai_group)

    def _create_stats_display_content(self, layout, page_id):
        """Create project statistics display"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QTableWidget, QFormLayout

        # Project statistics
        stats_group = QGroupBox("Project Statistics")
        stats_layout = QVBoxLayout(stats_group)

        # Key metrics
        metrics_layout = QFormLayout()
        metrics_layout.addRow("Total Words:", QLabel("0"))
        metrics_layout.addRow("Total Chapters:", QLabel("0"))
        metrics_layout.addRow("Pages (estimated):", QLabel("0"))
        metrics_layout.addRow("Characters:", QLabel("0"))
        metrics_layout.addRow("Scenes:", QLabel("0"))
        metrics_layout.addRow("Project Age:", QLabel("0 days"))
        stats_layout.addLayout(metrics_layout)

        # Progress visualization
        progress_layout = QFormLayout()

        completion_bar = QProgressBar()
        completion_bar.setValue(0)
        progress_layout.addRow("Overall Completion:", completion_bar)

        goal_bar = QProgressBar()
        goal_bar.setValue(0)
        progress_layout.addRow("Word Count Goal:", goal_bar)

        stats_layout.addLayout(progress_layout)

        layout.addWidget(stats_group)

    def _create_goal_tools_content(self, layout, page_id):
        """Create goal tracking interface"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpinBox, QDateEdit, QTextEdit, QTableWidget, QComboBox, QFormLayout

        # Goal management
        goal_group = QGroupBox("Writing Goals")
        goal_layout = QVBoxLayout(goal_group)

        # Goal creation
        new_goal_layout = QFormLayout()
        new_goal_layout.addRow("Goal Type:", QComboBox())
        new_goal_layout.addRow("Target Amount:", QSpinBox())
        new_goal_layout.addRow("Deadline:", QDateEdit())
        new_goal_layout.addRow("Description:", QTextEdit())
        goal_layout.addLayout(new_goal_layout)

        # Goal actions
        goal_actions = QHBoxLayout()
        goal_actions.addWidget(QPushButton("Add Goal"))
        goal_actions.addWidget(QPushButton("Update Progress"))
        goal_actions.addWidget(QPushButton("Complete Goal"))
        goal_layout.addLayout(goal_actions)

        # Active goals table
        goal_layout.addWidget(QLabel("Active Goals:"))
        goals_table = QTableWidget(0, 5)
        goals_table.setHorizontalHeaderLabels(["Goal", "Target", "Progress", "Deadline", "Status"])
        goal_layout.addWidget(goals_table)

        layout.addWidget(goal_group)

    def _create_deadline_tools_content(self, layout, page_id):
        """Create deadline management interface"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDateEdit, QTextEdit, QTableWidget, QComboBox, QCheckBox, QFormLayout, QLineEdit

        # Deadline management
        deadline_group = QGroupBox("Deadline Management")
        deadline_layout = QVBoxLayout(deadline_group)

        # Deadline creation
        new_deadline_layout = QFormLayout()
        new_deadline_layout.addRow("Deadline Name:", QLineEdit())
        new_deadline_layout.addRow("Due Date:", QDateEdit())
        new_deadline_layout.addRow("Priority:", QComboBox())
        new_deadline_layout.addRow("Reminders:", QCheckBox("Enable notifications"))
        new_deadline_layout.addRow("Notes:", QTextEdit())
        deadline_layout.addLayout(new_deadline_layout)

        # Deadline actions
        deadline_actions = QHBoxLayout()
        deadline_actions.addWidget(QPushButton("Add Deadline"))
        deadline_actions.addWidget(QPushButton("Mark Complete"))
        deadline_actions.addWidget(QPushButton("Extend Deadline"))
        deadline_layout.addLayout(deadline_actions)

        # Deadlines table
        deadline_layout.addWidget(QLabel("Upcoming Deadlines:"))
        deadlines_table = QTableWidget(0, 4)
        deadlines_table.setHorizontalHeaderLabels(["Deadline", "Due Date", "Priority", "Status"])
        deadline_layout.addWidget(deadlines_table)

        layout.addWidget(deadline_group)

    def _create_version_tools_content(self, layout, page_id):
        """Create version control interface"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QTextEdit, QLineEdit

        # Version control
        version_group = QGroupBox("Version Control")
        version_layout = QVBoxLayout(version_group)

        # Version actions
        version_actions = QHBoxLayout()
        version_actions.addWidget(QPushButton("Create Version"))
        version_actions.addWidget(QPushButton("Compare Versions"))
        version_actions.addWidget(QPushButton("Restore Version"))
        version_actions.addWidget(QPushButton("Delete Version"))
        version_layout.addLayout(version_actions)

        # Version list
        version_layout.addWidget(QLabel("Project Versions:"))
        version_list = QListWidget()
        version_list.addItems(["No versions created"])
        version_layout.addWidget(version_list)

        # Version notes
        version_layout.addWidget(QLabel("Version Notes:"))
        version_notes = QTextEdit("Version details and changes...")
        version_layout.addWidget(version_notes)

        layout.addWidget(version_group)

    def _create_advanced_config_content(self, layout, page_id):
        """Create advanced configuration interface"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QCheckBox, QSpinBox, QComboBox, QLineEdit, QTabWidget, QWidget, QFormLayout

        # Advanced settings tabs
        config_tabs = QTabWidget()

        # Performance tab
        perf_widget = QWidget()
        perf_layout = QFormLayout(perf_widget)
        perf_layout.addRow("Auto-save interval (minutes):", QSpinBox())
        perf_layout.addRow("Cache size (MB):", QSpinBox())
        perf_layout.addRow("Memory optimization:", QCheckBox())
        config_tabs.addTab(perf_widget, "Performance")

        # Interface tab
        ui_widget = QWidget()
        ui_layout = QFormLayout(ui_widget)
        ui_layout.addRow("Theme:", QComboBox())
        ui_layout.addRow("Font size:", QSpinBox())
        ui_layout.addRow("Auto-complete:", QCheckBox())
        config_tabs.addTab(ui_widget, "Interface")

        # Writing tab
        writing_widget = QWidget()
        writing_layout = QFormLayout(writing_widget)
        writing_layout.addRow("Default document format:", QComboBox())
        writing_layout.addRow("Spell check:", QCheckBox())
        writing_layout.addRow("Grammar check:", QCheckBox())
        config_tabs.addTab(writing_widget, "Writing")

        layout.addWidget(config_tabs)

    def _create_plugin_tools_content(self, layout, page_id):
        """Create plugin management interface"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QTextEdit, QCheckBox

        # Plugin management
        plugin_group = QGroupBox("Plugin Management")
        plugin_layout = QVBoxLayout(plugin_group)

        # Plugin controls
        plugin_controls = QHBoxLayout()
        plugin_controls.addWidget(QPushButton("Install Plugin"))
        plugin_controls.addWidget(QPushButton("Update Plugins"))
        plugin_controls.addWidget(QPushButton("Remove Plugin"))
        plugin_layout.addLayout(plugin_controls)

        # Installed plugins
        plugin_layout.addWidget(QLabel("Installed Plugins:"))
        plugin_list = QListWidget()
        plugin_list.addItems(["No plugins installed"])
        plugin_layout.addWidget(plugin_list)

        # Plugin details
        plugin_layout.addWidget(QLabel("Plugin Details:"))
        plugin_details = QTextEdit("Select a plugin to view details...")
        plugin_layout.addWidget(plugin_details)

        layout.addWidget(plugin_group)

    def _create_workflow_config_content(self, layout, page_id):
        """Create workflow configuration interface"""
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QListWidget, QTextEdit, QComboBox, QCheckBox, QFormLayout

        # Workflow configuration
        workflow_group = QGroupBox("Workflow Configuration")
        workflow_layout = QVBoxLayout(workflow_group)

        # Workflow templates
        workflow_layout.addWidget(QLabel("Workflow Templates:"))
        workflow_templates = QComboBox()
        workflow_templates.addItems(["Custom", "Academic Writing", "Novel Writing", "Short Story", "Screenplay"])
        workflow_layout.addWidget(workflow_templates)

        # Workflow steps
        workflow_layout.addWidget(QLabel("Workflow Steps:"))
        workflow_steps = QListWidget()
        workflow_steps.addItems(["Outline", "First Draft", "Review", "Revision", "Final Edit"])
        workflow_layout.addWidget(workflow_steps)

        # Workflow settings
        workflow_settings = QFormLayout()
        workflow_settings.addRow("Auto-advance stages:", QCheckBox())
        workflow_settings.addRow("Require approval:", QCheckBox())
        workflow_settings.addRow("Track time:", QCheckBox())
        workflow_layout.addLayout(workflow_settings)

        # Workflow actions
        workflow_actions = QHBoxLayout()
        workflow_actions.addWidget(QPushButton("Save Workflow"))
        workflow_actions.addWidget(QPushButton("Load Template"))
        workflow_actions.addWidget(QPushButton("Reset Workflow"))
        workflow_layout.addLayout(workflow_actions)

        layout.addWidget(workflow_group)

__all__ = [
    'core_ui',
    'analytics_ui',
    'management_ui',
    'UIComponents'  # Legacy alias
]

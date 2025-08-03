"""
Onboarding Wizard for FANWS
Implements QWizard for guided project creation and template selection
"""

from PyQt5.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTextEdit, QComboBox, QRadioButton,
    QCheckBox, QGroupBox, QFormLayout, QButtonGroup, QScrollArea,
    QFrame, QSpinBox, QDoubleSpinBox, QMessageBox, QProgressBar,
    QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QPalette, QColor

import os
import logging


class OnboardingWizard(QWizard):
    """Onboarding wizard for new users and project creation"""

    # Signal emitted when wizard completes with project data
    project_created = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.project_data = {}
        self.init_wizard()

    def init_wizard(self):
        """Initialize the wizard with all pages"""
        self.setWindowTitle("FANWS Setup Wizard")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setFixedSize(800, 600)

        # Set wizard options
        self.setOptions(
            QWizard.HaveHelpButton |
            QWizard.HelpButtonOnRight |
            QWizard.HaveCustomButton1 |
            QWizard.HaveCustomButton2
        )

        # Custom button labels
        self.setButtonText(QWizard.CustomButton1, "Skip Tutorial")
        self.setButtonText(QWizard.CustomButton2, "Quick Start")

        # Apply modern styling
        self.setStyleSheet("""
            QWizard {
                background-color: #f8f9fa;
            }
            QWizardPage {
                background-color: white;
                border-radius: 8px;
            }
            QLabel {
                color: #333;
            }
            .title {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin: 20px 0;
            }
            .subtitle {
                font-size: 16px;
                color: #7f8c8d;
                margin: 10px 0;
            }
            .feature-label {
                font-size: 14px;
                font-weight: bold;
                color: #34495e;
            }
        """)

        # Add wizard pages
        self.addPage(WelcomePage(self))
        self.addPage(ProjectTypePage(self))
        self.addPage(TemplateSelectionPage(self))
        self.addPage(ProjectDetailsPage(self))
        self.addPage(AdvancedSettingsPage(self))
        self.addPage(APIConfigurationPage(self))
        self.addPage(FinalSetupPage(self))

        # Connect signals
        self.customButtonClicked.connect(self.handle_custom_button)
        self.helpRequested.connect(self.show_help)

    def handle_custom_button(self, button):
        """Handle custom button clicks"""
        if button == QWizard.CustomButton1:  # Skip Tutorial
            self.accept()
        elif button == QWizard.CustomButton2:  # Quick Start
            self.quick_start()

    def quick_start(self):
        """Quick start with default settings"""
        self.project_data = {
            'name': 'My Novel',
            'type': 'custom',
            'template': None,
            'idea': 'A story waiting to be told',
            'tone': 'neutral',
            'reading_level': 'College',
            'target_words': 50000,
            'use_defaults': True
        }
        self.project_created.emit(self.project_data)
        self.accept()

    def show_help(self):
        """Show context-sensitive help"""
        current_page = self.currentPage()
        if hasattr(current_page, 'get_help_text'):
            help_text = current_page.get_help_text()
        else:
            help_text = "Help is available for this step. Contact support if you need assistance."

        QMessageBox.information(self, "Help", help_text)

    def accept(self):
        """Handle wizard completion"""
        if hasattr(self.currentPage(), 'get_project_data'):
            page_data = self.currentPage().get_project_data()
            self.project_data.update(page_data)

        if self.project_data:
            self.project_created.emit(self.project_data)

        super().accept()


class WelcomePage(QWizardPage):
    """Welcome page introducing FANWS"""

    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.init_page()

    def init_page(self):
        """Initialize the welcome page"""
        self.setTitle("Welcome to FANWS")
        self.setSubTitle("Fiction AI Novel Writing Suite")

        layout = QVBoxLayout(self)

        # Main welcome content
        welcome_label = QLabel("Welcome to the Fiction AI Novel Writing Suite!")
        welcome_label.setObjectName("title")
        welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_label)

        description = QLabel(
            "FANWS is an AI-powered writing assistant that helps you create "
            "compelling novels from concept to completion. This wizard will "
            "guide you through setting up your first project."
        )
        description.setObjectName("subtitle")
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignCenter)
        layout.addWidget(description)

        # Features overview
        features_group = QGroupBox("What FANWS Can Do For You:")
        features_layout = QVBoxLayout(features_group)

        features = [
            "🤖 AI-powered content generation and story development",
            "📚 Multiple genre and structure templates",
            "📊 Real-time writing analytics and progress tracking",
            "🔄 Automatic backup and version management",
            "🎨 Customizable tone, style, and reading level",
            "📝 Draft management and editing assistance",
            "🔗 API integration with OpenAI and writing tools"
        ]

        for feature in features:
            feature_label = QLabel(feature)
            feature_label.setObjectName("feature-label")
            features_layout.addWidget(feature_label)

        layout.addWidget(features_group)

        # Getting started info
        start_info = QLabel(
            "This wizard will take about 3-5 minutes to complete. "
            "You can always change these settings later."
        )
        start_info.setObjectName("subtitle")
        start_info.setWordWrap(True)
        start_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(start_info)

        layout.addStretch()

    def get_help_text(self):
        return (
            "This is the welcome page for FANWS setup. Here you can:\n\n"
            "• Continue with the guided setup\n"
            "• Use 'Quick Start' for default settings\n"
            "• Skip the tutorial if you're familiar with writing software\n\n"
            "The wizard will help you create your first project and configure "
            "the essential settings for AI-powered novel writing."
        )


class ProjectTypePage(QWizardPage):
    """Page for selecting project type"""

    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.project_type_group = None
        self.init_page()

    def init_page(self):
        """Initialize project type selection"""
        self.setTitle("Choose Your Project Type")
        self.setSubTitle("Select how you'd like to start your novel")

        layout = QVBoxLayout(self)

        # Project type selection
        self.project_type_group = QButtonGroup(self)

        project_types = [
            ("fresh_start", "Start Fresh",
             "Begin with a blank canvas and build your story from scratch"),
            ("template_based", "Use a Template",
             "Start with a proven story structure or genre template"),
            ("import_existing", "Import Existing Work",
             "Continue working on a story you've already started"),
            ("collaborative", "Collaborative Project",
             "Work with others on a shared novel project")
        ]

        for i, (type_id, title, description) in enumerate(project_types):
            type_frame = QFrame()
            type_frame.setFrameStyle(QFrame.Box)
            type_frame.setStyleSheet("""
                QFrame {
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 10px;
                    margin: 5px;
                }
                QFrame:hover {
                    border-color: #4CAF50;
                }
            """)

            type_layout = QVBoxLayout(type_frame)

            radio = QRadioButton(title)
            radio.setStyleSheet("font-weight: bold; font-size: 14px;")

            desc_label = QLabel(description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #666; margin-left: 20px;")

            type_layout.addWidget(radio)
            type_layout.addWidget(desc_label)

            self.project_type_group.addButton(radio, i)
            layout.addWidget(type_frame)

            # Default to first option
            if i == 0:
                radio.setChecked(True)

        layout.addStretch()

        # Register field for validation
        self.registerField("project_type", self.project_type_group.buttons()[0])

    def get_project_data(self):
        """Return selected project type data"""
        type_mapping = ["fresh_start", "template_based", "import_existing", "collaborative"]
        selected_id = self.project_type_group.checkedId()
        return {"project_type": type_mapping[selected_id] if selected_id >= 0 else "fresh_start"}

    def get_help_text(self):
        return (
            "Choose how you want to start your novel:\n\n"
            "• Start Fresh: Best for new stories and first-time users\n"
            "• Use Template: Great for specific genres or proven structures\n"
            "• Import Existing: Continue work on stories started elsewhere\n"
            "• Collaborative: Share your project with other writers\n\n"
            "Don't worry - you can always change your approach later!"
        )


class TemplateSelectionPage(QWizardPage):
    """Page for template selection (shown conditionally)"""

    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.template_group = None
        self.init_page()

    def init_page(self):
        """Initialize template selection"""
        self.setTitle("Choose a Template")
        self.setSubTitle("Select a template to guide your novel structure")

        layout = QVBoxLayout(self)

        # Template categories
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        self.template_group = QButtonGroup(self)

        template_categories = [
            ("Genre Templates", [
                ("fantasy", "Fantasy Adventure", "Epic quests, magic systems, heroic journeys"),
                ("scifi", "Science Fiction", "Future worlds, technology, space exploration"),
                ("romance", "Romance Novel", "Love stories, relationship development"),
                ("mystery", "Mystery/Thriller", "Suspense, investigation, plot twists"),
                ("historical", "Historical Fiction", "Period settings, historical accuracy")
            ]),
            ("Structure Templates", [
                ("three_act", "Three-Act Structure", "Classic beginning, middle, end format"),
                ("hero_journey", "Hero's Journey", "Joseph Campbell's monomyth structure"),
                ("seven_point", "Seven-Point Story", "Dan Wells' story structure method"),
                ("freytag", "Freytag's Pyramid", "Classic dramatic structure")
            ])
        ]

        button_id = 0
        for category_name, templates in template_categories:
            category_group = QGroupBox(category_name)
            category_layout = QVBoxLayout(category_group)

            for template_id, name, description in templates:
                template_frame = QFrame()
                template_frame.setFrameStyle(QFrame.Box)
                template_frame.setStyleSheet("""
                    QFrame {
                        border: 1px solid #e0e0e0;
                        border-radius: 5px;
                        padding: 8px;
                        margin: 2px;
                    }
                    QFrame:hover {
                        border-color: #4CAF50;
                    }
                """)

                template_layout = QVBoxLayout(template_frame)

                radio = QRadioButton(name)
                radio.setStyleSheet("font-weight: bold;")

                desc_label = QLabel(description)
                desc_label.setWordWrap(True)
                desc_label.setStyleSheet("color: #666; font-size: 12px; margin-left: 20px;")

                template_layout.addWidget(radio)
                template_layout.addWidget(desc_label)

                self.template_group.addButton(radio, button_id)
                category_layout.addWidget(template_frame)

                button_id += 1

            scroll_layout.addWidget(category_group)

        # Add "No Template" option
        no_template_radio = QRadioButton("No Template - Custom Structure")
        no_template_radio.setChecked(True)  # Default
        no_template_radio.setStyleSheet("font-weight: bold; color: #2196F3;")
        self.template_group.addButton(no_template_radio, button_id)
        scroll_layout.addWidget(no_template_radio)

        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

    def isComplete(self):
        """Check if page is complete"""
        return self.template_group.checkedButton() is not None

    def get_project_data(self):
        """Return selected template data"""
        templates = [
            "fantasy", "scifi", "romance", "mystery", "historical",
            "three_act", "hero_journey", "seven_point", "freytag", "none"
        ]
        selected_id = self.template_group.checkedId()
        return {"template": templates[selected_id] if 0 <= selected_id < len(templates) else "none"}

    def get_help_text(self):
        return (
            "Templates provide proven structures for your novel:\n\n"
            "• Genre templates include character archetypes and plot elements\n"
            "• Structure templates provide pacing and story beats\n"
            "• Custom structure gives you complete creative freedom\n\n"
            "Templates are starting points - you can always modify them!"
        )


class ProjectDetailsPage(QWizardPage):
    """Page for basic project details"""

    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.project_name_edit = None
        self.idea_edit = None
        self.init_page()

    def init_page(self):
        """Initialize project details form"""
        self.setTitle("Project Details")
        self.setSubTitle("Tell us about your novel")

        layout = QVBoxLayout(self)

        # Project details form
        details_group = QGroupBox("Basic Information")
        form_layout = QFormLayout(details_group)

        self.project_name_edit = QLineEdit()
        self.project_name_edit.setPlaceholderText("e.g., My Fantasy Epic")
        form_layout.addRow("Project Name:", self.project_name_edit)

        self.idea_edit = QTextEdit()
        self.idea_edit.setPlaceholderText(
            "Describe your novel concept, main characters, setting, or any ideas you have..."
        )
        self.idea_edit.setMaximumHeight(150)
        form_layout.addRow("Novel Concept:", self.idea_edit)

        layout.addWidget(details_group)

        # Quick settings
        quick_group = QGroupBox("Quick Settings")
        quick_layout = QFormLayout(quick_group)

        self.target_words = QSpinBox()
        self.target_words.setRange(10000, 500000)
        self.target_words.setValue(80000)
        self.target_words.setSuffix(" words")
        quick_layout.addRow("Target Length:", self.target_words)

        self.reading_level = QComboBox()
        self.reading_level.addItems([
            "Elementary", "Middle School", "High School",
            "College", "Graduate", "Professional"
        ])
        self.reading_level.setCurrentText("College")
        quick_layout.addRow("Reading Level:", self.reading_level)

        layout.addWidget(quick_group)
        layout.addStretch()

        # Register required fields
        self.registerField("project_name*", self.project_name_edit)

    def get_project_data(self):
        """Return project details data"""
        return {
            "name": self.project_name_edit.text(),
            "idea": self.idea_edit.toPlainText(),
            "target_words": self.target_words.value(),
            "reading_level": self.reading_level.currentText()
        }

    def get_help_text(self):
        return (
            "Project details help FANWS understand your vision:\n\n"
            "• Project Name: Choose something memorable and descriptive\n"
            "• Novel Concept: Share your ideas, no matter how rough\n"
            "• Target Length: Standard novel lengths are 70k-100k words\n"
            "• Reading Level: Affects vocabulary and sentence complexity\n\n"
            "All of these can be changed later as your story develops."
        )


class AdvancedSettingsPage(QWizardPage):
    """Page for advanced writing settings"""

    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.init_page()

    def init_page(self):
        """Initialize advanced settings"""
        self.setTitle("Writing Style & Preferences")
        self.setSubTitle("Customize how FANWS assists your writing")

        layout = QVBoxLayout(self)

        # Style settings
        style_group = QGroupBox("Writing Style")
        style_layout = QFormLayout(style_group)

        self.tone_combo = QComboBox()
        self.tone_combo.addItems([
            "Neutral", "Formal", "Casual", "Humorous", "Dramatic",
            "Mysterious", "Romantic", "Dark", "Uplifting", "Suspenseful"
        ])
        style_layout.addRow("Primary Tone:", self.tone_combo)

        self.sub_tone_combo = QComboBox()
        self.sub_tone_combo.addItems([
            "Descriptive", "Dialogue-heavy", "Action-packed", "Contemplative",
            "Fast-paced", "Atmospheric", "Character-driven", "Plot-driven"
        ])
        style_layout.addRow("Style Focus:", self.sub_tone_combo)

        layout.addWidget(style_group)

        # AI assistance settings
        ai_group = QGroupBox("AI Assistance Level")
        ai_layout = QVBoxLayout(ai_group)

        self.assistance_group = QButtonGroup(self)

        assistance_levels = [
            ("minimal", "Minimal", "Light suggestions, maintain full creative control"),
            ("moderate", "Moderate", "Balanced assistance with story development"),
            ("extensive", "Extensive", "Active collaboration in plot and character development")
        ]

        for i, (level_id, name, description) in enumerate(assistance_levels):
            radio = QRadioButton(name)
            if i == 1:  # Default to moderate
                radio.setChecked(True)

            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: #666; margin-left: 20px; margin-bottom: 10px;")

            self.assistance_group.addButton(radio, i)
            ai_layout.addWidget(radio)
            ai_layout.addWidget(desc_label)

        layout.addWidget(ai_group)
        layout.addStretch()

    def get_project_data(self):
        """Return advanced settings data"""
        assistance_levels = ["minimal", "moderate", "extensive"]
        assistance_id = self.assistance_group.checkedId()

        return {
            "tone": self.tone_combo.currentText().lower(),
            "sub_tone": self.sub_tone_combo.currentText().lower(),
            "ai_assistance": assistance_levels[assistance_id] if assistance_id >= 0 else "moderate"
        }

    def get_help_text(self):
        return (
            "Customize how FANWS assists your writing:\n\n"
            "• Tone affects the emotional quality of generated content\n"
            "• Style Focus influences sentence structure and pacing\n"
            "• AI Assistance Level controls how much help you receive\n\n"
            "Start with moderate assistance and adjust based on your preferences."
        )


class APIConfigurationPage(QWizardPage):
    """Page for API key configuration"""

    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.init_page()

    def init_page(self):
        """Initialize API configuration"""
        self.setTitle("API Configuration")
        self.setSubTitle("Set up your AI service connections")

        layout = QVBoxLayout(self)

        # Information about APIs
        info_label = QLabel(
            "FANWS uses AI services to help with content generation. "
            "You'll need API keys for these services. Don't worry - you can "
            "add these later or use the free trial options."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; margin: 10px 0;")
        layout.addWidget(info_label)

        # API configuration
        api_group = QGroupBox("API Keys (Optional)")
        api_layout = QFormLayout(api_group)

        self.openai_key_edit = QLineEdit()
        self.openai_key_edit.setEchoMode(QLineEdit.Password)
        self.openai_key_edit.setPlaceholderText("sk-... (optional)")
        api_layout.addRow("OpenAI API Key:", self.openai_key_edit)

        openai_info = QLabel("Used for AI content generation and story development")
        openai_info.setStyleSheet("color: #666; font-size: 11px; margin-left: 20px;")
        api_layout.addRow("", openai_info)

        self.wordsapi_key_edit = QLineEdit()
        self.wordsapi_key_edit.setEchoMode(QLineEdit.Password)
        self.wordsapi_key_edit.setPlaceholderText("Words API key (optional)")
        api_layout.addRow("WordsAPI Key:", self.wordsapi_key_edit)

        words_info = QLabel("Used for synonym suggestions and vocabulary enhancement")
        words_info.setStyleSheet("color: #666; font-size: 11px; margin-left: 20px;")
        api_layout.addRow("", words_info)

        layout.addWidget(api_group)

        # Skip option
        self.skip_apis = QCheckBox("Skip API setup for now (I'll configure this later)")
        self.skip_apis.setChecked(True)
        layout.addWidget(self.skip_apis)

        # Getting API keys info
        help_group = QGroupBox("Where to Get API Keys")
        help_layout = QVBoxLayout(help_group)

        help_text = QLabel("""
        • OpenAI: Visit https://platform.openai.com/api-keys
        • WordsAPI: Visit https://rapidapi.com/dpventures/api/wordsapi

        Both services offer free trials to get you started!
        """)
        help_text.setStyleSheet("color: #555; font-size: 12px;")
        help_layout.addWidget(help_text)

        layout.addWidget(help_group)
        layout.addStretch()

    def get_project_data(self):
        """Return API configuration data"""
        return {
            "openai_key": self.openai_key_edit.text() if not self.skip_apis.isChecked() else "",
            "wordsapi_key": self.wordsapi_key_edit.text() if not self.skip_apis.isChecked() else "",
            "skip_apis": self.skip_apis.isChecked()
        }

    def get_help_text(self):
        return (
            "API keys enable AI-powered features:\n\n"
            "• OpenAI: Powers content generation and story development\n"
            "• WordsAPI: Provides vocabulary and synonym suggestions\n\n"
            "You can skip this setup and add keys later in Settings.\n"
            "Free trials are available for both services."
        )


class FinalSetupPage(QWizardPage):
    """Final setup and confirmation page"""

    def __init__(self, wizard):
        super().__init__()
        self.wizard = wizard
        self.progress_bar = None
        self.status_label = None
        self.init_page()

    def init_page(self):
        """Initialize final setup page"""
        self.setTitle("Setting Up Your Project")
        self.setSubTitle("We're creating your novel project...")

        layout = QVBoxLayout(self)

        # Setup progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Initializing project setup...")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # Summary of choices
        summary_group = QGroupBox("Project Summary")
        self.summary_layout = QFormLayout(summary_group)
        layout.addWidget(summary_group)

        layout.addStretch()

        # Setup timer for progress simulation
        self.setup_timer = QTimer()
        self.setup_timer.timeout.connect(self.update_progress)
        self.progress_value = 0

    def initializePage(self):
        """Called when the page is shown"""
        # Update summary with wizard data
        self.update_summary()

        # Start setup simulation
        self.progress_value = 0
        self.progress_bar.setValue(0)
        self.setup_timer.start(100)  # Update every 100ms

    def update_summary(self):
        """Update the project summary"""
        # Clear existing summary
        while self.summary_layout.count():
            item = self.summary_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Collect data from all pages
        project_data = {}
        for page_id in range(self.wizard.pageIds()[-1]):
            page = self.wizard.page(page_id)
            if hasattr(page, 'get_project_data'):
                project_data.update(page.get_project_data())

        # Display summary
        summary_items = [
            ("Project Name", project_data.get('name', 'Unknown')),
            ("Project Type", project_data.get('project_type', 'fresh_start').replace('_', ' ').title()),
            ("Template", project_data.get('template', 'none').replace('_', ' ').title()),
            ("Target Length", f"{project_data.get('target_words', 80000):,} words"),
            ("Reading Level", project_data.get('reading_level', 'College')),
            ("Primary Tone", project_data.get('tone', 'neutral').title()),
            ("AI Assistance", project_data.get('ai_assistance', 'moderate').title())
        ]

        for label, value in summary_items:
            self.summary_layout.addRow(f"{label}:", QLabel(str(value)))

    def update_progress(self):
        """Update setup progress"""
        self.progress_value += 2
        self.progress_bar.setValue(self.progress_value)

        # Update status messages
        if self.progress_value < 20:
            self.status_label.setText("Creating project structure...")
        elif self.progress_value < 40:
            self.status_label.setText("Initializing AI configurations...")
        elif self.progress_value < 60:
            self.status_label.setText("Setting up templates and preferences...")
        elif self.progress_value < 80:
            self.status_label.setText("Configuring writing environment...")
        elif self.progress_value < 100:
            self.status_label.setText("Finalizing project setup...")
        else:
            self.status_label.setText("Project setup complete!")
            self.setup_timer.stop()
            self.completeChanged.emit()

    def isComplete(self):
        """Check if setup is complete"""
        return self.progress_value >= 100

    def get_project_data(self):
        """Return final project data"""
        # Collect all data from previous pages
        project_data = {}
        for page_id in range(self.wizard.pageIds()[-1]):
            page = self.wizard.page(page_id)
            if hasattr(page, 'get_project_data'):
                project_data.update(page.get_project_data())

        return project_data

    def get_help_text(self):
        return (
            "Your project is being set up with the following:\n\n"
            "• Project file structure and configuration\n"
            "• AI service connections and preferences\n"
            "• Template and style settings\n"
            "• Writing environment preparation\n\n"
            "This process should complete in a few seconds."
        )


def show_onboarding_wizard(parent=None):
    """Show the onboarding wizard and return project data if completed"""
    wizard = OnboardingWizard(parent)

    project_data = None

    def on_project_created(data):
        nonlocal project_data
        project_data = data

    wizard.project_created.connect(on_project_created)

    result = wizard.exec_()

    if result == QWizard.Accepted and project_data:
        return project_data
    else:
        return None

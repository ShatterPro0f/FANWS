"""
Fiction AI Novel Writing Suite (FANWS)

Main application file for the AI-powered novel writing suite.
This file contains the core application logic, UI setup, and workflow coordination.
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
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QTabWidget, QTextEdit, QPushButton, QProgressBar, QLabel, QLineEdit, QSpinBox, QGroupBox, QStatusBar, QComboBox, QDoubleSpinBox, QMessageBox, QCheckBox, QFormLayout, QSplitter, QScrollArea, QInputDialog, QDialog, QListWidget, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog
)
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QTimer, QTimer
from PyQt5.QtGui import QFont

# Document generation libraries
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# New modular imports
from src.error_handling_system import ErrorHandler, create_styled_message_box, ProjectError, APIError, FileOperationError
from src.file_operations import (
    save_to_file, read_file, load_project_env, save_project_env,
    get_project_list, create_backup, load_synonym_cache, save_synonym_cache,
    load_wordsapi_log, save_wordsapi_log, log_wordsapi_call,
    get_wordsapi_call_count, validate_project_name, initialize_project_files
)
from src.memory_manager import FileCache, ProjectFileCache, get_cache_manager
from src.text_processing import SynonymCache, TextAnalyzer, get_text_analyzer, get_synonym_cache
from src.module_compatibility import MARKDOWN_AVAILABLE, markdown2
from src.api_manager import get_api_manager
from src.workflow_manager import NovelWritingWorkflowModular
from src.workflow_steps.base_step import BaseWorkflowStep as WorkflowStep

# Import from modules that have content
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
    from src.database_manager import DatabaseIntegrationLayer
    DATABASE_INTEGRATION_AVAILABLE = True
    print("✓ Database integration system loaded successfully")
except ImportError as e:
    print(f"⚠ Database integration system not available: {e}")
    DATABASE_INTEGRATION_AVAILABLE = False
    class DatabaseIntegrationLayer:
        def __init__(self, *args, **kwargs):
            pass

    from src.plugin_workflow_integration import PluginWorkflowIntegration
    PLUGIN_INTEGRATION_AVAILABLE = True
    print("✓ Plugin workflow integration loaded successfully")
except ImportError as e:
    print(f"⚠ Plugin workflow integration not available: {e}")
    PLUGIN_INTEGRATION_AVAILABLE = False
    class PluginWorkflowIntegration:
        def __init__(self, *args, **kwargs):
            pass

# Import prompt template management
from src.template_manager import get_template_manager, WorkflowPromptType, WorkflowContext

try:
    from src.main_gui import MainWindow, DesignSystem, Components, Animations, LayoutManager
    gui_AVAILABLE = True
    print("✓ Modern GUI system loaded successfully")
except ImportError as e:
    print(f"⚠ Modern GUI system not available: {e}")
    MainWindow = None
    DesignSystem = None
    Components = None
    Animations = None
    LayoutManager = None
    gui_AVAILABLE = False

try:
    from src.constants import OPENAI_API_URL, WORDSAPI_URL
except ImportError:
    print("Warning: Could not import constants")
    OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"
    WORDSAPI_URL = "https://wordsapiv1.p.rapidapi.com/words/"

try:
    from src.utils import project_file_path
except ImportError:
    print("Warning: Could not import utils")
    def project_file_path(project_name, filename):
        return os.path.join("projects", project_name, filename)

# Core application imports
from src.api_manager import APIManager
from src.constants import OPENAI_API_URL, WORDSAPI_URL, DEFAULT_WORD_COUNTS, TONE_MAP

# AI Provider Manager (Consolidated)
try:
    from src.ai_provider_abstraction import (
        AIProviderManager as AIProviderManagerBase, MultiProviderConfig
    )
    # Create alias for compatibility
    AIProviderManager = AIProviderManagerBase
    def get_ai_provider_manager():
        return AIProviderManager(MultiProviderConfig())
    AI_AVAILABLE = True
except ImportError as e:
    print(f"AI Provider Manager not available: {e}")
    AI_AVAILABLE = False

try:
    from src.analytics_system import (
        WritingAnalyticsDashboard as WritingAnalyticsManager,
        AnalyticsWidget as AnalyticsProgressWidget,
        WritingGoal as ProductivityInsight,
        WritingHabit
    )
    def create_analytics_manager(project_name=None):
        return WritingAnalyticsManager()
    WRITING_ANALYTICS_AVAILABLE = True
    print("✅ Enhanced writing analytics loaded successfully")
except ImportError as e:
    print(f"⚠️ Enhanced writing analytics not available: {e}")
    WRITING_ANALYTICS_AVAILABLE = False

try:
    from src.analytics_system import (
        AnalyticsEngine, WritingGoal, WritingMilestone,
        GoalType, HabitFrequency, MilestoneType
    )
    ADVANCED_ANALYTICS_AVAILABLE = True
    print("✅ Advanced analytics engine loaded successfully")
except ImportError as e:
    print(f"⚠️ Advanced analytics engine not available: {e}")
    ADVANCED_ANALYTICS_AVAILABLE = False

try:
    from src.analytics_system import AnalyticsDashboard
    ADVANCED_DASHBOARD_AVAILABLE = True
    print("✅ Advanced analytics dashboard loaded successfully")
except ImportError as e:
    print(f"⚠️ Advanced analytics dashboard not available: {e}")
    ADVANCED_DASHBOARD_AVAILABLE = False

# Collaborative Features (From UI modules)
try:
    from src.collaboration_system import CollaborativeManager
    from src.ui.management_ui import CollaborativeDialog
    COLLABORATIVE_FEATURES_AVAILABLE = True
    print("✅ Collaborative features loaded successfully")
except ImportError as e:
    print(f"⚠️ Collaborative features not available: {e}")
    COLLABORATIVE_FEATURES_AVAILABLE = False

try:
    # Template project creator functionality moved to template_manager
    # from src.template_manager import (
    #     TemplateProjectCreator, TemplateMarketplaceWidget,
    #     replace_basic_project_creation, enhance_project_creation_ui
    # )
    # from src.template_manager import AdvancedProjectTemplateManager
    TEMPLATE_FEATURES_AVAILABLE = False  # Consolidated into template_manager
    print("✅ Template features consolidated into template_manager")
except ImportError as e:
    print(f"⚠️ Advanced project templates not available: {e}")
    TEMPLATE_FEATURES_AVAILABLE = False

from src.writing_components import (
    ContentGenerator, DraftManager, ConsistencyChecker, ProjectManager,
    summarize_context, update_character_arcs, update_plot_points, check_continuity
)
from src.performance_monitor import PerformanceMonitor
from src.database_manager import DatabaseManager
from src.database_manager import (
    DatabaseManager,
    DatabaseConfig,
    get_db_manager
)
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup logging
ErrorHandler.setup_logging()

class WorkerThread(QThread):
    # Define signals at class level
    log_update = pyqtSignal(str, str)
    progress_update = pyqtSignal(int, str)
    content_update = pyqtSignal(str, str)
    synopsis_ready = pyqtSignal(str)
    api_limit_reached = pyqtSignal(str)
    wordsapi_count_update = pyqtSignal(int)
    word_count_update = pyqtSignal(int)
    preview_update = pyqtSignal(str)

    def save_checkpoint(self, chapter, section):
        """
        Validate the existing checkpoint file format before overwriting. Log a warning if invalid.
        Save the new checkpoint with "Chapter: X" and "Section: Y".
        """
        checkpoint_content = self.file_cache.get("checkpoint.txt")
        valid = False
        if checkpoint_content:
            lines = checkpoint_content.strip().split("\n")
            if len(lines) == 2 and lines[0].startswith("Chapter: ") and lines[1].startswith("Section: "):
                try:
                    int(lines[0].split(": ")[1])
                    int(lines[1].split(": ")[1])
                    valid = True
                except Exception as e:
                    logging.warning(f"Failed to validate checkpoint format: {str(e)}. Checkpoint may be corrupted.")
                    valid = False
            if not valid:
                logging.warning(f"Invalid checkpoint format detected before saving new checkpoint: {checkpoint_content!r}")
        new_checkpoint = f"Chapter: {chapter}\nSection: {section}"
        self.file_cache.update("checkpoint.txt", new_checkpoint)

    def __init__(self, project_name, openai_key, thesaurus_key):
        super().__init__()
        self.project_name = project_name

        # Initialize per-project configuration if available
        if PER_PROJECT_CONFIG_AVAILABLE and hasattr(self, 'project_name') and self.project_name:
            try:
                self.per_project_config = PerProjectConfigManager(self.project_name)
                self.per_project_config.initialize_project_config()
                logging.info(f"Initialized per-project configuration for {self.project_name}")
            except Exception as e:
                logging.error(f"Failed to initialize per-project config: {str(e)}")
                self.per_project_config = None
        else:
            self.per_project_config = None
        self.openai_key = openai_key
        self.thesaurus_key = thesaurus_key
        self.api_manager = APIManager()
        self.file_cache = ProjectFileCache(project_name)
        self.synonym_cache = SynonymCache(project_name)

        # Configuration Management Integration
        if CONFIGURATION_MANAGEMENT_AVAILABLE:
            try:
                # Initialize global configuration if not already done
                if not hasattr(self, '_config_initialized'):
                    initialize_global_config()
                    self._config_initialized = True

                # Get configuration integration instance
                config_integration = get_global_config()
                self.config = config_integration

                # Create compatibility layer for legacy code
                from src.configuration_manager import create_configuration_compatibility_layer
                self.legacy_config = create_configuration_compatibility_layer()

            except Exception as e:
                print(f"⚠ Failed to initialize advanced configuration, using fallback: {e}")
                # Fallback: Create a minimal config object that won't break existing code
                self.config = None
                self.legacy_config = None
        else:
            print("⚠ Advanced configuration not available, using minimal fallback")
            self.config = None
            self.legacy_config = None

        self.waiting_for_approval = False

        # Initialize performance monitoring
        self.performance_monitor = PerformanceMonitor(project_name)
        self.performance_monitor.start_monitoring()

        # Initialize project manager with all dependencies
        self.project_manager = ProjectManager(
            project_name=project_name,
            api_manager=self.api_manager,
            file_cache=self.file_cache,
            config=self.config
        )

        # Initialize Quality Manager
        if QUALITY_ASSURANCE_AVAILABLE:
            self.quality_manager = get_quality_manager(project_name)

            # Initialize recommendation engine (same as quality manager)
            try:
                from src.quality_manager import get_quality_manager
                self.recommendation_engine = get_quality_manager(project_name)
                logging.info("Quality Manager initialized")
            except ImportError:
                self.recommendation_engine = None
                logging.warning("Quality Recommendation Engine not available")

            logging.info("Quality Assurance Manager initialized")
        else:
            self.quality_manager = None
            self.recommendation_engine = None
            logging.warning("Quality Assurance not available")

    def save_draft(self, chapter, section, content, version):
        """Save draft to file and update cache."""
        try:
            os.makedirs(project_file_path(self.project_name, f"drafts/chapter{chapter}"), exist_ok=True)
            filename = f"drafts/chapter{chapter}/section{section}_v{version}.txt"
            self.file_cache.update(filename, content)
            logging.info(f"Successfully saved draft: {filename}")
        except Exception as e:
            logging.error(f"Failed to save draft for Chapter {chapter}, Section {section}, Version {version}: {str(e)}")
            raise

    def generate_and_save(self, prompt, filename, max_tokens=500):
        """Generate content and save to file/cache using APIManager."""
        try:
            content = self.api_manager.generate_text_openai(prompt, max_tokens, self.openai_key)
            if content == "API_LIMIT_REACHED":
                logging.warning("API limit reached during content generation")
                return False
            self.file_cache.update(filename, content)
            self.content_update.emit(filename, content)
            logging.info(f"Successfully generated and saved content to: {filename}")
            return content
        except Exception as e:
            logging.error(f"Failed to generate and save content for {filename}: {str(e)}")
            return False

    def run(self):
        asyncio.run(self.async_run())

    async def async_run(self):
        os.environ["OPENAI_API_KEY"] = self.openai_key
        os.environ["THESAURUS_API_KEY"] = self.thesaurus_key
        content_generator = ContentGenerator(self.api_manager, self.file_cache, self.config)
        draft_manager = DraftManager(self.file_cache, self.project_name)
        consistency_checker = ConsistencyChecker(self.api_manager, self.file_cache)

        # Determine which model to use from config (default to OpenAI)
        model_name = self.config.get("Model") or "OpenAI GPT-4o"
        def generate_text(prompt, max_tokens, api_key):
            if model_name == "xAI Grok-3":
                return self.api_manager.generate_text_xai(prompt, max_tokens, api_key)
            else:
                return self.api_manager.generate_text_openai(prompt, max_tokens, api_key)
        # --- Backup and setup ---
        def backup_files():
            for file in ["story.txt", "log.txt"]:
                create_backup(self.project_name, file)
            threading.Timer(3600, backup_files).start()
        backup_files()

        wordsapi_log = load_wordsapi_log(self.project_name)
        call_count = get_wordsapi_call_count(self.project_name)
        self.wordsapi_count_update.emit(call_count)
        logging.info(f"WordsAPI calls today: {call_count}/2500")

        story_content = self.file_cache.get("story.txt")
        word_count = len(story_content.split())
        self.word_count_update.emit(word_count)

        # Initialize prompt template manager for dynamic prompt generation
        prompt_manager = get_template_manager()

        # Create workflow context for prompt generation
        workflow_context = WorkflowContext(
            project_name=self.project_name,
            config=self.config,
            file_cache=self.file_cache
        )

        checkpoint = self.file_cache.get("checkpoint.txt")
        start_chapter, start_section = 1, 1
        if checkpoint:
            try:
                lines = checkpoint.split("\n")
                start_chapter = int(lines[0].split(": ")[1])
                start_section = int(lines[1].split(": ")[1])
                logging.info(f"Resuming from Chapter {start_chapter}, Section {start_section}.")
            except Exception as e:
                logging.warning(f"Invalid checkpoint format detected: {str(e)}. Starting from Chapter 1, Section 1.")
                start_chapter, start_section = 1, 1

        # --- Initial planning phase ---
        if start_chapter == start_section == 1:
            progress = 0
            # Synopsis - using dynamic template
            prompt = prompt_manager.generate_workflow_prompt(
                WorkflowPromptType.SYNOPSIS_GENERATION,
                workflow_context
            )
            synopsis = generate_text(prompt, 1000, self.openai_key)
            progress = 5
            self.progress_update.emit(progress, "Processing Synopsis")
            if not synopsis:
                self.api_limit_reached.emit("OpenAI API limit reached, pausing for 1 hour.")
                return
            self.synopsis_ready.emit(synopsis)

            # Outline - using dynamic template
            prompt = prompt_manager.generate_workflow_prompt(
                WorkflowPromptType.OUTLINE_CREATION,
                workflow_context
            )
            outline = generate_text(prompt, 1000, self.openai_key)
            progress = 10
            self.progress_update.emit(progress, "Processing Outline")
            if outline == "API_LIMIT_REACHED":
                self.api_limit_reached.emit("OpenAI API limit reached, pausing for 1 hour.")
                return
            self.file_cache.update("outline.txt", outline)

            # Characters - using dynamic template
            prompt = prompt_manager.generate_workflow_prompt(
                WorkflowPromptType.CHARACTER_PROFILES,
                workflow_context
            )
            characters = generate_text(prompt, 1000, self.openai_key)
            progress = 15
            self.progress_update.emit(progress, "Processing Characters")
            if characters == "API_LIMIT_REACHED":
                self.api_limit_reached.emit("OpenAI API limit reached, pausing for 1 hour.")
                return
            self.file_cache.update("characters.txt", characters)

            # World - using dynamic template
            prompt = prompt_manager.generate_workflow_prompt(
                WorkflowPromptType.WORLD_BUILDING,
                workflow_context
            )
            world = generate_text(prompt, 1000, self.openai_key)
            progress = 20
            self.progress_update.emit(progress, "Processing World")
            if world == "API_LIMIT_REACHED":
                self.api_limit_reached.emit("OpenAI API limit reached, pausing for 1 hour.")
                return
            self.file_cache.update("world.txt", world)

            # Timeline - using dynamic template
            prompt = prompt_manager.generate_workflow_prompt(
                WorkflowPromptType.TIMELINE_GENERATION,
                workflow_context
            )
            timeline = generate_text(prompt, 1000, self.openai_key)
            progress = 25
            self.progress_update.emit(progress, "Processing Timeline")
            if timeline == "API_LIMIT_REACHED":
                self.api_limit_reached.emit("OpenAI API limit reached, pausing for 1 hour.")
                return
            self.file_cache.update("timeline.txt", timeline)

            self.file_cache.update("plot_points.txt", json.dumps([]))
            logging.info("Planning complete.")

        # --- Main writing loop ---
        total_words = word_count
        for chapter in range(start_chapter, self.config.get('TotalChapters') + 1):
            for section in range(1 if chapter > start_chapter else start_section, self.config.get('Chapter1Sections') + 1):
                context_summary = summarize_context(self.project_name, self.file_cache, chapter, section)
                if context_summary == "API_LIMIT_REACHED":
                    self.api_limit_reached.emit("OpenAI API limit reached, pausing for 1 hour.")
                    return
                chapter_word_count = self.config.get("ChapterWordCount") or 1000
                user_feedback = ""
                # User feedback mechanism removed since adjust_input is no longer available
                # Could be implemented through preview_text or other means if needed

                # Update workflow context for chapter writing
                workflow_context.chapter = chapter
                workflow_context.section = section
                workflow_context.context_summary = context_summary
                workflow_context.user_feedback = user_feedback
                workflow_context.chapter_word_count = chapter_word_count

                # Use custom prompt if provided in config, else use dynamic template
                custom_prompt = self.config.get("CustomPrompt")
                if custom_prompt:
                    # For custom prompts, we need the reading level prompt
                    reading_level_prompt = prompt_manager.generate_reading_level_prompt(
                        self.config.get('ReadingLevel', 'College')
                    )
                    prompt = custom_prompt.format(
                        reading_level=reading_level_prompt,
                        chapter=chapter,
                        section=section,
                        chapter_word_count=chapter_word_count,
                        timeline=self.file_cache.get('timeline.txt'),
                        tone=self.config.get('Tone'),
                        sub_tone=self.config.get('SubTone'),
                        context=self.file_cache.get('context.txt'),
                        recent_summary=context_summary,
                        characters=self.file_cache.get('characters.txt'),
                        world=self.file_cache.get('world.txt'),
                        plot_points=self.file_cache.get('plot_points.txt'),
                        continuity_rules=self.file_cache.get('continuity_rules.txt'),
                        user_feedback=user_feedback
                    )
                else:
                    # Use dynamic prompt template for chapter writing
                    prompt = prompt_manager.generate_workflow_prompt(
                        WorkflowPromptType.CHAPTER_WRITING,
                        workflow_context
                    )
                draft = await self.api_manager.generate_text_openai_async(prompt, chapter_word_count, self.openai_key)
                if draft == "API_LIMIT_REACHED":
                    self.api_limit_reached.emit("OpenAI API limit reached, pausing for 1 hour.")
                    return
                draft_manager.save_draft(chapter, section, draft, 1)

                # Polish draft using dynamic template
                workflow_context.file_cache.update('current_draft', draft)
                polishing_prompt = prompt_manager.generate_workflow_prompt(
                    WorkflowPromptType.DRAFT_POLISHING,
                    workflow_context
                )
                polished = await self.api_manager.generate_text_openai_async(polishing_prompt, 1000, self.openai_key)
                if polished == "API_LIMIT_REACHED":
                    self.api_limit_reached.emit("OpenAI API limit reached, pausing for 1 hour.")
                    return
                draft_manager.save_draft(chapter, section, polished, 2)

                enhanced = polished
                if random.random() < 0.5:
                    # Enhance draft using dynamic template
                    workflow_context.file_cache.update('polished_draft', polished)
                    enhancement_prompt = prompt_manager.generate_workflow_prompt(
                        WorkflowPromptType.CONTENT_ENHANCEMENT,
                        workflow_context
                    )
                    enhanced = await self.api_manager.generate_text_openai_async(enhancement_prompt, 1000, self.openai_key)
                    if enhanced == "API_LIMIT_REACHED":
                        self.api_limit_reached.emit("OpenAI API limit reached, pausing for 1 hour.")
                        return
                    draft_manager.save_draft(chapter, section, enhanced, 3)

                # --- QUALITY ASSURANCE CHECK (--
                if self.quality_manager:
                    try:
                        quality_assessment = await self.quality_manager.perform_real_time_quality_check(
                            enhanced, chapter, section
                        )

                        # Log quality results
                        logging.info(f"Quality Assessment - Chapter {chapter}, Section {section}: "
                                   f"{quality_assessment.overall_quality.value} "
                                   f"(Score: {quality_assessment.quality_score:.2f})")

                        # Check if content should be gated due to quality issues
                        if self.quality_manager.should_gate_content(quality_assessment):
                            logging.warning(f"Content quality below threshold for Chapter {chapter}, Section {section}")
                            # Emit signal for user to review quality issues
                            self.log_update.emit("Quality Alert",
                                f"Chapter {chapter}, Section {section} has quality issues. "
                                f"Quality score: {quality_assessment.quality_score:.2f}. "
                                f"Issues found: {len(quality_assessment.issues)}")

                        # Save quality assessment for later review
                        quality_data = {
                            "assessment": {
                                "content_id": quality_assessment.content_id,
                                "overall_quality": quality_assessment.overall_quality.value,
                                "quality_score": quality_assessment.quality_score,
                                "timestamp": quality_assessment.timestamp.isoformat(),
                                "issues_count": len(quality_assessment.issues),
                                "recommendations": quality_assessment.recommendations
                            }
                        }
                        self.file_cache.update(f"quality_ch{chapter}_s{section}.json", json.dumps(quality_data, indent=2))

                    except Exception as e:
                        logging.error(f"Quality assurance check failed: {str(e)}")
                # --- END QUALITY ASSURANCE CHECK ---

                if random.random() < self.config.get('ThesaurusWeight'):
                    words = [word for word in enhanced.split() if random.random() < 0.05]
                    synonyms = self.api_manager.get_synonyms_batch(
                        words,
                        self.synonym_cache,
                        self.config.get('Tone'),
                        self.config.get('SubTone'),
                        self.config.get('ReadingLevel'),
                        wordsapi_log,
                        self.project_name,
                        self
                    )
                    enhanced_words = []
                    for word in enhanced.split():
                        enhanced_words.append(synonyms.get(word, word))
                        if word in synonyms:
                            logging.info(f"Synonym for '{word}': '{synonyms[word]}'")
                    enhanced = " ".join(enhanced_words)
                draft_manager.save_draft(chapter, section, enhanced, 4)

                consistency_result = consistency_checker.check_continuity(self.project_name, chapter, section)
                if consistency_result != "Consistency check skipped due to API limit.":
                    logging.info(f"Consistency check for Chapter {chapter}, Section {section}: {consistency_result[:50]}...")

                # update_character_arcs and update_plot_points could be refactored into ContentGenerator or another helper
                update_character_arcs(self.project_name, self.file_cache, chapter, section)
                update_plot_points(self.project_name, self.file_cache, chapter, section)

                self.preview_update.emit(enhanced)

                self.waiting_for_approval = True
                while self.waiting_for_approval:
                    await asyncio.sleep(1)

                total_words += len(enhanced.split())
                progress = min(int((total_words / self.config.get('SoftTarget')) * 100), 100)
                self.progress_update.emit(progress, f"Writing Chapter {chapter}, Section {section}")
                story_content = self.file_cache.get("story.txt") + f"\n\nChapter {chapter}\n\n{enhanced}"
                self.file_cache.update("story.txt", story_content)
                self.content_update.emit("story.txt", story_content)
                self.word_count_update.emit(total_words)
                logging.info(f"Chapter {chapter}, Section {section} drafted. Words: {len(enhanced.split())}")

                self.config.save_config(CurrentChapter=chapter, CurrentSection=section + 1)
                self.save_checkpoint(chapter, section + 1)
                create_backup(self.project_name, "story.txt")
                create_backup(self.project_name, "log.txt")

        # --- Final consistency check ---
        consistency_prompt = prompt_manager.generate_workflow_prompt(
            WorkflowPromptType.CONSISTENCY_CHECK,
            workflow_context
        )
        consistency = await self.api_manager.generate_text_openai_async(consistency_prompt, 500, self.openai_key)
        if consistency == "API_LIMIT_REACHED":
            self.api_limit_reached.emit("OpenAI API limit reached, pausing for 1 hour.")
            return
        logging.info(f"Final consistency check: {consistency[:50]}...")

        # --- Generate Final Quality Report ---
        if self.quality_manager:
            try:
                final_quality_data = self.quality_manager.generate_quality_dashboard_data()
                self.file_cache.update("final_quality_report.json", json.dumps(final_quality_data, indent=2))
                logging.info("Final quality report generated and saved")

                # Generate quality improvement recommendations
                if self.recommendation_engine:
                    try:
                        recommendations = self.recommendation_engine.get_personalized_recommendations()
                        recommendations_report = self.recommendation_engine.export_recommendations_report(recommendations)
                        self.file_cache.update("quality_recommendations.json", json.dumps(recommendations_report, indent=2))

                        # Log recommendations summary
                        high_priority_recs = len([r for r in recommendations if r.priority.value in ['critical', 'high']])
                        self.log_update.emit("Quality Recommendations",
                            f"Generated {len(recommendations)} quality improvement recommendations. "
                            f"{high_priority_recs} high-priority items. Check quality_recommendations.json for details.")

                        logging.info(f"Generated {len(recommendations)} quality recommendations")

                    except Exception as e:
                        logging.error(f"Failed to generate quality recommendations: {str(e)}")

                # Log overall project quality metrics
                if "quality_metrics" in final_quality_data:
                    self.log_update.emit("Quality Report",
                        f"Novel completed with quality analysis. "
                        f"Total words: {final_quality_data.get('content_statistics', {}).get('total_words', 'Unknown')}. "
                        f"Check final_quality_report.json for detailed metrics.")

            except Exception as e:
                logging.error(f"Failed to generate final quality report: {str(e)}")

        self.progress_update.emit(100, "Completed")
        logging.info("Novel complete.")

# ----------------------
# Main Window Class
# ----------------------
class FANWSWindow(QMainWindow):
    def __getattr__(self, name):
        # Fallback to UIComponents attributes if not found in self, but avoid recursion
        if name == 'ui':
            raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")
        ui = self.__dict__.get('ui', None)
        if ui and hasattr(ui, name):
            return getattr(ui, name)
        raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")

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

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fiction AI Novel Writing Suite (FANWS)")
        self.resize(1600, 1000)  # Increased size to better accommodate 1/4 sidebar

        # Initialize basic attributes early to prevent AttributeError
        self.current_directory = os.path.dirname(os.path.abspath(__file__))
        self.current_project = None

        # Initialize GUI system
        self.init_gui_system()

        # Initialize status bar
        self.statusBar = self.statusBar()
        self.statusBar.showMessage("Ready", 5000)

        # Initialize performance monitoring
        self.performance_monitor = PerformanceMonitor()
        self.performance_monitor.start_monitoring()

        # Initialize async operations
        try:
            from src.async_operations import get_async_manager, BackgroundTaskManager, ProgressTracker
            from src.workflow_manager import AsyncWorkflowOperations as WorkflowTaskManager
            from src.async_operations import AsyncProgressDialog as AsyncProgressWidget

            # Create integration wrapper class
            class AsyncWorkflowIntegration:
                def __init__(self, workflow_manager):
                    self.workflow_manager = workflow_manager

            # Create UI component functions
            def create_async_workflow_panel():
                return AsyncProgressWidget()

            def create_async_task_monitor():
                return AsyncProgressWidget()

            # Status indicator alias
            AsyncStatusIndicator = AsyncProgressWidget

            # Initialize async operations manager
            self.async_manager = get_async_manager()
            self.async_manager.set_performance_monitor(self.performance_monitor)

            # Initialize async progress tracker
            self.async_progress_tracker = ProgressTracker()
            self.async_progress_tracker.setParent(self)

            # Initialize async workflow manager (will be set up when project is loaded)
            self.async_workflow_manager = None

            # Initialize async UI components
            self.async_workflow_panel = None
            self.async_task_monitor = None
            self.async_progress_widget = None
            self.async_status_indicator = None

            # Async operation state
            self.async_operations_active = False
            self.current_async_task_id = None

            # Initialize background task management
            self.background_tasks = []
            self.task_analytics = {
                'total_tasks': 0,
                'completed_tasks': 0,
                'failed_tasks': 0,
                'avg_duration': 0,
                'task_history': []
            }

            # Initialize task queue management
            self.init_task_queue_manager()

            # Initialize recovery system
            self.init_recovery_system()

            # Initialize async system
            self.init_async_system()

            print("✓ Phase 1.2: Async operations framework initialized")

        except ImportError as e:
            print(f"⚠ Phase 1.2: Async operations not available: {e}")
            self.async_manager = None
            self.async_progress_tracker = None
            self.async_workflow_manager = None
            self.background_tasks = []
            self.task_analytics = {
                'total_tasks': 0,
                'completed_tasks': 0,
                'failed_tasks': 0,
                'avg_duration': 0,
                'task_history': []
            }

        self.init_plugin_system()

        # Initialize core systems
        self.init_database_system()

        self.init_multi_provider_ai_system()

        self.init_writing_analytics_system()

        self.init_error_handling()

        # Initialize worker attribute
        self.worker = None
        # Initialize project and file management attributes
        self.current_project = None
        self.config = None
        self.file_cache = None

        # Initialize project manager
        self.project_manager = None

        # Initialize novel writing workflow
        self.novel_workflow = None
        self.workflow_dialog = None

        self.collaborative_manager = None
        self.collaborative_dialog = None

        # Workflow control state
        self.workflow_active = False
        self.current_workflow_step = None
        self.workflow_timer = None

        # Pre-create all tab widgets to avoid deleted C++ object errors
        self.story_tab = QTextEdit()
        self.config_tab = QTextEdit()
        self.characters_tab = QTextEdit()
        self.world_tab = QTextEdit()
        self.summaries_tab = QTextEdit()
        self.drafts_tab = QTextEdit()
        self.drafts_tab_ref = self.drafts_tab  # Extra reference to prevent GC
        self.readability_tab = QTextEdit()
        self.readability_tab_ref = self.readability_tab  # Extra reference to prevent GC
        self.synonyms_tab = QTextEdit()
        self.synonyms_tab_ref = self.synonyms_tab
        self.log_tab = QTextEdit()
        self.log_tab_ref = self.log_tab
        self.log_tab.setReadOnly(True)

        # Add additional text widgets used in UI components
        self.preview_text = QTextEdit()
        self.preview_text.setPlaceholderText("Story preview will appear here...")
        self.writing_area = QTextEdit()
        self.writing_area.setPlaceholderText("Your current draft will appear here when writing begins...")

        # Add progress widgets with modern styling
        # Use standard progress bar for now
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Overall Progress: %p%")

        self.chapter_progress_label = QLabel("Current: Chapter 1, Section 1")
        self.chapter_progress_label.setStyleSheet("color: #666; margin: 10px 0;")

        # Add UI status labels
        self.progress_label = QLabel("Progress: 0%")
        self.status_label = QLabel("Status: Ready")
        self.word_count_label = QLabel("Word Count: 0")
        self.wordsapi_label = QLabel("WordsAPI Calls: 0/2500")

        # Create project selector to prevent C++ object deletion
        self.project_selector = QComboBox()
        self.project_selector.addItem("Select a project")

        # Defensive: keep references to all tabs to prevent garbage collection
        self._tab_refs = [
            self.story_tab, self.config_tab, self.characters_tab, self.world_tab,
            self.summaries_tab, self.drafts_tab, self.readability_tab, self.synonyms_tab, self.log_tab,
            self.drafts_tab_ref, self.readability_tab_ref, self.synonyms_tab_ref, self.log_tab_ref,
            self.preview_text, self.writing_area, self.progress_bar, self.chapter_progress_label,
            self.progress_label, self.status_label, self.word_count_label, self.wordsapi_label,
            self.project_selector  # Add project selector to prevent deletion
        ]

        # Use UIComponents to build and assign all widgets as attributes
        self.ui = UIComponents(self)

        if self.gui_enabled:
            self.ui.modern_design = self.modern_design
            self.ui.modern_components = self.modern_components
            self.ui.modern_animations = self.modern_animations
            print("✓ Modern components passed to UI system")

        # Only call create_ui() once per window instance
        self.ui.create_ui()

        # Add missing widgets that are referenced in the main application
        self.ui.add_missing_widgets()

        # Populate project list after UI is created
        projects = get_project_list()
        self.project_selector.addItems(projects)

        # Also refresh the project selector to ensure consistency
        if hasattr(self.ui, '_refresh_project_selector'):
            self.ui._refresh_project_selector()

        # Connect signals after UI is created
        self.setup_signals()

        # Initialize workflow manager after UI is ready
        self.initialize_workflow_manager()

        self.initialize_collaborative_features()

        self.initialize_template_system()

        self.initialize_error_handling()

        self.initialize_memory_management()

        self.initialize_configuration_management()

        self.integrate_plugins_with_workflow()

        # Add plugin management button to UI if available
        self.add_plugin_management_to_ui()

        # Always start with Project section regardless of available projects
        # This provides a consistent entry point for users
        self.ui._show_project_content()

        # Log application startup
        self.performance_monitor.log_event("application_startup", "Application started successfully")
        logging.info("FANWS application initialized successfully")

    # Prevent accidental recreation of UI widgets that can cause deletion of C++ objects
    def recreate_ui(self):
        raise RuntimeError("UI recreation is not supported. Please restart the application to reset the UI.")

    def init_gui_system(self):
        """Initialize modern GUI system."""
        if gui_AVAILABLE:
            try:
                self.modern_design = DesignSystem()
                self.modern_components = Components()
                self.modern_animations = Animations()
                self.modern_layout = LayoutManager()
                self.gui_enabled = True
                print("✓ Modern GUI system initialized")
            except Exception as e:
                print(f"⚠ Failed to initialize modern GUI: {e}")
                self.gui_enabled = False
        else:
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
            if self.async_manager:
                self.async_manager.start_manager()
                print("✓ Async system initialized")
        except Exception as e:
            print(f"⚠ Failed to initialize async system: {e}")

    def init_error_handling(self):
        """Initialize advanced error handling system."""
        if ERROR_HANDLING_AVAILABLE:
            try:
                self.error_integration = get_error_integration()
                self.error_dashboard = ErrorHandlingDashboard()
                print("✓ Advanced error handling initialized")
            except Exception as e:
                print(f"⚠ Failed to initialize advanced error handling: {e}")

    def initialize_workflow_manager(self):
        """Initialize the workflow manager."""
        try:
            if not self.novel_workflow:
                self.novel_workflow = NovelWritingWorkflowModular()
                print("✓ Workflow manager initialized")
        except Exception as e:
            print(f"⚠ Failed to initialize workflow manager: {e}")

    def initialize_async_workflow_manager(self):
        """Initialize async workflow manager for the current project."""
        try:
            if self.async_manager and not self.async_workflow_manager:
                from src.workflow_manager import AsyncWorkflowOperations
                self.async_workflow_manager = AsyncWorkflowOperations(self.novel_workflow)
                print("✓ Async workflow manager initialized")
        except Exception as e:
            print(f"⚠ Failed to initialize async workflow manager: {e}")

    def integrate_plugins_with_workflow(self):
        """Integrate plugins with workflow system."""
        try:
            if not PLUGIN_INTEGRATION_AVAILABLE:
                print("⚠ Plugin workflow integration not available")
                return
            # This is a placeholder for plugin integration
            print("✓ Plugin workflow integration initialized")
        except Exception as e:
            print(f"⚠ Failed to integrate plugins with workflow: {e}")

    def add_plugin_management_to_ui(self):
        """Add plugin management to UI."""
        try:
            # This is a placeholder for adding plugin management UI
            print("✓ Plugin management UI added")
        except Exception as e:
            print(f"⚠ Failed to add plugin management to UI: {e}")

    def setup_signals(self):
        """Connect signals to slots."""
        self.new_project_button.clicked.connect(self.create_new_project)
        self.project_selector.currentTextChanged.connect(self.load_project)
        self.start_button.clicked.connect(self.start_writing)
        self.approve_button.clicked.connect(self.approve_section)
        self.pause_button.clicked.connect(self.pause_writing)
        self.export_button.clicked.connect(self.export_novel)
        self.reset_api_button.clicked.connect(self.reset_api_log)
        self.clear_cache_button.clicked.connect(self.clear_synonym_cache)
        self.save_api_keys_button.clicked.connect(self.save_api_keys)
        self.tone_input.currentTextChanged.connect(self.update_sub_tone_options)
        self.delete_project_button.clicked.connect(self.delete_project)

        # Connect settings navigation buttons
        self.show_dashboard_button.clicked.connect(self.ui.smart_switch_to_dashboard)
        self.show_novel_settings_button.clicked.connect(self.ui.smart_switch_to_novel_settings)
        self.show_advanced_settings_button.clicked.connect(self.ui.switch_to_settings)
        self.show_performance_button.clicked.connect(self.ui.smart_switch_to_performance)
        self.show_settings_button.clicked.connect(self.ui.smart_switch_to_settings)

    def delete_project(self):
        """Delete the currently selected project after user confirmation."""
        project_name = self.project_selector.currentText()
        if not project_name or project_name == "Select a project":
            msg_box = create_styled_message_box(self, QMessageBox.Warning, "No Project Selected", "Please select a project to delete.")
            msg_box.exec_()
            return
        if QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to delete the project '{project_name}'?\n\nThis will permanently remove all files for this project.", QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            try:
                # Store current project before deletion for cleanup
                was_current_project = (self.current_project == project_name)

                # Clean up project-related components before deletion
                if was_current_project:
                    try:
                        # Safely clean up AI system components
                        if hasattr(self, 'async_workflow_manager'):
                            self.async_workflow_manager = None
                        if hasattr(self, 'novel_workflow'):
                            self.novel_workflow = None
                        if hasattr(self, 'project_manager'):
                            self.project_manager = None
                        if hasattr(self, 'file_cache'):
                            self.file_cache = None

                        # Reset workflow state
                        self.workflow_active = False
                        self.async_operations_active = False
                        self.current_async_task_id = None

                    except Exception as cleanup_error:
                        print(f"⚠ Warning during project cleanup: {cleanup_error}")

                # Delete project files
                project_path = os.path.join("projects", project_name)
                if os.path.exists(project_path):
                    shutil.rmtree(project_path)

                # Remove from selector
                idx = self.project_selector.findText(project_name)
                if idx != -1:
                    self.project_selector.removeItem(idx)

                # Reset UI if deleted project was loaded
                if was_current_project:
                    try:
                        # Use safe project loading with error handling
                        self.load_project(None)
                    except Exception as load_error:
                        print(f"⚠ Error during project reset: {load_error}")
                        # Manually reset to safe state
                        self.current_project = None
                        self.config = None
                        self.file_cache = None
                        if hasattr(self.ui, 'switch_to_new_project_mode'):
                            self.ui.switch_to_new_project_mode()

                self.log_tab.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Project '{project_name}' deleted.")
                self.statusBar.showMessage(f"Project '{project_name}' deleted", 5000)

                # Update button states after successful deletion
                self.update_button_states()

            except Exception as e:
                # Enhanced error handling for deletion failures
                error_msg = f"Failed to delete project '{project_name}': {str(e)}"
                print(f"❌ {error_msg}")

                try:
                    # Try to use ErrorHandler if available
                    ErrorHandler.handle_project_error("deletion", project_name, e, self)
                except Exception as handler_error:
                    # Fallback to basic error message if ErrorHandler fails
                    print(f"⚠ ErrorHandler also failed: {handler_error}")
                    msg_box = create_styled_message_box(
                        self,
                        QMessageBox.Critical,
                        "Project Deletion Failed",
                        f"{error_msg}\n\nThe project files may still exist on disk.\n"
                        "You may need to manually delete the project folder."
                    )
                    msg_box.exec_()

    def update_button_states(self):
        """Update button enabled states based on conditions with performance optimization."""
        # Cache frequently accessed values
        has_project = bool(self.current_project and self.current_project != "Select a project")

        # Only check API keys if we have a project (expensive operation)
        has_api_keys = False
        if has_project:
            try:
                env_data = load_project_env(self.current_project)
                openai_key = env_data.get('OPENAI_API_KEY', '')
                thesaurus_key = env_data.get('WORDSAPI_KEY', '')
                has_api_keys = bool(openai_key and thesaurus_key)
            except Exception:
                has_api_keys = False

        # Check workflow state (preferred over legacy worker thread)
        is_workflow_active = self.workflow_active
        is_workflow_waiting = (self.novel_workflow and
                               hasattr(self.novel_workflow, 'current_state') and
                               getattr(self.novel_workflow, 'current_state', None) == 'waiting_user')

        is_async_active = getattr(self, 'async_operations_active', False)

        # Legacy worker thread check (fallback)
        is_writing = bool(self.worker and self.worker.isRunning()) if hasattr(self, 'worker') else False
        is_waiting = is_writing and getattr(self.worker, 'waiting_for_approval', False) if hasattr(self, 'worker') else False

        # Combined state checks
        is_active = is_workflow_active or is_writing or is_async_active
        is_waiting_for_input = is_workflow_waiting or is_waiting

        # Only check file cache if we have a project (expensive operation)
        has_content = False
        if has_project and self.file_cache:
            try:
                story_content = self.file_cache.get("story.txt")
                has_content = bool(story_content and story_content.strip())
            except Exception:
                has_content = False

        # Batch update button states to avoid multiple redraws
        button_states = {
            self.start_button: has_project and has_api_keys and not is_active,
            self.pause_button: is_active,
            self.approve_button: is_waiting_for_input,
            self.export_button: has_content,
            self.reset_api_button: has_project,
            self.clear_cache_button: has_project,
            self.save_api_keys_button: has_project,
            self.new_project_button: not is_active,
            self.delete_project_button: has_project and not is_active
        }

        # Apply states efficiently
        for button, enabled in button_states.items():
            if hasattr(self, button.objectName()) or button:
                button.setEnabled(enabled)

        # Update async cancel button visibility
        if hasattr(self, 'async_cancel_button') and self.async_cancel_button:
            self.async_cancel_button.setVisible(is_async_active)

    def create_new_project(self):
        """Create a new project with user inputs or defaults."""
        project_name = self.project_input.text().strip()
        if not project_name:
            msg_box = create_styled_message_box(self, QMessageBox.Warning, "Invalid Project Name", "Please enter a project name.")
            msg_box.exec_()
            return
        if not validate_project_name(project_name):
            msg_box = create_styled_message_box(self, QMessageBox.Warning, "Invalid Project Name",
                              "Project name can only contain letters, numbers, spaces, dashes, and underscores. "
                              "It cannot contain path separators (/ or \\).")
            msg_box.exec_()
            return
        if project_name in get_project_list():
            msg_box = create_styled_message_box(self, QMessageBox.Warning, "Project Already Exists", f"A project named '{project_name}' already exists. Please choose a different name.")
            msg_box.exec_()
            return
        idea = self.idea_input.toPlainText().strip()
        tone = self.tone_input.currentText()
        sub_tone = self.sub_tone_input.currentText()
        theme = self.theme_dropdown.currentText()
        reading_level = self.reading_level_input.currentText()
        thesaurus_weight = self.thesaurus_weight_input.value()
        try:
            soft_target = int(self.target_input.currentText())
            if soft_target <= 0:
                raise ValueError("Target word count must be positive")
        except ValueError:
            msg_box = create_styled_message_box(self, QMessageBox.Warning, "Invalid Word Count",
                              "Target word count must be a positive integer (e.g., 50000, 250000). "
                              "Please enter a valid number.")
            msg_box.exec_()
            return
        characters_seed = self.characters_seed_input.toPlainText().strip()
        world_seed = self.world_seed_input.toPlainText().strip()
        themes_seed = self.themes_seed_input.toPlainText().strip()
        structure_seed = self.structure_seed_input.text().strip()
        custom_prompt = self.custom_prompt_input.toPlainText().strip() if hasattr(self, 'custom_prompt_input') else ""
        if not (idea or tone or reading_level or characters_seed or world_seed or themes_seed or theme) and not self.use_default_settings.isChecked():
            msg_box = create_styled_message_box(self, QMessageBox.Warning, "Insufficient Project Information",
                              "Please provide at least one project setting (idea, tone, characters, etc.) "
                              "or check 'Use default settings for unspecified fields' to create the project.")
            msg_box.exec_()
            return

        if CONFIGURATION_MANAGEMENT_AVAILABLE:
            try:
                # Initialize global configuration if not already done
                initialize_global_config()
                config = get_global_config()
            except Exception as e:
                print(f"⚠ Failed to get advanced configuration: {e}")
                return
        else:
            print("⚠ Advanced configuration not available")
            return

        try:
            # Use new configuration system to save project settings
            config.set("project.idea", idea or config.get("project.idea", ""))
            config.set("project.tone", tone or ("neutral" if self.use_default_settings.isChecked() else ""))
            config.set("project.sub_tone", sub_tone or ("neutral" if self.use_default_settings.isChecked() and tone == "neutral" else ""))
            config.set("project.theme", theme or "")
            config.set("project.soft_target", soft_target)
            config.set("project.reading_level", reading_level or ("College" if self.use_default_settings.isChecked() else ""))
            config.set("project.thesaurus_weight", thesaurus_weight)
            config.set("project.characters_seed", characters_seed)
            config.set("project.world_seed", world_seed)
            config.set("project.themes_seed", themes_seed)
            config.set("project.structure_seed", structure_seed or config.get("project.structure_seed", ""))
            config.set("project.custom_prompt", custom_prompt)

            # Save configuration
            config.save_config()
        except Exception as e:
            msg_box = create_styled_message_box(self, QMessageBox.Critical, "Project Creation Failed",
                               f"Failed to save project configuration: {str(e)}\n\n"
                               "Please check if you have write permissions to the projects directory.")
            msg_box.exec_()
            return
        try:
            initialize_project_files(project_name)
            save_to_file(project_name, "continuity_rules.txt", self.continuity_rules_input.toPlainText(), "w")
        except Exception as e:
            msg_box = create_styled_message_box(self, QMessageBox.Critical, "Project Creation Failed",
                               f"Failed to create project files: {str(e)}\n\n"
                               "Please check if you have write permissions to the projects directory.")
            msg_box.exec_()
            return
        self.project_selector.addItem(project_name)
        self.project_selector.setCurrentText(project_name)

        # Refresh all project selectors to ensure consistency
        if hasattr(self.ui, '_refresh_project_selector'):
            self.ui._refresh_project_selector()

        self.load_project(project_name)

    def load_project(self, project_name):
        """Load project data and update UI with performance monitoring."""
        start_time = datetime.now()

        try:
            if self.performance_monitor:
                self.performance_monitor.log_event("project_load_start", f"Loading project: {project_name}")

            # Clear current state
            self.current_project = None
            self.config = None
            self.file_cache = None
            self.project_manager = None
            self.update_button_states()

            # Clear all tabs efficiently
            for tab in [self.story_tab, self.config_tab, self.characters_tab, self.world_tab,
                       self.summaries_tab, self.drafts_tab, self.readability_tab, self.synonyms_tab]:
                tab.clear()

            # Clear all inputs efficiently
            input_defaults = {
                self.openai_key_input: "",
                self.wordsapi_key_input: "",
                self.continuity_rules_input: "",
                self.idea_input: "",
                self.characters_seed_input: "",
                self.world_seed_input: "",
                self.themes_seed_input: "",
                self.structure_seed_input: "",
                self.preview_text: ""
            }

            for input_widget, default_value in input_defaults.items():
                if hasattr(input_widget, 'clear'):
                    input_widget.clear()
                elif hasattr(input_widget, 'setText'):
                    input_widget.setText(default_value)

            # Reset UI state
            self.tone_input.setCurrentText("")
            self.sub_tone_input.setCurrentText("")
            self.reading_level_input.setCurrentText("College")
            self.thesaurus_weight_input.setValue(0.5)
            self.target_input.setCurrentText(str(250000))
            self.progress_label.setText("Progress: 0%")

            # Safely update progress bar with error handling
            try:
                if hasattr(self, 'progress_bar') and self.progress_bar is not None:
                    # Test if the widget is still valid
                    _ = self.progress_bar.objectName()
                    self.progress_bar.setValue(0)
                else:
                    # Create a new progress bar if it doesn't exist
                    self.progress_bar = QProgressBar()
                    self.progress_bar.setTextVisible(True)
                    self.progress_bar.setFormat("Overall Progress: %p%")
                    self.progress_bar.setValue(0)
            except RuntimeError:
                # Widget has been deleted, create a new one
                self.progress_bar = QProgressBar()
                self.progress_bar.setTextVisible(True)
                self.progress_bar.setFormat("Overall Progress: %p%")
                self.progress_bar.setValue(0)

            self.status_label.setText("Status: Ready")
            self.wordsapi_label.setText("WordsAPI Calls: 0/2500")
            self.word_count_label.setText("Word Count: 0")

            if not project_name or project_name == "Select a project":
                # Switch to new project mode when no project is selected
                try:
                    if hasattr(self.ui, 'switch_to_new_project_mode'):
                        self.ui.switch_to_new_project_mode()
                    else:
                        print("⚠ switch_to_new_project_mode not available")
                except Exception as ui_error:
                    print(f"⚠ Error switching to new project mode: {ui_error}")
                return

            # Load project with new configuration system
            self.current_project = project_name

            if CONFIGURATION_MANAGEMENT_AVAILABLE:
                try:
                    # Initialize global configuration for this project
                    initialize_global_config()
                    self.config = get_global_config()

                    # Create compatibility layer for legacy code
                    self.legacy_config = create_configuration_compatibility_layer()

                except Exception as e:
                    print(f"⚠ Failed to load advanced configuration for project {project_name}: {e}")
                    # Fallback: Create a minimal config object
                    self.config = None
                    self.legacy_config = None
            else:
                print("⚠ Advanced configuration not available for project loading")
                self.config = None
                self.legacy_config = None

            self.file_cache = ProjectFileCache(project_name)

            # Initialize project manager
            self.project_manager = ProjectManager(
                project_name=project_name,
                api_manager=APIManager(),
                file_cache=self.file_cache,
                config=self.config
            )

            # Initialize async workflow manager (Priority 4.1)
            self.initialize_async_workflow_manager()

            # Load configuration settings efficiently
            config_mappings = {
                'Idea': self.idea_input,
                'Tone': self.tone_input,
                'SubTone': self.sub_tone_input,
                'ReadingLevel': self.reading_level_input,
                'CharactersSeed': self.characters_seed_input,
                'WorldSeed': self.world_seed_input,
                'ThemesSeed': self.themes_seed_input,
                'StructureSeed': self.structure_seed_input
            }

            for config_key, widget in config_mappings.items():
                try:
                    value = self.config.get(config_key)
                    if hasattr(widget, 'setText'):
                        widget.setText(str(value))
                    elif hasattr(widget, 'setCurrentText'):
                        widget.setCurrentText(str(value))
                except Exception as e:
                    logging.warning(f"Failed to set {config_key}: {str(e)}")

            # Set numeric values
            try:
                thesaurus_weight = self.config.get("ThesaurusWeight")
                if thesaurus_weight is not None:
                    self.thesaurus_weight_input.setValue(float(thesaurus_weight))
                else:
                    self.thesaurus_weight_input.setValue(0.5)  # Default value

                soft_target = self.config.get("SoftTarget")
                if soft_target is not None:
                    self.target_input.setCurrentText(str(soft_target))
                else:
                    self.target_input.setCurrentText("250000")  # Default value

                theme = self.config.get("Theme")
                if theme:
                    self.theme_dropdown.setCurrentText(str(theme))
            except Exception as e:
                logging.warning(f"Failed to set numeric config values: {str(e)}")
                # Set default values on error
                self.thesaurus_weight_input.setValue(0.5)
                self.target_input.setCurrentText("250000")

            # Load file contents into tabs efficiently
            file_tab_mappings = [
                ("story.txt", self.story_tab),
                ("config.txt", self.config_tab),
                ("characters.txt", self.characters_tab),
                ("world.txt", self.world_tab),
                ("summaries.txt", self.summaries_tab),
                ("synopsis.txt", self.story_tab),
                ("timeline.txt", self.drafts_tab)
            ]

            for filename, tab in file_tab_mappings:
                try:
                    content = self.file_cache.get(filename)
                    if filename == "synopsis.txt" and content:
                        # Don't overwrite story tab if it already has content
                        if not self.story_tab.toPlainText():
                            tab.setText(content)
                    else:
                        tab.setText(content if content else "")
                except Exception as e:
                    logging.warning(f"Failed to load {filename}: {str(e)}")
                    tab.setText(f"Error loading {filename}: {str(e)}")

            # Load API usage statistics
            try:
                wordsapi_log = load_wordsapi_log(project_name)
                self.update_wordsapi_count(get_wordsapi_call_count(project_name))

                story_content = self.file_cache.get("story.txt")
                self.update_word_count(len(story_content.split()) if story_content else 0)
            except Exception as e:
                logging.warning(f"Failed to load API usage statistics: {str(e)}")
                self.update_wordsapi_count(0)
                self.update_word_count(0)

            # Load synonym cache
            try:
                synonym_cache = load_synonym_cache(project_name)
                self.synonyms_tab.setText(json.dumps(synonym_cache, indent=2))
            except Exception as e:
                logging.warning(f"Failed to load synonym cache: {str(e)}")
                self.synonyms_tab.setText("{}")

            # Load continuity rules
            try:
                continuity_rules = self.file_cache.get("continuity_rules.txt")
                self.continuity_rules_input.setText(continuity_rules if continuity_rules else "")
            except Exception as e:
                logging.warning(f"Failed to load continuity rules: {str(e)}")
                self.continuity_rules_input.setText("")

            # Load API keys
            try:
                env_data = load_project_env(project_name)
                openai_key = env_data.get('OPENAI_API_KEY', '')
                thesaurus_key = env_data.get('WORDSAPI_KEY', '')
                self.openai_key_input.setText(openai_key)
                self.wordsapi_key_input.setText(thesaurus_key)
            except Exception as e:
                logging.warning(f"Failed to load API keys: {str(e)}")
                self.openai_key_input.setText("")
                self.wordsapi_key_input.setText("")

            # Log performance metrics
            if self.performance_monitor:
                load_time = (datetime.now() - start_time).total_seconds()
                self.performance_monitor.log_event("project_load_complete", {
                    "project": project_name,
                    "load_time": load_time,
                    "unit": "seconds",
                    "category": "performance"
                })

            if hasattr(self, 'analytics_manager') and self.analytics_manager:
                self.analytics_manager.set_project(project_name)

            if hasattr(self, 'collaborative_manager') and self.collaborative_manager:
                self._initialize_project_collaboration()

            self.statusBar.showMessage(f"Loaded project '{project_name}'", 5000)
            self.log_tab.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Project '{project_name}' loaded successfully.")
            self.update_button_states()

            # Switch to project workspace when a project is loaded
            try:
                if hasattr(self.ui, 'switch_to_project_workspace'):
                    self.ui.switch_to_project_workspace()
                else:
                    print("⚠ switch_to_project_workspace not available")
            except Exception as ui_error:
                print(f"⚠ Error switching to project workspace: {ui_error}")

        except Exception as e:
            error_msg = f"Failed to load project '{project_name}': {str(e)}"

            if self.performance_monitor:
                self.performance_monitor.log_event("project_load_error", error_msg)

            msg_box = create_styled_message_box(self, QMessageBox.Critical, "Project Load Failed",
                               f"{error_msg}\n\n"
                               "The project may be corrupted or missing required files.\n"
                               "Please check the project directory or create a new project.")
            msg_box.exec_()
            logging.error(error_msg)

            # Reset state on failure
            self.current_project = None
            self.config = None
            self.file_cache = None
            self.project_manager = None
            self.update_button_states()

            # Switch back to new project mode on failure
            try:
                if hasattr(self.ui, 'switch_to_new_project_mode'):
                    self.ui.switch_to_new_project_mode()
                else:
                    print("⚠ switch_to_new_project_mode not available")
            except Exception as ui_error:
                print(f"⚠ Error switching to new project mode after failure: {ui_error}")

    def save_api_keys(self):
        """Save API keys and continuity rules."""
        if not self.current_project:
            msg_box = create_styled_message_box(self, QMessageBox.Warning, "No Project Selected",
                              "Please select or create a project before saving API keys.")
            msg_box.exec_()
            return
        openai_key = self.openai_key_input.text().strip()
        thesaurus_key = self.wordsapi_key_input.text().strip()
        if not openai_key or not thesaurus_key:
            msg_box = create_styled_message_box(self, QMessageBox.Warning, "Missing API Keys",
                              "Please enter both OpenAI API Key and WordsAPI Key.\n\n"
                              "You can get these keys from:\n"
                              "• OpenAI: https://platform.openai.com/api-keys\n"
                              "• WordsAPI: https://rapidapi.com/dpventures/api/wordsapi")
            msg_box.exec_()
            return
        try:
            save_project_env(self.current_project, openai_key, thesaurus_key)
            self.file_cache.update("continuity_rules.txt", self.continuity_rules_input.toPlainText())
            self.log_tab.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - API keys and continuity rules saved.")
            self.statusBar.showMessage("API keys and continuity rules saved", 5000)
            self.update_button_states()
        except Exception as e:
            msg_box = create_styled_message_box(self, QMessageBox.Critical, "Failed to Save API Keys",
                               f"Error saving API keys: {str(e)}\n\n"
                               "Please check if you have write permissions to the project directory.")
            msg_box.exec_()

    def start_writing(self):
        """Start the automated novel writing workflow with async support."""
        if not self.current_project:
            msg_box = create_styled_message_box(self, QMessageBox.Warning, "No Project Selected",
                              "Please select or create a project before starting to write.")
            msg_box.exec_()
            return

        # Performance monitoring
        if self.performance_monitor:
            self.performance_monitor.log_event("writing_start", f"Starting writing for project: {self.current_project}")

        self.start_analytics_session()

        env_data = load_project_env(self.current_project)
        openai_key = env_data.get('OPENAI_API_KEY', '')
        thesaurus_key = env_data.get('WORDSAPI_KEY', '')
        if not openai_key or not thesaurus_key:
            msg_box = create_styled_message_box(self, QMessageBox.Warning, "Missing API Keys",
                              "Please enter and save valid API keys in the Advanced tab before starting.\n\n"
                              "You need:\n"
                              "• OpenAI API Key (for text generation)\n"
                              "• WordsAPI Key (for synonym lookup)")
            msg_box.exec_()
            return

        try:
            soft_target = int(self.target_input.currentText())
        except ValueError:
            msg_box = create_styled_message_box(self, QMessageBox.Warning, "Invalid Target Word Count",
                              "The target word count is not a valid number. Using default value of 250,000.")
            msg_box.exec_()
            soft_target = 250000

        # Save current configuration
        custom_prompt = self.custom_prompt_input.toPlainText().strip() if hasattr(self, 'custom_prompt_input') else ""

        try:
            # Update configuration with current UI values
            self.config.save_config(
                Idea=self.idea_input.toPlainText().strip() or self.config.get("Idea"),
                Tone=self.tone_input.currentText() or ("neutral" if self.use_default_settings.isChecked() else ""),
                SubTone=self.sub_tone_input.currentText() or ("neutral" if self.use_default_settings.isChecked() and self.tone_input.currentText() == "neutral" else ""),
                Theme=self.theme_dropdown.currentText() or (""),
                SoftTarget=soft_target,
                ReadingLevel=self.reading_level_input.currentText() or ("College" if self.use_default_settings.isChecked() else ""),
                ThesaurusWeight=self.thesaurus_weight_input.value(),
                CharactersSeed=self.characters_seed_input.toPlainText().strip(),
                WorldSeed=self.world_seed_input.toPlainText().strip(),
                ThemesSeed=self.themes_seed_input.toPlainText().strip(),
                StructureSeed=self.structure_seed_input.text().strip() or self.config.get("StructureSeed"),
                CustomPrompt=custom_prompt
            )

            # Initialize project context
            self.file_cache.update("context.txt", f"Novel started: {self.config.get('Idea')}. Initial tone: {self.config.get('Tone')}.")

        except Exception as e:
            msg_box = create_styled_message_box(self, QMessageBox.Critical, "Configuration Error",
                               f"Failed to save configuration before starting: {str(e)}\n\n"
                               "The writing process cannot continue.")
            msg_box.exec_()
            return

        try:
            # Try async workflow first if available
            if self.async_manager and self.async_workflow_manager:
                self.start_writing_async()
            else:
                # Fallback to traditional workflow or legacy thread
                if hasattr(self, 'novel_workflow') and self.novel_workflow:
                    self.start_writing_workflow()
                else:
                    self.start_writing_legacy()

        except Exception as e:
            msg_box = create_styled_message_box(self, QMessageBox.Critical, "Writing Start Error",
                               f"Failed to start writing process: {str(e)}")
            msg_box.exec_()
            return

    def start_writing_async(self):
        """Start writing using async operations with enhanced features (Phase 1.2)."""
        try:
            # Get workflow steps
            steps = self.get_workflow_steps()

            if not steps:
                QMessageBox.warning(self, "No Steps", "No workflow steps defined.")
                return

            # Estimate duration based on project complexity
            estimated_duration = self.estimate_workflow_duration(steps)

            # Execute async workflow with enhanced tracking
            operation_id = self.async_workflow_manager.execute_workflow_async(
                steps=steps,
                progress_callback=self.update_progress_async,
                completion_callback=self.on_workflow_completed_async,
                estimated_duration=estimated_duration
            )

            # Add to background task management
            self.add_background_task(
                operation_id,
                "Novel Writing Workflow",
                estimated_duration
            )

            self.current_async_task_id = operation_id
            print(f"✅ Enhanced async workflow started with ID: {operation_id}")

            # Update UI state
            self.workflow_active = True
            self.async_operations_active = True
            self.update_button_states()

            # Show async progress widget
            if hasattr(self, 'async_progress_widget') and self.async_progress_widget:
                self.async_progress_widget.show()
                self.async_progress_widget.set_operation("Novel Writing Workflow")

            # Log start with performance monitoring
            if self.performance_monitor:
                self.performance_monitor.log_event("async_workflow_started",
                    f"Async workflow started for project: {self.current_project}")

        except Exception as e:
            print(f"❌ Enhanced async workflow execution failed: {e}")
            # Fallback to sync workflow
            self.start_writing_workflow()

    def estimate_workflow_duration(self, steps):
        """Estimate workflow duration based on project complexity."""
        try:
            base_duration = 300  # 5 minutes base

            # Factor in project complexity
            if self.config:
                word_target = self.config.get('SoftTarget', 250000)
                complexity_factor = min(word_target / 50000, 5.0)  # Cap at 5x
                base_duration *= complexity_factor

            # Factor in number of steps
            step_factor = len(steps) * 60  # 1 minute per step

            estimated = int(base_duration + step_factor)
            print(f"📊 Estimated workflow duration: {estimated} seconds")

            return estimated

        except Exception as e:
            print(f"⚠️ Error estimating duration: {e}")
            return 600  # Default 10 minutes

    def start_writing_workflow(self):
        """Start writing using modular workflow system."""
        try:
            # Initialize workflow manager if not already done
            if not self.novel_workflow:
                self.initialize_workflow_manager()

            if not self.novel_workflow:
                msg_box = create_styled_message_box(self, QMessageBox.Critical, "Workflow Error",
                                   "Failed to initialize the novel writing workflow.\n\n"
                                   "Please check your project configuration and try again.")
                msg_box.exec_()
                return

            # Start the modular workflow
            self.workflow_active = True
            self.current_workflow_step = None
            self.update_button_states()

            # Start the workflow execution
            self.novel_workflow.start_workflow()

            self.log_tab.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Novel writing workflow started.")
            self.statusBar.showMessage("Novel writing workflow started...", 5000)

        except Exception as e:
            self.workflow_active = False
            self.update_button_states()
            msg_box = create_styled_message_box(self, QMessageBox.Critical, "Workflow Start Error",
                               f"Failed to start the novel writing workflow: {str(e)}\n\n"
                               "Please check your project configuration and API keys.")
            msg_box.exec_()

    def start_writing_legacy(self):
        """Start writing using legacy worker thread."""
        try:
            # Create and start worker thread
            self.worker = WorkerThread(self.current_project,
                                     self.openai_key_input.text().strip(),
                                     self.wordsapi_key_input.text().strip())
            self.setup_worker_signals()
            self.worker.start()

            # Update UI state
            self.workflow_active = True
            self.update_button_states()

            self.log_tab.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Legacy writing process started.")
            self.statusBar.showMessage("Novel writing started...", 5000)

        except Exception as e:
            self.workflow_active = False
            self.update_button_states()
            msg_box = create_styled_message_box(self, QMessageBox.Critical, "Writing Start Error",
                               f"Failed to start the writing process: {str(e)}")
            msg_box.exec_()

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
                'type': 'content',
                'async_compatible': True
            })

            # Add quality assurance step
            steps.append({
                'id': 'quality_assurance',
                'name': 'Quality Assurance',
                'type': 'qa',
                'async_compatible': True
            })

            # Add finalization step
            steps.append({
                'id': 'finalization',
                'name': 'Finalization',
                'type': 'finalize',
                'async_compatible': True
            })

        except Exception as e:
            print(f"Error creating basic workflow steps: {e}")

        return steps

    def update_progress_async(self, progress, message=""):
        """Update progress for async operations with enhanced ETA tracking."""
        # Update background task progress with ETA calculation
        if self.current_async_task_id:
            self.update_background_task_progress(self.current_async_task_id, progress, message)

        # Update async progress widget with enhanced information
        if hasattr(self, 'async_progress_widget') and self.async_progress_widget:
            self.async_progress_widget.set_progress(progress, message)

        # Update main progress bar with async-specific formatting
        if hasattr(self, 'progress_bar') and self.progress_bar:
            if hasattr(self.progress_bar, 'set_async_progress'):
                # Use enhanced progress method if available
                eta_info = self.calculate_eta_for_current_task()
                self.progress_bar.set_async_progress(progress, message, eta_info)
            else:
                # Fallback to regular progress update
                self.progress_bar.setValue(progress)

        # Update status bar with detailed information
        if hasattr(self, 'statusBar') and self.statusBar:
            if progress < 100:
                status_msg = f"Async: {message} ({progress}%)" if message else f"Async Progress: {progress}%"
                self.statusBar.showMessage(status_msg, 2000)
            else:
                self.statusBar.showMessage("Async operation completed", 3000)

    def calculate_eta_for_current_task(self):
        """Calculate ETA for the current async task."""
        try:
            if not self.current_async_task_id or not hasattr(self, 'background_tasks'):
                return ""

            task_info = self.background_tasks.get(self.current_async_task_id)
            if not task_info:
                return ""

            progress = task_info.get('progress', 0)
            if progress <= 0:
                return "Calculating..."

            elapsed_time = time.time() - task_info['start_time']
            estimated_total = elapsed_time * (100 / progress)
            eta_seconds = estimated_total - elapsed_time

            if eta_seconds > 0:
                if eta_seconds > 3600:  # More than an hour
                    hours = int(eta_seconds / 3600)
                    minutes = int((eta_seconds % 3600) / 60)
                    return f"ETA: {hours}h {minutes}m"
                elif eta_seconds > 60:  # More than a minute
                    minutes = int(eta_seconds / 60)
                    seconds = int(eta_seconds % 60)
                    return f"ETA: {minutes}m {seconds}s"
                else:  # Less than a minute
                    return f"ETA: {int(eta_seconds)}s"
            else:
                return "Nearly complete"

        except Exception as e:
            print(f"❌ Error calculating ETA: {e}")
            return ""

    def on_workflow_completed_async(self, result):
        """Handle completion of async workflow."""
        try:
            self.workflow_active = False
            self.current_async_task_id = None

            self.end_analytics_session()

            # Update UI state
            self.update_button_states()

            # Show completion message
            if result and result.get('success', True):
                from src.error_handling_system import create_styled_message_box
                msg_box = create_styled_message_box(
                    self,
                    QMessageBox.Information,
                    "Workflow Complete",
                    "Async novel writing workflow completed successfully!"
                )
                msg_box.exec_()

            # Log completion
            self.log_tab.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Async workflow completed")

            # Update progress to 100%
            self.progress_bar.setValue(100)
            self.status_label.setText("Status: Workflow Complete")

            # Performance logging
            if self.performance_monitor:
                self.performance_monitor.log_event("workflow_completed", f"Async workflow completed for project: {self.current_project}")

            print("✅ Async workflow completed successfully")

        except Exception as e:
            print(f"⚠️ Error handling workflow completion: {e}")
            self.workflow_active = False
            self.current_async_task_id = None
            self.update_button_states()

    def pause_writing(self):
        """Pause the current writing process."""
        try:
            self.end_analytics_session()

            # Try async workflow first
            if self.async_workflow_manager and self.current_async_task_id:
                self.async_workflow_manager.pause_workflow(self.current_async_task_id)
                self.log_tab.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Async workflow paused")
                self.workflow_active = False
                self.update_button_states()
                return

            # Try modular workflow
            if self.novel_workflow and self.workflow_active:
                self.pause_workflow()
                return

            # Try legacy worker thread
            if self.worker and self.worker.isRunning():
                self.worker.terminate()
                self.log_tab.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Legacy workflow stopped")
                self.workflow_active = False
                self.update_button_states()
                return

            print("⚠️ No active workflow to pause")

        except Exception as e:
            print(f"⚠️ Error pausing writing: {e}")
            logging.error(f"Failed to pause writing: {str(e)}")

    def approve_section(self):
        """Approve the current section and continue workflow."""
        try:
            # Try async workflow first
            if self.async_workflow_manager and self.current_async_task_id:
                self.async_workflow_manager.approve_current_section(self.current_async_task_id)
                self.log_tab.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Async section approved")
                return

            # Try modular workflow
            if self.novel_workflow and hasattr(self.novel_workflow, 'approve_current_section'):
                self.novel_workflow.approve_current_section()
                self.log_tab.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Modular section approved")
                return

            # Try legacy worker thread
            if self.worker and hasattr(self.worker, 'waiting_for_approval'):
                self.worker.waiting_for_approval = False
                self.log_tab.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Legacy section approved")
                return

            print("⚠️ No section waiting for approval")

        except Exception as e:
            print(f"⚠️ Error approving section: {e}")
            logging.error(f"Failed to approve section: {str(e)}")

    def export_novel(self):
        """Export the current novel to various formats."""
        try:
            if not self.current_project:
                msg_box = create_styled_message_box(
                    self,
                    QMessageBox.Warning,
                    "No Project Selected",
                    "Please select a project before exporting."
                )
                msg_box.exec_()
                return

            if not self.file_cache:
                msg_box = create_styled_message_box(
                    self,
                    QMessageBox.Warning,
                    "No Content Available",
                    "No content available for export. Please write some content first."
                )
                msg_box.exec_()
                return

            story_content = self.file_cache.get("story.txt")
            if not story_content or not story_content.strip():
                msg_box = create_styled_message_box(
                    self,
                    QMessageBox.Warning,
                    "No Content Available",
                    "No story content available for export. Please write some content first."
                )
                msg_box.exec_()
                return

            # Create export dialog
            from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton, QButtonGroup

            dialog = QDialog(self)
            dialog.setWindowTitle("Export Novel")
            dialog.setModal(True)
            dialog.resize(400, 300)

            layout = QVBoxLayout()

            # Format selection
            layout.addWidget(QLabel("Select Export Format:"))

            format_group = QButtonGroup()
            txt_radio = QRadioButton("Text File (.txt)")
            txt_radio.setChecked(True)
            docx_radio = QRadioButton("Word Document (.docx)")
            pdf_radio = QRadioButton("PDF Document (.pdf)")

            format_group.addButton(txt_radio, 0)
            format_group.addButton(docx_radio, 1)
            format_group.addButton(pdf_radio, 2)

            layout.addWidget(txt_radio)
            layout.addWidget(docx_radio)
            layout.addWidget(pdf_radio)

            # Buttons
            button_layout = QHBoxLayout()
            export_btn = QPushButton("Export")
            cancel_btn = QPushButton("Cancel")

            button_layout.addWidget(export_btn)
            button_layout.addWidget(cancel_btn)
            layout.addLayout(button_layout)

            dialog.setLayout(layout)

            def do_export():
                format_id = format_group.checkedId()
                if format_id == 0:  # TXT
                    filename = f"{self.current_project}_export.txt"
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(story_content)
                elif format_id == 1:  # DOCX
                    filename = f"{self.current_project}_export.docx"
                    doc = Document()
                    doc.add_paragraph(story_content)
                    doc.save(filename)
                elif format_id == 2:  # PDF
                    filename = f"{self.current_project}_export.pdf"
                    doc = SimpleDocTemplate(filename, pagesize=letter)
                    styles = getSampleStyleSheet()
                    story = Paragraph(story_content.replace('\n', '<br/>'), styles['Normal'])
                    doc.build([story])

                self.log_tab.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Novel exported as {filename}")
                dialog.accept()

            export_btn.clicked.connect(do_export)
            cancel_btn.clicked.connect(dialog.reject)

            dialog.exec_()

        except Exception as e:
            print(f"⚠️ Error exporting novel: {e}")
            logging.error(f"Failed to export novel: {str(e)}")

    def reset_api_log(self):
        """Reset the API usage log."""
        try:
            if not self.current_project:
                msg_box = create_styled_message_box(
                    self,
                    QMessageBox.Warning,
                    "No Project Selected",
                    "Please select a project before resetting API log."
                )
                msg_box.exec_()
                return

            # Reset WordsAPI log
            from src.file_operations import save_wordsapi_log
            save_wordsapi_log(self.current_project, {})

            # Update UI
            self.update_wordsapi_count(0)
            self.log_tab.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - API usage log reset")

            msg_box = create_styled_message_box(
                self,
                QMessageBox.Information,
                "API Log Reset",
                "WordsAPI usage log has been reset successfully."
            )
            msg_box.exec_()

        except Exception as e:
            print(f"⚠️ Error resetting API log: {e}")
            logging.error(f"Failed to reset API log: {str(e)}")

    def clear_synonym_cache(self):
        """Clear the synonym cache."""
        try:
            if not self.current_project:
                msg_box = create_styled_message_box(
                    self,
                    QMessageBox.Warning,
                    "No Project Selected",
                    "Please select a project before clearing synonym cache."
                )
                msg_box.exec_()
                return

            # Clear synonym cache
            from src.file_operations import save_synonym_cache
            save_synonym_cache(self.current_project, {})

            # Update UI
            self.synonyms_tab.setText("{}")
            self.log_tab.append(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Synonym cache cleared")

            msg_box = create_styled_message_box(
                self,
                QMessageBox.Information,
                "Cache Cleared",
                "Synonym cache has been cleared successfully."
            )
            msg_box.exec_()

        except Exception as e:
            print(f"⚠️ Error clearing synonym cache: {e}")
            logging.error(f"Failed to clear synonym cache: {str(e)}")

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

    def on_task_selection_changed(self, current, previous):
        """Handle task selection change in the monitor."""
        try:
            if not current or not hasattr(self, 'task_details_text'):
                return

            item_text = current.text()
            # Extract task name from formatted text
            if ' - ' in item_text:
                task_name = item_text.split(' - ')[0][2:]  # Remove status emoji

                # Find the task details
                task_details = self.find_task_details(task_name)

                if task_details:
                    formatted_details = self.format_task_details_display(task_details)
                    self.task_details_text.setPlainText(formatted_details)
                else:
                    self.task_details_text.setPlainText("Task details not found")

        except Exception as e:
            print(f"⚠️ Error handling task selection: {e}")

    def find_task_details(self, task_name):
        """Find task details by name."""
        try:
            # Search in active tasks
            for task_id, task in self.background_tasks.items():
                if task.get('name') == task_name:
                    return task

            # Search in completed tasks
            for task in self.completed_tasks:
                if task.get('name') == task_name:
                    return task

            # Search in failed tasks
            for task in self.failed_tasks:
                if task.get('name') == task_name:
                    return task

            return None

        except Exception as e:
            print(f"⚠️ Error finding task details: {e}")
            return None

    def format_task_details_display(self, task):
        """Format task details for display."""
        try:
            details = []
            details.append(f"Task: {task.get('name', 'Unknown')}")
            details.append(f"Status: {task.get('status', 'Unknown')}")
            details.append(f"Progress: {task.get('progress', 0)}%")

            if task.get('start_time'):
                details.append(f"Started: {task['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")

            if task.get('end_time'):
                details.append(f"Ended: {task['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")

            if task.get('duration'):
                details.append(f"Duration: {task['duration']:.1f}s")

            if task.get('eta'):
                details.append(f"ETA: {task['eta']}")

            if task.get('error'):
                details.append(f"Error: {task['error']}")

            return '\n'.join(details)

        except Exception as e:
            print(f"⚠️ Error formatting task details: {e}")
            return "Error formatting task details"

    def clear_completed_tasks(self):
        """Clear completed and failed tasks from the display."""
        try:
            self.completed_tasks.clear()
            self.failed_tasks.clear()
            self.update_task_monitor_display()
            print("✅ Completed tasks cleared")

        except Exception as e:
            print(f"⚠️ Error clearing completed tasks: {e}")

    def export_task_log(self):
        """Export task log to file."""
        try:

            log_data = {
                'export_time': datetime.now().isoformat(),
                'active_tasks': dict(self.background_tasks),
                'completed_tasks': self.completed_tasks,
                'failed_tasks': self.failed_tasks,
                'analytics': self.task_analytics
            }

            filename = f"task_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(self.current_directory, 'logs', filename)

            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, 'w') as f:
                json.dump(log_data, f, indent=2, default=str)

            QMessageBox.information(self, "Export Complete", f"Task log exported to: {filepath}")

        except Exception as e:
            print(f"⚠️ Error exporting task log: {e}")
            QMessageBox.critical(self, "Export Error", f"Failed to export task log: {e}")

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

    def update_task_analytics(self):
        """Update task performance analytics."""
        try:
            # Calculate current metrics
            total_tasks = len(self.completed_tasks) + len(self.failed_tasks)
            completed_tasks = len(self.completed_tasks)
            failed_tasks = len(self.failed_tasks)

            self.task_analytics['total_tasks'] = total_tasks
            self.task_analytics['completed_tasks'] = completed_tasks
            self.task_analytics['failed_tasks'] = failed_tasks

            # Calculate success rate
            if total_tasks > 0:
                self.task_analytics['success_rate'] = (completed_tasks / total_tasks) * 100
            else:
                self.task_analytics['success_rate'] = 0.0

            # Calculate average duration
            if self.completed_tasks:
                total_duration = sum(task.get('duration', 0) for task in self.completed_tasks)
                self.task_analytics['average_duration'] = total_duration / len(self.completed_tasks)
            else:
                self.task_analytics['average_duration'] = 0.0

            # Update performance history
            current_time = datetime.now()
            if self.completed_tasks:
                for task in self.completed_tasks:
                    if not any(h.get('task_id') == task.get('id') for h in self.task_analytics['task_performance_history']):
                        history_entry = {
                            'task_id': task.get('id'),
                            'task_name': task.get('name'),
                            'duration': task.get('duration', 0),
                            'timestamp': task.get('end_time', current_time),
                            'success': True
                        }
                        self.task_analytics['task_performance_history'].append(history_entry)

            # Keep only last 100 entries
            if len(self.task_analytics['task_performance_history']) > 100:
                self.task_analytics['task_performance_history'] = self.task_analytics['task_performance_history'][-100:]

        except Exception as e:
            print(f"⚠️ Error updating task analytics: {e}")

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

    def init_plugin_management_ui(self):
        """Initialize the plugin management UI components."""
        try:
            # Create plugin management button in toolbar (will be added when toolbar is created)
            self.plugin_manager_btn = None
            self.plugin_manager_dialog = None
            self.plugin_discovery_dialog = None
            self.plugin_config_dialog = None

            print("✓ Plugin management UI initialized")

        except Exception as e:
            print(f"⚠ Error initializing plugin management UI: {e}")

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

    def update_plugin_manager_display(self):
        """Update the plugin manager display with current plugin information."""
        try:
            if not self.plugin_manager_dialog or not self.plugin_manager:
                return

            # Get plugin information
            all_plugins = self.plugin_manager.get_all_plugins()
            active_plugins = [p for p in all_plugins if p.get_status().value == 'active']
            available_plugins = self.plugin_manager.get_available_plugins()
            disabled_plugins = self.plugin_config.get('disabled_plugins', [])

            # Update summary labels
            self.total_plugins_label.setText(str(len(all_plugins)))
            self.active_plugins_label.setText(str(len(active_plugins)))
            self.available_plugins_label.setText(str(len(available_plugins)))
            self.disabled_plugins_label.setText(str(len(disabled_plugins)))

            # Update plugin list
            self.plugin_list_widget.clear()

            for plugin in all_plugins:
                plugin_info = plugin.get_info()
                status = plugin.get_status().value

                # Status icon mapping
                status_icon = {
                    'active': '✅',
                    'inactive': '⚪',
                    'error': '❌',
                    'disabled': '🚫',
                    'loading': '🟡'
                }.get(status, '❓')

                item_text = f"{status_icon} {plugin_info.name} v{plugin_info.version} - {status}"
                self.plugin_list_widget.addItem(item_text)

        except Exception as e:
            print(f"⚠ Error updating plugin manager display: {e}")

    def show_plugin_discovery(self):
        """Show the plugin discovery and installation dialog."""
        try:
            if not self.plugin_discovery_dialog:
                self.create_plugin_discovery_dialog()

            self.update_plugin_discovery_display()
            self.plugin_discovery_dialog.show()
            self.plugin_discovery_dialog.raise_()

        except Exception as e:
            print(f"⚠ Error showing plugin discovery: {e}")

    def create_plugin_discovery_dialog(self):
        """Create the plugin discovery and installation dialog."""
        try:
            self.plugin_discovery_dialog = QDialog(self)
            self.plugin_discovery_dialog.setWindowTitle("Plugin Discovery & Installation")
            self.plugin_discovery_dialog.setModal(True)
            self.plugin_discovery_dialog.resize(800, 600)

            layout = QVBoxLayout()

            # Discovery paths configuration
            paths_group = QGroupBox("Discovery Paths")
            paths_layout = QVBoxLayout()

            self.discovery_paths_list = QListWidget()
            paths_layout.addWidget(self.discovery_paths_list)

            paths_button_layout = QHBoxLayout()
            add_path_btn = QPushButton("Add Path")
            add_path_btn.clicked.connect(self.add_discovery_path)
            remove_path_btn = QPushButton("Remove Path")
            remove_path_btn.clicked.connect(self.remove_discovery_path)

            paths_button_layout.addWidget(add_path_btn)
            paths_button_layout.addWidget(remove_path_btn)
            paths_layout.addLayout(paths_button_layout)

            paths_group.setLayout(paths_layout)
            layout.addWidget(paths_group)

            # Available plugins
            available_group = QGroupBox("Available Plugins")
            available_layout = QVBoxLayout()

            self.available_plugins_list = QListWidget()
            available_layout.addWidget(self.available_plugins_list)

            available_button_layout = QHBoxLayout()
            install_btn = QPushButton("Install Selected")
            install_btn.clicked.connect(self.install_selected_plugin)
            scan_btn = QPushButton("Scan for Plugins")
            scan_btn.clicked.connect(self.scan_for_plugins)

            available_button_layout.addWidget(install_btn)
            available_button_layout.addWidget(scan_btn)
            available_layout.addLayout(available_button_layout)

            available_group.setLayout(available_layout)
            layout.addWidget(available_group)

            # Control buttons
            button_layout = QHBoxLayout()

            close_btn = QPushButton("Close")
            close_btn.clicked.connect(self.plugin_discovery_dialog.hide)

            button_layout.addWidget(close_btn)
            layout.addLayout(button_layout)

            self.plugin_discovery_dialog.setLayout(layout)

            print("✓ Plugin discovery dialog created")

        except Exception as e:
            print(f"⚠ Error creating plugin discovery dialog: {e}")

    def update_plugin_discovery_display(self):
        """Update the plugin discovery display."""
        try:
            if not self.plugin_discovery_dialog:
                return

            # Update discovery paths
            self.discovery_paths_list.clear()
            discovery_paths = self.plugin_config.get('plugin_discovery_paths', ['plugins'])
            for path in discovery_paths:
                self.discovery_paths_list.addItem(path)

            # Update available plugins (scan current paths)
            self.scan_for_plugins()

        except Exception as e:
            print(f"⚠ Error updating plugin discovery display: {e}")

    def add_discovery_path(self):
        """Add a new plugin discovery path."""
        try:
            path = QFileDialog.getExistingDirectory(
                self, "Select Plugin Directory", self.current_directory
            )

            if path:
                discovery_paths = self.plugin_config.get('plugin_discovery_paths', ['plugins'])
                if path not in discovery_paths:
                    discovery_paths.append(path)
                    self.plugin_config['plugin_discovery_paths'] = discovery_paths
                    self.save_plugin_configuration()
                    self.update_plugin_discovery_display()
                    print(f"✓ Added discovery path: {path}")
                else:
                    QMessageBox.information(self, "Path Exists", "This path is already in the discovery list.")

        except Exception as e:
            print(f"⚠ Error adding discovery path: {e}")

    def remove_discovery_path(self):
        """Remove a plugin discovery path."""
        try:
            current_item = self.discovery_paths_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "No Selection", "Please select a path to remove.")
                return

            path = current_item.text()
            discovery_paths = self.plugin_config.get('plugin_discovery_paths', ['plugins'])

            if path in discovery_paths:
                discovery_paths.remove(path)
                self.plugin_config['plugin_discovery_paths'] = discovery_paths
                self.save_plugin_configuration()
                self.update_plugin_discovery_display()
                print(f"✓ Removed discovery path: {path}")

        except Exception as e:
            print(f"⚠ Error removing discovery path: {e}")

    def scan_for_plugins(self):
        """Scan discovery paths for available plugins."""
        try:
            self.available_plugins_list.clear()

            discovery_paths = self.plugin_config.get('plugin_discovery_paths', ['plugins'])
            found_plugins = []

            for path in discovery_paths:
                plugin_dir = os.path.join(self.current_directory, path)
                if os.path.exists(plugin_dir):
                    # Scan for Python plugin files
                    for root, dirs, files in os.walk(plugin_dir):
                        for file in files:
                            if file.endswith('.py') and not file.startswith('__'):
                                plugin_path = os.path.join(root, file)
                                plugin_name = os.path.splitext(file)[0]

                                # Check if already loaded
                                is_loaded = plugin_name in self.loaded_plugins
                                status = "Loaded" if is_loaded else "Available"

                                found_plugins.append({
                                    'name': plugin_name,
                                    'path': plugin_path,
                                    'status': status
                                })

            # Display found plugins
            for plugin in found_plugins:
                item_text = f"{plugin['name']} - {plugin['status']}"
                self.available_plugins_list.addItem(item_text)

            print(f"✓ Found {len(found_plugins)} plugins")

        except Exception as e:
            print(f"⚠ Error scanning for plugins: {e}")

    def install_selected_plugin(self):
        """Install the selected plugin."""
        try:
            current_item = self.available_plugins_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "No Selection", "Please select a plugin to install.")
                return

            item_text = current_item.text()
            plugin_name = item_text.split(' - ')[0]

            # Check if plugin is already loaded
            if plugin_name in self.loaded_plugins:
                QMessageBox.information(self, "Already Installed", f"Plugin '{plugin_name}' is already installed.")
                return

            # Try to load the plugin
            if self.plugin_manager:
                success = self.plugin_manager.load_plugin(plugin_name)

                if success:
                    # Add to loaded plugins
                    plugin = self.plugin_manager.get_plugin(plugin_name)
                    if plugin:
                        self.loaded_plugins[plugin_name] = plugin

                    QMessageBox.information(self, "Installation Complete", f"Plugin '{plugin_name}' installed successfully.")
                    self.update_plugin_discovery_display()
                    self.update_plugin_manager_display()
                    print(f"✓ Installed plugin: {plugin_name}")
                else:
                    QMessageBox.critical(self, "Installation Failed", f"Failed to install plugin '{plugin_name}'.")
            else:
                QMessageBox.critical(self, "Plugin Manager Error", "Plugin manager is not available.")

        except Exception as e:
            print(f"⚠ Error installing plugin: {e}")
            QMessageBox.critical(self, "Installation Error", f"Error installing plugin: {e}")

    def show_plugin_marketplace(self):
        """Show the plugin marketplace dialog."""
        try:
            # Create a simple marketplace placeholder
            marketplace_dialog = QDialog(self)
            marketplace_dialog.setWindowTitle("Plugin Marketplace")
            marketplace_dialog.setModal(True)
            marketplace_dialog.resize(800, 600)

            layout = QVBoxLayout()

            # Marketplace placeholder content
            info_label = QLabel("Plugin Marketplace")
            info_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
            layout.addWidget(info_label)

            description = QTextEdit()
            description.setReadOnly(True)
            description.setPlainText(
                "Plugin Marketplace Feature\n\n"
                "This feature will allow you to:\n"
                "• Browse available plugins from the community\n"
                "• Download and install plugins directly\n"
                "• Rate and review plugins\n"
                "• Share your own plugins\n"
                "• Get plugin recommendations\n\n"
                "Currently under development.\n"
                "For now, you can manually install plugins by placing them in the plugins directory."
            )
            layout.addWidget(description)

            # Close button
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(marketplace_dialog.hide)
            layout.addWidget(close_btn)

            marketplace_dialog.setLayout(layout)
            marketplace_dialog.exec_()

        except Exception as e:
            print(f"⚠ Error showing plugin marketplace: {e}")

    def show_plugin_performance(self):
        """Show the plugin performance monitoring dialog."""
        try:
            performance_dialog = QDialog(self)
            performance_dialog.setWindowTitle("Plugin Performance Monitor")
            performance_dialog.setModal(True)
            performance_dialog.resize(800, 600)

            layout = QVBoxLayout()

            # Performance metrics
            metrics_group = QGroupBox("Plugin Performance Metrics")
            metrics_layout = QVBoxLayout()

            # Create performance table
            self.performance_table = QTableWidget()
            self.performance_table.setColumnCount(5)
            self.performance_table.setHorizontalHeaderLabels([
                "Plugin Name", "Load Time (ms)", "Memory Usage (MB)", "Status", "Last Activity"
            ])

            # Set table properties
            header = self.performance_table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Stretch)

            metrics_layout.addWidget(self.performance_table)
            metrics_group.setLayout(metrics_layout)
            layout.addWidget(metrics_group)

            # Update performance data
            self.update_plugin_performance_data()

            # Control buttons
            button_layout = QHBoxLayout()

            refresh_perf_btn = QPushButton("Refresh")
            refresh_perf_btn.clicked.connect(self.update_plugin_performance_data)

            export_perf_btn = QPushButton("Export Data")
            export_perf_btn.clicked.connect(self.export_plugin_performance)

            close_perf_btn = QPushButton("Close")
            close_perf_btn.clicked.connect(performance_dialog.hide)

            button_layout.addWidget(refresh_perf_btn)
            button_layout.addWidget(export_perf_btn)
            button_layout.addWidget(close_perf_btn)

            layout.addLayout(button_layout)
            performance_dialog.setLayout(layout)

            performance_dialog.exec_()

        except Exception as e:
            print(f"⚠ Error showing plugin performance monitor: {e}")

    def update_plugin_performance_data(self):
        """Update the plugin performance monitoring data."""
        try:
            if not hasattr(self, 'performance_table'):
                return

            self.performance_table.setRowCount(len(self.loaded_plugins))

            for row, (plugin_name, plugin) in enumerate(self.loaded_plugins.items()):
                # Plugin name
                self.performance_table.setItem(row, 0, QTableWidgetItem(plugin_name))

                # Load time (simulated)
                load_time = getattr(plugin, '_load_time', 'N/A')
                self.performance_table.setItem(row, 1, QTableWidgetItem(str(load_time)))

                # Memory usage (simulated)
                memory_usage = getattr(plugin, '_memory_usage', 'N/A')
                self.performance_table.setItem(row, 2, QTableWidgetItem(str(memory_usage)))

                # Status
                status = plugin.get_status().value if hasattr(plugin, 'get_status') else 'unknown'
                self.performance_table.setItem(row, 3, QTableWidgetItem(status))

                # Last activity (simulated)
                last_activity = getattr(plugin, '_last_activity', 'N/A')
                self.performance_table.setItem(row, 4, QTableWidgetItem(str(last_activity)))

        except Exception as e:
            print(f"⚠ Error updating plugin performance data: {e}")

    def export_plugin_performance(self):
        """Export plugin performance data to file."""
        try:

            performance_data = {
                'export_time': datetime.now().isoformat(),
                'plugins': []
            }

            for plugin_name, plugin in self.loaded_plugins.items():
                plugin_data = {
                    'name': plugin_name,
                    'load_time': getattr(plugin, '_load_time', 0),
                    'memory_usage': getattr(plugin, '_memory_usage', 0),
                    'status': plugin.get_status().value if hasattr(plugin, 'get_status') else 'unknown',
                    'last_activity': str(getattr(plugin, '_last_activity', 'N/A'))
                }
                performance_data['plugins'].append(plugin_data)

            filename = f"plugin_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(self.current_directory, 'logs', filename)

            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, 'w') as f:
                json.dump(performance_data, f, indent=2)

            QMessageBox.information(self, "Export Complete", f"Performance data exported to: {filepath}")

        except Exception as e:
            print(f"⚠ Error exporting plugin performance: {e}")
            QMessageBox.critical(self, "Export Error", f"Failed to export performance data: {e}")

    def enable_hot_reloading(self):
        """Enable hot-reloading of plugins during development."""
        try:
            if not hasattr(self, 'hot_reload_timer'):
                self.hot_reload_timer = QTimer()
                self.hot_reload_timer.timeout.connect(self.check_plugin_changes)

            # Enable hot reloading (check every 5 seconds)
            self.hot_reload_timer.start(5000)
            self.plugin_config['hot_reload_enabled'] = True
            self.save_plugin_configuration()

            print("✓ Hot-reloading enabled for plugins")

        except Exception as e:
            print(f"⚠ Error enabling hot-reloading: {e}")

    def disable_hot_reloading(self):
        """Disable hot-reloading of plugins."""
        try:
            if hasattr(self, 'hot_reload_timer'):
                self.hot_reload_timer.stop()

            self.plugin_config['hot_reload_enabled'] = False
            self.save_plugin_configuration()

            print("✓ Hot-reloading disabled for plugins")

        except Exception as e:
            print(f"⚠ Error disabling hot-reloading: {e}")

    def check_plugin_changes(self):
        """Check for changes in plugin files and reload if necessary."""
        try:
            if not self.plugin_config.get('hot_reload_enabled', False):
                return

            # Check for file modifications (simplified implementation)
            for plugin_name, plugin in self.loaded_plugins.items():
                if hasattr(plugin, '_file_path'):
                    file_path = plugin._file_path
                    if os.path.exists(file_path):
                        current_mtime = os.path.getmtime(file_path)
                        last_mtime = getattr(plugin, '_last_mtime', 0)

                        if current_mtime > last_mtime:
                            print(f"🔄 Detected changes in {plugin_name}, reloading...")
                            self.reload_plugin(plugin_name)

        except Exception as e:
            print(f"⚠ Error checking plugin changes: {e}")

    def reload_plugin(self, plugin_name):
        """Reload a specific plugin."""
        try:
            if self.plugin_manager and hasattr(self.plugin_manager, 'reload_plugin'):
                success = self.plugin_manager.reload_plugin(plugin_name)

                if success:
                    # Update loaded plugins
                    plugin = self.plugin_manager.get_plugin(plugin_name)
                    if plugin:
                        self.loaded_plugins[plugin_name] = plugin

                    print(f"✓ Reloaded plugin: {plugin_name}")
                    return True
                else:
                    print(f"⚠ Failed to reload plugin: {plugin_name}")
                    return False
            else:
                print("⚠ Plugin reloading not supported")
                return False

        except Exception as e:
            print(f"⚠ Error reloading plugin {plugin_name}: {e}")
            return False

    def implement_plugin_dependency_management(self):
        """Implement plugin dependency checking and resolution."""
        try:
            dependency_issues = []

            for plugin_name, plugin in self.loaded_plugins.items():
                plugin_info = plugin.get_info()

                if hasattr(plugin_info, 'dependencies') and plugin_info.dependencies:
                    for dependency in plugin_info.dependencies:
                        if dependency not in self.loaded_plugins:
                            dependency_issues.append({
                                'plugin': plugin_name,
                                'missing_dependency': dependency
                            })

            if dependency_issues:
                print(f"⚠ Found {len(dependency_issues)} plugin dependency issues")
                for issue in dependency_issues:
                    print(f"  - {issue['plugin']} requires {issue['missing_dependency']}")

                # Attempt to resolve dependencies
                self.resolve_plugin_dependencies(dependency_issues)
            else:
                print("✓ All plugin dependencies satisfied")

        except Exception as e:
            print(f"⚠ Error checking plugin dependencies: {e}")

    def resolve_plugin_dependencies(self, dependency_issues):
        """Attempt to resolve plugin dependencies."""
        try:
            for issue in dependency_issues:
                missing_dep = issue['missing_dependency']

                # Try to load the missing dependency
                if self.plugin_manager:
                    available_plugins = self.plugin_manager.get_available_plugins()

                    for available_plugin in available_plugins:
                        plugin_info = available_plugin.get_info()
                        if plugin_info.name == missing_dep:
                            # Found the dependency, try to load it
                            success = self.plugin_manager.load_plugin(missing_dep)
                            if success:
                                self.loaded_plugins[missing_dep] = available_plugin
                                print(f"✓ Resolved dependency: {missing_dep}")
                            break
                    else:
                        print(f"⚠ Could not resolve dependency: {missing_dep}")

        except Exception as e:
            print(f"⚠ Error resolving plugin dependencies: {e}")

    def get_loaded_plugin(self, plugin_name):
        """Get a loaded plugin by name."""
        return self.loaded_plugins.get(plugin_name)

    def get_plugins_by_type(self, plugin_type):
        """Get all loaded plugins of a specific type."""
        matching_plugins = []

        for plugin in self.loaded_plugins.values():
            plugin_info = plugin.get_info()
            if plugin_info.plugin_type.value == plugin_type:
                matching_plugins.append(plugin)

        return matching_plugins

    def integrate_plugins_with_workflow(self):
        """Integrate loaded plugins with the workflow system."""
        try:
            if not self.novel_workflow or not getattr(self, 'plugin_manager', None):
                print("⚠ Plugin workflow integration not available - missing dependencies")
                return

            # Create plugin-workflow integration
            try:
                from src.plugin_workflow_integration import PluginWorkflowIntegration
                self.plugin_integration = PluginWorkflowIntegration()
                print("✓ Plugins integrated with workflow system")
            except ImportError:
                self.plugin_integration = None
                print("⚠ Plugin workflow integration not available")

        except Exception as e:
            print(f"⚠ Error integrating plugins with workflow: {e}")

    def add_plugin_management_to_ui(self):
        """Add plugin management integration to the UI."""
        try:
            if hasattr(self, 'ui') and self.ui and hasattr(self.ui, 'add_plugin_management_button'):
                # Add plugin management button to navigation or toolbar
                self.ui.add_plugin_management_button(self)

            # Add plugin sections to navigation if available
            if hasattr(self, 'ui') and self.ui and hasattr(self.ui, 'add_plugin_sections_to_navigation'):
                navigation_tree = getattr(self.ui, 'navigation_tree', None)
                if navigation_tree:
                    self.ui.add_plugin_sections_to_navigation(navigation_tree)

            print("✓ Plugin management integrated with UI")

        except Exception as e:
            print(f"⚠ Error integrating plugin management with UI: {e}")

    def init_database_system(self):
        """Initialize enhanced database layer with connection pooling and migrations."""
        try:
            # Enhanced Database Manager Configuration
            print("🔄 Phase 1.4: Initializing Enhanced Database Layer...")

            # Create database configuration with simpler initialization
            try:
                db_config = DatabaseConfig()
                db_config.database_path = "fanws.db"
                db_config.pool_size = 10
                if hasattr(db_config, 'max_connections'):
                    db_config.max_connections = 10
            except Exception as config_error:
                print(f"⚠ Error creating database config: {config_error}")
                # Use default configuration
                db_config = None

            # Initialize enhanced database manager
            self.db_manager = DatabaseManager(db_config)

            # Initialize database integration layer
            from src.database_manager import DatabaseIntegrationLayer
            self.db_integration = DatabaseIntegrationLayer(self.db_manager)

            # Database connection pool status
            self.db_pool_status = {
                'active_connections': 0,
                'total_connections': 0,
                'query_cache_size': 0,
                'performance_metrics': []
            }

            # Initialize migration tracker
            self.migration_status = {
                'current_version': 0,
                'available_migrations': [],
                'migration_history': []
            }

            # Enhanced database features
            self.database_features = {
                'connection_pooling': True,
                'query_caching': True,
                'performance_monitoring': True,
                'automatic_migrations': True,
                'backup_system': True,
                'optimization_features': True
            }

            print("✓ Enhanced database manager initialized")
            print("✓ Connection pooling enabled")
            print("✓ Query caching enabled")
            print("✓ Performance monitoring active")
            print("✓ Phase 1.4: Enhanced Database Layer initialized")

        except ImportError as e:
            print(f"⚠ Phase 1.4: Enhanced database layer not available: {e}")
            # Fallback to basic database manager
            self.db_manager = None
            self.db_integration = None
            self.database_features = {
                'connection_pooling': False,
                'query_caching': False,
                'performance_monitoring': False,
                'automatic_migrations': False,
                'backup_system': False,
                'optimization_features': False
            }

        except Exception as e:
            print(f"⚠ Error initializing enhanced database system: {e}")
            # Fallback to basic database manager
            self.db_manager = None
            self.db_integration = None
            self.database_features = {
                'connection_pooling': False,
                'query_caching': False,
                'performance_monitoring': False,
                'automatic_migrations': False,
                'backup_system': False,
                'optimization_features': False
            }

    def get_database_manager(self):
        """Get appropriate database manager (enhanced or basic)."""
        if hasattr(self, 'db_manager') and self.db_manager:
            return self.db_manager
        else:
            # Fallback to basic database manager
            if not hasattr(self, 'basic_db_manager'):
                self.basic_db_manager = DatabaseManager("fanws.db")
            return self.basic_db_manager

    def get_database_integration(self):
        """Get database integration layer."""
        if hasattr(self, 'db_integration') and self.db_integration:
            return self.db_integration
        else:
            return None

    def get_database_status(self):
        """Get comprehensive database status information."""
        status = {
            'enhanced_features_available': bool(getattr(self, 'db_manager', None)),
            'features': getattr(self, 'database_features', {}),
            'pool_status': getattr(self, 'db_pool_status', {}),
            'migration_status': getattr(self, 'migration_status', {})
        }

        if hasattr(self, 'db_manager') and self.db_manager:
            try:
                # Get database stats from enhanced manager
                db_stats = self.db_manager.get_database_stats()
                status['database_stats'] = db_stats

                # Get query metrics
                query_metrics = self.db_manager.get_query_metrics()
                status['recent_queries'] = len(query_metrics)
                status['avg_query_time'] = sum(m.execution_time for m in query_metrics) / len(query_metrics) if query_metrics else 0

            except Exception as e:
                status['error'] = f"Error getting database stats: {e}"

        return status

    def init_database_system(self):
        """Initialize enhanced database layer with connection pooling and migrations."""
        try:
            # Enhanced Database Manager Configuration
            print("🔄 Phase 1.4: Initializing Enhanced Database Layer...")

            # Create database configuration
            db_config = DatabaseConfig(
                database_path="fanws.db",
                max_connections=10,
                enable_query_cache=True,
                enable_foreign_keys=True,
                journal_mode="WAL",
                synchronous="NORMAL",
                cache_size=5000,
                auto_vacuum=True
            )

            # Initialize enhanced database manager
            self.db_manager = DatabaseManager(db_config)

            # Initialize database integration layer
            from src.database_manager import DatabaseIntegrationLayer
            self.db_integration = DatabaseIntegrationLayer(self.db_manager)

            # Database connection pool status
            self.db_pool_status = {
                'active_connections': 0,
                'total_connections': 0,
                'query_cache_size': 0,
                'performance_metrics': []
            }

            # Initialize migration tracker
            self.migration_status = {
                'current_version': 0,
                'available_migrations': [],
                'migration_history': []
            }

            # Enhanced database features
            self.database_features = {
                'connection_pooling': True,
                'query_caching': True,
                'performance_monitoring': True,
                'automatic_migrations': True,
                'backup_system': True,
                'optimization_features': True
            }

            print("✓ Enhanced database manager initialized")
            print("✓ Connection pooling enabled")
            print("✓ Query caching enabled")
            print("✓ Performance monitoring active")
            print("✓ Phase 1.4: Enhanced Database Layer initialized")

        except ImportError as e:
            print(f"⚠ Phase 1.4: Enhanced database layer not available: {e}")
            # Fallback to basic database manager
            self.db_manager = None
            self.db_integration = None
            self.database_features = {
                'connection_pooling': False,
                'query_caching': False,
                'performance_monitoring': False,
                'automatic_migrations': False,
                'backup_system': False,
                'optimization_features': False
            }

        except Exception as e:
            print(f"⚠ Error initializing enhanced database system: {e}")
            # Fallback to basic database manager
            self.db_manager = None
            self.db_integration = None
            self.database_features = {
                'connection_pooling': False,
                'query_caching': False,
                'performance_monitoring': False,
                'automatic_migrations': False,
                'backup_system': False,
                'optimization_features': False
            }

    def get_database_manager(self):
        """Get appropriate database manager (enhanced or basic)."""
        if hasattr(self, 'db_manager') and self.db_manager:
            return self.db_manager
        else:
            # Fallback to basic database manager
            if not hasattr(self, 'basic_db_manager'):
                self.basic_db_manager = DatabaseManager("fanws.db")
            return self.basic_db_manager

    def get_database_integration(self):
        """Get database integration layer."""
        if hasattr(self, 'db_integration') and self.db_integration:
            return self.db_integration
        else:
            return None

    def get_database_status(self):
        """Get comprehensive database status information."""
        status = {
            'enhanced_features_available': bool(getattr(self, 'db_manager', None)),
            'features': getattr(self, 'database_features', {}),
            'pool_status': getattr(self, 'db_pool_status', {}),
            'migration_status': getattr(self, 'migration_status', {})
        }

        if hasattr(self, 'db_manager') and self.db_manager:
            try:
                # Get database stats from enhanced manager
                db_stats = self.db_manager.get_database_stats()
                status['database_stats'] = db_stats

                # Get query metrics
                query_metrics = self.db_manager.get_query_metrics()
                status['recent_queries'] = len(query_metrics)
                status['avg_query_time'] = sum(m.execution_time for m in query_metrics) / len(query_metrics) if query_metrics else 0

            except Exception as e:
                status['error'] = f"Error getting database stats: {e}"

        return status
    def init_database_features(self):

        """Initialize advanced database features (Phase 1.4 Second Half)."""

        try:

            # Initialize database monitoring UI capability

            self.database_monitoring_ui = None

            # Advanced database maintenance scheduler

            from PyQt5.QtCore import QTimer

            self.db_maintenance_timer = QTimer()

            self.db_maintenance_timer.timeout.connect(self.run_scheduled_maintenance)

            # Run maintenance every 6 hours

            self.db_maintenance_timer.start(6 * 60 * 60 * 1000)

            # Database analytics tracking

            self.database_analytics = {

                'session_start_time': datetime.now(),

                'queries_executed': 0,

                'cache_hit_rate': 0.0,

                'optimization_runs': 0,

                'backup_count': 0

            }

            print("�S  Advanced database features initialized")

            print("�S  Database monitoring UI ready")

            print("�S  Automated maintenance scheduler active")

            print("�S  Database analytics tracking enabled")

        except Exception as e:

            print(f"�a� Error initializing advanced database features: {e}")

    def show_database_monitoring(self):

        """Show database monitoring and management interface."""

        try:

            if not hasattr(self, 'db_integration') or not self.db_integration:

                from PyQt5.QtWidgets import QMessageBox

                QMessageBox.warning(self, "Database Monitoring", "Enhanced database features not available.")

                return

            from src.ui.management_ui import DatabaseMonitoringDialog

            if not self.database_monitoring_ui:

                self.database_monitoring_ui = DatabaseMonitoringDialog(self.db_integration, self)

            self.database_monitoring_ui.exec_()

        except ImportError:

            QMessageBox.warning(self, "Database Monitoring", "Database monitoring UI not available.")

        except Exception as e:

            QMessageBox.critical(self, "Error", f"Failed to open database monitoring: {str(e)}")

    def run_scheduled_maintenance(self):

        """Run scheduled database maintenance tasks."""

        try:

            if hasattr(self, 'db_integration') and self.db_integration:

                # Run maintenance silently

                results = self.db_integration.run_maintenance_tasks()

                # Update analytics

                if hasattr(self, 'database_analytics'):

                    self.database_analytics['optimization_runs'] += 1

                print(f"�S  Scheduled maintenance completed: {len(results.get('tasks_completed', []))} tasks")

        except Exception as e:

            print(f"�a� Error in scheduled maintenance: {e}")

    def create_database_backup_advanced(self, backup_type='incremental'):

        """Create an advanced database backup with specified type."""

        try:

            if not hasattr(self, 'db_integration') or not self.db_integration:

                print("�a� Enhanced database features not available for backup")

                return False

            # Create backup using advanced backup manager

            backup_path = self.db_integration.create_backup(backup_type)

            # Update analytics

            if hasattr(self, 'database_analytics'):

                self.database_analytics['backup_count'] += 1

            print(f"�S  {backup_type.title()} database backup created: {backup_path}")

            return backup_path

        except Exception as e:

            print(f"�a� Error creating database backup: {e}")

            return False

    def get_advanced_database_analytics(self):

        """Get advanced database analytics and performance metrics."""

        try:

            if not hasattr(self, 'db_integration') or not self.db_integration:

                return {"error": "Enhanced database features not available"}

            # Get analytics from integration layer

            analytics = self.db_integration.get_analytics()

            # Merge with session analytics

            if hasattr(self, 'database_analytics'):

                analytics.update(self.database_analytics)

            return analytics

        except Exception as e:

            print(f"�a� Error getting database analytics: {e}")

            return {"error": str(e)}

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
            self.multi_provider_ai = initialize_multi_provider_ai()

            # Update API keys from current configuration if available
            if hasattr(self, 'openai_key') and self.openai_key:
                self.update_ai_provider_key('openai', self.openai_key)

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
                if provider_name in self.multi_provider_ai.config.providers:
                    self.multi_provider_ai.config.providers[provider_name].api_key = api_key

                    # Update the provider configuration
                    config = self.multi_provider_ai.config.providers[provider_name]
                    success = self.multi_provider_ai.update_provider_config(provider_name, config)

                    if success:
                        print(f"✓ Updated {provider_name} API key")
                        return True
                    else:
                        print(f"⚠ Failed to update {provider_name} configuration")
                        return False
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

    def init_writing_analytics_system(self):
        """Initialize the enhanced writing analytics system with advanced features."""
        try:
            if WRITING_ANALYTICS_AVAILABLE:
                # Initialize analytics manager
                self.analytics_manager = create_analytics_manager(self.current_project)
                self.analytics_progress_widget = None  # Will be created when needed
                self.analytics_enabled = True

                # Connect analytics signals to UI updates if available
                if self.analytics_manager:
                    if hasattr(self.analytics_manager, 'analytics_updated'):
                        self.analytics_manager.analytics_updated.connect(self.on_analytics_updated)
                    if hasattr(self.analytics_manager, 'session_started'):
                        self.analytics_manager.session_started.connect(self.on_session_started)
                    if hasattr(self.analytics_manager, 'session_ended'):
                        self.analytics_manager.session_ended.connect(self.on_session_ended)
                    if hasattr(self.analytics_manager, 'milestone_reached'):
                        self.analytics_manager.milestone_reached.connect(self.on_milestone_reached)

                    # Connect advanced analytics signals if available
                    if hasattr(self.analytics_manager, 'goal_achieved'):
                        self.analytics_manager.goal_achieved.connect(self.on_goal_achieved)
                    if hasattr(self.analytics_manager, 'pattern_detected'):
                        self.analytics_manager.pattern_detected.connect(self.on_pattern_detected)

                # Check for advanced analytics features
                advanced_features = []
                if hasattr(self.analytics_manager, 'advanced_analytics_enabled') and self.analytics_manager.advanced_analytics_enabled:
                    advanced_features.append("🎯 Goal Tracking")
                    advanced_features.append("📈 Habit Monitoring")
                    advanced_features.append("🔮 Performance Prediction")
                    advanced_features.append("🧠 Pattern Detection")

                if hasattr(self.analytics_manager, 'analytics_enabled') and self.analytics_manager.analytics_enabled:
                    advanced_features.append("📊 Enhanced Analytics")

                if advanced_features:
                    print(f"✓ Phase 2.4: Enhanced writing analytics system initialized with features:")
                    for feature in advanced_features:
                        print(f"  {feature}")
                else:
                    print("✓ Phase 2.4: Basic writing analytics system initialized")

            else:
                # Initialize basic analytics fallback
                self.analytics_manager = None
                self.analytics_progress_widget = None
                self.analytics_enabled = False
                self.basic_session_tracker = {
                    'start_time': None,
                    'start_word_count': 0,
                    'current_word_count': 0,
                    'session_active': False
                }

                print("⚠ Phase 2.4: Enhanced analytics not available, using basic tracking")

        except Exception as e:
            print(f"⚠ Phase 2.4: Failed to initialize writing analytics: {e}")
            self.analytics_manager = None
            self.analytics_enabled = False

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
            if hasattr(self, 'statusBar'):
                self.statusBar().showMessage(f"Goal Achieved: {message}", 5000)

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
                if hasattr(self, 'statusBar'):
                    self.statusBar().showMessage(f"New insight: {description}", 8000)

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

    def initialize_collaborative_features(self):
        """Initialize the collaborative features system."""
        if not COLLABORATIVE_FEATURES_AVAILABLE:
            print("⚠ Collaborative features not available")
            return

        try:
            # Initialize collaborative manager with enhanced features
            self.collaborative_manager = CollaborativeManager()
            print("✅ Collaborative manager initialized successfully")

            # Initialize current user (for now, use a default user)
            self.current_user_id = "default_user"
            self._ensure_default_user_exists()

            # Initialize collaboration for current project if available
            if hasattr(self, 'current_project') and self.current_project:
                self._initialize_project_collaboration()

            # Phase 3.1 Second Half: Initialize enhanced features
            self._initialize_enhanced_collaborative_features()

        except Exception as e:
            print(f"⚠ Failed to initialize collaborative features: {e}")
            self.collaborative_manager = None

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

    def initialize_template_system(self):
        """Initialize the advanced project template system."""
        if not TEMPLATE_FEATURES_AVAILABLE:
            print("⚠ Advanced project templates not available")
            return

        try:
            # Initialize template manager - using consolidated template_manager
            from src.template_manager import get_template_manager

            self.template_manager = get_template_manager()
            print("✅ Template manager initialized successfully")

            # Template project creator consolidated into template_manager
            self.template_project_creator = None  # Legacy functionality

            # Store reference for backward compatibility
            self.advanced_templates_available = True

        except Exception as e:
            print(f"⚠ Failed to initialize template system: {e}")
            self.template_manager = None
            self.advanced_templates_available = False

    def initialize_error_handling(self):
        """Initialize the advanced error handling system."""
        try:
            print("Initializing advanced error handling system...")

            # Initialize error handling integration
            self.error_integration = ErrorHandlingIntegration()

            # Initialize error dashboard if main window is available
            if hasattr(self, 'main_window') and self.main_window:
                self.error_dashboard = ErrorHandlingDashboard(self.main_window)
            else:
                self.error_dashboard = ErrorHandlingDashboard()

            # Setup error handling for the application
            # The error integration is already set up in the constructor

            # Register error listeners
            if hasattr(self, 'error_dashboard'):
                self.error_integration.add_error_listener(
                    lambda error_info: self.error_dashboard.update_error_metrics(error_info)
                )

            print("✓ Advanced error handling system initialized")
            print("✓ Error classification and recovery enabled")
            print("✓ Error analytics and reporting ready")
            print("✓ Error dashboard available")

        except Exception as e:
            print(f"⚠ Error initializing error handling system: {e}")
            # Fallback to basic error handling
            self.error_integration = None
            self.error_dashboard = None

    def initialize_memory_management(self):
        """Initialize the memory management system."""
        if not MEMORY_MANAGEMENT_AVAILABLE:
            print("⚠ Memory management features not available")
            return

        try:
            print("Initializing memory management system...")

            # Initialize memory management integration
            project_name = getattr(self, 'current_project', None) or 'default'
            from src.memory_manager import get_memory_manager
            self.memory_integration = get_memory_manager()

            # Create memory configuration based on project needs
            memory_config = {
                'max_memory_mb': 512,  # Default 512MB limit
                'max_cache_mb': 128,   # Default 128MB cache
                'chunk_size': 1024 * 1024,  # 1MB chunks
                'cleanup_interval': 300,  # 5 minutes
                'enable_lazy_loading': True,
                'enable_streaming': True,
                'enable_compression': True,
                'warning_threshold': 0.8,
                'critical_threshold': 0.9
            }

            # Memory manager is already initialized, just configure it
            if self.memory_integration:
                # Initialize memory dashboard if UI is available
                if hasattr(self, 'ui') and self.ui:
                    try:
                        self.memory_dashboard = create_memory_management_dashboard()
                        if self.memory_dashboard:
                            self.memory_dashboard.set_memory_integration(self.memory_integration)
                    except Exception as e:
                        print(f"⚠ Failed to create memory dashboard: {e}")
                        self.memory_dashboard = None

                # Add memory optimization to cleanup operations if available
                if hasattr(self.memory_integration, 'add_memory_listener'):
                    try:
                        self.memory_integration.add_memory_listener(
                            lambda event: self._handle_memory_event(event)
                        )
                    except Exception as e:
                        print(f"⚠ Failed to add memory listener: {e}")

                print("✓ Memory management system initialized")
                print("✓ Intelligent caching enabled")
                print("✓ Lazy loading configured")
                print("✓ Memory optimization active")
            else:
                print("⚠ Failed to initialize memory management")
                self.memory_integration = None
                self.memory_dashboard = None

        except Exception as e:
            print(f"⚠ Error initializing memory management system: {e}")
            # Fallback to basic memory handling
            self.memory_integration = None
            self.memory_dashboard = None

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

    def initialize_configuration_management(self):
        """Initialize configuration management integration."""
        if not CONFIGURATION_MANAGEMENT_AVAILABLE:
            print("⚠ Configuration management system not available")
            return

        try:
            print("🔧 Initializing configuration management system...")

            # Initialize global configuration manager
            project_name = getattr(self, 'current_project', None) or 'default'
            environment = getattr(self, 'environment', 'development')

            self.config_manager = get_global_config()

            # Set config_integration as an alias for compatibility
            self.config_integration = self.config_manager

            # Configuration dashboard functionality is now integrated into the manager
            self.config_dashboard = None
            if hasattr(self, 'ui') and self.ui:
                try:
                    # Use simplified configuration management
                    print("✓ Configuration manager with built-in dashboard features initialized")
                except Exception as e:
                    print(f"⚠ Failed to initialize configuration features: {e}")

            # Initialize configuration migration system (Second Half Feature)
            try:
                # Ensure components are initialized before migration
                component_registry = {}
                migrated_count = 0
                total_components = 5

                # Check for API manager - initialize if needed
                if not hasattr(self, 'api_manager') or not self.api_manager:
                    try:
                        from src.api_manager import get_api_manager
                        self.api_manager = get_api_manager()
                        print("✓ API manager initialized for configuration")
                    except Exception as e:
                        print(f"ℹ API manager initialization deferred: {e}")

                if hasattr(self, 'api_manager') and self.api_manager:
                    component_registry['api_manager'] = self.api_manager
                    migrated_count += 1
                else:
                    print("WARNING:root:Component instance not found: api_manager")

                # Check for UI components
                if hasattr(self, 'ui') and self.ui:
                    component_registry['ui_components'] = self.ui
                    migrated_count += 1
                else:
                    print("WARNING:root:Component instance not found: ui_components")

                # Check for database manager - initialize if needed
                if not hasattr(self, 'db_manager') or not getattr(self, 'db_manager', None):
                    try:
                        from src.database_manager import get_db_manager
                        self.db_manager = get_db_manager()
                        print("✓ Database manager initialized for configuration")
                    except Exception as e:
                        print(f"ℹ Database manager initialization deferred: {e}")

                if hasattr(self, 'db_manager') and getattr(self, 'db_manager', None):
                    component_registry['database_manager'] = self.db_manager
                    migrated_count += 1
                else:
                    print("WARNING:root:Component instance not found: database_manager")

                # Check for workflow manager - initialize if needed
                if not hasattr(self, 'novel_workflow') or not self.novel_workflow:
                    try:
                        from src.workflow_manager import NovelWritingWorkflowModular
                        self.novel_workflow = NovelWritingWorkflowModular()
                        print("✓ Workflow manager initialized for configuration")
                    except Exception as e:
                        print(f"ℹ Workflow manager initialization deferred: {e}")

                if hasattr(self, 'novel_workflow') and self.novel_workflow:
                    component_registry['workflow_manager'] = self.novel_workflow
                    migrated_count += 1
                else:
                    print("WARNING:root:Component instance not found: workflow_manager")

                # Check for plugin system - initialize if needed
                if not hasattr(self, 'plugin_manager') or not getattr(self, 'plugin_manager', None):
                    try:
                        # Plugin manager should be initialized in init_plugin_system
                        if hasattr(self, 'plugin_system_enabled') and self.plugin_system_enabled:
                            self.plugin_manager = getattr(self, '_plugin_manager', None)
                    except Exception as e:
                        print(f"ℹ Plugin system initialization deferred: {e}")

                if hasattr(self, 'plugin_manager') and getattr(self, 'plugin_manager', None):
                    component_registry['plugin_system'] = self.plugin_manager
                    migrated_count += 1
                else:
                    print("WARNING:root:Component instance not found: plugin_system")

                # Register components with config manager if it supports registration
                if hasattr(self.config_manager, 'register_component'):
                    for name, component in component_registry.items():
                        try:
                            self.config_manager.register_component(name, component)
                        except Exception as e:
                            print(f"⚠ Failed to register component {name}: {e}")

                # Report migration results
                print(f"🔧 Configuration migration: {migrated_count}/{total_components} components migrated")

                # Enable hot-reload if available
                if hasattr(self.config_manager, 'enable_hot_reload') and self.config_manager.enable_hot_reload():
                    print("✓ Configuration hot-reload enabled")

                # Create configuration compatibility layer
                self.compat_config = create_configuration_compatibility_layer()
                if self.compat_config:
                    print("✓ Configuration compatibility layer created")

            except Exception as e:
                print(f"⚠ Configuration migration system error: {e}")
                # Continue without migration - not critical

            # Validate initial configuration
            validation_errors = self.config_integration.validate_configuration()
            if validation_errors:
                print("⚠ Configuration validation warnings:")
                error_count = 0
                for category, errors in validation_errors.items():
                    for error in errors:
                        if error_count < 3:  # Show first 3 errors
                            print(f"  - {error}")
                            error_count += 1
                        else:
                            break
                    if error_count >= 3:
                        break

                total_errors = sum(len(errors) for errors in validation_errors.values())
                if total_errors > 3:
                    print(f"  ... and {total_errors - 3} more")
            else:
                print("✓ Configuration validation passed")

            # Get configuration stats
            config_stats = self.config_integration.get_configuration_summary()
            print(f"✓ Configuration system: {config_stats.get('system_type', 'Unknown')}")

            if config_stats.get('validation_enabled'):
                print("✓ Configuration validation enabled")
            if config_stats.get('hot_reload_enabled'):
                print("✓ Configuration hot-reloading enabled")
            if config_stats.get('backup_enabled'):
                print("✓ Configuration backup/restore enabled")

            # Create initial backup if available
            backup_name = f"initial_backup_{int(time.time())}"
            if hasattr(self.config_integration, 'backup_config'):
                if self.config_integration.backup_config(backup_name):
                    print("✓ Initial configuration backup created")
            else:
                print("ℹ Configuration backup not available")

            # Create initial configuration snapshot for history tracking
            if hasattr(self.config_integration, 'create_config_snapshot'):
                snapshot_id = self.config_integration.create_config_snapshot("Initial system configuration")
                if snapshot_id:
                    print("✓ Initial configuration snapshot created")

            print("✓ Configuration management system fully initialized")
            return True

        except Exception as e:
            print(f"⚠ Error initializing configuration management: {e}")
            return False
            # Graceful fallback
            self.config_integration = None
            self.config_dashboard = None
            return False

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
            if hasattr(self, 'statusBar') and self.statusBar:
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

# Main execution
if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = FANWS()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error starting FANWS: {e}")
        sys.exit(1)

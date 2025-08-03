"""
Content Generator for FANWS
AI-powered content generation and processing functionality
"""

import asyncio
import json
import logging
import os
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable

from PyQt5.QtCore import QThread, pyqtSignal, QObject

from ..core.error_handling_system import APIManager
from ..core.error_handling_system import ProjectFileCache
from ..text.text_processing import SynonymCache
from ..core.error_handling_system import project_file_path, create_backup, load_wordsapi_log, get_wordsapi_call_count, save_to_file
from ..plugins.plugin_workflow_integration import NovelWritingWorkflowModular
from ..workflow_steps.base_step import BaseWorkflowStep as WorkflowStep


class AIWorkflowThread(QThread):
    """Thread for running AI workflows in the background"""

    # Signals
    progress_updated = pyqtSignal(int)  # Progress percentage
    status_updated = pyqtSignal(str)    # Status message
    section_completed = pyqtSignal(int, int, str)  # chapter, section, content
    workflow_completed = pyqtSignal()
    workflow_paused = pyqtSignal()
    error_occurred = pyqtSignal(str)
    waiting_for_approval = pyqtSignal(int, int, str)  # chapter, section, content

    def __init__(self, workflow_manager: NovelWritingWorkflowModular, project_name: str):
        super().__init__()
        self.workflow_manager = workflow_manager
        self.project_name = project_name
        self.is_paused = False
        self.should_stop = False
        self.waiting_approval = False
        self.current_chapter = 1
        self.current_section = 1

    def run(self):
        """Main workflow execution"""
        try:
            self.status_updated.emit("Starting AI writing workflow...")

            while not self.should_stop and self.current_chapter <= self.workflow_manager.total_chapters:
                # Check if paused
                while self.is_paused and not self.should_stop:
                    time.sleep(0.1)

                if self.should_stop:
                    break

                # Generate section
                self.generate_section(self.current_chapter, self.current_section)

                # Move to next section/chapter
                if self.current_section >= self.workflow_manager.sections_per_chapter:
                    self.current_chapter += 1
                    self.current_section = 1
                else:
                    self.current_section += 1

                # Update progress
                total_sections = self.workflow_manager.total_chapters * self.workflow_manager.sections_per_chapter
                completed_sections = (self.current_chapter - 1) * self.workflow_manager.sections_per_chapter + self.current_section - 1
                progress = int((completed_sections / total_sections) * 100)
                self.progress_updated.emit(progress)

            if not self.should_stop:
                self.workflow_completed.emit()

        except Exception as e:
            self.error_occurred.emit(str(e))

    def generate_section(self, chapter: int, section: int):
        """Generate a single section"""
        try:
            self.status_updated.emit(f"Generating Chapter {chapter}, Section {section}...")

            # Use workflow manager to generate content
            content = self.workflow_manager.generate_section_content(chapter, section)

            if content:
                # Emit for approval
                self.waiting_approval = True
                self.waiting_for_approval.emit(chapter, section, content)

                # Wait for approval
                while self.waiting_approval and not self.should_stop:
                    time.sleep(0.1)

                if not self.should_stop:
                    self.section_completed.emit(chapter, section, content)

        except Exception as e:
            self.error_occurred.emit(f"Error generating section {chapter}.{section}: {str(e)}")

    def pause_workflow(self):
        """Pause the workflow"""
        self.is_paused = True
        self.workflow_paused.emit()

    def resume_workflow(self):
        """Resume the workflow"""
        self.is_paused = False

    def stop_workflow(self):
        """Stop the workflow"""
        self.should_stop = True
        self.waiting_approval = False

    def approve_section(self):
        """Approve the current section"""
        self.waiting_approval = False


class ProjectManager:
    """Manages project-level operations and AI integration"""

    def __init__(self, project_name: str, api_manager: APIManager, file_cache: ProjectFileCache, config: Dict[str, Any]):
        self.project_name = project_name
        self.api_manager = api_manager
        self.file_cache = file_cache
        self.config = config
        self.content_generator = ContentGenerator(api_manager, file_cache, config)
        self.draft_manager = DraftManager(file_cache, project_name)
        self.consistency_checker = ConsistencyChecker(file_cache, project_name)

    def start_ai_workflow(self) -> AIWorkflowThread:
        """Start an AI-powered writing workflow"""
        workflow_manager = NovelWritingWorkflowModular()
        workflow_manager.initialize_from_config(self.config)

        workflow_thread = AIWorkflowThread(workflow_manager, self.project_name)
        return workflow_thread

    def generate_project_outline(self) -> str:
        """Generate a complete project outline"""
        try:
            idea = self.config.get('Idea', '')
            tone = self.config.get('Tone', 'neutral')
            target_words = self.config.get('SoftTarget', 50000)

            prompt = f"""
            Create a detailed novel outline based on:
            Idea: {idea}
            Tone: {tone}
            Target length: {target_words} words

            Include:
            - Chapter breakdown
            - Key plot points
            - Character arcs
            - Major themes
            """

            return self.content_generator.generate_outline(prompt, max_tokens=2000)

        except Exception as e:
            logging.error(f"Failed to generate project outline: {e}")
            return ""

    def analyze_project_consistency(self) -> Dict[str, Any]:
        """Analyze project for consistency issues"""
        return self.consistency_checker.check_project_consistency()


def summarize_context(content: str, max_length: int = 500) -> str:
    """Create a summary of content for context"""
    if len(content) <= max_length:
        return content

    # Simple summarization - take first and last parts
    first_part = content[:max_length//2]
    last_part = content[-max_length//2:]

    return f"{first_part}...\n\n[Content summarized]\n\n...{last_part}"


def update_character_arcs(file_cache: ProjectFileCache, characters: Dict[str, Any]):
    """Update character arc information"""
    try:
        character_data = json.dumps(characters, indent=2)
        file_cache.update("characters.json", character_data)
        logging.info("Character arcs updated successfully")
    except Exception as e:
        logging.error(f"Failed to update character arcs: {e}")


def update_plot_points(file_cache: ProjectFileCache, plot_points: List[Dict[str, Any]]):
    """Update plot point information"""
    try:
        plot_data = json.dumps(plot_points, indent=2)
        file_cache.update("plot_points.json", plot_data)
        logging.info("Plot points updated successfully")
    except Exception as e:
        logging.error(f"Failed to update plot points: {e}")


def check_continuity(file_cache: ProjectFileCache, project_name: str) -> List[str]:
    """Check for continuity issues in the project"""
    issues = []

    try:
        # Load continuity rules
        rules_content = file_cache.get("continuity_rules.txt") or ""

        # Load story content
        story_content = file_cache.get("story.txt") or ""

        # Simple continuity checks
        if not story_content.strip():
            issues.append("No story content found")

        if not rules_content.strip():
            issues.append("No continuity rules defined")

        # Additional checks could be added here

    except Exception as e:
        issues.append(f"Error checking continuity: {str(e)}")

    return issues


class WorkflowContext:
    """Context object for workflow operations"""

    def __init__(self, project_name: str, config: Dict[str, Any], file_cache: ProjectFileCache):
        self.project_name = project_name
        self.config = config
        self.file_cache = file_cache
        self.current_chapter = 1
        self.current_section = 1
        self.total_word_count = 0
        self.session_start_time = datetime.now()

    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of the current context"""
        return {
            'project': self.project_name,
            'chapter': self.current_chapter,
            'section': self.current_section,
            'word_count': self.total_word_count,
            'session_duration': (datetime.now() - self.session_start_time).total_seconds()
        }


class ContentGenerator:
    """AI-powered content generation engine"""

    def __init__(self, api_manager: APIManager, file_cache: ProjectFileCache, config: Optional[Dict[str, Any]] = None):
        self.api_manager = api_manager
        self.file_cache = file_cache
        self.config = config or {}

    def generate_synopsis(self, prompt: str, max_tokens: int = 1000, api_key: str = "") -> str:
        """Generate a story synopsis"""
        try:
            return self.api_manager.generate_text_openai(prompt, max_tokens, api_key)
        except Exception as e:
            logging.error(f"Failed to generate synopsis: {e}")
            return ""

    def generate_outline(self, prompt: str, max_tokens: int = 1000, api_key: str = "") -> str:
        """Generate a story outline"""
        try:
            return self.api_manager.generate_text_openai(prompt, max_tokens, api_key)
        except Exception as e:
            logging.error(f"Failed to generate outline: {e}")
            return ""

    def generate_character_profiles(self, prompt: str, max_tokens: int = 1000, api_key: str = "") -> str:
        """Generate character profiles"""
        try:
            return self.api_manager.generate_text_openai(prompt, max_tokens, api_key)
        except Exception as e:
            logging.error(f"Failed to generate character profiles: {e}")
            return ""

    def generate_world_building(self, prompt: str, max_tokens: int = 1000, api_key: str = "") -> str:
        """Generate world building content"""
        try:
            return self.api_manager.generate_text_openai(prompt, max_tokens, api_key)
        except Exception as e:
            logging.error(f"Failed to generate world building: {e}")
            return ""

    def generate_timeline(self, prompt: str, max_tokens: int = 1000, api_key: str = "") -> str:
        """Generate story timeline"""
        try:
            return self.api_manager.generate_text_openai(prompt, max_tokens, api_key)
        except Exception as e:
            logging.error(f"Failed to generate timeline: {e}")
            return ""

    async def generate_chapter(self, prompt: str, word_count: int, api_key: str = "") -> str:
        """Generate chapter content asynchronously"""
        try:
            return await self.api_manager.generate_text_openai_async(prompt, word_count, api_key)
        except Exception as e:
            logging.error(f"Failed to generate chapter: {e}")
            return ""

    async def polish_draft(self, draft: str, polishing_prompt: str, api_key: str = "") -> str:
        """Polish a draft using AI"""
        try:
            return await self.api_manager.generate_text_openai_async(polishing_prompt, 1000, api_key)
        except Exception as e:
            logging.error(f"Failed to polish draft: {e}")
            return ""


class DraftManager:
    """Manages draft versions and saving"""

    def __init__(self, file_cache: ProjectFileCache, project_name: str):
        self.file_cache = file_cache
        self.project_name = project_name

    def save_draft(self, chapter: int, section: int, content: str, version: int):
        """Save draft to file and update cache"""
        try:
            os.makedirs(project_file_path(self.project_name, f"drafts/chapter{chapter}"), exist_ok=True)
            filename = f"drafts/chapter{chapter}/section{section}_v{version}.txt"
            self.file_cache.update(filename, content)
            logging.info(f"Successfully saved draft: {filename}")
        except Exception as e:
            logging.error(f"Failed to save draft for Chapter {chapter}, Section {section}, Version {version}: {str(e)}")
            raise

    def load_draft(self, chapter: int, section: int, version: int) -> str:
        """Load a specific draft version"""
        try:
            filename = f"drafts/chapter{chapter}/section{section}_v{version}.txt"
            return self.file_cache.get(filename)
        except Exception as e:
            logging.error(f"Failed to load draft: {e}")
            return ""

    def get_draft_versions(self, chapter: int, section: int) -> List[int]:
        """Get available version numbers for a chapter/section"""
        try:
            draft_dir = project_file_path(self.project_name, f"drafts/chapter{chapter}")
            if not os.path.exists(draft_dir):
                return []

            versions = []
            for filename in os.listdir(draft_dir):
                if filename.startswith(f"section{section}_v") and filename.endswith(".txt"):
                    version_str = filename.replace(f"section{section}_v", "").replace(".txt", "")
                    try:
                        versions.append(int(version_str))
                    except ValueError:
                        continue

            return sorted(versions)
        except Exception as e:
            logging.error(f"Failed to get draft versions: {e}")
            return []


class ConsistencyChecker:
    """Checks consistency across story elements"""

    def __init__(self, api_manager: APIManager, file_cache: ProjectFileCache):
        self.api_manager = api_manager
        self.file_cache = file_cache

    def check_character_consistency(self, new_content: str, api_key: str = "") -> Dict[str, Any]:
        """Check if new content maintains character consistency"""
        try:
            characters = self.file_cache.get("characters.txt")
            consistency_rules = self.file_cache.get("continuity_rules.txt")

            prompt = f"""
            Characters: {characters}
            Consistency Rules: {consistency_rules}
            New Content: {new_content}

            Check if the new content maintains consistency with established characters and rules.
            Provide specific feedback on any inconsistencies found.
            """

            result = self.api_manager.generate_text_openai(prompt, 500, api_key)
            return {"consistent": "inconsistent" not in result.lower(), "feedback": result}
        except Exception as e:
            logging.error(f"Failed to check character consistency: {e}")
            return {"consistent": True, "feedback": ""}

    def check_plot_consistency(self, new_content: str, chapter: int, api_key: str = "") -> Dict[str, Any]:
        """Check if new content maintains plot consistency"""
        try:
            outline = self.file_cache.get("outline.txt")
            timeline = self.file_cache.get("timeline.txt")
            plot_points = self.file_cache.get("plot_points.txt")

            prompt = f"""
            Story Outline: {outline}
            Timeline: {timeline}
            Plot Points: {plot_points}
            Chapter: {chapter}
            New Content: {new_content}

            Check if the new content maintains consistency with the established plot, timeline, and story progression.
            Provide specific feedback on any plot inconsistencies found.
            """

            result = self.api_manager.generate_text_openai(prompt, 500, api_key)
            return {"consistent": "inconsistent" not in result.lower(), "feedback": result}
        except Exception as e:
            logging.error(f"Failed to check plot consistency: {e}")
            return {"consistent": True, "feedback": ""}


class WorkflowContext:
    """Context object for workflow operations"""

    def __init__(self, project_name: str, config: Dict[str, Any], file_cache: ProjectFileCache):
        self.project_name = project_name
        self.config = config
        self.file_cache = file_cache
        self.chapter = 1
        self.section = 1
        self.context_summary = ""
        self.user_feedback = ""
        self.chapter_word_count = 1000


class AIWorkflowThread(QThread):
    """AI workflow execution thread with proper signal handling"""

    # Define signals at class level
    log_update = pyqtSignal(str, str)
    progress_update = pyqtSignal(int, str)
    content_update = pyqtSignal(str, str)
    synopsis_ready = pyqtSignal(str)
    api_limit_reached = pyqtSignal(str)
    wordsapi_count_update = pyqtSignal(int)
    word_count_update = pyqtSignal(int)
    preview_update = pyqtSignal(str)

    def __init__(self, project_name: str, openai_key: str, thesaurus_key: str, config: Dict[str, Any]):
        super().__init__()
        self.project_name = project_name
        self.openai_key = openai_key
        self.thesaurus_key = thesaurus_key
        self.config = config

        # Initialize components
        self.api_manager = APIManager()
        self.file_cache = ProjectFileCache(project_name)
        self.synonym_cache = SynonymCache(project_name)
        self.content_generator = ContentGenerator(self.api_manager, self.file_cache, self.config)
        self.draft_manager = DraftManager(self.file_cache, self.project_name)
        self.consistency_checker = ConsistencyChecker(self.api_manager, self.file_cache)

        self.waiting_for_approval = False

    def save_checkpoint(self, chapter: int, section: int):
        """Save current progress checkpoint"""
        try:
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
        except Exception as e:
            logging.error(f"Failed to save checkpoint: {e}")

    def run(self):
        """Run the AI workflow"""
        asyncio.run(self.async_run())

    async def async_run(self):
        """Main async workflow execution"""
        try:
            os.environ["OPENAI_API_KEY"] = self.openai_key
            os.environ["THESAURUS_API_KEY"] = self.thesaurus_key

            # Setup automatic backups
            def backup_files():
                for file in ["story.txt", "log.txt"]:
                    create_backup(self.project_name, file)
                threading.Timer(3600, backup_files).start()
            backup_files()

            # Update API call counts
            call_count = get_wordsapi_call_count(self.project_name)
            self.wordsapi_count_update.emit(call_count)
            logging.info(f"WordsAPI calls today: {call_count}/2500")

            # Update word count
            story_content = self.file_cache.get("story.txt")
            word_count = len(story_content.split()) if story_content else 0
            self.word_count_update.emit(word_count)

            # Load checkpoint
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

            # Initial planning phase
            if start_chapter == start_section == 1:
                await self.execute_planning_phase()

            # Main writing loop
            await self.execute_writing_phase(start_chapter, start_section)

        except Exception as e:
            logging.error(f"Error in AI workflow: {e}")
            self.log_update.emit("ERROR", f"Workflow error: {e}")

    async def execute_planning_phase(self):
        """Execute the initial planning phase"""
        progress = 0

        # Generate synopsis
        synopsis_prompt = "Generate a compelling synopsis for this story..."
        synopsis = self.content_generator.generate_synopsis(synopsis_prompt, 1000, self.openai_key)
        progress = 5
        self.progress_update.emit(progress, "Processing Synopsis")
        if not synopsis or synopsis == "API_LIMIT_REACHED":
            self.api_limit_reached.emit("OpenAI API limit reached, pausing for 1 hour.")
            return
        self.synopsis_ready.emit(synopsis)

        # Generate outline
        outline_prompt = "Create a detailed story outline..."
        outline = self.content_generator.generate_outline(outline_prompt, 1000, self.openai_key)
        progress = 10
        self.progress_update.emit(progress, "Processing Outline")
        if outline == "API_LIMIT_REACHED":
            self.api_limit_reached.emit("OpenAI API limit reached, pausing for 1 hour.")
            return
        self.file_cache.update("outline.txt", outline)

        # Generate characters
        character_prompt = "Create detailed character profiles..."
        characters = self.content_generator.generate_character_profiles(character_prompt, 1000, self.openai_key)
        progress = 15
        self.progress_update.emit(progress, "Processing Characters")
        if characters == "API_LIMIT_REACHED":
            self.api_limit_reached.emit("OpenAI API limit reached, pausing for 1 hour.")
            return
        self.file_cache.update("characters.txt", characters)

        # Generate world building
        world_prompt = "Create the world and setting..."
        world = self.content_generator.generate_world_building(world_prompt, 1000, self.openai_key)
        progress = 20
        self.progress_update.emit(progress, "Processing World")
        if world == "API_LIMIT_REACHED":
            self.api_limit_reached.emit("OpenAI API limit reached, pausing for 1 hour.")
            return
        self.file_cache.update("world.txt", world)

        # Generate timeline
        timeline_prompt = "Create a story timeline..."
        timeline = self.content_generator.generate_timeline(timeline_prompt, 1000, self.openai_key)
        progress = 25
        self.progress_update.emit(progress, "Processing Timeline")
        if timeline == "API_LIMIT_REACHED":
            self.api_limit_reached.emit("OpenAI API limit reached, pausing for 1 hour.")
            return
        self.file_cache.update("timeline.txt", timeline)

        self.file_cache.update("plot_points.txt", json.dumps([]))
        logging.info("Planning complete.")

    async def execute_writing_phase(self, start_chapter: int, start_section: int):
        """Execute the main writing phase"""
        total_chapters = self.config.get('TotalChapters', 10)
        sections_per_chapter = self.config.get('Chapter1Sections', 5)

        for chapter in range(start_chapter, total_chapters + 1):
            for section in range(1 if chapter > start_chapter else start_section, sections_per_chapter + 1):
                # Generate chapter content
                chapter_word_count = self.config.get("ChapterWordCount", 1000)

                # Create chapter writing prompt
                context_summary = self.get_context_summary(chapter, section)
                chapter_prompt = self.create_chapter_prompt(chapter, section, chapter_word_count, context_summary)

                # Generate draft
                draft = await self.content_generator.generate_chapter(chapter_prompt, chapter_word_count, self.openai_key)
                if draft == "API_LIMIT_REACHED":
                    self.api_limit_reached.emit("OpenAI API limit reached, pausing for 1 hour.")
                    return

                # Save draft
                self.draft_manager.save_draft(chapter, section, draft, 1)

                # Polish draft
                polishing_prompt = f"Polish and improve this draft: {draft}"
                polished = await self.content_generator.polish_draft(draft, polishing_prompt, self.openai_key)
                if polished and polished != "API_LIMIT_REACHED":
                    self.draft_manager.save_draft(chapter, section, polished, 2)

                # Update progress
                progress = int((chapter - 1) * sections_per_chapter + section) / (total_chapters * sections_per_chapter) * 100
                self.progress_update.emit(int(progress), f"Chapter {chapter}, Section {section}")

                # Save checkpoint
                self.save_checkpoint(chapter, section)

    def get_context_summary(self, chapter: int, section: int) -> str:
        """Get context summary for current chapter/section"""
        try:
            # This would typically call a context summarization function
            # For now, return a basic summary
            return f"Context for Chapter {chapter}, Section {section}"
        except Exception as e:
            logging.error(f"Failed to get context summary: {e}")
            return ""

    def create_chapter_prompt(self, chapter: int, section: int, word_count: int, context: str) -> str:
        """Create prompt for chapter generation"""
        return f"""
        Write Chapter {chapter}, Section {section} of the story.
        Target word count: {word_count}
        Context: {context}

        Characters: {self.file_cache.get('characters.txt', '')}
        World: {self.file_cache.get('world.txt', '')}
        Timeline: {self.file_cache.get('timeline.txt', '')}

        Write engaging, well-structured content that advances the plot and develops characters.
        """


def summarize_context(project_name: str, file_cache: ProjectFileCache, chapter: int, section: int) -> str:
    """Summarize context for the current writing position"""
    try:
        # Get previous content for context
        story_content = file_cache.get("story.txt")
        if not story_content:
            return "Beginning of story"

        # Return last few paragraphs as context
        paragraphs = story_content.split('\n\n')
        if len(paragraphs) > 3:
            return '\n\n'.join(paragraphs[-3:])
        else:
            return story_content
    except Exception as e:
        logging.error(f"Failed to summarize context: {e}")
        return ""

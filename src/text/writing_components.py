"""
Writing components module for FANWS application.
Contains specialized writing tools and components for creative writing.
"""

import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
try:
    from .text_processing import get_text_analyzer, get_synonym_cache
    from .text_processing import DatabaseManager
    from ..core.utils import count_words, count_characters, count_sentences, count_paragraphs
    from ..templates.template_manager import get_template_manager, WorkflowPromptType, WorkflowContext
except ImportError:
    # Fallback for direct execution
    try:
        from .text_processing import get_text_analyzer, get_synonym_cache
        from ..database.database_manager import DatabaseManager
        from ..core.utils import count_words, count_characters, count_sentences, count_paragraphs
        from ..templates.template_manager import get_template_manager, WorkflowPromptType, WorkflowContext
    except ImportError:
        # Create mock functions for testing
        def get_text_analyzer():
            return None

        def get_synonym_cache():
            return {}

        def count_words(text):
            return len(text.split())

        def get_template_manager():
            return None

        # Mock enums for testing
        class WorkflowPromptType:
            SYNOPSIS_GENERATION = "synopsis_generation"
            CHARACTER_PROFILES = "character_profiles"
            WORLD_BUILDING = "world_building"

        class WorkflowContext:
            pass

        def count_characters(text):
            return len(text)

        def count_sentences(text):
            return text.count('.') + text.count('!') + text.count('?')

        def count_paragraphs(text):
            return len([p for p in text.split('\n\n') if p.strip()])

        # Mock DatabaseManager
        class DatabaseManager:
            def __init__(self, db_path=None):
                pass

class WritingStats:
    """Calculate and track writing statistics."""

    def __init__(self):
        """Initialize writing statistics tracker."""
        self.session_start_time = datetime.now()
        self.session_word_count = 0
        self.total_words_written = 0
        self.daily_goals = {}
        self.writing_streaks = {}

    def update_stats(self, text: str, previous_text: str = "") -> Dict[str, Any]:
        """Update writing statistics."""
        current_words = count_words(text)
        previous_words = count_words(previous_text)

        words_added = current_words - previous_words
        if words_added > 0:
            self.session_word_count += words_added
            self.total_words_written += words_added

        stats = {
            'word_count': current_words,
            'character_count': count_characters(text, include_spaces=True),
            'character_count_no_spaces': count_characters(text, include_spaces=False),
            'sentence_count': count_sentences(text),
            'paragraph_count': count_paragraphs(text),
            'session_words': self.session_word_count,
            'session_duration': (datetime.now() - self.session_start_time).total_seconds(),
            'words_per_minute': self._calculate_wpm(),
            'pages_estimated': current_words / 250,  # Assuming 250 words per page
            'reading_time_minutes': current_words / 200  # Assuming 200 WPM reading speed
        }

        return stats

    def _calculate_wpm(self) -> float:
        """Calculate words per minute for current session."""
        session_duration = (datetime.now() - self.session_start_time).total_seconds()
        if session_duration > 0:
            return (self.session_word_count / session_duration) * 60
        return 0.0

    def set_daily_goal(self, words: int):
        """Set daily writing goal."""
        today = datetime.now().date()
        self.daily_goals[today] = words

    def get_daily_progress(self) -> Dict[str, Any]:
        """Get today's writing progress."""
        today = datetime.now().date()
        goal = self.daily_goals.get(today, 0)

        return {
            'goal': goal,
            'written': self.session_word_count,
            'percentage': (self.session_word_count / goal * 100) if goal > 0 else 0,
            'remaining': max(0, goal - self.session_word_count)
        }

class CharacterTracker:
    """Track characters and their development."""

    def __init__(self):
        """Initialize character tracker."""
        self.characters = {}
        self.character_arcs = {}
        self.relationships = {}

    def add_character(self, name: str, description: str = "",
                     traits: List[str] = None, background: str = ""):
        """Add a new character."""
        self.characters[name] = {
            'name': name,
            'description': description,
            'traits': traits or [],
            'background': background,
            'first_appearance': None,
            'last_appearance': None,
            'appearance_count': 0,
            'created_date': datetime.now().isoformat()
        }

        logging.info(f"Added character: {name}")

    def update_character(self, name: str, **kwargs):
        """Update character information."""
        if name in self.characters:
            self.characters[name].update(kwargs)
            logging.info(f"Updated character: {name}")

    def track_character_appearance(self, name: str, chapter: str, context: str = ""):
        """Track character appearance in text."""
        if name not in self.characters:
            self.add_character(name)

        character = self.characters[name]
        character['appearance_count'] += 1
        character['last_appearance'] = chapter

        if character['first_appearance'] is None:
            character['first_appearance'] = chapter

    def find_characters_in_text(self, text: str) -> List[str]:
        """Find mentioned characters in text."""
        mentioned_characters = []

        for name in self.characters.keys():
            if name.lower() in text.lower():
                mentioned_characters.append(name)

        return mentioned_characters

    def get_character_summary(self, name: str) -> Dict[str, Any]:
        """Get character summary."""
        if name not in self.characters:
            return {}

        character = self.characters[name]
        return {
            'name': name,
            'description': character.get('description', ''),
            'traits': character.get('traits', []),
            'background': character.get('background', ''),
            'appearances': character.get('appearance_count', 0),
            'first_seen': character.get('first_appearance'),
            'last_seen': character.get('last_appearance'),
            'arc_progress': self.character_arcs.get(name, {})
        }

    def get_all_characters(self) -> List[Dict[str, Any]]:
        """Get all characters with their summaries."""
        return [self.get_character_summary(name) for name in self.characters.keys()]

class PlotTracker:
    """Track plot points and story structure."""

    def __init__(self):
        """Initialize plot tracker."""
        self.plot_points = []
        self.story_arcs = {}
        self.themes = []
        self.conflicts = []

    def add_plot_point(self, title: str, description: str, chapter: str = "",
                      importance: str = "medium", status: str = "planned"):
        """Add a plot point."""
        plot_point = {
            'id': len(self.plot_points) + 1,
            'title': title,
            'description': description,
            'chapter': chapter,
            'importance': importance,  # low, medium, high, critical
            'status': status,  # planned, in_progress, completed, abandoned
            'created_date': datetime.now().isoformat(),
            'updated_date': datetime.now().isoformat()
        }

        self.plot_points.append(plot_point)
        logging.info(f"Added plot point: {title}")

        return plot_point['id']

    def update_plot_point(self, plot_id: int, **kwargs):
        """Update plot point."""
        for plot_point in self.plot_points:
            if plot_point['id'] == plot_id:
                plot_point.update(kwargs)
                plot_point['updated_date'] = datetime.now().isoformat()
                logging.info(f"Updated plot point: {plot_point['title']}")
                return True
        return False

    def get_plot_points_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get plot points by status."""
        return [pp for pp in self.plot_points if pp['status'] == status]

    def get_plot_points_by_importance(self, importance: str) -> List[Dict[str, Any]]:
        """Get plot points by importance."""
        return [pp for pp in self.plot_points if pp['importance'] == importance]

    def analyze_story_structure(self) -> Dict[str, Any]:
        """Analyze story structure."""
        total_points = len(self.plot_points)
        completed_points = len(self.get_plot_points_by_status('completed'))

        # Analyze by importance
        critical_points = len(self.get_plot_points_by_importance('critical'))
        high_points = len(self.get_plot_points_by_importance('high'))
        medium_points = len(self.get_plot_points_by_importance('medium'))
        low_points = len(self.get_plot_points_by_importance('low'))

        return {
            'total_plot_points': total_points,
            'completed_plot_points': completed_points,
            'completion_percentage': (completed_points / total_points * 100) if total_points > 0 else 0,
            'critical_points': critical_points,
            'high_importance_points': high_points,
            'medium_importance_points': medium_points,
            'low_importance_points': low_points,
            'story_arcs': len(self.story_arcs),
            'themes': len(self.themes),
            'conflicts': len(self.conflicts)
        }

class WritingPromptGenerator:
    """Generate writing prompts and suggestions."""

    def __init__(self):
        """Initialize writing prompt generator."""
        self.prompt_templates = {
            'character': [
                "Write about a character who discovers they have {trait}.",
                "Describe a character whose greatest fear is {fear}.",
                "Create a character who must choose between {choice1} and {choice2}.",
                "Write about someone who has been keeping {secret} for years."
            ],
            'setting': [
                "Describe a scene taking place in {location} during {time}.",
                "Write about a world where {condition} is the norm.",
                "Create a setting where {element} is forbidden.",
                "Describe a place that can only be reached by {method}."
            ],
            'conflict': [
                "Write about a conflict between {party1} and {party2} over {object}.",
                "Describe a situation where {character} must overcome {obstacle}.",
                "Create a scene where {event} threatens to destroy {thing}.",
                "Write about a character torn between {loyalty1} and {loyalty2}."
            ],
            'theme': [
                "Explore the theme of {theme} through a story about {situation}.",
                "Write about how {concept} affects {character_type}.",
                "Create a story that examines {philosophical_question}.",
                "Explore the relationship between {element1} and {element2}."
            ]
        }

        self.prompt_elements = {
            'trait': ['telepathy', 'immortality', 'the ability to see the future', 'perfect memory', 'invisibility'],
            'fear': ['being forgotten', 'losing control', 'being alone', 'making the wrong choice', 'disappointing others'],
            'choice1': ['love', 'power', 'truth', 'freedom', 'family'],
            'choice2': ['duty', 'safety', 'peace', 'success', 'revenge'],
            'secret': ['a hidden identity', 'a terrible mistake', 'a forbidden love', 'a dangerous ability', 'a family curse'],
            'location': ['an abandoned space station', 'a floating city', 'an underground library', 'a parallel dimension', 'a time loop'],
            'time': ['the last day of the world', 'a century in the future', 'the moment before everything changed', 'a single heartbeat', 'eternity'],
            'condition': ['magic is real but hidden', 'memories can be traded', 'death is temporary', 'emotions have colors', 'time moves backwards'],
            'element': ['music', 'laughter', 'dreams', 'mirrors', 'shadows'],
            'method': ['solving a riddle', 'making a sacrifice', 'telling a truth', 'facing a fear', 'letting go'],
            'party1': ['the past', 'tradition', 'the individual', 'nature', 'the heart'],
            'party2': ['the future', 'progress', 'society', 'technology', 'the mind'],
            'object': ['a single word', 'a forgotten promise', 'the last remaining hope', 'a dangerous secret', 'the right to choose'],
            'character': ['a hero', 'a villain', 'an ordinary person', 'a child', 'an elder'],
            'obstacle': ['their own fears', 'a powerful enemy', 'a moral dilemma', 'a physical challenge', 'a time limit'],
            'event': ['a natural disaster', 'a betrayal', 'a discovery', 'a reunion', 'a revelation'],
            'thing': ['a relationship', 'a community', 'a way of life', 'a belief system', 'a world'],
            'loyalty1': ['family', 'friends', 'country', 'principles', 'the past'],
            'loyalty2': ['duty', 'love', 'justice', 'survival', 'the future'],
            'theme': ['redemption', 'sacrifice', 'identity', 'belonging', 'transformation'],
            'situation': ['a reunion', 'a journey', 'a competition', 'a crisis', 'a discovery'],
            'concept': ['technology', 'isolation', 'power', 'change', 'tradition'],
            'character_type': ['leaders', 'outcasts', 'families', 'communities', 'individuals'],
            'philosophical_question': ['what makes us human', 'the nature of reality', 'the meaning of success', 'the price of knowledge', 'the value of truth'],
            'element1': ['tradition', 'innovation', 'individual', 'collective', 'natural'],
            'element2': ['change', 'stability', 'freedom', 'security', 'artificial']
        }

    def generate_prompt(self, category: str = None) -> str:
        """Generate a writing prompt."""
        import random

        if category is None:
            category = random.choice(list(self.prompt_templates.keys()))

        if category not in self.prompt_templates:
            return "Write about something that matters to you."

        template = random.choice(self.prompt_templates[category])

        # Replace placeholders with random elements
        import re
        placeholders = re.findall(r'\{(\w+)\}', template)

        for placeholder in placeholders:
            if placeholder in self.prompt_elements:
                replacement = random.choice(self.prompt_elements[placeholder])
                template = template.replace(f'{{{placeholder}}}', replacement)

        return template

    def generate_multiple_prompts(self, count: int = 5, category: str = None) -> List[str]:
        """Generate multiple writing prompts."""
        prompts = []
        for _ in range(count):
            prompts.append(self.generate_prompt(category))
        return prompts

class WritingTimer:
    """Timer for writing sessions and productivity tracking."""

    def __init__(self):
        """Initialize writing timer."""
        self.session_start = None
        self.session_end = None
        self.is_active = False
        self.total_time = 0
        self.break_time = 0
        self.pomodoro_count = 0
        self.session_history = []

    def start_session(self):
        """Start a writing session."""
        self.session_start = datetime.now()
        self.is_active = True
        logging.info("Writing session started")

    def end_session(self):
        """End a writing session."""
        if self.is_active and self.session_start:
            self.session_end = datetime.now()
            session_duration = (self.session_end - self.session_start).total_seconds()
            self.total_time += session_duration
            self.is_active = False

            # Record session
            self.session_history.append({
                'start': self.session_start.isoformat(),
                'end': self.session_end.isoformat(),
                'duration': session_duration,
                'words_written': 0  # This would be updated externally
            })

            logging.info(f"Writing session ended. Duration: {session_duration:.0f} seconds")
            return session_duration
        return 0

    def get_session_duration(self) -> float:
        """Get current session duration in seconds."""
        if self.is_active and self.session_start:
            return (datetime.now() - self.session_start).total_seconds()
        return 0

    def get_formatted_time(self, seconds: float) -> str:
        """Format time duration."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

    def get_productivity_stats(self) -> Dict[str, Any]:
        """Get productivity statistics."""
        total_sessions = len(self.session_history)
        if total_sessions == 0:
            return {
                'total_sessions': 0,
                'total_time': 0,
                'average_session_time': 0,
                'longest_session': 0,
                'shortest_session': 0
            }

        session_durations = [s['duration'] for s in self.session_history]

        return {
            'total_sessions': total_sessions,
            'total_time': self.total_time,
            'average_session_time': sum(session_durations) / len(session_durations),
            'longest_session': max(session_durations),
            'shortest_session': min(session_durations),
            'current_session_duration': self.get_session_duration(),
            'is_active': self.is_active
        }

class WritingGoals:
    """Manage writing goals and progress tracking."""

    def __init__(self):
        """Initialize writing goals manager."""
        self.goals = {}
        self.achievements = []

    def set_goal(self, goal_type: str, target: int, deadline: str = None,
                description: str = ""):
        """Set a writing goal."""
        goal_id = len(self.goals) + 1
        self.goals[goal_id] = {
            'id': goal_id,
            'type': goal_type,  # daily, weekly, monthly, project, custom
            'target': target,
            'current': 0,
            'deadline': deadline,
            'description': description,
            'created_date': datetime.now().isoformat(),
            'status': 'active'  # active, completed, paused, abandoned
        }

        logging.info(f"Set {goal_type} goal: {target}")
        return goal_id

    def update_progress(self, goal_id: int, progress: int):
        """Update goal progress."""
        if goal_id in self.goals:
            goal = self.goals[goal_id]
            goal['current'] = progress

            # Check if goal is completed
            if progress >= goal['target']:
                goal['status'] = 'completed'
                self.achievements.append({
                    'goal_id': goal_id,
                    'goal_type': goal['type'],
                    'target': goal['target'],
                    'completed_date': datetime.now().isoformat(),
                    'description': goal['description']
                })
                logging.info(f"Goal completed: {goal['description']}")

            return True
        return False

    def get_active_goals(self) -> List[Dict[str, Any]]:
        """Get all active goals."""
        return [goal for goal in self.goals.values() if goal['status'] == 'active']

    def get_goal_progress(self, goal_id: int) -> Dict[str, Any]:
        """Get progress for a specific goal."""
        if goal_id not in self.goals:
            return {}

        goal = self.goals[goal_id]
        progress_percentage = (goal['current'] / goal['target'] * 100) if goal['target'] > 0 else 0

        return {
            'goal_id': goal_id,
            'type': goal['type'],
            'target': goal['target'],
            'current': goal['current'],
            'remaining': max(0, goal['target'] - goal['current']),
            'progress_percentage': progress_percentage,
            'status': goal['status'],
            'deadline': goal['deadline'],
            'description': goal['description']
        }

    def get_all_achievements(self) -> List[Dict[str, Any]]:
        """Get all achievements."""
        return self.achievements

class ContentGenerator:
    """Generate various types of content for novel writing."""

    def __init__(self, api_manager, file_cache, config):
        """Initialize content generator with required dependencies."""
        self.api_manager = api_manager
        self.file_cache = file_cache
        self.config = config

    def generate_synopsis(self, idea: str, tone: str = "neutral", length: str = "medium") -> str:
        """Generate a synopsis based on the given idea."""
        try:
            # Use dynamic prompt template
            prompt_manager = get_template_manager()
            if prompt_manager:
                # Create a minimal workflow context for standalone generation
                context = type('WorkflowContext', (), {
                    'idea': idea,
                    'tone': tone,
                    'length': length,
                    'project_name': '',
                    'config': {},
                    'file_cache': self.file_cache
                })()

                prompt = prompt_manager.generate_workflow_prompt(
                    WorkflowPromptType.STANDALONE_SYNOPSIS,
                    context
                )
            else:
                # Fallback to hardcoded prompt
                prompt = f"Create a {length} synopsis for a novel with the following idea: {idea}. The tone should be {tone}. Include main characters, plot outline, and key themes."

            response = self.api_manager.generate_text(prompt)
            if response:
                return response
            else:
                return f"Synopsis for: {idea}\n\nThis story explores themes of {tone} narrative with compelling characters and plot development."
        except Exception as e:
            logging.error(f"Failed to generate synopsis: {str(e)}")
            return f"Error generating synopsis: {str(e)}"

    def generate_character_profile(self, character_name: str, role: str = "main character") -> str:
        """Generate a detailed character profile."""
        try:
            # Use dynamic prompt template
            prompt_manager = get_template_manager()
            if prompt_manager:
                # Create a minimal workflow context for standalone generation
                context = type('WorkflowContext', (), {
                    'character_name': character_name,
                    'role': role,
                    'project_name': '',
                    'config': {},
                    'file_cache': self.file_cache
                })()

                prompt = prompt_manager.generate_workflow_prompt(
                    WorkflowPromptType.STANDALONE_CHARACTER,
                    context
                )
            else:
                # Fallback to hardcoded prompt
                prompt = f"Create a detailed character profile for {character_name}, who is a {role}. Include personality traits, background, motivations, and character arc potential."

            response = self.api_manager.generate_text(prompt)
            if response:
                return response
            else:
                return f"Character Profile: {character_name}\n\nRole: {role}\nPersonality: [To be developed]\nBackground: [To be developed]\nMotivations: [To be developed]"
        except Exception as e:
            logging.error(f"Failed to generate character profile: {str(e)}")
            return f"Error generating character profile: {str(e)}"

    def generate_world_building(self, setting: str, genre: str = "fiction") -> str:
        """Generate world-building content."""
        try:
            # Use dynamic prompt template
            prompt_manager = get_template_manager()
            if prompt_manager:
                # Create a minimal workflow context for standalone generation
                context = type('WorkflowContext', (), {
                    'setting': setting,
                    'genre': genre,
                    'project_name': '',
                    'config': {},
                    'file_cache': self.file_cache
                })()

                prompt = prompt_manager.generate_workflow_prompt(
                    WorkflowPromptType.STANDALONE_WORLD,
                    context
                )
            else:
                # Fallback to hardcoded prompt
                prompt = f"Create detailed world-building content for a {genre} story set in {setting}. Include geography, culture, history, and key locations."

            response = self.api_manager.generate_text(prompt)
            if response:
                return response
            else:
                return f"World Building: {setting}\n\nGenre: {genre}\nGeography: [To be developed]\nCulture: [To be developed]\nHistory: [To be developed]"
        except Exception as e:
            logging.error(f"Failed to generate world building: {str(e)}")
            return f"Error generating world building: {str(e)}"

class DraftManager:
    """Manage draft versions and revisions."""

    def __init__(self, file_cache):
        """Initialize draft manager with file cache."""
        self.file_cache = file_cache
        self.draft_versions = {}

    def save_draft(self, chapter: int, section: int, content: str, version: int = 1) -> bool:
        """Save a draft version."""
        try:
            filename = f"drafts/chapter{chapter}/section{section}_v{version}.txt"
            self.file_cache.update(filename, content)

            # Track version
            key = f"ch{chapter}_s{section}"
            if key not in self.draft_versions:
                self.draft_versions[key] = []
            self.draft_versions[key].append(version)

            return True
        except Exception as e:
            logging.error(f"Failed to save draft: {str(e)}")
            return False

    def load_draft(self, chapter: int, section: int, version: int = 1) -> Optional[str]:
        """Load a specific draft version."""
        try:
            filename = f"drafts/chapter{chapter}/section{section}_v{version}.txt"
            return self.file_cache.get(filename)
        except Exception as e:
            logging.error(f"Failed to load draft: {str(e)}")
            return None

    def get_draft_versions(self, chapter: int, section: int) -> List[int]:
        """Get all available versions for a chapter/section."""
        key = f"ch{chapter}_s{section}"
        return self.draft_versions.get(key, [])

    def compare_drafts(self, chapter: int, section: int, version1: int, version2: int) -> Dict[str, Any]:
        """Compare two draft versions."""
        try:
            draft1 = self.load_draft(chapter, section, version1)
            draft2 = self.load_draft(chapter, section, version2)

            if not draft1 or not draft2:
                return {"error": "One or both drafts not found"}

            # Simple comparison
            words1 = len(draft1.split())
            words2 = len(draft2.split())

            return {
                "version1_words": words1,
                "version2_words": words2,
                "word_difference": words2 - words1,
                "version1_length": len(draft1),
                "version2_length": len(draft2)
            }
        except Exception as e:
            return {"error": str(e)}

class ConsistencyChecker:
    """Check consistency across the novel."""

    def __init__(self, file_cache):
        """Initialize consistency checker with file cache."""
        self.file_cache = file_cache
        self.character_names = set()
        self.location_names = set()
        self.timeline_events = []

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract characters, locations, and other entities from text."""
        entities = {
            "characters": [],
            "locations": [],
            "objects": []
        }

        try:
            # Simple regex-based entity extraction
            # This could be enhanced with NLP libraries

            # Look for capitalized words that might be names
            words = text.split()
            for word in words:
                if word.istitle() and len(word) > 2:
                    # Simple heuristic: if it appears multiple times, it's likely a name
                    if text.count(word) > 1:
                        entities["characters"].append(word)

            # Remove duplicates
            entities["characters"] = list(set(entities["characters"]))

            return entities
        except Exception as e:
            logging.error(f"Failed to extract entities: {str(e)}")
            return entities

    def check_character_consistency(self, story_content: str) -> List[str]:
        """Check for character name consistency issues."""
        issues = []

        try:
            entities = self.extract_entities(story_content)
            characters = entities["characters"]

            # Check for similar names that might be typos
            for i, char1 in enumerate(characters):
                for char2 in characters[i+1:]:
                    if self._are_similar_names(char1, char2):
                        issues.append(f"Similar character names detected: '{char1}' and '{char2}' - possible typo?")

            return issues
        except Exception as e:
            logging.error(f"Failed to check character consistency: {str(e)}")
            return [f"Error checking consistency: {str(e)}"]

    def _are_similar_names(self, name1: str, name2: str) -> bool:
        """Check if two names are similar (possible typos)."""
        # Simple similarity check based on edit distance
        if abs(len(name1) - len(name2)) > 2:
            return False

        # Count different characters
        differences = 0
        for i in range(min(len(name1), len(name2))):
            if name1[i] != name2[i]:
                differences += 1

        return differences <= 2

class ProjectManager:
    """Manage project-level operations and coordination."""

    def __init__(self, project_name: str, api_manager, file_cache, config):
        """Initialize project manager with required dependencies."""
        self.project_name = project_name
        self.api_manager = api_manager
        self.file_cache = file_cache
        self.config = config
        self.content_generator = ContentGenerator(api_manager, file_cache, config)
        self.draft_manager = DraftManager(file_cache)
        self.consistency_checker = ConsistencyChecker(file_cache)

    def get_project_status(self) -> Dict[str, Any]:
        """Get comprehensive project status."""
        try:
            story_content = self.file_cache.get("story.txt") or ""
            synopsis_content = self.file_cache.get("synopsis.txt") or ""
            characters_content = self.file_cache.get("characters.txt") or ""
            world_content = self.file_cache.get("world.txt") or ""

            status = {
                "has_story": bool(story_content.strip()),
                "has_synopsis": bool(synopsis_content.strip()),
                "has_characters": bool(characters_content.strip()),
                "has_world": bool(world_content.strip()),
                "word_count": len(story_content.split()) if story_content else 0,
                "target_words": self.config.get("SoftTarget", 250000),
                "completion_percentage": 0
            }

            if status["target_words"] > 0:
                status["completion_percentage"] = min(100, (status["word_count"] / status["target_words"]) * 100)

            return status
        except Exception as e:
            logging.error(f"Failed to get project status: {str(e)}")
            return {"error": str(e)}

    def initialize_project(self, project_settings: Dict[str, Any]) -> bool:
        """Initialize a new project with basic content."""
        try:
            # Generate synopsis if not exists
            if not self.file_cache.get("synopsis.txt"):
                synopsis = self.content_generator.generate_synopsis(
                    project_settings.get("synopsis_prompt", "A compelling story"),
                    self.config.get("Tone", "neutral")
                )
                self.file_cache.update("synopsis.txt", synopsis)

            # Generate character profiles if character seed is provided
            characters_seed = project_settings.get("characters_seed", "")
            if characters_seed and not self.file_cache.get("characters.txt"):
                characters = self.content_generator.generate_character_profile(
                    "Main Character", "protagonist"
                )
                self.file_cache.update("characters.txt", characters)

            # Generate world building if world seed is provided
            world_seed = project_settings.get("world_seed", "")
            if world_seed and not self.file_cache.get("world.txt"):
                world = self.content_generator.generate_world_building(
                    world_seed, "fiction"
                )
                self.file_cache.update("world.txt", world)

            # Initialize story file if it doesn't exist
            if not self.file_cache.get("story.txt"):
                self.file_cache.update("story.txt", "")

            return True
        except Exception as e:
            logging.error(f"Failed to initialize project: {str(e)}")
            return False

    def cleanup_project(self):
        """Clean up project resources."""
        try:
            # Save any pending changes
            if hasattr(self.file_cache, 'save_pending'):
                self.file_cache.save_pending()

            logging.info(f"Project '{self.project_name}' cleaned up successfully")
        except Exception as e:
            logging.error(f"Failed to cleanup project: {str(e)}")

# Global instances
_writing_stats = None
_character_tracker = None
_plot_tracker = None
_prompt_generator = None
_writing_timer = None
_writing_goals = None

def get_writing_stats() -> WritingStats:
    """Get global writing statistics instance."""
    global _writing_stats
    if _writing_stats is None:
        _writing_stats = WritingStats()
    return _writing_stats

def get_character_tracker() -> CharacterTracker:
    """Get global character tracker instance."""
    global _character_tracker
    if _character_tracker is None:
        _character_tracker = CharacterTracker()
    return _character_tracker

def get_plot_tracker() -> PlotTracker:
    """Get global plot tracker instance."""
    global _plot_tracker
    if _plot_tracker is None:
        _plot_tracker = PlotTracker()
    return _plot_tracker

def get_prompt_generator() -> WritingPromptGenerator:
    """Get global prompt generator instance."""
    global _prompt_generator
    if _prompt_generator is None:
        _prompt_generator = WritingPromptGenerator()
    return _prompt_generator

def get_writing_timer() -> WritingTimer:
    """Get global writing timer instance."""
    global _writing_timer
    if _writing_timer is None:
        _writing_timer = WritingTimer()
    return _writing_timer

def get_writing_goals() -> WritingGoals:
    """Get global writing goals instance."""
    global _writing_goals
    if _writing_goals is None:
        _writing_goals = WritingGoals()
    return _writing_goals

def summarize_context(project_name: str, file_cache, chapter: int, section: int) -> str:
    """Summarize the current context for the writing process."""
    try:
        # Get current story content
        story_content = file_cache.get("story.txt") or ""
        characters_content = file_cache.get("characters.txt") or ""
        world_content = file_cache.get("world.txt") or ""

        # Create a summary of the current context
        context_summary = f"Current Context for Chapter {chapter}, Section {section}:\n\n"

        # Add story summary
        if story_content:
            story_words = story_content.split()
            word_count = len(story_words)
            context_summary += f"Story Progress: {word_count} words written\n"

            # Get last few paragraphs for context
            paragraphs = story_content.split('\n\n')
            if paragraphs:
                last_paragraphs = paragraphs[-3:] if len(paragraphs) > 3 else paragraphs
                context_summary += f"Recent content: {' '.join(last_paragraphs)[:500]}...\n\n"

        # Add character information
        if characters_content:
            context_summary += f"Characters: {characters_content[:300]}...\n\n"

        # Add world information
        if world_content:
            context_summary += f"World: {world_content[:300]}...\n\n"

        return context_summary

    except Exception as e:
        logging.error(f"Failed to summarize context: {str(e)}")
        return f"Context summary unavailable: {str(e)}"

def update_character_arcs(project_name: str, file_cache, chapter: int, section: int) -> bool:
    """Update character arcs based on current story progress."""
    try:
        # Get current character data
        characters_content = file_cache.get("characters.txt") or ""
        story_content = file_cache.get("story.txt") or ""

        # Simple character arc tracking
        if characters_content and story_content:
            # This is a placeholder - could be enhanced with AI analysis
            arc_update = f"\n\nCharacter Arc Update - Chapter {chapter}, Section {section}:\n"
            arc_update += f"Story progression continues with established characters.\n"

            # Update the characters file
            updated_characters = characters_content + arc_update
            file_cache.update("characters.txt", updated_characters)

            return True

        return False

    except Exception as e:
        logging.error(f"Failed to update character arcs: {str(e)}")
        return False

def update_plot_points(project_name: str, file_cache, chapter: int, section: int) -> bool:
    """Update plot points based on current story progress."""
    try:
        # Get current plot data
        summaries_content = file_cache.get("summaries.txt") or ""
        story_content = file_cache.get("story.txt") or ""

        # Simple plot point tracking
        if story_content:
            plot_update = f"\n\nPlot Update - Chapter {chapter}, Section {section}:\n"
            plot_update += f"Story continues with chapter {chapter} development.\n"

            # Update the summaries file
            updated_summaries = summaries_content + plot_update
            file_cache.update("summaries.txt", updated_summaries)

            return True

        return False

    except Exception as e:
        logging.error(f"Failed to update plot points: {str(e)}")
        return False

def check_continuity(project_name: str, file_cache, chapter: int, section: int) -> List[str]:
    """Check for continuity issues in the story."""
    try:
        # Get story content
        story_content = file_cache.get("story.txt") or ""
        continuity_rules = file_cache.get("continuity_rules.txt") or ""

        issues = []

        # Basic continuity checks
        if story_content:
            # Check for character name consistency
            character_checker = ConsistencyChecker(file_cache)
            character_issues = character_checker.check_character_consistency(story_content)
            issues.extend(character_issues)

            # Check for timeline issues (placeholder)
            if "yesterday" in story_content.lower() and "tomorrow" in story_content.lower():
                issues.append("Potential timeline inconsistency detected")

        return issues

    except Exception as e:
        logging.error(f"Failed to check continuity: {str(e)}")
        return [f"Continuity check failed: {str(e)}"]

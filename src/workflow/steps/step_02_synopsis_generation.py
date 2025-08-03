#!/usr/bin/env python3
"""
Step 2: AI-Powered Synopsis Generation
Generate comprehensive synopsis using AI with quality analysis.
"""

import os
import json
import logging
from typing import Dict, Any
from ...plugins.plugin_workflow_integration import BaseWorkflowStep

class Step02SynopsisGeneration(BaseWorkflowStep):
    """
    Step 2: AI-Powered Synopsis Generation with quality analysis.
    Uses AI to generate a comprehensive synopsis based on the novel idea.
    """

    def __init__(self, workflow_instance):
        """Initialize Step 2 with workflow instance."""
        super().__init__(workflow_instance)

    def execute(self) -> bool:
        """Execute Step 2: AI-Powered Synopsis Generation."""
        synopsis_results = {
            'success': False,
            'synopsis_generated': False,
            'quality_score': 0,
            'word_count': 0,
            'ai_used': False,
            'fallback_used': False,
            'errors': [],
            'warnings': [],
            'metadata': {}
        }

        try:
            self.update_progress(0)
            self.log_action("Generating AI-powered synopsis...")

            # Generate synopsis using AI
            if hasattr(self.workflow, 'api_manager') and self.workflow.api_manager:
                prompt = self.create_synopsis_prompt()
                response = self.workflow.api_manager.generate_text(prompt)

                if response:
                    synopsis_results['ai_used'] = True
                    synopsis_results['synopsis_generated'] = True
                    self.workflow.synopsis = response
                    synopsis_results['word_count'] = len(response.split())

                    # Analyze quality
                    quality_analysis = self.analyze_synopsis_quality(response)
                    synopsis_results['quality_score'] = quality_analysis['score']
                    synopsis_results['metadata'] = quality_analysis

                    self.log_action(f"AI synopsis generated: {synopsis_results['word_count']} words, quality: {synopsis_results['quality_score']}")
                else:
                    # Fallback to basic synopsis
                    fallback_synopsis = self.generate_fallback_synopsis()
                    if fallback_synopsis:
                        synopsis_results['fallback_used'] = True
                        synopsis_results['synopsis_generated'] = True
                        self.workflow.synopsis = fallback_synopsis
                        synopsis_results['word_count'] = len(fallback_synopsis.split())
                        synopsis_results['warnings'].append("Used fallback synopsis generation")
                        self.log_action("Fallback synopsis generated")

            self.update_progress(50)

            # Save synopsis to file
            if synopsis_results['synopsis_generated']:
                synopsis_path = os.path.join(self.workflow.project_path, "synopsis.txt")
                with open(synopsis_path, 'w', encoding='utf-8') as f:
                    f.write(self.workflow.synopsis)

                self.log_action(f"Synopsis saved to {synopsis_path}")

            self.update_progress(75)

            # Validate synopsis
            validation_result = self.validate_synopsis(self.workflow.synopsis)
            synopsis_results['validation_passed'] = validation_result['is_valid']

            if not validation_result['is_valid']:
                synopsis_results['warnings'].extend(validation_result['warnings'])

            self.update_progress(100)

            # Determine success
            synopsis_results['success'] = (
                synopsis_results['synopsis_generated'] and
                synopsis_results['word_count'] >= 300 and
                synopsis_results['quality_score'] >= 60
            )

            # Save step data
            self.save_step_data(synopsis_results)

            if synopsis_results['success']:
                self.log_action("AI synopsis generation completed successfully")
                # Update workflow state
                if hasattr(self.workflow, 'current_step'):
                    self.workflow.current_step = 3
            else:
                self.log_action("Synopsis generation completed with issues")

            return synopsis_results['success']

        except Exception as e:
            synopsis_results['errors'].append(str(e))
            self.handle_error(e, "synopsis generation")
            self.save_step_data(synopsis_results)
            return False

    def create_synopsis_prompt(self) -> str:
        """Create a comprehensive prompt for synopsis generation."""
        genre = getattr(self.workflow, 'genre', 'fiction')
        tone = getattr(self.workflow, 'novel_tone', 'neutral')
        idea = getattr(self.workflow, 'novel_idea', 'A compelling story')
        word_count = getattr(self.workflow, 'target_word_count', 80000)

        prompt = f"""You are a professional novelist creating a comprehensive synopsis for a {genre} novel.

NOVEL DETAILS:
- Genre: {genre}
- Tone: {tone}
- Idea: {idea}
- Target Length: {word_count} words

REQUIREMENTS:
Create a detailed synopsis (500-800 words) that includes:

1. SETTING AND WORLD: Establish the time, place, and world where the story unfolds
2. MAIN CHARACTER: Introduce the protagonist with clear motivation and internal conflict
3. CENTRAL CONFLICT: Define the main problem or challenge driving the story
4. PLOT STRUCTURE: Outline the beginning, middle, and end with key plot points
5. SUPPORTING CHARACTERS: Introduce key secondary characters and their roles
6. THEMES: Identify the deeper themes and messages
7. STAKES: Clarify what the protagonist stands to gain or lose
8. RESOLUTION: Provide a satisfying conclusion that ties up the main plot threads

The synopsis should maintain a {tone} tone and capture the essence of the {genre} genre.
Write in third person present tense and focus on the main storyline.
"""
        return prompt

    def analyze_synopsis_quality(self, synopsis: str) -> Dict[str, Any]:
        """Analyze the quality of the generated synopsis."""
        analysis = {
            'score': 0,
            'word_count': len(synopsis.split()),
            'character_count': len(synopsis),
            'has_protagonist': False,
            'has_conflict': False,
            'has_resolution': False,
            'tone_consistency': 0,
            'genre_elements': 0,
            'structure_score': 0,
            'recommendations': []
        }

        # Word count scoring
        word_count = analysis['word_count']
        if 500 <= word_count <= 800:
            analysis['score'] += 30
        elif 400 <= word_count <= 900:
            analysis['score'] += 20
        elif 300 <= word_count <= 1000:
            analysis['score'] += 10

        # Content analysis
        synopsis_lower = synopsis.lower()

        # Check for protagonist
        protagonist_words = ['protagonist', 'hero', 'main character', 'leads', 'follows']
        if any(word in synopsis_lower for word in protagonist_words):
            analysis['has_protagonist'] = True
            analysis['score'] += 15

        # Check for conflict
        conflict_words = ['conflict', 'problem', 'challenge', 'obstacle', 'struggle', 'must']
        if any(word in synopsis_lower for word in conflict_words):
            analysis['has_conflict'] = True
            analysis['score'] += 15

        # Check for resolution
        resolution_words = ['resolves', 'solution', 'overcomes', 'achieves', 'succeeds', 'conclusion']
        if any(word in synopsis_lower for word in resolution_words):
            analysis['has_resolution'] = True
            analysis['score'] += 15

        # Genre elements
        genre_words = {
            'fantasy': ['magic', 'wizard', 'dragon', 'quest', 'kingdom', 'sword'],
            'sci-fi': ['future', 'space', 'technology', 'alien', 'robot', 'planet'],
            'mystery': ['murder', 'detective', 'clue', 'investigation', 'suspect', 'solve'],
            'romance': ['love', 'relationship', 'heart', 'passion', 'romance', 'beloved'],
            'thriller': ['danger', 'chase', 'escape', 'threat', 'suspense', 'race']
        }

        genre = getattr(self.workflow, 'genre', '').lower()
        if genre in genre_words:
            genre_count = sum(1 for word in genre_words[genre] if word in synopsis_lower)
            analysis['genre_elements'] = genre_count
            analysis['score'] += min(genre_count * 3, 15)

        # Structure scoring
        paragraphs = synopsis.split('\n\n')
        if len(paragraphs) >= 3:
            analysis['structure_score'] = min(len(paragraphs) * 2, 10)
            analysis['score'] += analysis['structure_score']

        # Generate recommendations
        if not analysis['has_protagonist']:
            analysis['recommendations'].append("Add clearer protagonist introduction")
        if not analysis['has_conflict']:
            analysis['recommendations'].append("Strengthen central conflict description")
        if not analysis['has_resolution']:
            analysis['recommendations'].append("Include resolution or conclusion")
        if analysis['word_count'] < 500:
            analysis['recommendations'].append("Expand synopsis to 500+ words")
        if analysis['genre_elements'] < 3:
            analysis['recommendations'].append(f"Include more {genre} genre elements")

        return analysis

    def generate_fallback_synopsis(self) -> str:
        """Generate a basic fallback synopsis when AI is unavailable."""
        genre = getattr(self.workflow, 'genre', 'fiction')
        tone = getattr(self.workflow, 'novel_tone', 'neutral')
        idea = getattr(self.workflow, 'novel_idea', 'A compelling story')
        word_count = getattr(self.workflow, 'target_word_count', 80000)

        fallback = f"""In this {genre} novel, the story follows a protagonist who must navigate the challenges of {idea}.

Set in a {tone} world, the main character faces significant obstacles that test their resolve and character. The central conflict revolves around the core premise of the story, driving the narrative forward through a series of escalating challenges.

As the story progresses, the protagonist must confront both external threats and internal struggles, leading to personal growth and transformation. The supporting characters play crucial roles in shaping the journey, each contributing to the overall narrative arc.

The themes of the novel explore deeper questions about human nature, morality, and the choices we make in difficult circumstances. The {tone} tone permeates throughout, creating an atmosphere that enhances the storytelling experience.

The climax brings all the story elements together in a satisfying resolution, where the protagonist must make their final choice and face the consequences of their actions. The conclusion ties up the main plot threads while leaving room for reflection on the themes and messages presented throughout the novel.

This {word_count}-word novel promises to deliver an engaging {genre} experience that will resonate with readers long after they finish the final page."""

        return fallback

    def validate_synopsis(self, synopsis: str) -> Dict[str, Any]:
        """Validate the synopsis for basic requirements."""
        validation = {
            'is_valid': False,
            'warnings': [],
            'word_count': len(synopsis.split()),
            'character_count': len(synopsis)
        }

        # Check minimum word count
        if validation['word_count'] < 200:
            validation['warnings'].append("Synopsis too short (minimum 200 words)")

        # Check maximum word count
        if validation['word_count'] > 1200:
            validation['warnings'].append("Synopsis too long (maximum 1200 words)")

        # Check for basic content
        if not synopsis.strip():
            validation['warnings'].append("Synopsis is empty")

        # Check for genre mention
        genre = getattr(self.workflow, 'genre', '').lower()
        if genre and genre not in synopsis.lower():
            validation['warnings'].append(f"Genre '{genre}' not mentioned in synopsis")

        # Determine validity
        validation['is_valid'] = (
            validation['word_count'] >= 200 and
            validation['word_count'] <= 1200 and
            len(validation['warnings']) == 0
        )

        return validation

    def validate_prerequisites(self) -> bool:
        """Validate prerequisites for Step 2."""
        # Check if Step 1 completed successfully
        step_1_data = self.load_step_data()
        if not step_1_data:
            # Try to load from previous step
            step_1_file = os.path.join(self.workflow.project_path, "step_01_data.json")
            if not os.path.exists(step_1_file):
                self.log_action("Step 1 data not found", "ERROR")
                return False

        # Check required workflow attributes
        required_attrs = ['novel_idea', 'genre', 'novel_tone', 'target_word_count']
        for attr in required_attrs:
            if not hasattr(self.workflow, attr) or not getattr(self.workflow, attr):
                self.log_action(f"Required attribute {attr} not set", "ERROR")
                return False

        return True

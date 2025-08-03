#!/usr/bin/env python3
"""
Step 3: Synopsis Refinement
Iterative refinement of the synopsis through analysis and improvement.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any
try:
    from ...plugins.plugin_workflow_integration import BaseWorkflowStep
except ImportError:
    from base_step import BaseWorkflowStep

class Step03SynopsisRefinement(BaseWorkflowStep):
    """
    Step 3: Synopsis Refinement Loop with user feedback integration.
    Refines the synopsis based on user feedback and quality analysis.
    """

    def __init__(self, workflow_instance):
        """Initialize Step 3 with workflow instance."""
        super().__init__(workflow_instance)

    def execute(self) -> bool:
        """Execute Step 3: Synopsis Refinement Loop."""
        refinement_results = {
            'success': False,
            'refinement_completed': False,
            'iterations_performed': 0,
            'quality_improved': False,
            'user_feedback_processed': False,
            'final_quality_score': 0,
            'errors': [],
            'warnings': [],
            'refinement_history': []
        }

        try:
            self.update_progress(0)
            self.log_action("Starting synopsis refinement loop...")

            # Initial quality assessment
            initial_analysis = self.analyze_synopsis_quality(self.workflow.synopsis)
            initial_score = initial_analysis['score']

            self.log_action(f"Initial synopsis quality score: {initial_score}")

            # Simulate user feedback (in real implementation, this would come from GUI)
            user_feedback = "Make the synopsis more engaging and add more details about the world-building"

            if user_feedback:
                refinement_results['user_feedback_processed'] = True

                # Process feedback and refine
                refined_synopsis = self.refine_synopsis_with_feedback(self.workflow.synopsis, user_feedback)

                if refined_synopsis:
                    # Update synopsis
                    self.workflow.synopsis = refined_synopsis
                    refinement_results['iterations_performed'] += 1

                    # Analyze improved quality
                    final_analysis = self.analyze_synopsis_quality(self.workflow.synopsis)
                    final_score = final_analysis['score']

                    refinement_results['final_quality_score'] = final_score
                    refinement_results['quality_improved'] = final_score > initial_score

                    # Log refinement
                    self.log_action(f"Synopsis refined: score {initial_score} → {final_score}")

                    # Save refinement history
                    refinement_history = {
                        'iteration': refinement_results['iterations_performed'],
                        'timestamp': datetime.now().isoformat(),
                        'user_feedback': user_feedback,
                        'initial_score': initial_score,
                        'final_score': final_score,
                        'improvement': final_score - initial_score
                    }

                    refinement_results['refinement_history'].append(refinement_history)

                else:
                    refinement_results['warnings'].append("Synopsis refinement failed")

            self.update_progress(75)

            # Save refined synopsis
            synopsis_path = os.path.join(self.workflow.project_path, "synopsis.txt")
            with open(synopsis_path, 'w', encoding='utf-8') as f:
                f.write(self.workflow.synopsis)

            # Save refinement history
            history_path = os.path.join(self.workflow.project_path, "metadata", "refinement_history.json")
            os.makedirs(os.path.dirname(history_path), exist_ok=True)
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(refinement_results['refinement_history'], f, indent=2)

            self.update_progress(100)

            # Determine success
            refinement_results['success'] = (
                refinement_results['user_feedback_processed'] and
                refinement_results['final_quality_score'] >= 70
            )

            refinement_results['refinement_completed'] = True

            # Save step data
            self.save_step_data(refinement_results)

            if refinement_results['success']:
                self.log_action("Synopsis refinement completed successfully")
                # Update workflow state
                if hasattr(self.workflow, 'current_step'):
                    self.workflow.current_step = 4
            else:
                self.log_action("Synopsis refinement completed with issues")

            return refinement_results['success']

        except Exception as e:
            refinement_results['errors'].append(str(e))
            self.handle_error(e, "synopsis refinement")
            self.save_step_data(refinement_results)
            return False

    def analyze_synopsis_quality(self, synopsis: str) -> Dict[str, Any]:
        """Analyze the quality of the synopsis."""
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

    def refine_synopsis_with_feedback(self, synopsis: str, feedback: str) -> str:
        """Refine the synopsis based on user feedback."""
        if not hasattr(self.workflow, 'api_manager') or not self.workflow.api_manager:
            return synopsis  # Return original if no AI available

        try:
            genre = getattr(self.workflow, 'genre', 'fiction')
            tone = getattr(self.workflow, 'novel_tone', 'neutral')

            prompt = f"""You are a professional editor helping to refine a novel synopsis based on user feedback.

CURRENT SYNOPSIS:
{synopsis}

USER FEEDBACK:
{feedback}

TASK:
Rewrite the synopsis to address the user's feedback while maintaining the core story elements.
Keep the same genre ({genre}) and tone ({tone}).
Ensure the revised synopsis is 500-800 words and flows naturally.

REVISED SYNOPSIS:"""

            response = self.workflow.api_manager.generate_text(prompt)

            if response and len(response.split()) >= 200:
                return response
            else:
                return synopsis  # Return original if refinement failed

        except Exception as e:
            self.log_action(f"Synopsis refinement failed: {str(e)}", "ERROR")
            return synopsis

    def validate_prerequisites(self) -> bool:
        """Validate prerequisites for Step 3."""
        # Check if Step 2 completed successfully
        step_2_data_file = os.path.join(self.workflow.project_path, "step_02_data.json")
        if not os.path.exists(step_2_data_file):
            self.log_action("Step 2 data not found", "ERROR")
            return False

        # Check if synopsis exists
        if not hasattr(self.workflow, 'synopsis') or not self.workflow.synopsis:
            self.log_action("Synopsis not found", "ERROR")
            return False

        return True

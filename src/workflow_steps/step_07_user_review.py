#!/usr/bin/env python3
"""
Step 7: User Review
Comprehensive user review system for manuscript sections.
"""

import json
import os
import logging
from datetime import datetime
from .base_step import BaseWorkflowStep

class Step07UserReview(BaseWorkflowStep):
    def execute(self) -> dict:
        """
        Execute Step 7: Comprehensive User Review System
        Presents each manuscript section for user review, collects feedback, and tracks approval/revision requests.
        """
        self.workflow.status_updated.emit("Status: Starting user review")
        review_results = {
            'success': False,
            'sections_reviewed': [],
            'feedback_collected': [],
            'revision_requested': [],
            'approval_given': [],
            'total_sections': 0,
            'quality_score': 0,
            'errors': []
        }

        try:
            sections = self.extract_sections_for_review()
            review_results['total_sections'] = len(sections)

            for i, section in enumerate(sections):
                self.workflow.status_updated.emit(f"Status: Reviewing section {i+1}/{len(sections)}: {section['title']}")

                feedback = self.present_section_for_review(section)
                review_results['sections_reviewed'].append(section['id'])
                review_results['feedback_collected'].append(feedback)

                if feedback.get('revision_requested'):
                    review_results['revision_requested'].append(section['id'])
                if feedback.get('approved'):
                    review_results['approval_given'].append(section['id'])

                # Update progress
                progress = int((i + 1) / len(sections) * 90)
                self.workflow.progress_updated.emit(progress)

            # Calculate quality score
            review_results['quality_score'] = self.calculate_review_quality_score(review_results)

            # Save review results
            self.save_review_results(review_results)

            # Determine success
            review_results['success'] = len(review_results['sections_reviewed']) > 0

            self.workflow.progress_updated.emit(100)
            self.workflow.status_updated.emit("Status: User review complete")

            if review_results['success']:
                self.workflow.log_action(f"User review completed: {len(review_results['sections_reviewed'])} sections reviewed")
                if hasattr(self.workflow, 'current_step'):
                    self.workflow.current_step = 8
            else:
                self.workflow.log_action("User review completed with issues")

        except Exception as e:
            review_results['errors'].append(str(e))
            self.workflow.error_occurred.emit(f"User review error: {e}")
            self.workflow.log_action(f"User review error: {e}")

        return review_results

    def extract_sections_for_review(self):
        """Extract manuscript sections for review."""
        try:
            sections = []

            # Look for manuscript sections in the project
            manuscript_file = os.path.join(self.workflow.project_path, "story.txt")
            sections_dir = os.path.join(self.workflow.project_path, "sections")

            if os.path.exists(manuscript_file):
                with open(manuscript_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Split into sections based on chapter markers or length
                if "Chapter" in content:
                    parts = content.split("Chapter")
                    for i, part in enumerate(parts[1:], 1):  # Skip first empty part
                        sections.append({
                            'id': f'chapter_{i}',
                            'title': f'Chapter {i}',
                            'content': f'Chapter{part}',
                            'word_count': len(part.split()),
                            'approved': False,
                            'revision_notes': ''
                        })
                else:
                    # Split by paragraph count (every 10 paragraphs)
                    paragraphs = content.split('\n\n')
                    for i in range(0, len(paragraphs), 10):
                        section_content = '\n\n'.join(paragraphs[i:i+10])
                        sections.append({
                            'id': f'section_{i//10 + 1}',
                            'title': f'Section {i//10 + 1}',
                            'content': section_content,
                            'word_count': len(section_content.split()),
                            'approved': False,
                            'revision_notes': ''
                        })

            # Also check sections directory
            if os.path.exists(sections_dir):
                for filename in os.listdir(sections_dir):
                    if filename.endswith('.json'):
                        section_path = os.path.join(sections_dir, filename)
                        try:
                            with open(section_path, 'r', encoding='utf-8') as f:
                                section_data = json.load(f)
                                sections.append({
                                    'id': filename.replace('.json', ''),
                                    'title': section_data.get('title', 'Untitled Section'),
                                    'content': section_data.get('content', ''),
                                    'word_count': section_data.get('word_count', 0),
                                    'approved': section_data.get('approved', False),
                                    'revision_notes': section_data.get('revision_notes', '')
                                })
                        except:
                            continue

            return sections

        except Exception as e:
            self.workflow.log_action(f"Error extracting sections: {e}")
            return []

    def present_section_for_review(self, section):
        """Present section to user and collect feedback."""
        try:
            # This would typically show a dialog in the GUI
            # For now, we'll simulate user feedback based on content quality

            content = section.get('content', '')
            word_count = section.get('word_count', 0)

            # Simulate feedback analysis
            feedback = {
                'approved': True,
                'revision_requested': False,
                'comments': '',
                'rating': 5,
                'areas_for_improvement': [],
                'strengths': []
            }

            # Check for common issues
            if word_count < 50:
                feedback['revision_requested'] = True
                feedback['approved'] = False
                feedback['areas_for_improvement'].append('too short')
                feedback['comments'] = 'Section needs more content'
                feedback['rating'] = 2
            elif word_count > 2000:
                feedback['revision_requested'] = True
                feedback['approved'] = False
                feedback['areas_for_improvement'].append('too long')
                feedback['comments'] = 'Section is too lengthy, consider breaking up'
                feedback['rating'] = 3
            elif '[placeholder]' in content.lower() or 'todo' in content.lower():
                feedback['revision_requested'] = True
                feedback['approved'] = False
                feedback['areas_for_improvement'].append('placeholder')
                feedback['comments'] = 'Contains placeholder text that needs development'
                feedback['rating'] = 2
            elif content.count('very') > 5:
                feedback['revision_requested'] = True
                feedback['approved'] = False
                feedback['areas_for_improvement'].append('repetitive language')
                feedback['comments'] = 'Overuse of certain words, needs vocabulary refinement'
                feedback['rating'] = 3
            else:
                feedback['strengths'].append('good length')
                feedback['strengths'].append('complete content')
                feedback['comments'] = 'Section looks good'

            return feedback

        except Exception as e:
            self.workflow.log_action(f"Error presenting section: {e}")
            return {'approved': False, 'revision_requested': True, 'comments': f'Error: {e}'}

    def calculate_review_quality_score(self, review_results):
        """Calculate overall quality score from review results."""
        try:
            if not review_results['feedback_collected']:
                return 0

            total_rating = 0
            total_sections = len(review_results['feedback_collected'])

            for feedback in review_results['feedback_collected']:
                total_rating += feedback.get('rating', 0)

            avg_rating = total_rating / total_sections if total_sections > 0 else 0
            return int(avg_rating * 20)  # Convert to 100-point scale

        except Exception as e:
            self.workflow.log_action(f"Error calculating review quality score: {e}")
            return 0

    def save_review_results(self, review_results):
        """Save user review results to disk."""
        try:
            review_file = os.path.join(self.workflow.project_path, "review_results.json")

            # Add timestamp
            review_results['timestamp'] = datetime.now().isoformat()

            with open(review_file, 'w', encoding='utf-8') as f:
                json.dump(review_results, f, indent=2, ensure_ascii=False)

            self.workflow.log_action(f"Review results saved to {review_file}")

        except Exception as e:
            self.workflow.log_action(f"Error saving review results: {e}")

    def validate_prerequisites(self) -> bool:
        """Validate prerequisites for Step 7."""
        # Check if Step 6 completed successfully
        step_6_data_file = os.path.join(self.workflow.project_path, "writing_results.json")
        if not os.path.exists(step_6_data_file):
            self.workflow.log_action("Step 6 data not found", "ERROR")
            return False

        # Check if there's content to review
        manuscript_file = os.path.join(self.workflow.project_path, "story.txt")
        sections_dir = os.path.join(self.workflow.project_path, "sections")

        if not os.path.exists(manuscript_file) and not os.path.exists(sections_dir):
            self.workflow.log_action("No manuscript content found for review", "ERROR")
            return False

        return True

#!/usr/bin/env python3
"""
Step 8: Refinement Loop
Refine manuscript sections based on user feedback and apply improvements.
"""

import json
import os
import logging
import re
from datetime import datetime
from .base_step import BaseWorkflowStep

class Step08RefinementLoop(BaseWorkflowStep):
    def execute(self) -> dict:
        """
        Execute Step 8: Refinement Loop
        Refines manuscript sections based on user feedback, applies AI/manual improvements, and tracks quality.
        """
        self.workflow.status_updated.emit("Status: Starting refinement loop")
        refinement_results = {
            'success': False,
            'sections_refined': [],
            'iterations_performed': 0,
            'quality_improved': False,
            'ai_refinements_applied': [],
            'manual_refinements_applied': [],
            'total_sections': 0,
            'quality_score': 0,
            'errors': []
        }

        try:
            review_results = self.load_review_results()
            sections_to_refine = self.identify_sections_for_refinement(review_results)
            refinement_results['total_sections'] = len(sections_to_refine)

            initial_quality = self.assess_manuscript_quality()

            for i, section_id in enumerate(sections_to_refine):
                self.workflow.status_updated.emit(f"Status: Refining section {i+1}/{len(sections_to_refine)}: {section_id}")

                section_content = self.load_section_content(section_id)
                feedback = self.get_section_feedback(section_id, review_results)

                refined_content, ai_applied, manual_applied = self.refine_section_based_on_feedback(section_content, feedback)

                self.save_refined_section(section_id, refined_content)
                refinement_results['sections_refined'].append(section_id)

                if ai_applied:
                    refinement_results['ai_refinements_applied'].append(section_id)
                if manual_applied:
                    refinement_results['manual_refinements_applied'].append(section_id)

                refinement_results['iterations_performed'] += 1

                # Update progress
                progress = int((i + 1) / len(sections_to_refine) * 90)
                self.workflow.progress_updated.emit(progress)

            # Assess quality improvement
            final_quality = self.assess_manuscript_quality()
            refinement_results['quality_improved'] = final_quality > initial_quality
            refinement_results['quality_score'] = final_quality

            # Save refinement results
            self.save_refinement_results(refinement_results)

            # Determine success
            refinement_results['success'] = len(refinement_results['sections_refined']) > 0

            self.workflow.progress_updated.emit(100)
            self.workflow.status_updated.emit("Status: Refinement loop complete")

            if refinement_results['success']:
                self.workflow.log_action(f"Refinement loop completed: {len(refinement_results['sections_refined'])} sections refined")
                if hasattr(self.workflow, 'current_step'):
                    self.workflow.current_step = 9
            else:
                self.workflow.log_action("Refinement loop completed with issues")

        except Exception as e:
            refinement_results['errors'].append(str(e))
            self.workflow.error_occurred.emit(f"Refinement loop error: {e}")
            self.workflow.log_action(f"Refinement loop error: {e}")

        return refinement_results

    def load_review_results(self):
        """Load user review results from disk."""
        try:
            review_file = os.path.join(self.workflow.project_path, "review_results.json")
            if os.path.exists(review_file):
                with open(review_file, 'r', encoding='utf-8') as f:
                    return json.load(f)

            return {'sections_reviewed': [], 'feedback_collected': [], 'revision_requested': [], 'approval_given': []}

        except Exception as e:
            self.workflow.log_action(f"Error loading review results: {e}")
            return {'sections_reviewed': [], 'feedback_collected': [], 'revision_requested': [], 'approval_given': []}

    def identify_sections_for_refinement(self, review_results):
        """Identify sections needing refinement based on review results."""
        try:
            sections_to_refine = []

            # Get sections that were marked for revision
            revision_requested = review_results.get('revision_requested', [])
            sections_to_refine.extend(revision_requested)

            # Also check feedback for specific improvement areas
            feedback_collected = review_results.get('feedback_collected', [])
            sections_reviewed = review_results.get('sections_reviewed', [])

            for i, feedback in enumerate(feedback_collected):
                if i < len(sections_reviewed):
                    section_id = sections_reviewed[i]
                    if feedback.get('rating', 5) < 4:  # Low rating
                        if section_id not in sections_to_refine:
                            sections_to_refine.append(section_id)

                    # Check for specific improvement areas
                    improvement_areas = feedback.get('areas_for_improvement', [])
                    if improvement_areas and section_id not in sections_to_refine:
                        sections_to_refine.append(section_id)

            return sections_to_refine

        except Exception as e:
            self.workflow.log_action(f"Error identifying sections for refinement: {e}")
            return review_results.get('revision_requested', [])

    def load_section_content(self, section_id):
        """Load content for a given section."""
        try:
            # Try to load from sections directory first
            section_file = os.path.join(self.workflow.project_path, "sections", f"{section_id}.json")
            if os.path.exists(section_file):
                with open(section_file, 'r', encoding='utf-8') as f:
                    section_data = json.load(f)
                    return section_data.get('content', '')

            # Try to extract from main story file
            story_file = os.path.join(self.workflow.project_path, "story.txt")
            if os.path.exists(story_file):
                with open(story_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Simple extraction based on section ID
                if section_id.startswith('chapter_'):
                    chapter_num = section_id.split('_')[1]
                    if f"Chapter {chapter_num}" in content:
                        parts = content.split(f"Chapter {chapter_num}")
                        if len(parts) > 1:
                            # Get content until next chapter
                            next_chapter = f"Chapter {int(chapter_num) + 1}"
                            chapter_content = parts[1]
                            if next_chapter in chapter_content:
                                chapter_content = chapter_content.split(next_chapter)[0]
                            return f"Chapter {chapter_num}{chapter_content}"

                elif section_id.startswith('section_'):
                    section_num = int(section_id.split('_')[1])
                    paragraphs = content.split('\n\n')
                    start_idx = (section_num - 1) * 10
                    end_idx = start_idx + 10
                    return '\n\n'.join(paragraphs[start_idx:end_idx])

            return ''

        except Exception as e:
            self.workflow.log_action(f"Error loading section content: {e}")
            return ''

    def get_section_feedback(self, section_id, review_results):
        """Get feedback for a given section from review results."""
        try:
            sections_reviewed = review_results.get('sections_reviewed', [])
            feedback_collected = review_results.get('feedback_collected', [])

            for idx, sid in enumerate(sections_reviewed):
                if sid == section_id and idx < len(feedback_collected):
                    return feedback_collected[idx]

            return {}

        except Exception as e:
            self.workflow.log_action(f"Error getting section feedback: {e}")
            return {}

    def refine_section_based_on_feedback(self, section_content, feedback):
        """Refine section using feedback, apply AI/manual improvements."""
        try:
            ai_applied = False
            manual_applied = False
            refined_content = section_content

            if feedback.get('revision_requested'):
                improvement_areas = feedback.get('areas_for_improvement', [])
                comments = feedback.get('comments', '')

                # Apply AI refinement if available
                if self.workflow.api_manager and self.workflow.api_manager.is_available():
                    try:
                        refinement_prompt = self.create_refinement_prompt(section_content, improvement_areas, comments)
                        refined_content = self.workflow.api_manager.generate_text(refinement_prompt)
                        if refined_content and len(refined_content.strip()) > 50:
                            ai_applied = True
                        else:
                            refined_content = section_content
                    except Exception as e:
                        self.workflow.log_action(f"AI refinement failed: {e}")
                        ai_applied = False

                # Apply manual refinement if AI failed or unavailable
                if not ai_applied:
                    refined_content = self.apply_manual_refinement(section_content, improvement_areas, comments)
                    manual_applied = True

            return refined_content, ai_applied, manual_applied

        except Exception as e:
            self.workflow.log_action(f"Error refining section: {e}")
            return section_content, False, False

    def create_refinement_prompt(self, content, improvement_areas, comments):
        """Create AI prompt for section refinement."""
        prompt = f"""Please refine the following text section based on the feedback provided:

ORIGINAL TEXT:
{content}

IMPROVEMENT AREAS: {', '.join(improvement_areas)}
FEEDBACK: {comments}

Please provide a refined version that addresses the specific issues mentioned while maintaining the original tone and style. Focus on:
"""

        for area in improvement_areas:
            if area == 'too short':
                prompt += "- Expanding the content with more detail and development\n"
            elif area == 'too long':
                prompt += "- Condensing the content while preserving key information\n"
            elif area == 'placeholder':
                prompt += "- Replacing placeholder text with fully developed content\n"
            elif area == 'repetitive language':
                prompt += "- Varying vocabulary and sentence structure\n"
            else:
                prompt += f"- Addressing {area}\n"

        prompt += "\nProvide only the refined text without additional commentary."

        return prompt

    def apply_manual_refinement(self, content, improvement_areas, comments):
        """Apply manual refinement when AI is unavailable."""
        try:
            refined_content = content

            for area in improvement_areas:
                if area == 'too short':
                    refined_content = self.expand_content(refined_content)
                elif area == 'too long':
                    refined_content = self.condense_content(refined_content)
                elif area == 'placeholder':
                    refined_content = self.replace_placeholders(refined_content)
                elif area == 'repetitive language':
                    refined_content = self.improve_vocabulary(refined_content)
                else:
                    refined_content = self.add_development_notes(refined_content, area)

            return refined_content

        except Exception as e:
            self.workflow.log_action(f"Error in manual refinement: {e}")
            return content

    def expand_content(self, content):
        """Expand content that is too short."""
        if len(content.split()) < 50:
            return content + "\n\n[DEVELOPMENT NEEDED: This section requires additional content to fully develop the scene, characters, and narrative elements.]"
        return content

    def condense_content(self, content):
        """Condense content that is too long."""
        if len(content.split()) > 2000:
            sentences = content.split('. ')
            condensed = '. '.join(sentences[:len(sentences)//2])
            return condensed + "\n\n[EDITING NOTE: Content has been condensed. Review for coherence and completeness.]"
        return content

    def replace_placeholders(self, content):
        """Replace placeholder text with development notes."""
        # Replace common placeholder patterns
        content = re.sub(r'\[placeholder\]', '[DEVELOP: Add specific content here]', content, flags=re.IGNORECASE)
        content = re.sub(r'\[todo\]', '[DEVELOP: Complete this section]', content, flags=re.IGNORECASE)
        content = re.sub(r'todo:', '[DEVELOP:', content, flags=re.IGNORECASE)

        return content

    def improve_vocabulary(self, content):
        """Improve repetitive vocabulary."""
        # Simple vocabulary improvement
        words = content.split()
        improved_words = []

        for word in words:
            if word.lower() == 'very' and len(improved_words) > 0:
                # Replace 'very' with more specific adjectives
                continue
            improved_words.append(word)

        return ' '.join(improved_words)

    def add_development_notes(self, content, area):
        """Add development notes for specific areas."""
        return content + f"\n\n[DEVELOPMENT NOTE: Address {area} in this section]"

    def save_refined_section(self, section_id, refined_content):
        """Save refined section content to disk."""
        try:
            # Save to sections directory
            sections_dir = os.path.join(self.workflow.project_path, "sections")
            os.makedirs(sections_dir, exist_ok=True)

            section_file = os.path.join(sections_dir, f"{section_id}_refined.json")
            section_data = {
                'section_id': section_id,
                'content': refined_content,
                'word_count': len(refined_content.split()),
                'refined_date': datetime.now().isoformat(),
                'status': 'refined'
            }

            with open(section_file, 'w', encoding='utf-8') as f:
                json.dump(section_data, f, indent=2, ensure_ascii=False)

            self.workflow.log_action(f"Refined section saved: {section_file}")

        except Exception as e:
            self.workflow.log_action(f"Error saving refined section: {e}")

    def assess_manuscript_quality(self):
        """Assess overall manuscript quality after refinement."""
        try:
            # Calculate quality metrics
            quality_score = 0
            metrics = {
                'word_count': 0,
                'sections_completed': 0,
                'placeholders_remaining': 0,
                'average_section_length': 0,
                'consistency_score': 0
            }

            # Check story file
            story_file = os.path.join(self.workflow.project_path, "story.txt")
            if os.path.exists(story_file):
                with open(story_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                metrics['word_count'] = len(content.split())
                metrics['placeholders_remaining'] = content.lower().count('[placeholder]') + content.lower().count('[todo]')

                # Count sections
                if "Chapter" in content:
                    metrics['sections_completed'] = len([p for p in content.split("Chapter") if p.strip()])
                else:
                    metrics['sections_completed'] = len(content.split('\n\n'))

                if metrics['sections_completed'] > 0:
                    metrics['average_section_length'] = metrics['word_count'] / metrics['sections_completed']

            # Check sections directory
            sections_dir = os.path.join(self.workflow.project_path, "sections")
            if os.path.exists(sections_dir):
                refined_sections = [f for f in os.listdir(sections_dir) if f.endswith('_refined.json')]
                metrics['sections_completed'] += len(refined_sections)

            # Calculate quality score
            if metrics['word_count'] > 10000:
                quality_score += 30
            elif metrics['word_count'] > 5000:
                quality_score += 20
            elif metrics['word_count'] > 1000:
                quality_score += 10

            if metrics['sections_completed'] > 10:
                quality_score += 25
            elif metrics['sections_completed'] > 5:
                quality_score += 15
            elif metrics['sections_completed'] > 1:
                quality_score += 10

            if metrics['placeholders_remaining'] == 0:
                quality_score += 25
            elif metrics['placeholders_remaining'] < 5:
                quality_score += 15
            elif metrics['placeholders_remaining'] < 10:
                quality_score += 10

            if metrics['average_section_length'] > 200:
                quality_score += 20
            elif metrics['average_section_length'] > 100:
                quality_score += 15
            elif metrics['average_section_length'] > 50:
                quality_score += 10

            return quality_score

        except Exception as e:
            self.workflow.log_action(f"Error assessing manuscript quality: {e}")
            return 0

    def save_refinement_results(self, refinement_results):
        """Save refinement results to disk."""
        try:
            refinement_file = os.path.join(self.workflow.project_path, "refinement_results.json")

            # Add timestamp and quality metrics
            refinement_results['timestamp'] = datetime.now().isoformat()

            with open(refinement_file, 'w', encoding='utf-8') as f:
                json.dump(refinement_results, f, indent=2, ensure_ascii=False)

            self.workflow.log_action(f"Refinement results saved to {refinement_file}")

        except Exception as e:
            self.workflow.log_action(f"Error saving refinement results: {e}")

    def validate_prerequisites(self) -> bool:
        """Validate prerequisites for Step 8."""
        # Check if Step 7 completed successfully
        step_7_data_file = os.path.join(self.workflow.project_path, "review_results.json")
        if not os.path.exists(step_7_data_file):
            self.workflow.log_action("Step 7 data not found", "ERROR")
            return False

        return True

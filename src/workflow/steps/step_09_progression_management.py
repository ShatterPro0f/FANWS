#!/usr/bin/env python3
"""
Step 9: Progression Management
Manage workflow progression and determine when to complete.
"""

import json
import os
import logging
from datetime import datetime
from ...plugins.plugin_workflow_integration import BaseWorkflowStep

class Step09ProgressionManagement(BaseWorkflowStep):
    def execute(self) -> dict:
        """
        Execute Step 9: Progression Management
        Determines whether to continue or complete the workflow based on various criteria.
        """
        self.workflow.status_updated.emit("Status: Evaluating workflow progression")
        progression_results = {
            'success': False,
            'workflow_status': 'in_progress',
            'completion_decision': False,
            'quality_assessment': {},
            'project_statistics': {},
            'recommendations': [],
            'errors': []
        }

        try:
            # Assess project quality and completeness
            progression_results['quality_assessment'] = self.assess_project_quality()
            progression_results['project_statistics'] = self.gather_project_statistics()

            # Determine if workflow should continue or complete
            progression_results['completion_decision'] = self.should_complete_workflow(
                progression_results['quality_assessment'],
                progression_results['project_statistics']
            )

            # Get recommendations based on current state
            progression_results['recommendations'] = self.generate_recommendations(
                progression_results['quality_assessment'],
                progression_results['project_statistics'],
                progression_results['completion_decision']
            )

            # Set workflow status
            if progression_results['completion_decision']:
                progression_results['workflow_status'] = 'completed'
                self.workflow.status_updated.emit("Status: Workflow completed successfully")
                if hasattr(self.workflow, 'current_step'):
                    self.workflow.current_step = 10  # Mark as completed
            else:
                progression_results['workflow_status'] = 'ready_for_next_iteration'
                self.workflow.status_updated.emit("Status: Ready for next iteration")
                if hasattr(self.workflow, 'current_step'):
                    self.workflow.current_step = 3  # Return to Step 3 for next iteration

            # Save progression results
            self.save_progression_results(progression_results)

            progression_results['success'] = True
            self.workflow.progress_updated.emit(100)

            self.workflow.log_action(f"Progression management completed: {progression_results['workflow_status']}")

        except Exception as e:
            progression_results['errors'].append(str(e))
            self.workflow.error_occurred.emit(f"Progression management error: {e}")
            self.workflow.log_action(f"Progression management error: {e}")

        return progression_results

    def assess_project_quality(self):
        """Assess overall project quality across multiple dimensions."""
        try:
            quality_assessment = {
                'content_quality': 0,
                'completeness': 0,
                'consistency': 0,
                'user_satisfaction': 0,
                'technical_quality': 0,
                'overall_score': 0
            }

            # Assess content quality
            quality_assessment['content_quality'] = self.assess_content_quality()

            # Assess completeness
            quality_assessment['completeness'] = self.assess_project_completeness()

            # Assess consistency
            quality_assessment['consistency'] = self.assess_project_consistency()

            # Assess user satisfaction (based on review results)
            quality_assessment['user_satisfaction'] = self.assess_user_satisfaction()

            # Assess technical quality
            quality_assessment['technical_quality'] = self.assess_technical_quality()

            # Calculate overall score
            scores = [v for v in quality_assessment.values() if isinstance(v, (int, float))]
            quality_assessment['overall_score'] = sum(scores) / len(scores) if scores else 0

            return quality_assessment

        except Exception as e:
            self.workflow.log_action(f"Error assessing project quality: {e}")
            return {'overall_score': 0}

    def assess_content_quality(self):
        """Assess the quality of the story content."""
        try:
            score = 0

            # Check story file
            story_file = os.path.join(self.workflow.project_path, "story.txt")
            if os.path.exists(story_file):
                with open(story_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                word_count = len(content.split())
                if word_count > 50000:
                    score += 40
                elif word_count > 20000:
                    score += 30
                elif word_count > 10000:
                    score += 20
                elif word_count > 5000:
                    score += 15
                elif word_count > 1000:
                    score += 10

                # Check for placeholders (negative impact)
                placeholder_count = content.lower().count('[placeholder]') + content.lower().count('[todo]')
                if placeholder_count == 0:
                    score += 30
                elif placeholder_count < 5:
                    score += 20
                elif placeholder_count < 10:
                    score += 10

                # Check for structural elements
                if "Chapter" in content:
                    score += 20
                elif content.count('\n\n') > 10:
                    score += 15

            return min(score, 100)

        except Exception as e:
            self.workflow.log_action(f"Error assessing content quality: {e}")
            return 0

    def assess_project_completeness(self):
        """Assess how complete the project is."""
        try:
            score = 0
            required_files = ['story.txt', 'characters.txt', 'synopsis.txt', 'timeline.txt']

            for filename in required_files:
                file_path = os.path.join(self.workflow.project_path, filename)
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    if len(content.strip()) > 100:
                        score += 25
                    elif len(content.strip()) > 50:
                        score += 15
                    elif len(content.strip()) > 10:
                        score += 10

            return min(score, 100)

        except Exception as e:
            self.workflow.log_action(f"Error assessing project completeness: {e}")
            return 0

    def assess_project_consistency(self):
        """Assess consistency across project elements."""
        try:
            score = 0

            # Check for timeline consistency
            timeline_file = os.path.join(self.workflow.project_path, "timeline.txt")
            story_file = os.path.join(self.workflow.project_path, "story.txt")

            if os.path.exists(timeline_file) and os.path.exists(story_file):
                with open(timeline_file, 'r', encoding='utf-8') as f:
                    timeline_content = f.read()
                with open(story_file, 'r', encoding='utf-8') as f:
                    story_content = f.read()

                # Simple consistency check
                if len(timeline_content) > 50 and len(story_content) > 500:
                    score += 30

            # Check for character consistency
            characters_file = os.path.join(self.workflow.project_path, "characters.txt")
            if os.path.exists(characters_file) and os.path.exists(story_file):
                with open(characters_file, 'r', encoding='utf-8') as f:
                    characters_content = f.read()

                # Extract character names and check if they appear in story
                character_names = []
                for line in characters_content.split('\n'):
                    if ':' in line:
                        name = line.split(':')[0].strip()
                        if len(name) > 1 and name not in character_names:
                            character_names.append(name)

                if character_names:
                    mentioned_count = sum(1 for name in character_names if name in story_content)
                    consistency_ratio = mentioned_count / len(character_names)
                    score += int(consistency_ratio * 40)

            # Check metadata consistency
            metadata_file = os.path.join(self.workflow.project_path, "project_metadata.json")
            if os.path.exists(metadata_file):
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)

                    if metadata.get('word_count_target') and metadata.get('current_word_count'):
                        target = metadata['word_count_target']
                        current = metadata['current_word_count']
                        if current >= target * 0.8:  # 80% of target
                            score += 30
                        elif current >= target * 0.5:  # 50% of target
                            score += 20
                        elif current >= target * 0.3:  # 30% of target
                            score += 10

                except:
                    pass

            return min(score, 100)

        except Exception as e:
            self.workflow.log_action(f"Error assessing project consistency: {e}")
            return 0

    def assess_user_satisfaction(self):
        """Assess user satisfaction based on review results."""
        try:
            score = 0

            # Check review results
            review_file = os.path.join(self.workflow.project_path, "review_results.json")
            if os.path.exists(review_file):
                with open(review_file, 'r', encoding='utf-8') as f:
                    review_results = json.load(f)

                # Calculate satisfaction from feedback
                feedback_collected = review_results.get('feedback_collected', [])
                if feedback_collected:
                    total_rating = 0
                    rating_count = 0

                    for feedback in feedback_collected:
                        if 'rating' in feedback:
                            total_rating += feedback['rating']
                            rating_count += 1

                    if rating_count > 0:
                        avg_rating = total_rating / rating_count
                        score = int((avg_rating / 5.0) * 100)

                # Check approval ratio
                approval_given = review_results.get('approval_given', [])
                sections_reviewed = review_results.get('sections_reviewed', [])

                if sections_reviewed:
                    approval_ratio = len(approval_given) / len(sections_reviewed)
                    if approval_ratio > 0.8:
                        score += 20
                    elif approval_ratio > 0.6:
                        score += 15
                    elif approval_ratio > 0.4:
                        score += 10

            return min(score, 100)

        except Exception as e:
            self.workflow.log_action(f"Error assessing user satisfaction: {e}")
            return 0

    def assess_technical_quality(self):
        """Assess technical quality of the project."""
        try:
            score = 0

            # Check file structure
            required_files = ['story.txt', 'characters.txt', 'synopsis.txt', 'timeline.txt']
            existing_files = [f for f in required_files if os.path.exists(os.path.join(self.workflow.project_path, f))]
            file_ratio = len(existing_files) / len(required_files)
            score += int(file_ratio * 40)

            # Check for backup files
            backups_dir = os.path.join(self.workflow.project_path, "backups")
            if os.path.exists(backups_dir):
                backup_files = os.listdir(backups_dir)
                if len(backup_files) > 0:
                    score += 20

            # Check for metadata
            metadata_file = os.path.join(self.workflow.project_path, "project_metadata.json")
            if os.path.exists(metadata_file):
                score += 20

            # Check for logs
            logs_dir = os.path.join(self.workflow.project_path, "logs")
            if os.path.exists(logs_dir):
                score += 20

            return min(score, 100)

        except Exception as e:
            self.workflow.log_action(f"Error assessing technical quality: {e}")
            return 0

    def gather_project_statistics(self):
        """Gather comprehensive project statistics."""
        try:
            stats = {
                'total_word_count': 0,
                'chapter_count': 0,
                'character_count': 0,
                'refinement_iterations': 0,
                'review_sessions': 0,
                'quality_improvements': 0,
                'time_spent': 0,
                'files_created': 0
            }

            # Count words in story
            story_file = os.path.join(self.workflow.project_path, "story.txt")
            if os.path.exists(story_file):
                with open(story_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    stats['total_word_count'] = len(content.split())
                    stats['chapter_count'] = content.count("Chapter")

            # Count characters
            characters_file = os.path.join(self.workflow.project_path, "characters.txt")
            if os.path.exists(characters_file):
                with open(characters_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    stats['character_count'] = len([line for line in content.split('\n') if ':' in line])

            # Count refinement iterations
            refinement_file = os.path.join(self.workflow.project_path, "refinement_results.json")
            if os.path.exists(refinement_file):
                with open(refinement_file, 'r', encoding='utf-8') as f:
                    refinement_data = json.load(f)
                    stats['refinement_iterations'] = refinement_data.get('iterations_performed', 0)

            # Count review sessions
            review_file = os.path.join(self.workflow.project_path, "review_results.json")
            if os.path.exists(review_file):
                with open(review_file, 'r', encoding='utf-8') as f:
                    review_data = json.load(f)
                    stats['review_sessions'] = len(review_data.get('sections_reviewed', []))

            # Count files
            try:
                all_files = []
                for root, dirs, files in os.walk(self.workflow.project_path):
                    all_files.extend([os.path.join(root, f) for f in files])
                stats['files_created'] = len(all_files)
            except:
                stats['files_created'] = 0

            return stats

        except Exception as e:
            self.workflow.log_action(f"Error gathering project statistics: {e}")
            return {}

    def should_complete_workflow(self, quality_assessment, project_statistics):
        """Determine if the workflow should be completed."""
        try:
            # Completion criteria
            criteria_met = 0
            total_criteria = 6

            # 1. Minimum quality threshold
            if quality_assessment.get('overall_score', 0) >= 70:
                criteria_met += 1

            # 2. Minimum word count
            if project_statistics.get('total_word_count', 0) >= 10000:
                criteria_met += 1

            # 3. User satisfaction
            if quality_assessment.get('user_satisfaction', 0) >= 60:
                criteria_met += 1

            # 4. Content completeness
            if quality_assessment.get('completeness', 0) >= 80:
                criteria_met += 1

            # 5. Multiple refinement iterations
            if project_statistics.get('refinement_iterations', 0) >= 2:
                criteria_met += 1

            # 6. Review sessions completed
            if project_statistics.get('review_sessions', 0) >= 3:
                criteria_met += 1

            # Require at least 4 out of 6 criteria
            completion_threshold = 4
            return criteria_met >= completion_threshold

        except Exception as e:
            self.workflow.log_action(f"Error determining completion: {e}")
            return False

    def generate_recommendations(self, quality_assessment, project_statistics, completion_decision):
        """Generate recommendations based on current project state."""
        try:
            recommendations = []

            if completion_decision:
                recommendations.append("✅ Project meets completion criteria")
                recommendations.append("📋 Consider final proofreading and formatting")
                recommendations.append("💾 Create final backup of all project files")
                recommendations.append("📊 Review project statistics for future reference")
            else:
                # Identify areas for improvement
                if quality_assessment.get('content_quality', 0) < 60:
                    recommendations.append("📝 Focus on expanding story content and reducing placeholders")

                if quality_assessment.get('completeness', 0) < 70:
                    recommendations.append("📋 Complete missing project files (characters, synopsis, timeline)")

                if quality_assessment.get('user_satisfaction', 0) < 50:
                    recommendations.append("👥 Address user feedback in next review cycle")

                if project_statistics.get('total_word_count', 0) < 5000:
                    recommendations.append("📊 Increase overall word count through content development")

                if project_statistics.get('refinement_iterations', 0) < 2:
                    recommendations.append("🔄 Perform additional refinement iterations")

                if not recommendations:
                    recommendations.append("🔄 Continue with next iteration to further improve quality")

            return recommendations

        except Exception as e:
            self.workflow.log_action(f"Error generating recommendations: {e}")
            return ["Continue workflow development"]

    def save_progression_results(self, progression_results):
        """Save progression management results to disk."""
        try:
            progression_file = os.path.join(self.workflow.project_path, "progression_results.json")

            # Add timestamp
            progression_results['timestamp'] = datetime.now().isoformat()

            with open(progression_file, 'w', encoding='utf-8') as f:
                json.dump(progression_results, f, indent=2, ensure_ascii=False)

            self.workflow.log_action(f"Progression results saved to {progression_file}")

        except Exception as e:
            self.workflow.log_action(f"Error saving progression results: {e}")

    def validate_prerequisites(self) -> bool:
        """Validate prerequisites for Step 9."""
        # Check if Step 8 completed successfully
        refinement_file = os.path.join(self.workflow.project_path, "refinement_results.json")
        if not os.path.exists(refinement_file):
            self.workflow.log_action("Step 8 data not found", "ERROR")
            return False

        return True

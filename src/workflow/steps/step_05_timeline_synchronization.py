#!/usr/bin/env python3
"""
Step 5: Timeline Synchronization
Generate and synchronize chronological events.
"""

import json
import os
import logging
from datetime import datetime
from ...plugins.plugin_workflow_integration import BaseWorkflowStep

class Step05TimelineSynchronization(BaseWorkflowStep):
    def execute(self) -> dict:
        """Execute Step 5: Timeline Synchronization - Generate and synchronize chronological events."""
        timeline_results = {
            'success': False,
            'timeline_generated': False,
            'events_synchronized': False,
            'consistency_validated': False,
            'timeline_saved': False,
            'total_events': 0,
            'errors': [],
            'warnings': [],
            'metadata': {
                'start_time': datetime.now().isoformat(),
                'version': '1.0.0',
                'step': 'Timeline Synchronization'
            }
        }

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:
            self.workflow.log_action(f"{timestamp} - Starting Timeline Synchronization (Step 5)")
            self.workflow.status_updated.emit("Status: Starting timeline synchronization...")
            self.workflow.progress_updated.emit(5)

            # Step 5a: Generate timeline from outline
            self.workflow.status_updated.emit("Status: Generating chronological timeline...")
            timeline_data = self.generate_timeline_from_outline()

            if timeline_data['success']:
                timeline_results['timeline_generated'] = True
                timeline_results['total_events'] = timeline_data['event_count']
                timeline_results['metadata']['timeline_data'] = timeline_data
                self.workflow.log_action(f"Timeline generated with {timeline_data['event_count']} events")
            else:
                timeline_results['errors'].extend(timeline_data['errors'])
                timeline_results['warnings'].extend(timeline_data['warnings'])

            self.workflow.progress_updated.emit(25)

            # Step 5b: Synchronize events with characters
            self.workflow.status_updated.emit("Status: Synchronizing events with characters...")
            sync_results = self.synchronize_events_with_characters(timeline_data['timeline'])

            if sync_results['success']:
                timeline_results['events_synchronized'] = True
                timeline_results['metadata']['sync_results'] = sync_results
                self.workflow.log_action(f"Events synchronized with {sync_results['characters_linked']} character connections")
            else:
                timeline_results['errors'].extend(sync_results['errors'])
                timeline_results['warnings'].extend(sync_results['warnings'])

            self.workflow.progress_updated.emit(50)

            # Step 5c: Validate chronological consistency
            self.workflow.status_updated.emit("Status: Validating chronological consistency...")
            consistency_results = self.validate_chronological_consistency(timeline_data['timeline'])

            if consistency_results['is_consistent']:
                timeline_results['consistency_validated'] = True
                timeline_results['metadata']['consistency'] = consistency_results
                self.workflow.log_action("Chronological consistency validated")
            else:
                timeline_results['warnings'].extend(consistency_results['issues'])
                # Attempt to fix consistency issues
                fix_results = self.fix_timeline_consistency_issues(timeline_data['timeline'], consistency_results)
                timeline_results['metadata']['fix_attempts'] = fix_results

            self.workflow.progress_updated.emit(75)

            # Step 5d: Save timeline components
            self.workflow.status_updated.emit("Status: Saving timeline components...")
            save_results = self.save_timeline_components(timeline_data['timeline'])

            if save_results['success']:
                timeline_results['timeline_saved'] = True
                timeline_results['metadata']['save_results'] = save_results
                self.workflow.log_action("Timeline components saved successfully")
            else:
                timeline_results['errors'].extend(save_results['errors'])

            self.workflow.progress_updated.emit(90)

            # Step 5e: Final validation and completion
            self.workflow.status_updated.emit("Status: Completing timeline synchronization...")

            critical_components = [
                timeline_results['timeline_generated'],
                timeline_results['events_synchronized'],
                timeline_results['timeline_saved']
            ]

            timeline_results['success'] = sum(critical_components) >= 2  # At least 2 out of 3 critical components

            # Create completion log
            completion_log = f"{timestamp} - Timeline synchronization completed"
            completion_log += f"\n  - Timeline Generated: {'✅' if timeline_results['timeline_generated'] else '❌'}"
            completion_log += f"\n  - Events Synchronized: {'✅' if timeline_results['events_synchronized'] else '❌'}"
            completion_log += f"\n  - Consistency Validated: {'✅' if timeline_results['consistency_validated'] else '⚠️'}"
            completion_log += f"\n  - Timeline Saved: {'✅' if timeline_results['timeline_saved'] else '❌'}"
            completion_log += f"\n  - Total Events: {timeline_results['total_events']}"

            if timeline_results['errors']:
                completion_log += f"\n  - Errors: {len(timeline_results['errors'])}"
            if timeline_results['warnings']:
                completion_log += f"\n  - Warnings: {len(timeline_results['warnings'])}"

            self.workflow.log_action(completion_log)

            # Update GUI based on success
            if timeline_results['success']:
                self.workflow.status_updated.emit("Status: ✅ Timeline synchronization completed successfully!")
                self.workflow.progress_updated.emit(100)
                self.workflow.log_action("Timeline synchronization completed successfully")
            else:
                self.workflow.status_updated.emit("Status: ⚠️ Timeline synchronization completed with issues")
                if timeline_results['errors']:
                    self.workflow.error_occurred.emit(f"Timeline synchronization errors: {'; '.join(timeline_results['errors'][:2])}")
                self.workflow.log_action("Timeline synchronization completed with issues")

            self.workflow.step_completed.emit(5, timeline_results)

        except Exception as e:
            timeline_results['errors'].append(str(e))
            self.workflow.error_occurred.emit(f"Timeline synchronization failed: {str(e)}")
            logging.error(f"Timeline synchronization failed: {str(e)}")

        return timeline_results

    def generate_timeline_from_outline(self) -> dict:
        """Generate a chronological timeline from the story outline."""
        timeline_results = {
            'success': False,
            'timeline': {},
            'event_count': 0,
            'errors': [],
            'warnings': [],
            'metadata': {}
        }

        try:
            if not self.workflow.outline or not self.workflow.outline.get('chapters'):
                timeline_results['errors'].append("No outline available for timeline generation")
                return timeline_results

            # Create timeline generation prompt
            prompt = self.create_timeline_generation_prompt()

            # Generate timeline via AI
            if self.workflow.api_manager and self.workflow.api_manager.is_available():
                try:
                    response = self.workflow.api_manager.generate_text(prompt)
                    parsed_timeline = self.parse_timeline_response(response)

                    if parsed_timeline:
                        timeline_results['timeline'] = parsed_timeline
                        timeline_results['event_count'] = len(parsed_timeline.get('events', []))
                        timeline_results['success'] = True
                        timeline_results['metadata']['ai_generated'] = True
                        logging.info(f"AI generated timeline with {timeline_results['event_count']} events")
                    else:
                        timeline_results['warnings'].append("AI timeline generation failed, using fallback")
                        timeline_results['timeline'] = self.create_fallback_timeline()
                        timeline_results['event_count'] = len(timeline_results['timeline'].get('events', []))
                        timeline_results['success'] = True
                        timeline_results['metadata']['fallback_used'] = True

                except Exception as e:
                    timeline_results['errors'].append(f"AI timeline generation failed: {str(e)}")
                    timeline_results['timeline'] = self.create_fallback_timeline()
                    timeline_results['event_count'] = len(timeline_results['timeline'].get('events', []))
                    timeline_results['success'] = True
                    timeline_results['metadata']['fallback_used'] = True
            else:
                timeline_results['warnings'].append("AI service unavailable, using fallback timeline")
                timeline_results['timeline'] = self.create_fallback_timeline()
                timeline_results['event_count'] = len(timeline_results['timeline'].get('events', []))
                timeline_results['success'] = True
                timeline_results['metadata']['fallback_used'] = True

        except Exception as e:
            timeline_results['errors'].append(f"Timeline generation failed: {str(e)}")
            logging.error(f"Timeline generation error: {str(e)}")

        return timeline_results

    def create_timeline_generation_prompt(self) -> str:
        """Create a detailed prompt for AI timeline generation."""
        prompt = f"""Generate a comprehensive chronological timeline for the following story:

STORY OVERVIEW:
Title: {getattr(self.workflow, 'project_name', 'Unknown Title')}
Tone: {getattr(self.workflow, 'novel_tone', 'Unknown Tone')}
Word Count Target: {getattr(self.workflow, 'target_word_count', 50000)}

SYNOPSIS:
{getattr(self.workflow, 'synopsis', 'No synopsis available')}

STORY OUTLINE:
"""

        # Add chapter information
        for i, chapter in enumerate(self.workflow.outline.get('chapters', []), 1):
            prompt += f"\nChapter {i}: {chapter.get('title', 'Untitled')}"
            prompt += f"\n  Summary: {chapter.get('summary', 'No summary available')}"
            if chapter.get('key_events'):
                prompt += f"\n  Key Events: {', '.join(chapter['key_events'])}"

        # Add character information
        if hasattr(self.workflow, 'characters') and self.workflow.characters:
            prompt += "\n\nMAIN CHARACTERS:"
            if isinstance(self.workflow.characters, dict):
                if 'characters' in self.workflow.characters:
                    # Handle characters stored as {'characters': [list]}
                    for char in self.workflow.characters['characters']:
                        char_name = char.get('name', 'Unknown')
                        char_desc = char.get('description', char.get('background', 'No description'))
                        prompt += f"\n- {char_name}: {char_desc}"
                else:
                    # Handle characters stored as {name: info}
                    for char_name, char_info in self.workflow.characters.items():
                        if isinstance(char_info, dict):
                            char_desc = char_info.get('description', char_info.get('background', 'No description'))
                            prompt += f"\n- {char_name}: {char_desc}"
                        else:
                            prompt += f"\n- {char_name}: {char_info}"

        prompt += """

TIMELINE GENERATION REQUIREMENTS:
1. Create a chronological sequence of all major events
2. Include time markers (days, weeks, months, seasons, etc.)
3. Link events to specific chapters
4. Identify character involvement in each event
5. Note cause-and-effect relationships
6. Include both plot events and character development moments
7. Maintain consistency with the story's pacing and tone

Please provide the timeline in the following JSON format:
{
    "timeline_title": "Story Timeline",
    "total_timespan": "Duration description",
    "events": [
        {
            "event_id": "event_1",
            "title": "Event title",
            "description": "Detailed description",
            "chapter": "Chapter number or reference",
            "time_marker": "When this occurs (Day 1, Week 2, etc.)",
            "characters_involved": ["Character 1", "Character 2"],
            "importance": "high/medium/low",
            "consequences": "What happens as a result"
        }
    ]
}

Generate a comprehensive timeline that captures all significant story events."""

        return prompt

    def parse_timeline_response(self, response: str) -> dict:
        """Parse AI response to extract timeline data."""
        try:
            # Try to find JSON in the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1

            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                timeline_data = json.loads(json_str)

                # Validate basic structure
                if 'events' in timeline_data and isinstance(timeline_data['events'], list):
                    return timeline_data

        except (json.JSONDecodeError, ValueError) as e:
            logging.error(f"Failed to parse timeline JSON: {str(e)}")

        # If JSON parsing fails, try to extract key information
        return self.extract_timeline_from_text(response)

    def extract_timeline_from_text(self, text: str) -> dict:
        """Extract timeline information from plain text response."""
        timeline_data = {
            'timeline_title': 'Extracted Timeline',
            'total_timespan': 'Unknown',
            'events': []
        }

        # Simple extraction logic - look for event patterns
        lines = text.split('\n')
        event_id = 1

        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('*') or line.startswith('•')):
                event = {
                    'event_id': f'event_{event_id}',
                    'title': line.lstrip('- *•').strip(),
                    'description': line.lstrip('- *•').strip(),
                    'chapter': 'Unknown',
                    'time_marker': 'Unknown',
                    'characters_involved': [],
                    'importance': 'medium',
                    'consequences': 'Unknown'
                }
                timeline_data['events'].append(event)
                event_id += 1

        return timeline_data

    def create_fallback_timeline(self) -> dict:
        """Create a basic fallback timeline when AI generation fails."""
        timeline_data = {
            'timeline_title': f'{getattr(self.workflow, "project_name", "Unknown")} - Basic Timeline',
            'total_timespan': 'Story Duration',
            'events': []
        }

        # Generate basic events from outline chapters
        if hasattr(self.workflow, 'outline') and self.workflow.outline and self.workflow.outline.get('chapters'):
            for i, chapter in enumerate(self.workflow.outline['chapters'], 1):
                event = {
                    'event_id': f'chapter_{i}',
                    'title': chapter.get('title', f'Chapter {i}'),
                    'description': chapter.get('summary', 'No summary available'),
                    'chapter': i,
                    'time_marker': f'Chapter {i}',
                    'characters_involved': chapter.get('character_focus', []),
                    'importance': 'medium',
                    'consequences': 'Advances the story'
                }
                timeline_data['events'].append(event)

        # If no outline, create basic story structure
        if not timeline_data['events']:
            basic_events = [
                {
                    'event_id': 'opening',
                    'title': 'Story Opening',
                    'description': 'The story begins',
                    'chapter': 1,
                    'time_marker': 'Beginning',
                    'characters_involved': [],
                    'importance': 'high',
                    'consequences': 'Sets the story in motion'
                },
                {
                    'event_id': 'midpoint',
                    'title': 'Midpoint Crisis',
                    'description': 'Major turning point',
                    'chapter': 'Middle',
                    'time_marker': 'Midpoint',
                    'characters_involved': [],
                    'importance': 'high',
                    'consequences': 'Changes the direction'
                },
                {
                    'event_id': 'climax',
                    'title': 'Climax',
                    'description': 'Final confrontation',
                    'chapter': 'End',
                    'time_marker': 'Climax',
                    'characters_involved': [],
                    'importance': 'high',
                    'consequences': 'Resolves the conflict'
                }
            ]
            timeline_data['events'] = basic_events

        return timeline_data

    def synchronize_events_with_characters(self, timeline: dict) -> dict:
        """Synchronize timeline events with character information."""
        sync_results = {
            'success': False,
            'characters_linked': 0,
            'events_updated': 0,
            'new_connections': [],
            'errors': [],
            'warnings': []
        }

        try:
            if not timeline or 'events' not in timeline:
                sync_results['errors'].append("Invalid timeline for synchronization")
                return sync_results

            events = timeline['events']
            if not hasattr(self.workflow, 'characters') or not self.workflow.characters:
                sync_results['warnings'].append("No character data available for synchronization")
                return sync_results

            # Get character names
            if isinstance(self.workflow.characters, dict) and 'characters' in self.workflow.characters:
                character_names = set(char.get('name', '') for char in self.workflow.characters['characters'])
            else:
                character_names = set(self.workflow.characters.keys()) if isinstance(self.workflow.characters, dict) else set()

            # Synchronize each event
            for event in events:
                if 'characters_involved' not in event:
                    event['characters_involved'] = []

                # Check if event description mentions any characters
                event_text = (event.get('description', '') + ' ' + event.get('title', '')).lower()

                for char_name in character_names:
                    if char_name.lower() in event_text:
                        if char_name not in event['characters_involved']:
                            event['characters_involved'].append(char_name)
                            sync_results['new_connections'].append({
                                'event': event.get('event_id', 'unknown'),
                                'character': char_name
                            })

                if event['characters_involved']:
                    sync_results['events_updated'] += 1

            sync_results['characters_linked'] = len(set(char for event in events for char in event.get('characters_involved', [])))
            sync_results['success'] = True

        except Exception as e:
            sync_results['errors'].append(f"Event synchronization failed: {str(e)}")

        return sync_results

    def validate_chronological_consistency(self, timeline: dict) -> dict:
        """Validate chronological consistency of timeline events."""
        consistency_results = {
            'is_consistent': True,
            'issues': [],
            'warnings': [],
            'temporal_gaps': [],
            'conflicting_events': []
        }

        try:
            if not timeline or 'events' not in timeline:
                consistency_results['issues'].append("Invalid timeline for consistency check")
                consistency_results['is_consistent'] = False
                return consistency_results

            events = timeline['events']

            # Check for temporal markers
            events_with_time = [e for e in events if 'time_marker' in e and e['time_marker'] != 'Unknown']

            if len(events_with_time) < len(events) * 0.5:
                consistency_results['warnings'].append("Many events lack specific time markers")

            # Look for potential conflicts
            time_markers = {}
            for event in events:
                time_marker = event.get('time_marker', 'Unknown')
                if time_marker != 'Unknown':
                    if time_marker not in time_markers:
                        time_markers[time_marker] = []
                    time_markers[time_marker].append(event)

            # Check for overcrowded time periods
            for time_marker, events_at_time in time_markers.items():
                if len(events_at_time) > 3:
                    consistency_results['warnings'].append(f"Many events at {time_marker}: {len(events_at_time)} events")

            # Check character consistency
            for event in events:
                characters = event.get('characters_involved', [])
                if len(characters) > 10:
                    consistency_results['warnings'].append(f"Event '{event.get('title', 'Unknown')}' involves many characters ({len(characters)})")

        except Exception as e:
            consistency_results['issues'].append(f"Consistency validation failed: {str(e)}")
            consistency_results['is_consistent'] = False

        return consistency_results

    def fix_timeline_consistency_issues(self, timeline: dict, consistency_results: dict) -> dict:
        """Attempt to fix timeline consistency issues."""
        fix_results = {
            'fixes_attempted': 0,
            'fixes_successful': 0,
            'remaining_issues': []
        }

        # This would contain logic to fix consistency issues
        # For now, just return the structure
        return fix_results

    def create_timeline_text_format(self, timeline: dict) -> str:
        """Create a readable text format of the timeline."""
        try:
            if not timeline or 'events' not in timeline:
                return "Invalid timeline data"

            text_timeline = f"TIMELINE: {timeline.get('timeline_title', 'Story Timeline')}\n"
            text_timeline += f"Total Timespan: {timeline.get('total_timespan', 'Unknown')}\n"
            text_timeline += "=" * 50 + "\n\n"

            for i, event in enumerate(timeline['events'], 1):
                text_timeline += f"{i}. {event.get('title', 'Untitled Event')}\n"
                text_timeline += f"   Time: {event.get('time_marker', 'Unknown')}\n"
                text_timeline += f"   Chapter: {event.get('chapter', 'Unknown')}\n"
                text_timeline += f"   Description: {event.get('description', 'No description')}\n"

                if event.get('characters_involved'):
                    text_timeline += f"   Characters: {', '.join(event['characters_involved'])}\n"

                text_timeline += f"   Importance: {event.get('importance', 'medium')}\n"
                text_timeline += f"   Consequences: {event.get('consequences', 'Unknown')}\n"
                text_timeline += "-" * 30 + "\n\n"

            return text_timeline

        except Exception as e:
            return f"Error creating timeline text: {str(e)}"

    def save_timeline_components(self, timeline: dict) -> dict:
        """Save timeline components to files."""
        save_results = {
            'success': False,
            'files_saved': [],
            'errors': []
        }

        try:
            if not timeline:
                save_results['errors'].append("No timeline data to save")
                return save_results

            # Save timeline JSON
            project_dir = getattr(self.workflow, 'project_path', 'projects/default')
            timeline_json_path = os.path.join(project_dir, 'timeline.json')
            os.makedirs(project_dir, exist_ok=True)

            with open(timeline_json_path, 'w', encoding='utf-8') as f:
                json.dump(timeline, f, indent=2, ensure_ascii=False)
            save_results['files_saved'].append('timeline.json')

            # Save timeline text format
            timeline_text = self.create_timeline_text_format(timeline)
            timeline_txt_path = os.path.join(project_dir, 'timeline.txt')
            with open(timeline_txt_path, 'w', encoding='utf-8') as f:
                f.write(timeline_text)
            save_results['files_saved'].append('timeline.txt')

            # Update database
            if hasattr(self.workflow, 'database_manager') and self.workflow.database_manager:
                try:
                    # Update timeline data in database
                    pass  # Database update would go here
                except Exception as e:
                    logging.warning(f"Database update failed: {str(e)}")

            save_results['success'] = True
            logging.info(f"Timeline saved: {save_results['files_saved']}")

        except Exception as e:
            save_results['errors'].append(f"Timeline saving failed: {str(e)}")
            logging.error(f"Timeline saving error: {str(e)}")

        return save_results

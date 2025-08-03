#!/usr/bin/env python3
"""
Step 4: Structural Planning
Comprehensive structural planning and outline creation.
"""

import json
import os
import logging
from .base_step import BaseWorkflowStep

class Step04StructuralPlanning(BaseWorkflowStep):
    def execute(self) -> dict:
        """Execute Step 4: Structural Planning Automation with comprehensive component generation."""
        planning_results = {
            'success': False,
            'outline_generated': False,
            'characters_generated': False,
            'world_details_generated': False,
            'components_saved': False,
            'validation_passed': False,
            'errors': [],
            'warnings': [],
            'metadata': {},
            'generated_components': {}
        }

        try:
            self.workflow.status_updated.emit("Status: Starting structural planning automation...")
            self.workflow.progress_updated.emit(0)

            # Generate 25-chapter outline
            self.workflow.status_updated.emit("Status: Generating 25-chapter outline...")
            outline_result = self.generate_outline()
            planning_results['outline_generated'] = outline_result['success']
            planning_results['generated_components']['outline'] = outline_result

            if outline_result['success']:
                self.workflow.outline = outline_result['outline']
            else:
                planning_results['errors'].extend(outline_result['errors'])

            self.workflow.progress_updated.emit(33)

            # Generate character profiles
            self.workflow.status_updated.emit("Status: Creating character profiles...")
            character_result = self.generate_characters()
            planning_results['characters_generated'] = character_result['success']
            planning_results['generated_components']['characters'] = character_result

            if character_result['success']:
                self.workflow.characters = character_result['characters']
            else:
                planning_results['errors'].extend(character_result['errors'])

            self.workflow.progress_updated.emit(66)

            # Generate world details
            self.workflow.status_updated.emit("Status: Building world details...")
            world_result = self.generate_world()
            planning_results['world_details_generated'] = world_result['success']
            planning_results['generated_components']['world_details'] = world_result

            if world_result['success']:
                self.workflow.world_details = world_result['world_details']
            else:
                planning_results['errors'].extend(world_result['errors'])

            self.workflow.progress_updated.emit(85)

            # Save all components
            save_result = self.save_structural_components(planning_results)
            planning_results['components_saved'] = save_result['success']

            if not save_result['success']:
                planning_results['errors'].extend(save_result['errors'])

            self.workflow.progress_updated.emit(100)

            # Determine success
            planning_results['success'] = (
                planning_results['outline_generated'] and
                planning_results['characters_generated'] and
                planning_results['world_details_generated'] and
                planning_results['components_saved']
            )

            if planning_results['success']:
                self.workflow.status_updated.emit("Status: Structural planning completed successfully!")
                self.workflow.log_action("Structural planning completed successfully")
                self.workflow.current_step = 5
            else:
                self.workflow.status_updated.emit("Status: Structural planning completed with issues")
                self.workflow.log_action("Structural planning completed with issues")

            self.workflow.step_completed.emit(4, planning_results)

        except Exception as e:
            planning_results['errors'].append(str(e))
            self.workflow.error_occurred.emit(f"Structural planning failed: {str(e)}")
            logging.error(f"Structural planning failed: {str(e)}")

        return planning_results

    def generate_outline(self) -> dict:
        """Generate a comprehensive 25-chapter outline."""
        result = {
            'success': False,
            'outline': {},
            'errors': []
        }

        try:
            if self.workflow.api_manager:
                prompt = f"""Create a detailed 25-chapter outline for a {self.workflow.genre} novel.

NOVEL DETAILS:
- Genre: {self.workflow.genre}
- Tone: {self.workflow.novel_tone}
- Synopsis: {self.workflow.synopsis}
- Target Length: {self.workflow.target_word_count} words

REQUIREMENTS:
- Exactly 25 chapters
- Each chapter 8,000-12,000 words
- Clear three-act structure
- Character development arcs
- Rising action and climax

Format as JSON with chapters array containing:
- chapter_number
- title
- summary
- key_events
- character_focus
- estimated_words

Return only the JSON, no additional text."""

                response = self.workflow.api_manager.generate_text(prompt)

                if response:
                    try:
                        outline_data = json.loads(response)
                        if self.validate_outline(outline_data):
                            result['success'] = True
                            result['outline'] = outline_data
                        else:
                            result['errors'].append("Invalid outline format")
                    except json.JSONDecodeError:
                        result['errors'].append("Invalid JSON response")
                else:
                    result['errors'].append("Empty AI response")

            # Fallback outline if AI fails
            if not result['success']:
                fallback_outline = self.create_fallback_outline()
                result['success'] = True
                result['outline'] = fallback_outline

        except Exception as e:
            result['errors'].append(str(e))

        return result

    def generate_characters(self) -> dict:
        """Generate character profiles."""
        result = {
            'success': False,
            'characters': {},
            'errors': []
        }

        try:
            if self.workflow.api_manager:
                prompt = f"""Create detailed character profiles for a {self.workflow.genre} novel.

NOVEL DETAILS:
- Genre: {self.workflow.genre}
- Synopsis: {self.workflow.synopsis}

REQUIREMENTS:
- 5-7 main characters
- Include protagonist, antagonist, and supporting characters
- Physical and personality descriptions
- Character arcs and motivations

Format as JSON with characters array containing:
- name
- role (protagonist/antagonist/supporting)
- physical_description
- personality_traits
- background
- motivations
- character_arc

Return only the JSON, no additional text."""

                response = self.workflow.api_manager.generate_text(prompt)

                if response:
                    try:
                        character_data = json.loads(response)
                        result['success'] = True
                        result['characters'] = character_data
                    except json.JSONDecodeError:
                        result['errors'].append("Invalid JSON response")
                else:
                    result['errors'].append("Empty AI response")

            # Fallback characters if AI fails
            if not result['success']:
                fallback_characters = self.create_fallback_characters()
                result['success'] = True
                result['characters'] = fallback_characters

        except Exception as e:
            result['errors'].append(str(e))

        return result

    def generate_world(self) -> dict:
        """Generate world details."""
        result = {
            'success': False,
            'world_details': {},
            'errors': []
        }

        try:
            if self.workflow.api_manager:
                prompt = f"""Create detailed world-building for a {self.workflow.genre} novel.

NOVEL DETAILS:
- Genre: {self.workflow.genre}
- Synopsis: {self.workflow.synopsis}

REQUIREMENTS:
- Setting descriptions
- Cultural elements
- Rules and systems
- Atmosphere and tone

Format as JSON with world elements containing:
- setting_name
- description
- culture
- rules
- atmosphere
- unique_features

Return only the JSON, no additional text."""

                response = self.workflow.api_manager.generate_text(prompt)

                if response:
                    try:
                        world_data = json.loads(response)
                        result['success'] = True
                        result['world_details'] = world_data
                    except json.JSONDecodeError:
                        result['errors'].append("Invalid JSON response")
                else:
                    result['errors'].append("Empty AI response")

            # Fallback world if AI fails
            if not result['success']:
                fallback_world = self.create_fallback_world()
                result['success'] = True
                result['world_details'] = fallback_world

        except Exception as e:
            result['errors'].append(str(e))

        return result

    def validate_outline(self, outline: dict) -> bool:
        """Validate outline structure."""
        try:
            if not isinstance(outline, dict):
                return False

            chapters = outline.get('chapters', [])
            if not isinstance(chapters, list) or len(chapters) != 25:
                return False

            for chapter in chapters:
                if not all(key in chapter for key in ['chapter_number', 'title', 'summary']):
                    return False

            return True

        except Exception:
            return False

    def create_fallback_outline(self) -> dict:
        """Create a basic fallback outline."""
        outline = {
            'title': f'{self.workflow.project_name} - Outline',
            'total_chapters': 25,
            'chapters': []
        }

        for i in range(1, 26):
            chapter = {
                'chapter_number': i,
                'title': f'Chapter {i}',
                'summary': f'Chapter {i} continues the story development.',
                'key_events': ['Story progression'],
                'character_focus': ['Main characters'],
                'estimated_words': 10000
            }
            outline['chapters'].append(chapter)

        return outline

    def create_fallback_characters(self) -> dict:
        """Create basic fallback characters."""
        characters = {
            'characters': [
                {
                    'name': 'Protagonist',
                    'role': 'protagonist',
                    'physical_description': 'To be determined',
                    'personality_traits': ['Determined', 'Brave'],
                    'background': 'Background to be developed',
                    'motivations': ['Main goal achievement'],
                    'character_arc': 'Growth throughout the story'
                },
                {
                    'name': 'Antagonist',
                    'role': 'antagonist',
                    'physical_description': 'To be determined',
                    'personality_traits': ['Cunning', 'Powerful'],
                    'background': 'Background to be developed',
                    'motivations': ['Opposition to protagonist'],
                    'character_arc': 'Conflict escalation'
                }
            ]
        }

        return characters

    def create_fallback_world(self) -> dict:
        """Create basic fallback world details."""
        world = {
            'setting_name': f'{self.workflow.project_name} World',
            'description': 'World setting to be developed',
            'culture': 'Cultural elements to be defined',
            'rules': 'World rules to be established',
            'atmosphere': self.workflow.novel_tone,
            'unique_features': ['Feature 1', 'Feature 2']
        }

        return world

    def save_structural_components(self, planning_results: dict) -> dict:
        """Save all structural planning components."""
        save_result = {
            'success': False,
            'saved_components': [],
            'errors': []
        }

        try:
            # Save outline
            if self.workflow.outline:
                outline_path = os.path.join(self.workflow.project_path, "metadata", "outline.json")
                with open(outline_path, 'w', encoding='utf-8') as f:
                    json.dump(self.workflow.outline, f, indent=2, ensure_ascii=False)
                save_result['saved_components'].append('outline')

            # Save characters
            if self.workflow.characters:
                characters_path = os.path.join(self.workflow.project_path, "metadata", "characters.json")
                with open(characters_path, 'w', encoding='utf-8') as f:
                    json.dump(self.workflow.characters, f, indent=2, ensure_ascii=False)
                save_result['saved_components'].append('characters')

            # Save world details
            if self.workflow.world_details:
                world_path = os.path.join(self.workflow.project_path, "metadata", "world_details.json")
                with open(world_path, 'w', encoding='utf-8') as f:
                    json.dump(self.workflow.world_details, f, indent=2, ensure_ascii=False)
                save_result['saved_components'].append('world_details')

            # Save planning results
            planning_path = os.path.join(self.workflow.project_path, "metadata", "structural_planning.json")
            with open(planning_path, 'w', encoding='utf-8') as f:
                json.dump(planning_results, f, indent=2, ensure_ascii=False)
            save_result['saved_components'].append('planning_results')

            save_result['success'] = len(save_result['saved_components']) > 0

        except Exception as e:
            save_result['errors'].append(str(e))

        return save_result

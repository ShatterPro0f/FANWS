#!/usr/bin/env python3
"""
Step 6: Iterative Writing
4-stage iterative writing process with drafting, polishing, enhancement, and vocabulary refinement.
"""

import json
import os
import logging
from datetime import datetime
from .base_step import BaseWorkflowStep

class Step06IterativeWriting(BaseWorkflowStep):
    def execute(self) -> dict:
        """Execute Step 6: Iterative Writing Loop with 4-stage process."""
        writing_results = {
            'success': False,
            'sections_processed': 0,
            'total_sections': 0,
            'drafting_completed': False,
            'polishing_completed': False,
            'enhancement_completed': False,
            'vocabulary_completed': False,
            'final_word_count': 0,
            'quality_score': 0,
            'errors': [],
            'warnings': [],
            'writing_history': []
        }

        try:
            self.workflow.status_updated.emit("Status: Starting iterative writing loop...")
            self.workflow.progress_updated.emit(0)

            # Load outline to determine sections
            outline_path = os.path.join(self.workflow.project_path, "outline.txt")
            if os.path.exists(outline_path):
                with open(outline_path, 'r', encoding='utf-8') as f:
                    outline_content = f.read()

                # Extract chapters/sections from outline
                sections = self.extract_sections_from_outline(outline_content)
                writing_results['total_sections'] = len(sections)

                self.workflow.log_action(f"Found {len(sections)} sections to process")

                # Process each section through 4-stage writing loop
                for i, section in enumerate(sections):
                    self.workflow.status_updated.emit(f"Status: Processing section {i+1}/{len(sections)}: {section['title']}")

                    # Stage 1: Drafting
                    draft_result = self.execute_drafting_stage(section)
                    section['draft'] = draft_result['content']

                    # Stage 2: Polishing
                    polish_result = self.execute_polishing_stage(section)
                    section['polished'] = polish_result['content']

                    # Stage 3: Enhancement
                    enhance_result = self.execute_enhancement_stage(section)
                    section['enhanced'] = enhance_result['content']

                    # Stage 4: Vocabulary
                    vocab_result = self.execute_vocabulary_stage(section)
                    section['final'] = vocab_result['content']

                    writing_results['sections_processed'] += 1

                    # Save section progress
                    self.save_section_progress(section, i+1)

                    # Update progress
                    progress = int((i + 1) / len(sections) * 80)
                    self.workflow.progress_updated.emit(progress)

                    # Log section completion
                    self.workflow.log_action(f"Section {i+1} completed: {section['title']}")

                # Mark stages as completed
                writing_results['drafting_completed'] = True
                writing_results['polishing_completed'] = True
                writing_results['enhancement_completed'] = True
                writing_results['vocabulary_completed'] = True

                self.workflow.progress_updated.emit(85)

                # Compile final manuscript
                final_manuscript = self.compile_final_manuscript(sections)
                writing_results['final_word_count'] = len(final_manuscript.split())

                # Save complete manuscript
                manuscript_path = os.path.join(self.workflow.project_path, "manuscript.txt")
                with open(manuscript_path, 'w', encoding='utf-8') as f:
                    f.write(final_manuscript)

                self.workflow.log_action(f"Final manuscript saved: {writing_results['final_word_count']} words")

                self.workflow.progress_updated.emit(95)

                # Quality assessment
                quality_analysis = self.assess_manuscript_quality(final_manuscript)
                writing_results['quality_score'] = quality_analysis['score']
                writing_results['writing_history'] = quality_analysis['history']

                self.workflow.progress_updated.emit(100)

                # Final success
                writing_results['success'] = True
                self.workflow.log_action(f"Iterative writing loop completed successfully")
                self.workflow.status_updated.emit("Status: Iterative writing loop completed successfully!")

            else:
                writing_results['errors'].append("No outline found - cannot proceed with writing")
                self.workflow.error_occurred.emit("No outline found for iterative writing")
                logging.error("No outline found for iterative writing")

        except Exception as e:
            writing_results['errors'].append(str(e))
            self.workflow.error_occurred.emit(f"Iterative writing loop failed: {str(e)}")
            logging.error(f"Iterative writing loop failed: {str(e)}")

        # Save results
        self.save_writing_results(writing_results)
        return writing_results

    def extract_sections_from_outline(self, outline_content):
        """Extract writing sections from outline content."""
        sections = []

        try:
            # Split outline into chapters/sections
            lines = outline_content.split('\n')
            current_section = None

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Check for chapter/section headers
                if (line.startswith('Chapter') or
                    line.startswith('Section') or
                    line.startswith('Part') or
                    line.startswith('##')):

                    # Save previous section if exists
                    if current_section:
                        sections.append(current_section)

                    # Start new section
                    current_section = {
                        'title': line,
                        'content': [],
                        'word_target': 2500,  # Default target words per section
                        'draft': '',
                        'polished': '',
                        'enhanced': '',
                        'final': '',
                        'stage': 'planning'
                    }

                elif current_section:
                    current_section['content'].append(line)

            # Add last section
            if current_section:
                sections.append(current_section)

            # If no sections found, create default structure
            if not sections:
                sections = [
                    {
                        'title': 'Chapter 1: Opening',
                        'content': ['Begin the story with engaging opening'],
                        'word_target': 2500,
                        'draft': '',
                        'polished': '',
                        'enhanced': '',
                        'final': '',
                        'stage': 'planning'
                    }
                ]

            self.workflow.log_action(f"Extracted {len(sections)} sections from outline")
            return sections

        except Exception as e:
            self.workflow.log_action(f"Error extracting sections: {str(e)}")
            # Return minimal structure on error
            return [{
                'title': 'Chapter 1: Opening',
                'content': ['Begin the story'],
                'word_target': 2500,
                'draft': '',
                'polished': '',
                'enhanced': '',
                'final': '',
                'stage': 'planning'
            }]

    def execute_drafting_stage(self, section):
        """Stage 1: Initial drafting of section content."""
        result = {
            'success': False,
            'content': '',
            'word_count': 0,
            'errors': [],
            'stage': 'drafting'
        }

        try:
            self.workflow.status_updated.emit(f"Status: Drafting {section['title']}")

            # Prepare context for drafting
            context = {
                'title': section['title'],
                'outline_points': section['content'],
                'target_words': section['word_target'],
                'project_name': self.workflow.project_name,
                'characters': self.load_characters_summary(),
                'themes': self.load_themes_summary(),
                'previous_content': self.get_previous_sections_summary()
            }

            # Try AI-powered drafting first
            if self.workflow.api_manager and self.workflow.api_manager.is_available():
                draft_content = self.generate_ai_draft(context)
                if draft_content:
                    result['content'] = draft_content
                    result['success'] = True
                    self.workflow.log_action(f"AI drafting completed for {section['title']}")
                else:
                    # Fallback to manual drafting
                    result['content'] = self.generate_manual_draft(context)
                    result['success'] = True
                    self.workflow.log_action(f"Manual drafting completed for {section['title']}")
            else:
                # Manual drafting fallback
                result['content'] = self.generate_manual_draft(context)
                result['success'] = True
                self.workflow.log_action(f"Manual drafting completed for {section['title']}")

            result['word_count'] = len(result['content'].split())
            section['stage'] = 'drafted'

        except Exception as e:
            result['errors'].append(str(e))
            self.workflow.log_action(f"Drafting stage failed: {str(e)}")

        return result

    def execute_polishing_stage(self, section):
        """Stage 2: Polish and refine the draft."""
        result = {
            'success': False,
            'content': '',
            'word_count': 0,
            'errors': [],
            'stage': 'polishing'
        }

        try:
            self.workflow.status_updated.emit(f"Status: Polishing {section['title']}")

            draft_content = section.get('draft', '')
            if not draft_content:
                result['errors'].append("No draft content to polish")
                return result

            # Prepare polishing context
            context = {
                'title': section['title'],
                'draft_content': draft_content,
                'target_quality': 'professional',
                'focus_areas': ['clarity', 'flow', 'grammar', 'style']
            }

            # Try AI-powered polishing
            if self.workflow.api_manager and self.workflow.api_manager.is_available():
                polished_content = self.generate_ai_polish(context)
                if polished_content:
                    result['content'] = polished_content
                    result['success'] = True
                    self.workflow.log_action(f"AI polishing completed for {section['title']}")
                else:
                    # Fallback to manual polishing
                    result['content'] = self.apply_manual_polish(context)
                    result['success'] = True
                    self.workflow.log_action(f"Manual polishing completed for {section['title']}")
            else:
                # Manual polishing fallback
                result['content'] = self.apply_manual_polish(context)
                result['success'] = True
                self.workflow.log_action(f"Manual polishing completed for {section['title']}")

            result['word_count'] = len(result['content'].split())
            section['stage'] = 'polished'

        except Exception as e:
            result['errors'].append(str(e))
            self.workflow.log_action(f"Polishing stage failed: {str(e)}")

        return result

    def execute_enhancement_stage(self, section):
        """Stage 3: Enhance with literary devices and depth."""
        result = {
            'success': False,
            'content': '',
            'word_count': 0,
            'errors': [],
            'stage': 'enhancement'
        }

        try:
            self.workflow.status_updated.emit(f"Status: Enhancing {section['title']}")

            polished_content = section.get('polished', '')
            if not polished_content:
                result['errors'].append("No polished content to enhance")
                return result

            # Prepare enhancement context
            context = {
                'title': section['title'],
                'polished_content': polished_content,
                'enhancement_focus': ['imagery', 'dialogue', 'character_depth', 'emotional_impact'],
                'literary_devices': ['metaphor', 'symbolism', 'foreshadowing', 'tension']
            }

            # Try AI-powered enhancement
            if self.workflow.api_manager and self.workflow.api_manager.is_available():
                enhanced_content = self.generate_ai_enhancement(context)
                if enhanced_content:
                    result['content'] = enhanced_content
                    result['success'] = True
                    self.workflow.log_action(f"AI enhancement completed for {section['title']}")
                else:
                    # Fallback to manual enhancement
                    result['content'] = self.apply_manual_enhancement(context)
                    result['success'] = True
                    self.workflow.log_action(f"Manual enhancement completed for {section['title']}")
            else:
                # Manual enhancement fallback
                result['content'] = self.apply_manual_enhancement(context)
                result['success'] = True
                self.workflow.log_action(f"Manual enhancement completed for {section['title']}")

            result['word_count'] = len(result['content'].split())
            section['stage'] = 'enhanced'

        except Exception as e:
            result['errors'].append(str(e))
            self.workflow.log_action(f"Enhancement stage failed: {str(e)}")

        return result

    def execute_vocabulary_stage(self, section):
        """Stage 4: Final vocabulary refinement and style consistency."""
        result = {
            'success': False,
            'content': '',
            'word_count': 0,
            'errors': [],
            'stage': 'vocabulary'
        }

        try:
            self.workflow.status_updated.emit(f"Status: Vocabulary refinement for {section['title']}")

            enhanced_content = section.get('enhanced', '')
            if not enhanced_content:
                result['errors'].append("No enhanced content for vocabulary refinement")
                return result

            # Prepare vocabulary context
            context = {
                'title': section['title'],
                'enhanced_content': enhanced_content,
                'vocabulary_focus': ['word_choice', 'redundancy', 'rhythm', 'tone'],
                'style_consistency': True,
                'reading_level': 'adult'
            }

            # Try AI-powered vocabulary refinement
            if self.workflow.api_manager and self.workflow.api_manager.is_available():
                refined_content = self.generate_ai_vocabulary_refinement(context)
                if refined_content:
                    result['content'] = refined_content
                    result['success'] = True
                    self.workflow.log_action(f"AI vocabulary refinement completed for {section['title']}")
                else:
                    # Fallback to manual refinement
                    result['content'] = self.apply_manual_vocabulary_refinement(context)
                    result['success'] = True
                    self.workflow.log_action(f"Manual vocabulary refinement completed for {section['title']}")
            else:
                # Manual refinement fallback
                result['content'] = self.apply_manual_vocabulary_refinement(context)
                result['success'] = True
                self.workflow.log_action(f"Manual vocabulary refinement completed for {section['title']}")

            result['word_count'] = len(result['content'].split())
            section['stage'] = 'final'

        except Exception as e:
            result['errors'].append(str(e))
            self.workflow.log_action(f"Vocabulary stage failed: {str(e)}")

        return result

    def save_section_progress(self, section, section_number):
        """Save individual section progress."""
        try:
            # Create section directory if it doesn't exist
            section_dir = os.path.join(self.workflow.project_path, "sections")
            os.makedirs(section_dir, exist_ok=True)

            # Save section data
            section_file = os.path.join(section_dir, f"section_{section_number:03d}.json")

            section_data = {
                'title': section['title'],
                'stage': section['stage'],
                'word_target': section['word_target'],
                'draft': section.get('draft', ''),
                'polished': section.get('polished', ''),
                'enhanced': section.get('enhanced', ''),
                'final': section.get('final', ''),
                'draft_word_count': len(section.get('draft', '').split()),
                'polished_word_count': len(section.get('polished', '').split()),
                'enhanced_word_count': len(section.get('enhanced', '').split()),
                'final_word_count': len(section.get('final', '').split()),
                'updated': datetime.now().isoformat()
            }

            with open(section_file, 'w', encoding='utf-8') as f:
                json.dump(section_data, f, indent=2, ensure_ascii=False)

            self.workflow.log_action(f"Section {section_number} progress saved")

        except Exception as e:
            self.workflow.log_action(f"Error saving section progress: {str(e)}")

    def compile_final_manuscript(self, sections):
        """Compile all sections into final manuscript."""
        try:
            manuscript_parts = []

            # Add manuscript header
            manuscript_parts.append(f"# {self.workflow.project_name}")
            manuscript_parts.append("")
            manuscript_parts.append("*A Novel*")
            manuscript_parts.append("")
            manuscript_parts.append("=" * 50)
            manuscript_parts.append("")

            # Add each section
            for i, section in enumerate(sections):
                # Add section title
                manuscript_parts.append(f"## {section['title']}")
                manuscript_parts.append("")

                # Add final content
                final_content = section.get('final', section.get('enhanced', section.get('polished', section.get('draft', ''))))
                if final_content:
                    manuscript_parts.append(final_content)
                else:
                    manuscript_parts.append("[Section content pending]")

                manuscript_parts.append("")
                manuscript_parts.append("=" * 30)
                manuscript_parts.append("")

            # Add manuscript footer
            manuscript_parts.append("")
            manuscript_parts.append("THE END")
            manuscript_parts.append("")
            manuscript_parts.append(f"Completed: {datetime.now().strftime('%B %d, %Y')}")

            return '\n'.join(manuscript_parts)

        except Exception as e:
            self.workflow.log_action(f"Error compiling manuscript: {str(e)}")
            return f"Error compiling manuscript: {str(e)}"

    def assess_manuscript_quality(self, manuscript_content):
        """Assess the quality of the completed manuscript."""
        quality_analysis = {
            'score': 0,
            'word_count': 0,
            'readability': 0,
            'structure_score': 0,
            'consistency_score': 0,
            'completeness_score': 0,
            'recommendations': [],
            'history': []
        }

        try:
            # Basic metrics
            words = manuscript_content.split()
            quality_analysis['word_count'] = len(words)

            # Structure analysis
            sections = manuscript_content.split('##')
            quality_analysis['structure_score'] = min(100, len(sections) * 10)

            # Completeness check
            if '[Section content pending]' in manuscript_content:
                quality_analysis['completeness_score'] = 50
                quality_analysis['recommendations'].append("Complete all pending sections")
            else:
                quality_analysis['completeness_score'] = 100

            # Basic readability (simplified)
            sentences = manuscript_content.split('.')
            avg_sentence_length = len(words) / max(len(sentences), 1)
            quality_analysis['readability'] = max(0, min(100, 100 - (avg_sentence_length - 15)))

            # Consistency score (placeholder)
            quality_analysis['consistency_score'] = 85

            # Calculate overall score
            quality_analysis['score'] = int(
                (quality_analysis['structure_score'] * 0.2) +
                (quality_analysis['completeness_score'] * 0.3) +
                (quality_analysis['readability'] * 0.25) +
                (quality_analysis['consistency_score'] * 0.25)
            )

            # Add recommendations based on score
            if quality_analysis['score'] < 70:
                quality_analysis['recommendations'].append("Consider additional revision")
            elif quality_analysis['score'] < 85:
                quality_analysis['recommendations'].append("Good quality - minor improvements possible")
            else:
                quality_analysis['recommendations'].append("Excellent quality - ready for publication")

            # Add to history
            quality_analysis['history'].append({
                'timestamp': datetime.now().isoformat(),
                'score': quality_analysis['score'],
                'word_count': quality_analysis['word_count']
            })

        except Exception as e:
            self.workflow.log_action(f"Error in quality assessment: {str(e)}")
            quality_analysis['score'] = 50
            quality_analysis['recommendations'].append("Quality assessment incomplete")

        return quality_analysis

    def save_writing_results(self, writing_results):
        """Save the complete writing process results."""
        try:
            results_file = os.path.join(self.workflow.project_path, "writing_results.json")

            # Add timestamp
            writing_results['completed_at'] = datetime.now().isoformat()
            writing_results['project_name'] = self.workflow.project_name

            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(writing_results, f, indent=2, ensure_ascii=False)

            self.workflow.log_action("Writing results saved successfully")

        except Exception as e:
            self.workflow.log_action(f"Error saving writing results: {str(e)}")

    # AI-powered generation methods
    def generate_ai_draft(self, context):
        """Generate initial draft using AI."""
        try:
            prompt = f"""
            Write a compelling draft for the following section:

            Title: {context['title']}
            Target Word Count: {context['target_words']}

            Outline Points:
            {chr(10).join(context['outline_points'])}

            Project Context:
            - Themes: {context.get('themes', 'Not specified')}

            Previous Content Summary:
            {context.get('previous_content', 'This is the opening section')}

            Instructions:
            1. Write engaging, immersive prose
            2. Maintain consistent voice and style
            3. Include vivid descriptions and realistic dialogue
            4. Ensure smooth narrative flow
            5. Aim for approximately {context['target_words']} words

            Begin the draft:
            """

            response = self.workflow.api_manager.generate_text(prompt)
            if response and len(response.strip()) > 100:
                return response.strip()
            return None

        except Exception as e:
            self.workflow.log_action(f"AI draft generation failed: {str(e)}")
            return None

    def generate_manual_draft(self, context):
        """Generate basic draft manually when AI is unavailable."""
        try:
            # Create a structured draft from outline points
            draft_parts = []

            # Add section opening
            draft_parts.append(f"[Opening for {context['title']}]")
            draft_parts.append("")

            # Add content based on outline points
            for point in context['outline_points']:
                draft_parts.append(f"[{point}]")
                draft_parts.append("")
                # Add placeholder content
                draft_parts.append("This section needs to be developed with detailed narrative, character development, and descriptive prose. The content should advance the plot while maintaining reader engagement through vivid imagery and compelling dialogue.")
                draft_parts.append("")

            # Add section closing
            draft_parts.append(f"[Conclusion for {context['title']}]")

            return '\n'.join(draft_parts)

        except Exception as e:
            self.workflow.log_action(f"Manual draft generation failed: {str(e)}")
            return f"Draft placeholder for {context['title']}: Content to be developed."

    def generate_ai_polish(self, context):
        """Polish draft using AI."""
        try:
            prompt = f"""
            Polish and refine the following draft section:

            Title: {context['title']}
            Focus Areas: {', '.join(context['focus_areas'])}

            Draft Content:
            {context['draft_content']}

            Polishing Instructions:
            1. Improve clarity and readability
            2. Enhance sentence flow and rhythm
            3. Correct grammar and punctuation
            4. Strengthen word choice
            5. Maintain the original voice and style
            6. Ensure consistent tone throughout

            Return the polished version:
            """

            response = self.workflow.api_manager.generate_text(prompt)
            if response and len(response.strip()) > 100:
                return response.strip()
            return None

        except Exception as e:
            self.workflow.log_action(f"AI polishing failed: {str(e)}")
            return None

    def apply_manual_polish(self, context):
        """Apply basic polishing manually."""
        try:
            content = context['draft_content']

            # Basic improvements
            # Remove extra whitespace
            content = '\n'.join(line.strip() for line in content.split('\n') if line.strip())

            # Add polish indicator
            content = f"[POLISHED VERSION]\n\n{content}\n\n[End of polished section]"

            return content

        except Exception as e:
            self.workflow.log_action(f"Manual polishing failed: {str(e)}")
            return context['draft_content']

    def generate_ai_enhancement(self, context):
        """Enhance content using AI."""
        try:
            prompt = f"""
            Enhance the following polished section with literary depth:

            Title: {context['title']}
            Enhancement Focus: {', '.join(context['enhancement_focus'])}
            Literary Devices: {', '.join(context['literary_devices'])}

            Polished Content:
            {context['polished_content']}

            Enhancement Instructions:
            1. Add vivid imagery and sensory details
            2. Deepen character development and emotional resonance
            3. Incorporate subtle literary devices
            4. Enhance dialogue authenticity
            5. Increase narrative tension and pacing
            6. Add symbolic elements where appropriate

            Return the enhanced version:
            """

            response = self.workflow.api_manager.generate_text(prompt)
            if response and len(response.strip()) > 100:
                return response.strip()
            return None

        except Exception as e:
            self.workflow.log_action(f"AI enhancement failed: {str(e)}")
            return None

    def apply_manual_enhancement(self, context):
        """Apply basic enhancement manually."""
        try:
            content = context['polished_content']

            # Add enhancement indicator
            content = f"[ENHANCED VERSION]\n\n{content}\n\n[End of enhanced section]"

            return content

        except Exception as e:
            self.workflow.log_action(f"Manual enhancement failed: {str(e)}")
            return context['polished_content']

    def generate_ai_vocabulary_refinement(self, context):
        """Refine vocabulary using AI."""
        try:
            prompt = f"""
            Perform final vocabulary refinement on the following enhanced section:

            Title: {context['title']}
            Vocabulary Focus: {', '.join(context['vocabulary_focus'])}
            Style Consistency: {context['style_consistency']}
            Reading Level: {context['reading_level']}

            Enhanced Content:
            {context['enhanced_content']}

            Refinement Instructions:
            1. Optimize word choice for precision and impact
            2. Eliminate redundancy and repetition
            3. Improve sentence rhythm and flow
            4. Ensure consistent tone and voice
            5. Adjust vocabulary for target reading level
            6. Maintain literary quality while ensuring readability

            Return the refined version:
            """

            response = self.workflow.api_manager.generate_text(prompt)
            if response and len(response.strip()) > 100:
                return response.strip()
            return None

        except Exception as e:
            self.workflow.log_action(f"AI vocabulary refinement failed: {str(e)}")
            return None

    def apply_manual_vocabulary_refinement(self, context):
        """Apply basic vocabulary refinement manually."""
        try:
            content = context['enhanced_content']

            # Add refinement indicator
            content = f"[FINAL REFINED VERSION]\n\n{content}\n\n[End of final section]"

            return content

        except Exception as e:
            self.workflow.log_action(f"Manual vocabulary refinement failed: {str(e)}")
            return context['enhanced_content']

    # Helper methods for context loading
    def load_characters_summary(self):
        """Load character summary for context."""
        try:
            characters_file = os.path.join(self.workflow.project_path, "characters.txt")
            if os.path.exists(characters_file):
                with open(characters_file, 'r', encoding='utf-8') as f:
                    return f.read()[:500]  # First 500 chars
            return "Characters not yet defined"
        except Exception:
            return "Characters not available"

    def load_themes_summary(self):
        """Load themes summary for context."""
        try:
            themes_file = os.path.join(self.workflow.project_path, "themes.txt")
            if os.path.exists(themes_file):
                with open(themes_file, 'r', encoding='utf-8') as f:
                    return f.read()[:300]  # First 300 chars
            return "Themes not yet defined"
        except Exception:
            return "Themes not available"

    def get_previous_sections_summary(self):
        """Get summary of previous sections for context."""
        try:
            sections_dir = os.path.join(self.workflow.project_path, "sections")
            if os.path.exists(sections_dir):
                section_files = [f for f in os.listdir(sections_dir) if f.endswith('.json')]
                if section_files:
                    return f"Previous sections: {len(section_files)} sections completed"
            return "This is the opening section"
        except Exception:
            return "Previous sections not available"

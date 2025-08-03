#!/usr/bin/env python3
"""
Step 11: Completion and Export
Final completion validation and comprehensive export functionality.
"""

import json
import os
import logging
import shutil
import zipfile
from datetime import datetime
from typing import Dict, Any, List
from ...plugins.plugin_workflow_integration import BaseWorkflowStep

class Step11CompletionExport(BaseWorkflowStep):
    def execute(self) -> dict:
        """
        Execute Step 11: Completion and Export
        Performs final validation, creates exports, and completes the workflow.
        """
        self.workflow.status_updated.emit("Status: Finalizing project and preparing exports")
        completion_results = {
            'success': False,
            'validation_passed': False,
            'exports_created': [],
            'final_statistics': {},
            'project_summary': {},
            'export_formats': [],
            'archive_created': False,
            'completion_timestamp': None,
            'errors': [],
            'warnings': []
        }

        try:
            # Final project validation
            completion_results['validation_passed'] = self.perform_final_validation()

            if not completion_results['validation_passed']:
                completion_results['warnings'].append("Project validation failed, but continuing with export")

            # Gather final statistics
            completion_results['final_statistics'] = self.gather_final_statistics()
            completion_results['project_summary'] = self.create_project_summary()

            self.workflow.progress_updated.emit(25)

            # Create exports in multiple formats
            completion_results['exports_created'] = self.create_all_exports()
            completion_results['export_formats'] = [export['format'] for export in completion_results['exports_created']]

            self.workflow.progress_updated.emit(60)

            # Create project archive
            completion_results['archive_created'] = self.create_project_archive()

            self.workflow.progress_updated.emit(80)

            # Generate completion report
            self.generate_completion_report(completion_results)

            # Mark completion timestamp
            completion_results['completion_timestamp'] = datetime.now().isoformat()

            # Save final project state
            self.save_final_project_state(completion_results)

            completion_results['success'] = True
            self.workflow.progress_updated.emit(100)

            self.workflow.status_updated.emit("Status: Project completed successfully!")
            self.workflow.log_action("Novel workflow completed successfully")

            # Update workflow state to completed
            if hasattr(self.workflow, 'current_step'):
                self.workflow.current_step = 11
                self.workflow.workflow_completed = True

        except Exception as e:
            completion_results['errors'].append(str(e))
            self.workflow.error_occurred.emit(f"Completion error: {e}")
            self.workflow.log_action(f"Completion error: {e}")

        return completion_results

    def perform_final_validation(self) -> bool:
        """Perform comprehensive final validation of the project."""
        try:
            validation_checks = {
                'story_exists': False,
                'story_has_content': False,
                'characters_defined': False,
                'synopsis_complete': False,
                'timeline_exists': False,
                'minimum_word_count': False,
                'metadata_complete': False
            }

            # Check story file
            story_file = os.path.join(self.workflow.project_path, "story.txt")
            if os.path.exists(story_file):
                validation_checks['story_exists'] = True
                with open(story_file, 'r', encoding='utf-8') as f:
                    story_content = f.read()
                    if len(story_content.strip()) > 1000:
                        validation_checks['story_has_content'] = True
                    if len(story_content.split()) >= 5000:
                        validation_checks['minimum_word_count'] = True

            # Check characters file
            characters_file = os.path.join(self.workflow.project_path, "characters.txt")
            if os.path.exists(characters_file):
                with open(characters_file, 'r', encoding='utf-8') as f:
                    characters_content = f.read()
                    if len(characters_content.strip()) > 100:
                        validation_checks['characters_defined'] = True

            # Check synopsis file
            synopsis_file = os.path.join(self.workflow.project_path, "synopsis.txt")
            if os.path.exists(synopsis_file):
                with open(synopsis_file, 'r', encoding='utf-8') as f:
                    synopsis_content = f.read()
                    if len(synopsis_content.strip()) > 300:
                        validation_checks['synopsis_complete'] = True

            # Check timeline file
            timeline_file = os.path.join(self.workflow.project_path, "timeline.txt")
            if os.path.exists(timeline_file):
                with open(timeline_file, 'r', encoding='utf-8') as f:
                    timeline_content = f.read()
                    if len(timeline_content.strip()) > 50:
                        validation_checks['timeline_exists'] = True

            # Check metadata
            metadata_file = os.path.join(self.workflow.project_path, "project_metadata.json")
            if os.path.exists(metadata_file):
                validation_checks['metadata_complete'] = True

            # Save validation results
            validation_file = os.path.join(self.workflow.project_path, "final_validation.json")
            with open(validation_file, 'w', encoding='utf-8') as f:
                json.dump(validation_checks, f, indent=2)

            # Consider validation passed if most critical checks pass
            critical_checks = ['story_exists', 'story_has_content', 'synopsis_complete']
            passed_critical = sum(1 for check in critical_checks if validation_checks[check])

            return passed_critical >= 2  # At least 2 out of 3 critical checks

        except Exception as e:
            self.workflow.log_action(f"Validation error: {e}")
            return False

    def gather_final_statistics(self) -> Dict[str, Any]:
        """Gather comprehensive final project statistics."""
        try:
            stats = {
                'total_word_count': 0,
                'chapter_count': 0,
                'character_count': 0,
                'page_count_estimate': 0,
                'workflow_duration': 0,
                'files_created': 0,
                'iterations_completed': 0,
                'quality_scores': {},
                'export_timestamp': datetime.now().isoformat()
            }

            # Story statistics
            story_file = os.path.join(self.workflow.project_path, "story.txt")
            if os.path.exists(story_file):
                with open(story_file, 'r', encoding='utf-8') as f:
                    story_content = f.read()
                    stats['total_word_count'] = len(story_content.split())
                    stats['chapter_count'] = story_content.count("Chapter")
                    # Estimate pages (250 words per page)
                    stats['page_count_estimate'] = max(1, stats['total_word_count'] // 250)

            # Character count
            characters_file = os.path.join(self.workflow.project_path, "characters.txt")
            if os.path.exists(characters_file):
                with open(characters_file, 'r', encoding='utf-8') as f:
                    characters_content = f.read()
                    # Count character entries (lines with colons)
                    stats['character_count'] = len([line for line in characters_content.split('\n') if ':' in line])

            # Count all files in project
            try:
                file_count = 0
                for root, dirs, files in os.walk(self.workflow.project_path):
                    file_count += len(files)
                stats['files_created'] = file_count
            except:
                stats['files_created'] = 0

            # Load progression results for quality scores
            progression_file = os.path.join(self.workflow.project_path, "progression_results.json")
            if os.path.exists(progression_file):
                with open(progression_file, 'r', encoding='utf-8') as f:
                    progression_data = json.load(f)
                    stats['quality_scores'] = progression_data.get('quality_assessment', {})

            # Estimate workflow duration from project creation
            metadata_file = os.path.join(self.workflow.project_path, "project_metadata.json")
            if os.path.exists(metadata_file):
                try:
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        if 'created_date' in metadata:
                            created_date = datetime.fromisoformat(metadata['created_date'].replace('Z', '+00:00'))
                            duration = datetime.now() - created_date.replace(tzinfo=None)
                            stats['workflow_duration'] = duration.total_seconds() / 3600  # Hours
                except:
                    pass

            return stats

        except Exception as e:
            self.workflow.log_action(f"Error gathering statistics: {e}")
            return {}

    def create_project_summary(self) -> Dict[str, Any]:
        """Create a comprehensive project summary."""
        try:
            summary = {
                'project_name': os.path.basename(self.workflow.project_path),
                'genre': getattr(self.workflow, 'genre', 'Unknown'),
                'tone': getattr(self.workflow, 'novel_tone', 'Unknown'),
                'target_audience': getattr(self.workflow, 'target_audience', 'General'),
                'word_count_target': getattr(self.workflow, 'target_word_count', 50000),
                'completion_date': datetime.now().isoformat(),
                'workflow_version': 'FANWS 1.0',
                'description': '',
                'key_themes': [],
                'main_characters': [],
                'plot_summary': ''
            }

            # Extract description from synopsis
            synopsis_file = os.path.join(self.workflow.project_path, "synopsis.txt")
            if os.path.exists(synopsis_file):
                with open(synopsis_file, 'r', encoding='utf-8') as f:
                    synopsis_content = f.read()
                    # Use first paragraph as description
                    paragraphs = synopsis_content.split('\n\n')
                    if paragraphs:
                        summary['description'] = paragraphs[0][:500]  # First 500 chars
                    summary['plot_summary'] = synopsis_content

            # Extract main characters
            characters_file = os.path.join(self.workflow.project_path, "characters.txt")
            if os.path.exists(characters_file):
                with open(characters_file, 'r', encoding='utf-8') as f:
                    characters_content = f.read()
                    for line in characters_content.split('\n'):
                        if ':' in line:
                            character_name = line.split(':')[0].strip()
                            if len(character_name) > 1:
                                summary['main_characters'].append(character_name)

            # Extract themes from themes file if it exists
            themes_file = os.path.join(self.workflow.project_path, "themes.txt")
            if os.path.exists(themes_file):
                with open(themes_file, 'r', encoding='utf-8') as f:
                    themes_content = f.read()
                    # Simple theme extraction
                    lines = [line.strip() for line in themes_content.split('\n') if line.strip()]
                    summary['key_themes'] = lines[:5]  # Top 5 themes

            return summary

        except Exception as e:
            self.workflow.log_action(f"Error creating project summary: {e}")
            return {}

    def create_all_exports(self) -> List[Dict[str, Any]]:
        """Create exports in multiple formats."""
        exports_created = []

        try:
            # Create exports directory
            exports_dir = os.path.join(self.workflow.project_path, "exports")
            os.makedirs(exports_dir, exist_ok=True)

            # 1. Plain Text Export
            txt_export = self.create_text_export(exports_dir)
            if txt_export:
                exports_created.append(txt_export)

            # 2. Formatted Text Export
            formatted_export = self.create_formatted_export(exports_dir)
            if formatted_export:
                exports_created.append(formatted_export)

            # 3. JSON Project Export
            json_export = self.create_json_export(exports_dir)
            if json_export:
                exports_created.append(json_export)

            # 4. Markdown Export
            md_export = self.create_markdown_export(exports_dir)
            if md_export:
                exports_created.append(md_export)

            # 5. Project Package Export
            package_export = self.create_package_export(exports_dir)
            if package_export:
                exports_created.append(package_export)

        except Exception as e:
            self.workflow.log_action(f"Error creating exports: {e}")

        return exports_created

    def create_text_export(self, exports_dir: str) -> Dict[str, Any]:
        """Create plain text export of the novel."""
        try:
            export_file = os.path.join(exports_dir, f"{os.path.basename(self.workflow.project_path)}_novel.txt")

            with open(export_file, 'w', encoding='utf-8') as f:
                # Write header
                f.write(f"NOVEL EXPORT\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Project: {os.path.basename(self.workflow.project_path)}\n")
                f.write("=" * 50 + "\n\n")

                # Write story content
                story_file = os.path.join(self.workflow.project_path, "story.txt")
                if os.path.exists(story_file):
                    with open(story_file, 'r', encoding='utf-8') as story_f:
                        f.write(story_f.read())

            return {
                'format': 'txt',
                'file_path': export_file,
                'file_size': os.path.getsize(export_file),
                'created': datetime.now().isoformat()
            }

        except Exception as e:
            self.workflow.log_action(f"Text export error: {e}")
            return None

    def create_formatted_export(self, exports_dir: str) -> Dict[str, Any]:
        """Create formatted text export with proper formatting."""
        try:
            export_file = os.path.join(exports_dir, f"{os.path.basename(self.workflow.project_path)}_formatted.txt")

            with open(export_file, 'w', encoding='utf-8') as f:
                # Write title page
                project_name = os.path.basename(self.workflow.project_path)
                f.write(f"\n\n\n{project_name.upper()}\n\n")
                f.write(f"A Novel\n\n")
                f.write(f"Generated by FANWS\n")
                f.write(f"{datetime.now().strftime('%B %Y')}\n")
                f.write("\n" + "=" * 50 + "\n\n")

                # Write synopsis
                synopsis_file = os.path.join(self.workflow.project_path, "synopsis.txt")
                if os.path.exists(synopsis_file):
                    f.write("SYNOPSIS\n\n")
                    with open(synopsis_file, 'r', encoding='utf-8') as synopsis_f:
                        f.write(synopsis_f.read())
                    f.write("\n\n" + "=" * 50 + "\n\n")

                # Write story with proper formatting
                story_file = os.path.join(self.workflow.project_path, "story.txt")
                if os.path.exists(story_file):
                    with open(story_file, 'r', encoding='utf-8') as story_f:
                        story_content = story_f.read()
                        # Add proper chapter formatting
                        formatted_content = story_content.replace("Chapter", "\n\nChapter")
                        f.write(formatted_content)

            return {
                'format': 'formatted_txt',
                'file_path': export_file,
                'file_size': os.path.getsize(export_file),
                'created': datetime.now().isoformat()
            }

        except Exception as e:
            self.workflow.log_action(f"Formatted export error: {e}")
            return None

    def create_json_export(self, exports_dir: str) -> Dict[str, Any]:
        """Create JSON export with all project data."""
        try:
            export_file = os.path.join(exports_dir, f"{os.path.basename(self.workflow.project_path)}_project.json")

            project_data = {
                'metadata': {
                    'project_name': os.path.basename(self.workflow.project_path),
                    'export_date': datetime.now().isoformat(),
                    'export_version': '1.0',
                    'workflow_system': 'FANWS'
                },
                'content': {},
                'statistics': self.gather_final_statistics(),
                'summary': self.create_project_summary()
            }

            # Load all content files
            content_files = ['story.txt', 'synopsis.txt', 'characters.txt', 'timeline.txt', 'themes.txt', 'notes.txt']

            for filename in content_files:
                file_path = os.path.join(self.workflow.project_path, filename)
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        project_data['content'][filename.replace('.txt', '')] = f.read()

            # Save JSON export
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)

            return {
                'format': 'json',
                'file_path': export_file,
                'file_size': os.path.getsize(export_file),
                'created': datetime.now().isoformat()
            }

        except Exception as e:
            self.workflow.log_action(f"JSON export error: {e}")
            return None

    def create_markdown_export(self, exports_dir: str) -> Dict[str, Any]:
        """Create Markdown export for easy viewing and publishing."""
        try:
            export_file = os.path.join(exports_dir, f"{os.path.basename(self.workflow.project_path)}_novel.md")

            with open(export_file, 'w', encoding='utf-8') as f:
                project_name = os.path.basename(self.workflow.project_path)

                # Write markdown header
                f.write(f"# {project_name}\n\n")
                f.write(f"*Generated by FANWS on {datetime.now().strftime('%B %d, %Y')}*\n\n")
                f.write("---\n\n")

                # Write synopsis
                synopsis_file = os.path.join(self.workflow.project_path, "synopsis.txt")
                if os.path.exists(synopsis_file):
                    f.write("## Synopsis\n\n")
                    with open(synopsis_file, 'r', encoding='utf-8') as synopsis_f:
                        f.write(synopsis_f.read())
                    f.write("\n\n---\n\n")

                # Write characters
                characters_file = os.path.join(self.workflow.project_path, "characters.txt")
                if os.path.exists(characters_file):
                    f.write("## Characters\n\n")
                    with open(characters_file, 'r', encoding='utf-8') as char_f:
                        characters_content = char_f.read()
                        # Convert to markdown list format
                        for line in characters_content.split('\n'):
                            if ':' in line:
                                f.write(f"- **{line}**\n")
                            elif line.strip():
                                f.write(f"  {line}\n")
                    f.write("\n---\n\n")

                # Write story content
                f.write("## Story\n\n")
                story_file = os.path.join(self.workflow.project_path, "story.txt")
                if os.path.exists(story_file):
                    with open(story_file, 'r', encoding='utf-8') as story_f:
                        story_content = story_f.read()
                        # Convert chapters to markdown headers
                        formatted_content = story_content.replace("Chapter", "### Chapter")
                        f.write(formatted_content)

            return {
                'format': 'markdown',
                'file_path': export_file,
                'file_size': os.path.getsize(export_file),
                'created': datetime.now().isoformat()
            }

        except Exception as e:
            self.workflow.log_action(f"Markdown export error: {e}")
            return None

    def create_package_export(self, exports_dir: str) -> Dict[str, Any]:
        """Create a complete project package with all files."""
        try:
            export_file = os.path.join(exports_dir, f"{os.path.basename(self.workflow.project_path)}_complete_package.zip")

            with zipfile.ZipFile(export_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add all project files
                for root, dirs, files in os.walk(self.workflow.project_path):
                    # Skip the exports directory to avoid recursion
                    if 'exports' in root:
                        continue

                    for file in files:
                        file_path = os.path.join(root, file)
                        # Get relative path for archive
                        arcname = os.path.relpath(file_path, self.workflow.project_path)
                        zipf.write(file_path, arcname)

            return {
                'format': 'zip_package',
                'file_path': export_file,
                'file_size': os.path.getsize(export_file),
                'created': datetime.now().isoformat()
            }

        except Exception as e:
            self.workflow.log_action(f"Package export error: {e}")
            return None

    def create_project_archive(self) -> bool:
        """Create a complete project archive for backup."""
        try:
            archives_dir = os.path.join(self.workflow.project_path, "archives")
            os.makedirs(archives_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_file = os.path.join(archives_dir, f"project_complete_{timestamp}.zip")

            with zipfile.ZipFile(archive_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.workflow.project_path):
                    # Skip archives directory to avoid recursion
                    if 'archives' in root:
                        continue

                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, self.workflow.project_path)
                        zipf.write(file_path, arcname)

            self.workflow.log_action(f"Project archive created: {archive_file}")
            return True

        except Exception as e:
            self.workflow.log_action(f"Archive creation error: {e}")
            return False

    def generate_completion_report(self, completion_results: Dict[str, Any]):
        """Generate a comprehensive completion report."""
        try:
            report_file = os.path.join(self.workflow.project_path, "completion_report.md")

            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("# Project Completion Report\n\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Project:** {os.path.basename(self.workflow.project_path)}\n\n")

                # Summary
                f.write("## Summary\n\n")
                if completion_results['success']:
                    f.write("✅ **Project completed successfully!**\n\n")
                else:
                    f.write("⚠️ **Project completed with issues**\n\n")

                # Statistics
                stats = completion_results.get('final_statistics', {})
                f.write("## Project Statistics\n\n")
                f.write(f"- **Total Word Count:** {stats.get('total_word_count', 'N/A'):,}\n")
                f.write(f"- **Estimated Pages:** {stats.get('page_count_estimate', 'N/A')}\n")
                f.write(f"- **Chapters:** {stats.get('chapter_count', 'N/A')}\n")
                f.write(f"- **Characters:** {stats.get('character_count', 'N/A')}\n")
                f.write(f"- **Files Created:** {stats.get('files_created', 'N/A')}\n")

                if stats.get('workflow_duration'):
                    f.write(f"- **Workflow Duration:** {stats['workflow_duration']:.1f} hours\n")

                f.write("\n")

                # Exports
                f.write("## Exports Created\n\n")
                for export in completion_results.get('exports_created', []):
                    f.write(f"- **{export['format'].upper()}:** {os.path.basename(export['file_path'])}")
                    f.write(f" ({export['file_size']:,} bytes)\n")

                # Validation
                f.write("\n## Final Validation\n\n")
                if completion_results['validation_passed']:
                    f.write("✅ All validation checks passed\n")
                else:
                    f.write("⚠️ Some validation checks failed\n")

                # Errors and Warnings
                if completion_results.get('errors'):
                    f.write("\n## Errors\n\n")
                    for error in completion_results['errors']:
                        f.write(f"- ❌ {error}\n")

                if completion_results.get('warnings'):
                    f.write("\n## Warnings\n\n")
                    for warning in completion_results['warnings']:
                        f.write(f"- ⚠️ {warning}\n")

            self.workflow.log_action(f"Completion report generated: {report_file}")

        except Exception as e:
            self.workflow.log_action(f"Error generating completion report: {e}")

    def save_final_project_state(self, completion_results: Dict[str, Any]):
        """Save the final project state."""
        try:
            final_state_file = os.path.join(self.workflow.project_path, "final_project_state.json")

            final_state = {
                'completion_results': completion_results,
                'workflow_complete': True,
                'final_step': 11,
                'completion_timestamp': datetime.now().isoformat(),
                'project_path': self.workflow.project_path,
                'workflow_version': 'FANWS 1.0'
            }

            with open(final_state_file, 'w', encoding='utf-8') as f:
                json.dump(final_state, f, indent=2, ensure_ascii=False)

            self.workflow.log_action(f"Final project state saved: {final_state_file}")

        except Exception as e:
            self.workflow.log_action(f"Error saving final project state: {e}")

    def validate_prerequisites(self) -> bool:
        """Validate prerequisites for Step 11."""
        # Check if Step 9 or 10 completed successfully
        progression_file = os.path.join(self.workflow.project_path, "progression_results.json")
        recovery_file = os.path.join(self.workflow.project_path, "workflow_state.json")

        if not (os.path.exists(progression_file) or os.path.exists(recovery_file)):
            self.workflow.log_action("Previous workflow steps not found", "ERROR")
            return False

        # Check if story exists
        story_file = os.path.join(self.workflow.project_path, "story.txt")
        if not os.path.exists(story_file):
            self.workflow.log_action("Story file not found", "ERROR")
            return False

        return True

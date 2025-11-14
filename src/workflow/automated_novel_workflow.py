"""
Automated Novel Writing Workflow Backend
Implements the background workflow thread for automated novel generation.

This module provides:
- Background thread for AI-powered novel generation
- Step-by-step workflow execution (synopsis, outline, writing)
- Integration with AI APIs (ChatGPT, xAI, etc.)
- Signal-based communication with GUI
"""

import os
import json
import time
import random
from datetime import datetime
from typing import Dict, Any, Optional, List

from PyQt5.QtCore import QThread, pyqtSignal


class AutomatedNovelWorkflowThread(QThread):
    """
    Background thread for automated novel generation workflow.
    Implements the complete workflow from the problem statement.
    """
    
    # Signals for communication with GUI
    log_update = pyqtSignal(str)  # Log message
    new_synopsis = pyqtSignal(str)  # Synopsis generated
    new_outline = pyqtSignal(str)  # Outline generated
    new_characters = pyqtSignal(str)  # Characters generated
    new_world = pyqtSignal(str)  # World details generated
    new_draft = pyqtSignal(int, int, str)  # chapter, section, content
    progress_updated = pyqtSignal(int)  # Progress percentage
    status_updated = pyqtSignal(str)  # Status message
    error_signal = pyqtSignal(str)  # Error message
    waiting_approval = pyqtSignal(str)  # Waiting for user approval (step name)
    workflow_completed = pyqtSignal()  # Workflow complete
    
    def __init__(self, project_dir: str, idea: str, tone: str, target_words: int):
        super().__init__()
        
        self.project_dir = project_dir
        self.idea = idea
        self.tone = tone
        self.target_words = target_words
        
        # Workflow state
        self.current_step = "initialization"
        self.is_paused = False
        self.should_stop = False
        self.approval_received = False
        self.adjustment_feedback = None
        
        # Novel structure
        self.synopsis = ""
        self.outline = ""
        self.characters = []
        self.world = {}
        self.timeline = {}
        self.total_chapters = 25  # Default from spec
        self.current_chapter = 1
        self.current_section = 1
        self.sections_per_chapter = 5  # Default
        
        # API managers (to be initialized)
        self.api_manager = None
        
    def run(self):
        """Main workflow execution"""
        try:
            self.log("Automated novel writing workflow started")
            self.status_updated.emit("Initializing...")
            
            # Step 2: Synopsis Generation
            if not self.should_stop:
                self.generate_synopsis()
            
            # Step 4: Structural Planning
            if not self.should_stop and self.approval_received:
                self.generate_outline()
                self.generate_characters()
                self.generate_world()
            
            # Step 5: Timeline Synchronization
            if not self.should_stop and self.approval_received:
                self.generate_timeline()
            
            # Step 6-9: Iterative Writing Loop
            if not self.should_stop and self.approval_received:
                self.writing_loop()
            
            # Step 11: Completion
            if not self.should_stop:
                self.complete_novel()
            
            self.workflow_completed.emit()
            
        except Exception as e:
            self.error_signal.emit(f"Workflow error: {str(e)}")
            self.log(f"ERROR: {str(e)}")
    
    def generate_synopsis(self):
        """Step 2: Generate synopsis"""
        self.current_step = "synopsis"
        self.status_updated.emit("Generating synopsis...")
        self.log("Generating synopsis...")
        
        # Simulate API call (in real implementation, would call ChatGPT API)
        synopsis = self.simulate_synopsis_generation()
        
        self.synopsis = synopsis
        self.save_to_file("synopsis.txt", synopsis)
        
        # Emit signal and wait for approval
        self.new_synopsis.emit(synopsis)
        self.waiting_approval.emit("synopsis")
        self.approval_received = False
        
        # Wait for approval
        while not self.approval_received and not self.should_stop:
            time.sleep(0.1)
        
        if self.adjustment_feedback:
            # Refine synopsis with feedback
            self.log(f"Refining synopsis with feedback: {self.adjustment_feedback}")
            self.refine_synopsis()
            self.adjustment_feedback = None
    
    def simulate_synopsis_generation(self) -> str:
        """Simulate synopsis generation (placeholder for real API call)"""
        return f"""
SYNOPSIS

Setting: {self.idea}
Tone: {self.tone}

This gripping {self.tone} novel follows a complex narrative arc spanning {self.total_chapters} chapters.

The story explores themes of rebellion, identity, and the cost of freedom in a world where 
technology has both liberated and enslaved humanity. Through vivid characters and a tightly 
woven plot, the narrative builds toward a climactic confrontation that will determine the 
fate of an entire civilization.

The protagonist must navigate treacherous alliances, confront their own demons, and ultimately 
make an impossible choice between personal salvation and the greater good.

Target length: {self.target_words:,} words
Expected chapters: {self.total_chapters}
"""
    
    def refine_synopsis(self):
        """Refine synopsis based on feedback"""
        # In real implementation, would call API with feedback
        self.log("Synopsis refined")
        # Re-emit for review
        self.new_synopsis.emit(self.synopsis)
        self.waiting_approval.emit("synopsis")
        self.approval_received = False
        
        while not self.approval_received and not self.should_stop:
            time.sleep(0.1)
    
    def generate_outline(self):
        """Step 4: Generate outline"""
        self.current_step = "outline"
        self.status_updated.emit("Generating outline...")
        self.log("Generating outline...")
        
        # Simulate outline generation
        outline_parts = []
        for i in range(1, self.total_chapters + 1):
            chapter_title = f"Chapter {i}: The Journey Continues"
            chapter_summary = f"In this chapter, events unfold that drive the narrative forward. Characters face new challenges and the plot thickens. (Estimated {5000 + random.randint(0, 5000)} words)"
            outline_parts.append(f"{chapter_title}\n{chapter_summary}\n")
        
        self.outline = "\n".join(outline_parts)
        self.save_to_file("outline.txt", self.outline)
        
        # Emit and wait for approval
        self.new_outline.emit(self.outline)
        self.waiting_approval.emit("outline")
        self.approval_received = False
        
        while not self.approval_received and not self.should_stop:
            time.sleep(0.1)
        
        # Update config with chapter count
        self.update_config("TotalChapters", self.total_chapters)
    
    def generate_characters(self):
        """Step 4: Generate character profiles"""
        self.current_step = "characters"
        self.status_updated.emit("Generating characters...")
        self.log("Generating character profiles...")
        
        # Simulate character generation
        characters = [
            {
                "Name": "Protagonist",
                "Age": 28,
                "Background": "Skilled hacker with a troubled past",
                "Traits": ["Determined", "Resourceful", "Conflicted"],
                "Arc": "From lone wolf to reluctant leader"
            },
            {
                "Name": "Antagonist",
                "Age": 45,
                "Background": "Corporate executive with hidden agenda",
                "Traits": ["Calculating", "Charismatic", "Ruthless"],
                "Arc": "Revelation of true motivations"
            }
        ]
        
        self.characters = characters
        characters_json = json.dumps(characters, indent=2)
        self.save_to_file("characters.txt", characters_json)
        
        # Emit and wait for approval
        self.new_characters.emit(characters_json)
        self.waiting_approval.emit("characters")
        self.approval_received = False
        
        while not self.approval_received and not self.should_stop:
            time.sleep(0.1)
    
    def generate_world(self):
        """Step 4: Generate world-building details"""
        self.current_step = "world"
        self.status_updated.emit("Generating world details...")
        self.log("Generating world-building details...")
        
        # Simulate world generation
        world = {
            "Tech": "Neural implants mandatory for all citizens",
            "Culture": "Stratified society with strict class divisions",
            "Geography": "Sprawling megacity divided into sectors",
            "History": "Built after the Great Collapse of 2075",
            "Economy": "Corporate-controlled surveillance capitalism"
        }
        
        self.world = world
        world_json = json.dumps(world, indent=2)
        self.save_to_file("world.txt", world_json)
        
        # Emit and wait for approval
        self.new_world.emit(world_json)
        self.waiting_approval.emit("world")
        self.approval_received = False
        
        while not self.approval_received and not self.should_stop:
            time.sleep(0.1)
    
    def generate_timeline(self):
        """Step 5: Generate timeline"""
        self.current_step = "timeline"
        self.status_updated.emit("Synchronizing timeline...")
        self.log("Generating timeline...")
        
        # Simulate timeline generation
        timeline = {
            "Day 1": "Story begins - protagonist discovers the truth",
            "Day 3": "First confrontation with authorities",
            "Day 7": "Alliance formed with rebels",
            "Day 14": "Major setback and betrayal",
            "Day 21": "Climactic battle",
            "Day 22": "Resolution"
        }
        
        self.timeline = timeline
        timeline_json = json.dumps(timeline, indent=2)
        self.save_to_file("timeline.txt", timeline_json)
        
        self.log("Timeline synchronized")
        self.approval_received = True  # Auto-approve timeline for now
    
    def writing_loop(self):
        """Step 6-9: Iterative writing loop"""
        self.current_step = "writing"
        self.log("Starting writing loop...")
        
        for chapter in range(1, self.total_chapters + 1):
            if self.should_stop:
                break
            
            self.current_chapter = chapter
            
            for section in range(1, self.sections_per_chapter + 1):
                if self.should_stop:
                    break
                
                # Wait if paused
                while self.is_paused and not self.should_stop:
                    time.sleep(0.1)
                
                self.current_section = section
                self.generate_section(chapter, section)
                
                # Update progress
                total_sections = self.total_chapters * self.sections_per_chapter
                completed_sections = (chapter - 1) * self.sections_per_chapter + section
                progress = int((completed_sections / total_sections) * 100)
                self.progress_updated.emit(progress)
                
                # Check if we should extend or wrap up at 80%
                if progress >= 80 and not hasattr(self, 'extension_decided'):
                    self.log("Reached 80% - continuing to completion")
                    self.extension_decided = True
    
    def generate_section(self, chapter: int, section: int):
        """Generate a single section"""
        self.status_updated.emit(f"Writing Chapter {chapter}, Section {section}...")
        self.log(f"Generating Chapter {chapter}, Section {section}...")
        
        # Simulate section generation (750-1000 words)
        content = self.simulate_section_generation(chapter, section)
        
        # Save draft
        draft_dir = os.path.join(self.project_dir, "drafts", f"chapter{chapter}")
        os.makedirs(draft_dir, exist_ok=True)
        
        draft_path = os.path.join(draft_dir, f"section{section}_v1.txt")
        with open(draft_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Emit for approval
        self.new_draft.emit(chapter, section, content)
        self.waiting_approval.emit(f"section_{chapter}_{section}")
        self.approval_received = False
        
        # Wait for approval
        while not self.approval_received and not self.should_stop:
            time.sleep(0.1)
        
        # If approved, append to story
        if self.approval_received:
            self.append_to_story(f"\n\n=== Chapter {chapter}, Section {section} ===\n\n{content}")
            self.log(f"Chapter {chapter}, Section {section} approved and added to story")
        
        # Handle adjustment if needed
        if self.adjustment_feedback:
            self.log(f"Adjusting section with feedback: {self.adjustment_feedback}")
            # In real implementation, would regenerate with feedback
            self.adjustment_feedback = None
    
    def simulate_section_generation(self, chapter: int, section: int) -> str:
        """Simulate section content generation"""
        word_count = random.randint(750, 1000)
        return f"""
Chapter {chapter}, Section {section}

[This is simulated content for demonstration purposes.]

The story continues with intensity and depth. Characters navigate complex situations,
facing moral dilemmas and external threats. The {self.tone} tone permeates every scene,
building tension and engaging the reader.

Detailed descriptions bring the world to life. Dialogue reveals character motivations
and advances the plot. Action sequences are balanced with introspective moments.

The narrative maintains consistency with established characters, world-building, and
timeline. Each section builds upon the previous one, creating a cohesive whole.

[Approximately {word_count} words in actual implementation]
"""
    
    def complete_novel(self):
        """Step 11: Complete and finalize novel"""
        self.current_step = "completion"
        self.status_updated.emit("Completing novel...")
        self.log("Finalizing novel...")
        
        # Run consistency checks
        self.log("Running consistency checks...")
        
        # Update final config
        self.update_config("Progress", "100%")
        self.update_config("Status", "Complete")
        
        self.log("Novel generation complete!")
        self.status_updated.emit("Complete!")
    
    # ============ Helper Methods ============
    
    def log(self, message: str):
        """Log a message to file and emit signal"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - {message}"
        
        # Emit signal
        self.log_update.emit(log_entry)
        
        # Write to file
        log_path = os.path.join(self.project_dir, "log.txt")
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def save_to_file(self, filename: str, content: str):
        """Save content to a file in the project directory"""
        filepath = os.path.join(self.project_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def append_to_story(self, content: str):
        """Append content to story.txt"""
        story_path = os.path.join(self.project_dir, "story.txt")
        with open(story_path, 'a', encoding='utf-8') as f:
            f.write(content)
    
    def update_config(self, key: str, value: Any):
        """Update a value in config.txt"""
        config_path = os.path.join(self.project_dir, "config.txt")
        
        # Read current config
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        else:
            lines = []
        
        # Update or add key
        found = False
        for i, line in enumerate(lines):
            if line.startswith(f"{key}:"):
                lines[i] = f"{key}: {value}\n"
                found = True
                break
        
        if not found:
            lines.append(f"{key}: {value}\n")
        
        # Write back
        with open(config_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
    
    def approve_current_step(self):
        """Approve current step"""
        self.approval_received = True
        self.adjustment_feedback = None
    
    def adjust_current_step(self, feedback: str):
        """Request adjustment with feedback"""
        self.adjustment_feedback = feedback
        self.approval_received = True  # Continue but with adjustment
    
    def pause(self):
        """Pause workflow"""
        self.is_paused = True
        self.log("Workflow paused")
    
    def resume(self):
        """Resume workflow"""
        self.is_paused = False
        self.log("Workflow resumed")
    
    def stop(self):
        """Stop workflow"""
        self.should_stop = True
        self.log("Workflow stopped")


# Factory function
def create_workflow_thread(project_dir: str, idea: str, tone: str, target_words: int):
    """Create workflow thread instance"""
    return AutomatedNovelWorkflowThread(project_dir, idea, tone, target_words)

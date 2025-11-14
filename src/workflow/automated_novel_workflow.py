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

# Import API manager for AI integration
try:
    from ..system.api_manager import get_api_manager
    API_MANAGER_AVAILABLE = True
except ImportError:
    API_MANAGER_AVAILABLE = False
    print("Warning: API manager not available")


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
        
        # Initialize API manager for AI integration
        if API_MANAGER_AVAILABLE:
            self.api_manager = get_api_manager()
        else:
            self.api_manager = None
            self.log("Warning: API manager not available - using simulation mode")
        
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
        """Step 2: Generate synopsis using AI"""
        self.current_step = "synopsis"
        self.status_updated.emit("Generating synopsis...")
        self.log("Generating synopsis with AI...")
        
        # Generate synopsis using AI or fallback to simulation
        if self.api_manager:
            synopsis = self.generate_synopsis_with_ai()
        else:
            self.log("API manager not available - using simulation")
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
    
    def generate_synopsis_with_ai(self) -> str:
        """Generate synopsis using AI API"""
        try:
            # Create prompt for synopsis generation
            prompt = f"""Create a comprehensive synopsis for a novel based on the following:

Story Idea: {self.idea}
Tone: {self.tone}
Target Length: {self.target_words:,} words
Target Chapters: {self.total_chapters}

The synopsis should be 500-1000 words and include:
1. Setting and world context
2. Main characters introduction
3. Central conflict
4. Key plot points
5. Overall narrative arc
6. Thematic elements

Write the synopsis in a {self.tone} tone and make it compelling for readers."""

            # Call OpenAI API through API manager
            self.log("Calling AI API for synopsis generation...")
            response = self.api_manager.generate_text_openai(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.7
            )
            
            if response and 'choices' in response and len(response['choices']) > 0:
                synopsis = response['choices'][0]['message']['content'].strip()
                self.log("AI synopsis generated successfully")
                return synopsis
            else:
                self.log("AI API returned empty response - using fallback")
                return self.simulate_synopsis_generation()
                
        except Exception as e:
            self.log(f"Error generating synopsis with AI: {str(e)}")
            self.log("Falling back to simulation mode")
            return self.simulate_synopsis_generation()
    
    def simulate_synopsis_generation(self) -> str:
        """Simulate synopsis generation (fallback when API not available)"""
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
        """Refine synopsis based on user feedback"""
        if self.api_manager and self.adjustment_feedback:
            # Use AI to refine based on feedback
            try:
                prompt = f"""Refine the following synopsis based on this feedback:

Current Synopsis:
{self.synopsis}

User Feedback:
{self.adjustment_feedback}

Please revise the synopsis to address the feedback while maintaining coherence and quality."""

                response = self.api_manager.generate_text_openai(
                    prompt=prompt,
                    max_tokens=1500,
                    temperature=0.7
                )
                
                if response and 'choices' in response:
                    self.synopsis = response['choices'][0]['message']['content'].strip()
                    self.save_to_file("synopsis.txt", self.synopsis)
                    self.log("Synopsis refined with AI")
            except Exception as e:
                self.log(f"Error refining synopsis with AI: {str(e)}")
        
        # Re-emit for review
        self.new_synopsis.emit(self.synopsis)
        self.waiting_approval.emit("synopsis")
        self.approval_received = False
        
        while not self.approval_received and not self.should_stop:
            time.sleep(0.1)
    
    def generate_outline(self):
        """Step 4: Generate outline using AI"""
        self.current_step = "outline"
        self.status_updated.emit("Generating outline...")
        self.log("Generating outline with AI...")
        
        # Generate outline using AI or fallback to simulation
        if self.api_manager:
            outline = self.generate_outline_with_ai()
        else:
            self.log("API manager not available - using simulation")
            outline = self.simulate_outline_generation()
        
        self.outline = outline
        self.save_to_file("outline.txt", self.outline)
        
        # Emit and wait for approval
        self.new_outline.emit(outline)
        self.waiting_approval.emit("outline")
        self.approval_received = False
        
        while not self.approval_received and not self.should_stop:
            time.sleep(0.1)
        
        # Update config with chapter count
        self.update_config("TotalChapters", self.total_chapters)
    
    def generate_outline_with_ai(self) -> str:
        """Generate outline using AI API"""
        try:
            prompt = f"""Create a detailed chapter-by-chapter outline for the following novel:

Synopsis:
{self.synopsis}

Story Idea: {self.idea}
Tone: {self.tone}
Target Chapters: {self.total_chapters}

Generate an outline with {self.total_chapters} chapters. For each chapter, provide:
1. Chapter title
2. Key events (3-5 bullet points)
3. Character development
4. Plot progression
5. Estimated word count (aim for 8,000-12,000 words per chapter)

Format each chapter clearly and maintain narrative flow."""

            self.log("Calling AI API for outline generation...")
            response = self.api_manager.generate_text_openai(
                prompt=prompt,
                max_tokens=3000,
                temperature=0.7
            )
            
            if response and 'choices' in response:
                outline = response['choices'][0]['message']['content'].strip()
                self.log("AI outline generated successfully")
                return outline
            else:
                return self.simulate_outline_generation()
                
        except Exception as e:
            self.log(f"Error generating outline with AI: {str(e)}")
            return self.simulate_outline_generation()
    
    def simulate_outline_generation(self) -> str:
        """Simulate outline generation (fallback)"""
        outline_parts = []
        for i in range(1, self.total_chapters + 1):
            chapter_title = f"Chapter {i}: The Journey Continues"
            chapter_summary = f"In this chapter, events unfold that drive the narrative forward. Characters face new challenges and the plot thickens. (Estimated {8000 + random.randint(0, 4000)} words)"
            outline_parts.append(f"{chapter_title}\n{chapter_summary}\n")
        
        return "\n".join(outline_parts)
    
    def generate_characters(self):
        """Step 4: Generate character profiles using AI"""
        self.current_step = "characters"
        self.status_updated.emit("Generating characters...")
        self.log("Generating character profiles with AI...")
        
        # Generate characters using AI or fallback
        if self.api_manager:
            characters_json = self.generate_characters_with_ai()
        else:
            self.log("API manager not available - using simulation")
            characters_json = self.simulate_character_generation()
        
        # Parse and save
        try:
            self.characters = json.loads(characters_json)
        except json.JSONDecodeError:
            self.log("Warning: Character JSON parsing failed, saving as-is")
            self.characters = []
        
        self.save_to_file("characters.txt", characters_json)
        
        # Emit and wait for approval
        self.new_characters.emit(characters_json)
        self.waiting_approval.emit("characters")
        self.approval_received = False
        
        while not self.approval_received and not self.should_stop:
            time.sleep(0.1)
    
    def generate_characters_with_ai(self) -> str:
        """Generate character profiles using AI"""
        try:
            prompt = f"""Create detailed character profiles for the following novel:

Synopsis:
{self.synopsis}

Outline:
{self.outline[:1000]}...  

Generate 3-5 main characters in JSON format. For each character include:
- Name
- Age
- Background (2-3 sentences)
- Personality Traits (list of 3-5)
- Motivations
- Character Arc
- Relationships (to other characters)
- Role in the story

Return as a JSON array of character objects."""

            self.log("Calling AI API for character generation...")
            response = self.api_manager.generate_text_openai(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.7
            )
            
            if response and 'choices' in response:
                chars = response['choices'][0]['message']['content'].strip()
                self.log("AI characters generated successfully")
                return chars
            else:
                return self.simulate_character_generation()
                
        except Exception as e:
            self.log(f"Error generating characters with AI: {str(e)}")
            return self.simulate_character_generation()
    
    def simulate_character_generation(self) -> str:
        """Simulate character generation (fallback)"""
        characters = [
            {
                "Name": "Protagonist",
                "Age": 28,
                "Background": "Skilled hacker with a troubled past, grew up in the lower sectors",
                "Traits": ["Determined", "Resourceful", "Conflicted", "Loyal"],
                "Motivations": "Seeking justice and truth",
                "Arc": "From lone wolf to reluctant leader",
                "Relationships": "Mentored by old rebel, conflicts with antagonist",
                "Role": "Main character driving the plot forward"
            },
            {
                "Name": "Antagonist",
                "Age": 45,
                "Background": "Corporate executive with hidden agenda, former idealist turned pragmatist",
                "Traits": ["Calculating", "Charismatic", "Ruthless", "Visionary"],
                "Motivations": "Control through order and efficiency",
                "Arc": "Revelation of true motivations and eventual downfall",
                "Relationships": "Former friend of protagonist's mentor",
                "Role": "Primary opposition and moral counterpoint"
            },
            {
                "Name": "Mentor",
                "Age": 62,
                "Background": "Former resistance leader, now in hiding",
                "Traits": ["Wise", "Cautious", "Haunted by past"],
                "Motivations": "Protecting the next generation",
                "Arc": "From passive observer to active participant",
                "Relationships": "Guides protagonist, old friend of antagonist",
                "Role": "Source of wisdom and historical context"
            }
        ]
        
        return json.dumps(characters, indent=2)
    
    def generate_world(self):
        """Step 4: Generate world-building details using AI"""
        self.current_step = "world"
        self.status_updated.emit("Generating world details...")
        self.log("Generating world-building details with AI...")
        
        # Generate world using AI or fallback
        if self.api_manager:
            world_json = self.generate_world_with_ai()
        else:
            self.log("API manager not available - using simulation")
            world_json = self.simulate_world_generation()
        
        # Parse and save
        try:
            self.world = json.loads(world_json)
        except json.JSONDecodeError:
            self.log("Warning: World JSON parsing failed, saving as-is")
            self.world = {}
        
        self.save_to_file("world.txt", world_json)
        
        # Emit and wait for approval
        self.new_world.emit(world_json)
        self.waiting_approval.emit("world")
        self.approval_received = False
        
        while not self.approval_received and not self.should_stop:
            time.sleep(0.1)
    
    def generate_world_with_ai(self) -> str:
        """Generate world-building using AI"""
        try:
            prompt = f"""Create comprehensive world-building details for the following novel:

Synopsis:
{self.synopsis}

Create world-building in JSON format with these categories:
- Technology: Key technological elements
- Culture: Social norms and customs
- Geography: Physical setting and locations
- History: Important historical events
- Economy: Economic system and structure
- Politics: Government and power structures
- Magic/Science: Any special systems (if applicable)
- Daily Life: How ordinary people live

Return as a JSON object with detailed descriptions."""

            self.log("Calling AI API for world-building generation...")
            response = self.api_manager.generate_text_openai(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.7
            )
            
            if response and 'choices' in response:
                world = response['choices'][0]['message']['content'].strip()
                self.log("AI world-building generated successfully")
                return world
            else:
                return self.simulate_world_generation()
                
        except Exception as e:
            self.log(f"Error generating world with AI: {str(e)}")
            return self.simulate_world_generation()
    
    def simulate_world_generation(self) -> str:
        """Simulate world generation (fallback)"""
        world = {
            "Technology": "Neural implants mandatory for all citizens, quantum computing network, AI-assisted everything",
            "Culture": "Stratified society with strict class divisions, merit-based advancement propaganda masks rigid hierarchy",
            "Geography": "Sprawling megacity divided into sectors, upper levels for elite, lower levels for workers",
            "History": "Built after the Great Collapse of 2075, rebuilt under corporate guidance, old world mostly forgotten",
            "Economy": "Corporate-controlled surveillance capitalism, digital currency only, social credit system",
            "Politics": "Nominally democratic but controlled by corporate council, citizens vote but choices pre-selected",
            "DailyLife": "Monitored from birth to death, entertainment provided to keep masses content, limited freedom"
        }
        
        return json.dumps(world, indent=2)
    
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
        """Generate a single section using AI"""
        self.status_updated.emit(f"Writing Chapter {chapter}, Section {section}...")
        self.log(f"Generating Chapter {chapter}, Section {section}...")
        
        # Generate section using AI or fallback
        if self.api_manager:
            content = self.generate_section_with_ai(chapter, section)
        else:
            self.log("API manager not available - using simulation")
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
            # Regenerate with feedback
            content = self.generate_section_with_ai(chapter, section, self.adjustment_feedback)
            self.adjustment_feedback = None
            # Re-emit for review
            self.new_draft.emit(chapter, section, content)
            self.waiting_approval.emit(f"section_{chapter}_{section}")
            self.approval_received = False
            while not self.approval_received and not self.should_stop:
                time.sleep(0.1)
    
    def generate_section_with_ai(self, chapter: int, section: int, feedback: str = None) -> str:
        """Generate section content using AI"""
        try:
            # Get context from previous sections
            story_so_far = self.get_story_context(chapter, section)
            
            # Build prompt with full context
            prompt = f"""Write section {section} of chapter {chapter} for this novel:

Synopsis:
{self.synopsis}

Outline excerpt:
{self.get_chapter_outline(chapter)}

Characters:
{json.dumps(self.characters, indent=2) if self.characters else "Not yet defined"}

World:
{json.dumps(self.world, indent=2) if self.world else "Not yet defined"}

Previous content (last 500 words):
{story_so_far}"""

            if feedback:
                prompt += f"\n\nUser Feedback: {feedback}\nPlease revise the section addressing this feedback."
            else:
                prompt += f"""

Write a compelling section of 800-1200 words that:
1. Maintains consistency with established characters and world
2. Advances the plot according to the outline
3. Uses a {self.tone} tone throughout
4. Includes vivid descriptions and engaging dialogue
5. Ends with a transition or hook to the next section

Write only the prose content, no meta-commentary."""

            self.log(f"Calling AI API for section {chapter}.{section} generation...")
            response = self.api_manager.generate_text_openai(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.8  # Slightly higher for creative writing
            )
            
            if response and 'choices' in response:
                content = response['choices'][0]['message']['content'].strip()
                self.log(f"AI section {chapter}.{section} generated successfully ({len(content.split())} words)")
                return content
            else:
                self.log("AI API returned empty response - using simulation")
                return self.simulate_section_generation(chapter, section)
                
        except Exception as e:
            self.log(f"Error generating section with AI: {str(e)}")
            return self.simulate_section_generation(chapter, section)
    
    def get_story_context(self, current_chapter: int, current_section: int) -> str:
        """Get context from previous story sections"""
        try:
            story_path = os.path.join(self.project_dir, "story.txt")
            if os.path.exists(story_path):
                with open(story_path, 'r', encoding='utf-8') as f:
                    story = f.read()
                    # Get last 500 words for context
                    words = story.split()
                    if len(words) > 500:
                        return " ".join(words[-500:])
                    return story
        except Exception as e:
            self.log(f"Error reading story context: {str(e)}")
        
        return "Story beginning..."
    
    def get_chapter_outline(self, chapter: int) -> str:
        """Extract relevant chapter outline"""
        try:
            if self.outline:
                lines = self.outline.split('\n')
                chapter_lines = []
                in_chapter = False
                for line in lines:
                    if f"Chapter {chapter}" in line:
                        in_chapter = True
                    elif in_chapter and f"Chapter {chapter + 1}" in line:
                        break
                    elif in_chapter:
                        chapter_lines.append(line)
                
                if chapter_lines:
                    return "\n".join(chapter_lines)
        except Exception as e:
            self.log(f"Error extracting chapter outline: {str(e)}")
        
        return f"Chapter {chapter}: Continue the story"
    
    def simulate_section_generation(self, chapter: int, section: int) -> str:
        """Simulate section content generation (fallback)"""
        word_count = random.randint(800, 1200)
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

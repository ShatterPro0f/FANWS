# Automated Novel Writing System

## Overview

The Automated Novel Writing System is a comprehensive GUI-based tool for generating full-length novels (200,000-300,000 words) with minimal user input. It integrates multiple AI tools and provides a step-by-step workflow from concept to completion.

## Features

### User Interface
- **Modern Dark Theme**: Professional dark-themed interface with resizable panels
- **Three-Panel Layout**:
  - **Left Sidebar (20%)**: Navigation to different views (Dashboard, Story, Logs, Config, Characters, World, Summaries, Drafts)
  - **Central Panel (60%)**: Dynamic content area for initialization, planning, and writing
  - **Right Panel (20%)**: Real-time dashboard with progress tracking, mood meter, and notifications
- **Bottom Status Bar**: Workflow controls (Resume, Stop) and status display

### Workflow Phases

#### 1. Initialization
- Input novel idea (e.g., "A hacker's rebellion in a dystopian city")
- Specify tone (e.g., "dark and tense")
- Set target word count (default: 250,000)
- Automatic project file creation

#### 2. Planning Phase
- **Synopsis Generation**: AI-generated 500-1000 word synopsis
- **Outline Creation**: 25 chapters with summaries and key events
- **Character Profiles**: Main characters with backgrounds, traits, and arcs
- **World Building**: Tech, culture, geography, and other world details
- **Timeline Synchronization**: Chronological consistency checking
- User approval/adjustment at each step

#### 3. Writing Phase
- Iterative section-by-section generation (500-1000 words per section)
- Real-time progress tracking
- Section approval workflow
- Adjustment capability with feedback
- Pause/resume functionality

#### 4. Completion
- Consistency checks
- Export to DOCX, PDF, or TXT formats

## File Structure

When you initialize a project, the following files are created:

```
projects/novel_YYYYMMDD_HHMMSS/
├── story.txt              # Final approved novel text
├── log.txt                # System logs with timestamps
├── config.txt             # Project configuration and progress
├── context.txt            # Narrative state tracking
├── characters.txt         # Character profiles (JSON)
├── world.txt             # World-building details (JSON)
├── summaries.txt         # Chapter summaries
├── weights.txt           # Tool usage weights
├── synopsis.txt          # Generated synopsis
├── outline.txt           # Generated outline
├── timeline.txt          # Timeline data
├── buffer_backup.txt     # Hourly backup
├── story_backup.txt      # Story backup
├── log_backup.txt        # Log backup
└── drafts/               # Draft versions by chapter
    └── chapter1/
        ├── section1_v1.txt
        ├── section2_v1.txt
        └── ...
```

## Usage

### Launching the GUI

```bash
# From the FANWS root directory
python fanws.py --automated-novel
```

Or use the test script:

```bash
python test_automated_gui.py
```

### Basic Workflow

1. **Start the Application**
   - Launch with `python fanws.py --automated-novel`
   
2. **Initialize Your Novel**
   - Enter your novel idea in the text area
   - Specify the tone/style
   - Set target word count
   - Click "Start Novel Generation"
   
3. **Review and Approve Planning**
   - Review generated synopsis
   - Click "Approve" or "Adjust" with feedback
   - Repeat for outline, characters, and world
   
4. **Monitor Writing Progress**
   - Watch real-time progress in the dashboard
   - Review each section as it's generated
   - Approve or request adjustments
   - Pause/resume as needed
   
5. **Export Your Novel**
   - File > Export Novel
   - Choose format (DOCX, PDF, TXT)
   - Save to your desired location

### Navigation

Use the sidebar buttons to view different aspects of your project:

- **Dashboard**: Overview shown in right panel
- **Story**: View the complete story text
- **Logs**: System activity with color-coded messages (info: white, warning: yellow, error: red)
- **Config**: Project configuration and settings
- **Characters**: Structured view of character profiles
- **World**: World-building details
- **Summaries**: Chapter summaries
- **Drafts**: Tree view of all draft versions

## Configuration

### API Keys

Configure your API keys in a `.env` file (copy from `.env.example`):

```bash
# AI Services
OPENAI_API_KEY=your_key_here
XAI_API_KEY=your_key_here
THESAURUS_API_KEY=your_key_here

# Web-based Tools (for Selenium automation)
SASSBOOK_USER=your_email
SASSBOOK_PASS=your_password
RYTR_USER=your_email
RYTR_PASS=your_password
GRAMMARLY_USER=your_email
GRAMMARLY_PASS=your_password
```

### Tool Integration

The system is designed to integrate with:
- **ChatGPT 4o API**: Project management, synopsis, outline, polishing
- **xAI API (Grok)**: Initial draft generation
- **Sassbook AI**: Creative enhancement
- **DeepL Write**: Sentence refinement
- **Perplexity**: Research and context
- **Thesaurus API**: Vocabulary adjustment
- **Rytr**: Backup draft generation
- **Grammarly**: Grammar and style correction

Note: Full integration with web-based tools (Selenium automation) is planned for future updates.

## Current Implementation

### Available Now
- ✅ Complete GUI interface
- ✅ Project initialization and file management
- ✅ Background workflow thread
- ✅ Real-time progress tracking
- ✅ Approval/adjustment workflow
- ✅ Export to multiple formats
- ✅ Log viewing with syntax highlighting
- ✅ Structured data display (JSON)

### Coming Soon
- 🔄 Full AI API integration (currently simulated)
- 🔄 Selenium automation for web tools
- 🔄 Advanced consistency checking
- 🔄 Enhanced mood and pacing analysis
- 🔄 Collaborative features

## Technical Details

### Architecture
- **GUI Framework**: PyQt5
- **Background Processing**: QThread for non-blocking workflow
- **Signal/Slot Communication**: PyQt signal system for GUI updates
- **File Format**: UTF-8 text files, JSON for structured data

### Requirements
- Python 3.8+
- PyQt5
- python-docx (for DOCX export)
- reportlab (for PDF export)
- Additional dependencies in `requirements.txt`

## Troubleshooting

### GUI doesn't launch
- Ensure PyQt5 is installed: `pip install PyQt5`
- Check for Python version 3.8 or higher

### Workflow not starting
- Check that the workflow backend is properly imported
- Review logs in the Logs tab for error messages

### Export fails
- Ensure python-docx is installed for DOCX export
- Ensure reportlab is installed for PDF export
- Check file permissions in the project directory

## Support

For issues, questions, or feature requests:
1. Check the User Guide (Help > User Guide in the GUI)
2. Review logs in the Logs tab
3. Open an issue on the GitHub repository

## Future Enhancements

Planned features for future releases:
- Real-time AI API integration
- Selenium-based automation for web tools
- Advanced analytics and visualization
- Multi-project management
- Cloud synchronization
- Collaborative editing
- Plugin system for custom AI providers
- Advanced export options (EPUB, Markdown)

---

**Note**: This is an automated system designed to assist with novel writing. While it generates content automatically, human review and editing are recommended for the best results.

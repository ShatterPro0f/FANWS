# Fiction AI Novel Writing Suite (FANWS)

**FANWS** is a comprehensive, AI-powered novel writing application designed to assist fiction authors with every aspect of the creative writing process. From initial concept to final export, FANWS provides intelligent tools, templates, and workflow management to enhance your writing productivity.

## ✨ Key Features

### 🤖 AI-Powered Writing Assistance
- **Multi-Provider AI Support** - OpenAI, Claude, and other leading AI providers
- **Intelligent Content Generation** - Characters, plot points, world-building, and narrative sections
- **Dynamic Template System** - Genre-specific templates for fantasy, mystery, romance, sci-fi, and more
- **Context-Aware Suggestions** - AI learns from your writing style and project history

### 📚 Comprehensive Project Management
- **Multi-Project Workspace** - Manage multiple novels simultaneously
- **Modular Workflow System** - Customizable writing workflows and step-by-step guidance
- **Version Control** - Track drafts, revisions, and template versions
- **Backup & Recovery** - Automated project backups and data protection

### 🎨 Advanced Writing Tools
- **Template Collections** - Pre-built frameworks for character development, plot structures, world-building
- **Text Analytics** - Readability analysis, word count tracking, writing statistics
- **Consistency Checking** - Character arc validation, plot continuity analysis
- **Synonym Integration** - Enhanced vocabulary suggestions with WordsAPI

### 🔌 Extensible Plugin Architecture
- **Plugin System** - Extend functionality with custom plugins
- **Content Generators** - Specialized content creation tools
- **Export Formats** - Multiple output formats (DOCX, EPUB, HTML, PDF)
- **Integration Support** - Third-party service integrations

### 🎯 Modern User Interface
- **Intuitive Design** - Clean, responsive interface with modern UI components
- **Performance Monitoring** - Real-time performance tracking and optimization
- **Collaborative Features** - Multi-user support and shared project functionality
- **Analytics Dashboard** - Writing progress, productivity insights, and goal tracking

## 🚀 Installation

### Prerequisites
- **Python 3.8 or higher** - Download from [python.org](https://www.python.org/downloads/)
- **Operating System** - Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Memory** - Minimum 4GB RAM, 8GB recommended
- **Storage** - 1GB free space for installation and project files

### Quick Start Installation
1. **Clone or download FANWS**
   ```bash
   git clone https://github.com/yourusername/FANWS.git
   cd FANWS
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python fanws.py
   ```

### Alternative Installation Methods
- **Virtual Environment** (Recommended):
  ```bash
  python -m venv fanws_env
  fanws_env\Scripts\activate  # Windows
  source fanws_env/bin/activate  # macOS/Linux
  pip install -r requirements.txt
  ```

- **Manual dependency installation**:
  ```bash
  pip install PyQt5 PyQtWebEngine PyYAML python-dotenv psutil tenacity python-docx markdown2 lz4 aiohttp requests nltk textstat scikit-learn numpy reportlab ebooklib pdfkit matplotlib pytest
  ```

## 🎯 Getting Started

### First Time Setup
1. **Launch FANWS** - Run `python fanws.py`
2. **Create your first project** - Click "Create New Project" in the sidebar
3. **Configure AI providers** - Go to Advanced Settings and add your API keys
4. **Choose a template** - Select from genre-specific writing templates
5. **Start writing** - Use the guided workflow or free-form writing mode

### Essential Configuration
- **OpenAI API Key** - For advanced AI writing assistance
- **WordsAPI Key** - For enhanced vocabulary and synonyms
- **Project Settings** - Configure word count goals, genres, and writing preferences
- **Template Preferences** - Select and customize writing templates

## 🎨 Core Workflows

### Novel Writing Process
1. **Project Creation** - Set up novel metadata, goals, and structure
2. **Template Selection** - Choose appropriate templates for your genre
3. **Character Development** - Create detailed character profiles and arcs
4. **World Building** - Develop settings, cultures, and fictional elements
5. **Plot Development** - Structure story arcs, conflicts, and resolutions
6. **Drafting** - AI-assisted writing with context awareness
7. **Review & Revision** - Consistency checking and readability analysis
8. **Export** - Generate final output in multiple formats

### Template System
- **Browse Collections** - Fantasy, Mystery, Romance, Sci-Fi, Character, Plot, World-building
- **Customize Variables** - Fill template variables with your story elements
- **Generate Content** - AI creates customized content based on templates
- **Save Configurations** - Reuse successful template combinations

## 📁 Project Structure

```
FANWS/
├── fanws.py                    # Main application entry point
├── requirements.txt            # Python dependencies
├── src/                        # Core application modules
│   ├── api_manager.py         # AI provider management
│   ├── workflow_manager.py    # Writing workflow system
│   ├── template_manager.py    # Template system
│   ├── ui/                    # User interface components
│   ├── plugin_system.py       # Plugin architecture
│   └── ...                    # Additional modules
├── plugins/                    # Plugin directory
│   ├── content_generators/    # Content generation plugins
│   ├── export_formats/        # Export format plugins
│   ├── text_processors/       # Text processing plugins
│   └── ...                    # Additional plugin categories
├── templates/                  # Writing templates
├── projects/                   # User project files
├── config/                     # Configuration files
├── metadata/                   # System metadata and templates
└── docs/                       # Documentation
```

## 🔧 Advanced Features

### Plugin Development
- **Custom Plugins** - Extend FANWS with your own functionality
- **Plugin API** - Comprehensive plugin development interface
- **Plugin Manager** - Install, configure, and manage plugins
- **Hot Reloading** - Develop plugins with instant updates

### Database Integration
- **Project Storage** - SQLite-based project and metadata storage
- **Performance Optimization** - Connection pooling and query optimization
- **Data Analytics** - Writing statistics and progress tracking
- **Backup Systems** - Automated data protection and recovery

### Collaborative Features
- **Multi-User Support** - Share projects with other writers
- **Real-Time Collaboration** - Simultaneous editing and feedback
- **Version Tracking** - Track changes and contributions
- **Notification System** - Stay updated on project activities

## 📊 Export Formats

FANWS supports comprehensive export options:
- **Microsoft Word (.docx)** - Industry-standard manuscript format
- **EPUB (.epub)** - E-book format for digital publishing
- **HTML (.html)** - Web-ready format with styling
- **PDF (.pdf)** - Print-ready format (requires wkhtmltopdf)
- **Plain Text (.txt)** - Universal text format
- **Markdown (.md)** - Writer-friendly markup format

## 🛠️ Troubleshooting

### Common Issues

**Application won't start**
- Verify Python 3.8+ is installed: `python --version`
- Check all dependencies are installed: `pip install -r requirements.txt`
- Review error logs in `logs/errors.log`

**AI features not working**
- Verify API keys in Advanced Settings
- Check internet connectivity
- Review API usage limits and quotas
- Check logs for specific error messages

**Performance issues**
- Close unnecessary projects
- Clear cache in Performance settings
- Check available system memory
- Review plugin performance in Plugin Manager

**Export failures**
- Verify write permissions in export directory
- Check available disk space
- For PDF export, ensure wkhtmltopdf is installed
- Review export logs for specific errors

### Getting Help
- **Documentation** - Check `docs/` directory for detailed guides
- **Template Guide** - See `metadata/template_usage_guide.md`
- **Database Schema** - Review `metadata/database_schema_guide.md`
- **System Information** - Check `metadata/system_information.json`
- **Logs** - Review `logs/` directory for detailed error information

## 🤝 Contributing

FANWS is designed to be extensible and welcomes contributions:
- **Plugin Development** - Create new plugins for specific writing needs
- **Template Creation** - Develop genre-specific writing templates
- **Bug Reports** - Report issues through the project's issue tracker
- **Feature Requests** - Suggest new functionality and improvements
- **Documentation** - Help improve user guides and technical documentation

## 📄 License

FANWS is released under the MIT License. See LICENSE file for details.

## 🔗 Resources

- **Project Website** - [Coming Soon]
- **User Guide** - `docs/user_guide.md`
- **Developer Documentation** - `docs/developer_guide.md`
- **Plugin Development Guide** - `docs/plugin_development.md`
- **Template Creation Guide** - `metadata/template_usage_guide.md`
- **API Documentation** - `docs/api_reference.md`

---

**Happy Writing!** 📝✨

*FANWS - Empowering authors with intelligent writing tools since 2025*
- **Reset caches or logs**
  - Use the Advanced tab to clear the synonym cache or reset the API log.
- **Still having issues?**
  - Restart the application and try again. If problems persist, check your internet connection and API limits.

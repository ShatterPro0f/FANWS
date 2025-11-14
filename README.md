# Fiction AI Novel Writing Suite (FANWS)

[![Tests](https://github.com/ShatterPro0f/FANWS/actions/workflows/tests.yml/badge.svg)](https://github.com/ShatterPro0f/FANWS/actions/workflows/tests.yml)

**FANWS** is a comprehensive, AI-powered novel writing application designed to assist fiction authors with every aspect of the creative writing process. From initial concept to final export, FANWS provides intelligent tools, templates, and workflow management to enhance your writing productivity.

## ✨ Key Features

### 🤖 AI-Powered Writing Assistance
- **Multi-Provider AI Support** - OpenAI, Claude, and other leading AI providers
- **Intelligent Content Generation** - Characters, plot points, world-building, and narrative sections
- **Dynamic Template System** - Genre-specific templates for fantasy, mystery, romance, sci-fi, and more
- **Context-Aware Suggestions** - AI learns from your writing style and project history
- **🆕 Automated Novel Writing** - Complete novel generation from concept to 200,000+ words with minimal input

### 📚 Comprehensive Project Management
- **Multi-Project Workspace** - Manage multiple novels simultaneously
- **Modular Workflow System** - Customizable writing workflows and step-by-step guidance
- **Version Control** - Track drafts, revisions, and template versions with conflict resolution
- **Backup & Recovery** - Automated project backups and data protection

### 🤝 Advanced Collaboration
- **Real-time Notifications** - System tray notifications for collaborative features
- **Version Conflict Handling** - Automatic detection and resolution of editing conflicts
- **Bug Reporting System** - Comprehensive error reporting with automatic log collection
- **User Activity Tracking** - Monitor active collaborators and concurrent edits

### 🎨 Professional Writing Tools
- **Template Collections** - Pre-built frameworks for character development, plot structures, world-building
- **Export Validation** - Multi-format export with integrity checking (DOCX, EPUB, HTML, PDF)
- **Text Analytics** - Readability analysis, word count tracking, writing statistics
- **Database Optimization** - SQLAlchemy connection pooling for reliable data management

### 🔌 Extensible Plugin Architecture
- **Enhanced Plugin System** - Thread-safe plugin execution with validation
- **Content Generators** - Specialized content creation tools
- **Export Formats** - Multiple output formats with validation
- **Integration Support** - Third-party service integrations

### 🎯 Modern User Interface
- **Intuitive Design** - Clean, responsive interface with PyQt5
- **Performance Monitoring** - Real-time performance tracking and optimization
- **System Tray Integration** - Background notifications and status monitoring
- **Analytics Dashboard** - Writing progress, productivity insights, and goal tracking
- **🆕 Automated Novel GUI** - Specialized interface for automated novel generation

## 🚀 Installation

### Prerequisites
- **Python 3.8 or higher** - Download from [python.org](https://www.python.org/downloads/)
- **Operating System** - Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Memory** - Minimum 4GB RAM, 8GB recommended
- **Storage** - 1GB free space for installation and project files

### Quick Start Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ShatterPro0f/FANWS.git
   cd FANWS
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run FANWS**
   ```bash
   python fanws.py
   ```

4. **Run Automated Novel Writer** (New!)
   ```bash
   python fanws.py --automated-novel
   ```

### Advanced Installation

For development or testing purposes:

```bash
# Install development dependencies
pip install -r requirements-test.txt

# Run tests
python -m pytest tests/

# Run with collaboration features
python fanws.py --enable-collaboration
```

## 📖 Usage

### Automated Novel Writing (New!)

Generate complete novels with minimal input:

1. **Launch Automated Mode** - Run `python fanws.py --automated-novel`
2. **Enter Your Idea** - Describe your novel concept
3. **Set Tone & Target** - Specify tone and target word count
4. **Review & Approve** - Review and approve synopsis, outline, characters, world-building
5. **Monitor Progress** - Watch real-time generation with automatic section creation
6. **Export** - Export finished novel in DOCX, PDF, or TXT format

See the [Automated Novel Writing Guide](docs/AUTOMATED_NOVEL_GUIDE.md) for detailed instructions.

### Creating Your First Project

1. **Launch FANWS** - Run `python fanws.py`
2. **Create New Project** - Click "New Project" and select your genre
3. **Choose Template** - Select from pre-built templates or create custom
4. **Start Writing** - Use AI assistance and workflow guidance
5. **Export** - Generate professional documents in multiple formats

### Key Workflows

#### AI-Assisted Writing
1. Select your preferred AI provider (OpenAI, Claude, etc.)
2. Choose content type (character, plot, world-building)
3. Provide context and prompts
4. Review and integrate AI suggestions
5. Continue iterative development

#### Collaborative Writing
1. Initialize collaboration features
2. Share project with team members
3. Monitor real-time notifications
4. Resolve version conflicts automatically
5. Track team member activity

#### Project Export
1. Select export formats (DOCX, EPUB, PDF, HTML)
2. Configure export settings
3. Run validation checks
4. Generate professional documents
5. Review export reports

## 🔧 Configuration

### API Keys
Configure AI providers in `config/app_config.json`:

```json
{
  "ai_providers": {
    "openai": {
      "api_key": "your-openai-key",
      "model": "gpt-4"
    },
    "claude": {
      "api_key": "your-claude-key",
      "model": "claude-3"
    }
  },
  "collaboration": {
    "notifications_enabled": true,
    "conflict_detection": true,
    "auto_backup": true
  }
}
```

### Database Configuration
```json
{
  "database": {
    "use_sqlalchemy": true,
    "pool_size": 10,
    "connection_timeout": 30
  }
}
```

## 🧪 Testing

FANWS includes comprehensive testing infrastructure:

### Run All Tests
```bash
python run_tests.py
```

### Specific Test Categories
```bash
# Unit tests
python run_tests.py --type unit

# Integration tests
python run_tests.py --type integration

# UI tests
python run_tests.py --type ui

# Plugin tests
python run_tests.py --type plugin
```

### Coverage Reports
```bash
python run_tests.py --coverage --report
```

## 📁 Project Structure

```
FANWS/
├── fanws.py              # Main application entry point
├── requirements.txt      # Core dependencies
├── requirements-test.txt # Test dependencies
├── src/                  # Source code
│   ├── core/            # Core system modules
│   ├── ai/              # AI integration
│   ├── ui/              # User interface
│   ├── workflow/        # Workflow management
│   ├── collaboration/   # Collaboration features
│   ├── database/        # Database management
│   └── plugins/         # Plugin system
├── tests/               # Test suite
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── ui/             # UI tests
├── docs/               # Documentation
├── config/             # Configuration files
├── templates/          # Writing templates
├── projects/           # User projects
└── scripts/            # Utility scripts
```

## 🔌 Plugin Development

### Creating a Plugin

1. **Plugin Structure**
   ```python
   class MyPlugin:
       def get_info(self):
           return {
               "name": "My Plugin",
               "version": "1.0.0",
               "description": "Custom functionality"
           }

       def execute(self, context):
           # Plugin logic here
           return {"success": True, "data": "result"}
   ```

2. **Plugin Registration**
   Place your plugin file in the `plugins/` directory and it will be automatically discovered.

3. **Plugin Validation**
   FANWS automatically validates plugins for required methods, dependencies, and security.

## 🤝 Contributing

We welcome contributions! Please see our [Development Guide](docs/DEVELOPMENT.md) for details on:

- Code style and standards
- Testing requirements
- Pull request process
- Issue reporting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Documentation
- [Development Guide](docs/DEVELOPMENT.md) - Developer documentation
- [API Reference](docs/API.md) - Complete API documentation
- [Changelog](docs/CHANGELOG.md) - Version history and updates

### Getting Help
- **Issues** - Report bugs or request features on [GitHub Issues](https://github.com/ShatterPro0f/FANWS/issues)
- **Bug Reports** - Use the built-in bug reporting system (`Help > Report Bug`)
- **Discussions** - Join community discussions on [GitHub Discussions](https://github.com/ShatterPro0f/FANWS/discussions)

### System Requirements

#### Minimum Requirements
- Python 3.8+
- 4GB RAM
- 1GB storage space
- Internet connection for AI features

#### Recommended Requirements
- Python 3.10+
- 8GB RAM
- 2GB storage space
- High-speed internet connection

#### Supported Platforms
- Windows 10/11
- macOS 10.14+
- Linux (Ubuntu 18.04+, CentOS 7+)

## 🎯 Roadmap

### Version 2.0 (Upcoming)
- [ ] Real-time collaborative editing
- [ ] Advanced AI model integration
- [ ] Cloud synchronization
- [ ] Mobile companion app
- [ ] Advanced analytics dashboard

### Version 1.5 (In Development)
- [x] Enhanced collaboration features
- [x] SQLAlchemy database optimization
- [x] Advanced plugin system
- [x] Comprehensive testing infrastructure
- [x] Version conflict resolution

---

**FANWS** - Empowering fiction authors with intelligent writing tools and collaborative features.

Made with ❤️ by the FANWS development team.

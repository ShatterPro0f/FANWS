# FANWS - AAWT Integration

This document describes how FANWS now works like AAWT (AI-Assisted Writing Tool).

## Overview

FANWS has been enhanced with AAWT-style components to provide a simpler, more focused writing application experience.

## New Entry Point

Use `aawt.py` as the simplified entry point:

```bash
python aawt.py
```

This provides the AAWT-style interface with all the features described in the AAWT README.

## Components

The following AAWT components have been integrated:

### Settings Manager
- **File**: `src/system/settings_manager.py`
- **Purpose**: Manages application settings with dot-notation access
- **Config File**: `config/user_settings.json`

### Database Manager
- **File**: `src/database/database_manager.py`
- **Purpose**: SQLite database with connection pooling
- **Features**: Connection pooling, query caching, transaction management

### Text Analyzer
- **File**: `src/text/text_processing.py`
- **Purpose**: Analyzes text for readability, grammar, and style
- **Features**: Word count, readability scores, repeated word detection

### Export Manager
- **File**: `src/system/export_manager.py`
- **Purpose**: Multi-format export (TXT, DOCX, PDF, EPUB, JSON)
- **Features**: Format validation, metadata inclusion, compression

### API Manager
- **File**: `src/system/api_manager.py`
- **Purpose**: AI API integration with caching
- **Features**: Multi-provider support, rate limiting, cost tracking

### File Operations
- **File**: `src/system/file_operations.py`
- **Purpose**: File I/O and project management
- **Features**: Memory-safe reading, project organization

## Directory Structure

```
FANWS/
├── aawt.py                  # AAWT-style entry point
├── fanws.py                 # Original FANWS entry point
├── config/
│   ├── user_settings.json   # User configuration
│   └── fanws.db             # SQLite database
├── projects/                # Project storage
├── exports/                 # Export output
├── logs/                    # Application logs
└── src/
    ├── system/              # Core system modules
    ├── database/            # Database components
    ├── text/                # Text processing
    └── ui/                  # User interface
```

## Configuration

Edit `config/user_settings.json` to customize:

- **UI Settings**: Theme, window size, fonts
- **Writing Settings**: Default tone, POV, genre
- **API Keys**: OpenAI, Anthropic, Google
- **Export Settings**: Format, directory, metadata
- **Performance**: Pool size, cache size

## Features

Following the AAWT README specifications, FANWS now provides:

1. **Project Management**: Create, load, and manage writing projects
2. **Text Analysis**: Real-time readability, grammar, and style checking
3. **AI Assistance**: Multi-provider AI integration (OpenAI, Anthropic, etc.)
4. **Export**: Multiple format support with validation
5. **Settings**: Persistent configuration with dot-notation access
6. **Database**: Connection pooling and query caching
7. **Performance Monitoring**: CPU, memory, and cache statistics

## Usage

### Command Line

```bash
# Launch AAWT-style interface
python aawt.py

# Original FANWS interface (if GUI environment available)
python fanws.py
```

### Programmatic

```python
from src.system.settings_manager import SettingsManager
from src.database.database_manager import DatabaseManager
from src.text.text_processing import TextAnalyzer
from src.system.export_manager import ExportManager
from src.system.api_manager import get_api_manager

# Initialize components
settings = SettingsManager('config/user_settings.json')
database = DatabaseManager('config/fanws.db', pool_size=5)
analyzer = TextAnalyzer()
exporter = ExportManager(settings)
api = get_api_manager()

# Use components
text = "Your writing content here..."
analysis = analyzer.analyze_text(text)
print(f"Word count: {analysis['word_count']}")
```

## Testing

Test component initialization:

```bash
python -c "
from src.system.settings_manager import SettingsManager
from src.database.database_manager import DatabaseManager
from src.text.text_processing import TextAnalyzer
from src.system.export_manager import ExportManager
from src.system.file_operations import FileOperations
from src.system.api_manager import get_api_manager

print('Testing AAWT components...')
settings = SettingsManager('config/user_settings.json')
database = DatabaseManager('config/fanws.db', 5)
analyzer = TextAnalyzer()
exporter = ExportManager(settings)
files = FileOperations()
api = get_api_manager()
print('✅ All components initialized successfully!')
"
```

## Differences from Original FANWS

- **Simpler Entry Point**: `aawt.py` provides cleaner initialization
- **AAWT Components**: Additional modules from AAWT for enhanced functionality
- **Settings Management**: Dot-notation config access
- **Database Integration**: Connection pooling and caching
- **Export Enhancement**: Multi-format support with validation

## Requirements

All dependencies are in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Key dependencies:
- PyQt5>=5.15.0 (GUI framework)
- python-docx>=0.8.11 (DOCX export)
- reportlab>=4.0.0 (PDF export)
- SQLAlchemy>=2.0.0 (Database)
- requests>=2.28.0 (API calls)

## Troubleshooting

### GUI Issues

If GUI doesn't work (headless environment):
```bash
export QT_QPA_PLATFORM=offscreen
python aawt.py
```

### Database Errors

Reset database:
```bash
rm config/fanws.db
python aawt.py  # Will recreate database
```

### Import Errors

Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Documentation

See the AAWT README (in this repository at the referenced Git URL) for comprehensive feature documentation including:

- Complete feature list
- Keyboard shortcuts
- Workflow guide
- API integration
- Export formats
- Performance optimization
- Troubleshooting

## Support

- **Logs**: Check `logs/fanws.log` for detailed information
- **Config**: Modify `config/user_settings.json` for customization
- **Issues**: File issues on GitHub repository

---

**FANWS** now provides AAWT-style functionality with all the features described in the comprehensive AAWT README documentation.

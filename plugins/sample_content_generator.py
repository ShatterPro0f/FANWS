"""
Sample Content Generator Plugin
Demonstrates how to create a custom content generator plugin for FANWS.
"""

import sys
import os
from typing import Dict, Any, List

# Add src to path for plugin imports
plugin_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(plugin_dir, '..', 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from src.plugins.plugin_system import ContentGeneratorPlugin, PluginInfo, PluginType
except ImportError:
    # Fallback for when the module structure is different
    try:
        from plugin_system import ContentGeneratorPlugin, PluginInfo, PluginType
    except ImportError:
        # Create stub classes if plugin system is not available
        class ContentGeneratorPlugin:
            def __init__(self, *args, **kwargs):
                pass
        class PluginInfo:
            def __init__(self, *args, **kwargs):
                pass
        class PluginType:
            pass

class SampleContentGeneratorPlugin(ContentGeneratorPlugin):
    """Sample content generator plugin for demonstration."""

    def __init__(self):
        super().__init__()
        self.supported_types = ['readme', 'documentation', 'summary']

    def get_info(self) -> PluginInfo:
        """Get plugin information."""
        return PluginInfo(
            name="Sample Content Generator",
            version="1.0.0",
            description="A sample content generator plugin for creating README files and documentation",
            author="FANWS Team",
            plugin_type=PluginType.CONTENT_GENERATOR,
            api_version="1.0.0",
            dependencies=[]
        )

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the plugin with configuration."""
        return True

    def cleanup(self) -> bool:
        """Clean up plugin resources."""
        return True

    def get_supported_types(self) -> List[str]:
        """Get supported content types."""
        return self.supported_types

    def generate_content(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate content based on prompt and context."""
        content_type = context.get('content_type', 'readme')

        if content_type == 'readme':
            return self._generate_readme(prompt, context)
        elif content_type == 'documentation':
            return self._generate_documentation(prompt, context)
        elif content_type == 'summary':
            return self._generate_summary(prompt, context)
        else:
            return self._generate_default_content(prompt, context)

    def _generate_readme(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate a README file."""
        title = context.get('title', 'Project')
        description = context.get('description', 'A sample project')
        author = context.get('author', 'Author')

        readme_content = f"""# {title}

## Description
{description}

## Features
- Feature 1
- Feature 2
- Feature 3

## Installation
```bash
# Clone the repository
git clone <repository-url>

# Install dependencies
pip install -r requirements.txt
```

## Usage
```python
# Basic usage example
from {title.lower().replace(' ', '_')} import main

main()
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License
This project is licensed under the MIT License.

## Author
{author}

## Contact
For questions or support, please contact [author email].
"""
        return readme_content

    def _generate_documentation(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate documentation content."""
        title = context.get('title', 'Documentation')
        sections = context.get('sections', ['Overview', 'Getting Started', 'API Reference'])

        doc_content = f"""# {title}

## Table of Contents
"""

        # Generate table of contents
        for section in sections:
            doc_content += f"- [{section}](#{section.lower().replace(' ', '-')})\n"

        doc_content += "\n"

        # Generate sections
        for section in sections:
            doc_content += f"## {section}\n\n"

            if section == 'Overview':
                doc_content += "This section provides an overview of the project.\n\n"
            elif section == 'Getting Started':
                doc_content += """### Prerequisites
- Python 3.7+
- Required dependencies

### Installation
1. Install the package
2. Configure settings
3. Start using the application

### Quick Start
Follow these steps to get started quickly.
"""
            elif section == 'API Reference':
                doc_content += """### Classes
- `MainClass`: Primary class for functionality
- `HelperClass`: Utility functions

### Methods
- `method1()`: Description of method 1
- `method2()`: Description of method 2

### Examples
```python
# Example usage
example_code()
```
"""
            else:
                doc_content += f"Content for {section} section.\n\n"

        return doc_content

    def _generate_summary(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate a summary."""
        title = context.get('title', 'Summary')
        data = context.get('data', {})

        summary = f"# {title}\n\n"

        if 'description' in data:
            summary += f"**Description:** {data['description']}\n\n"

        if 'features' in data:
            summary += "**Key Features:**\n"
            for feature in data['features']:
                summary += f"- {feature}\n"
            summary += "\n"

        if 'stats' in data:
            summary += "**Statistics:**\n"
            for key, value in data['stats'].items():
                summary += f"- {key}: {value}\n"
            summary += "\n"

        summary += "**Generated by:** FANWS Sample Content Generator Plugin\n"

        return summary

    def _generate_default_content(self, prompt: str, context: Dict[str, Any]) -> str:
        """Generate default content."""
        return f"""# Generated Content

## Prompt
{prompt}

## Context
{context}

## Generated Content
This is sample content generated by the FANWS Sample Content Generator Plugin.
The plugin can be customized to generate different types of content based on
the provided prompt and context.

## Usage
To use this plugin, provide a prompt and context dictionary with the following keys:
- content_type: The type of content to generate
- title: The title for the content
- description: A description of the content
- author: The author information
- Any additional context-specific data

## Supported Content Types
- readme: Generate README files
- documentation: Generate documentation
- summary: Generate summaries
- default: Generate basic content

Generated at: {context.get('timestamp', 'Unknown')}
"""

    def get_capabilities(self) -> List[str]:
        """Get list of capabilities."""
        return [
            'readme_generation',
            'documentation_generation',
            'summary_generation',
            'markdown_formatting',
            'template_based_content'
        ]

    def validate_context(self, context: Dict[str, Any]) -> bool:
        """Validate the provided context."""
        required_keys = ['content_type']

        for key in required_keys:
            if key not in context:
                return False

        content_type = context['content_type']
        if content_type not in self.supported_types:
            return False

        return True

    def get_template_variables(self, content_type: str) -> List[str]:
        """Get template variables for a content type."""
        if content_type == 'readme':
            return ['title', 'description', 'author', 'features', 'installation_steps']
        elif content_type == 'documentation':
            return ['title', 'sections', 'author', 'version']
        elif content_type == 'summary':
            return ['title', 'data', 'timestamp']
        else:
            return ['title', 'description', 'author']

    def get_output_format(self) -> str:
        """Get the output format."""
        return 'markdown'

    def supports_streaming(self) -> bool:
        """Check if plugin supports streaming generation."""
        return False

    def get_generation_options(self) -> Dict[str, Any]:
        """Get available generation options."""
        return {
            'max_length': 10000,
            'format': 'markdown',
            'include_toc': True,
            'include_examples': True
        }

# Plugin registration function
def register_plugin():
    """Register this plugin with the system."""
    from src.plugin_system import get_plugin_manager

    plugin_manager = get_plugin_manager()
    plugin_instance = SampleContentGeneratorPlugin()

    return plugin_manager.registry.register_plugin(plugin_instance.get_info())

# Make plugin discoverable
PLUGIN_CLASS = SampleContentGeneratorPlugin
PLUGIN_INFO = SampleContentGeneratorPlugin().get_info()

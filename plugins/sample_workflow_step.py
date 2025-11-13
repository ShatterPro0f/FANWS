"""
Sample Workflow Step Plugin
Demonstrates how to create a custom workflow step plugin for FANWS.
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
    from src.plugins.plugin_system import WorkflowStepPlugin, PluginInfo, PluginType
except ImportError:
    # Fallback for when the module structure is different
    try:
        from plugin_system import WorkflowStepPlugin, PluginInfo, PluginType
    except ImportError:
        # Create stub classes if plugin system is not available
        class WorkflowStepPlugin:
            def __init__(self, *args, **kwargs):
                pass
        class PluginInfo:
            def __init__(self, *args, **kwargs):
                pass
        class PluginType:
            pass

class SampleWorkflowStepPlugin(WorkflowStepPlugin):
    """Sample workflow step plugin for demonstration."""

    def __init__(self):
        super().__init__()
        self.workflow = None
        self.step_number = 10  # Custom step number

    def get_info(self) -> PluginInfo:
        """Get plugin information."""
        return PluginInfo(
            name="Sample Workflow Step",
            version="1.0.0",
            description="A sample workflow step plugin for demonstration",
            author="FANWS Team",
            plugin_type=PluginType.WORKFLOW_STEP,
            api_version="1.0.0",
            dependencies=[]
        )

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the plugin with configuration."""
        return True

    def cleanup(self) -> bool:
        """Clean up plugin resources."""
        return True

    def get_step_number(self) -> int:
        """Get the step number this plugin handles."""
        return self.step_number

    def get_step_name(self) -> str:
        """Get the name of this step."""
        return "Sample Processing Step"

    def get_step_description(self) -> str:
        """Get description of what this step does."""
        return "Performs sample processing operations on workflow data"

    def get_dependencies(self) -> List[int]:
        """Get list of step numbers this step depends on."""
        return [1, 2]  # Depends on steps 1 and 2

    def validate_prerequisites(self) -> bool:
        """Validate that prerequisites are met."""
        if not self.workflow:
            return False

        # Check if required data is available
        workflow_data = self.workflow.get_data()
        required_keys = ['project_description', 'title']

        for key in required_keys:
            if key not in workflow_data:
                return False

        return True

    def execute(self) -> Dict[str, Any]:
        """Execute the workflow step."""
        try:
            # Get workflow data
            workflow_data = self.workflow.get_data()

            # Perform sample processing
            title = workflow_data.get('title', 'Untitled')
            description = workflow_data.get('project_description', '')

            # Sample processing: create a summary
            summary = self._create_summary(title, description)

            # Sample processing: generate tags
            tags = self._generate_tags(description)

            # Update workflow data
            workflow_data['sample_summary'] = summary
            workflow_data['sample_tags'] = tags
            workflow_data['sample_processed'] = True

            # Store updated data
            self.workflow.set_data(workflow_data)

            return {
                'success': True,
                'message': 'Sample processing completed successfully',
                'data': {
                    'summary': summary,
                    'tags': tags,
                    'processed_items': len(tags)
                }
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Sample processing failed'
            }

    def _create_summary(self, title: str, description: str) -> str:
        """Create a summary of the project."""
        if not description:
            return f"Project: {title}"

        # Simple summarization (first 100 characters)
        if len(description) <= 100:
            return f"{title}: {description}"

        return f"{title}: {description[:97]}..."

    def _generate_tags(self, description: str) -> List[str]:
        """Generate tags from description."""
        if not description:
            return []

        # Simple tag generation based on keywords
        keywords = ['web', 'app', 'mobile', 'desktop', 'api', 'database',
                   'frontend', 'backend', 'python', 'javascript', 'react',
                   'vue', 'angular', 'django', 'flask', 'node', 'express']

        tags = []
        description_lower = description.lower()

        for keyword in keywords:
            if keyword in description_lower:
                tags.append(keyword)

        return tags[:5]  # Limit to 5 tags

    def get_capabilities(self) -> List[str]:
        """Get list of capabilities this plugin provides."""
        return [
            'summary_generation',
            'tag_generation',
            'data_processing',
            'workflow_integration'
        ]

    def get_output_format(self) -> Dict[str, Any]:
        """Get the format of output data."""
        return {
            'sample_summary': 'string',
            'sample_tags': 'list[string]',
            'sample_processed': 'boolean'
        }

    def set_workflow(self, workflow):
        """Set the workflow instance."""
        self.workflow = workflow

    def get_workflow(self):
        """Get the workflow instance."""
        return self.workflow

    def can_skip(self) -> bool:
        """Check if this step can be skipped."""
        return True  # This is an optional step

    def estimate_duration(self) -> int:
        """Estimate execution duration in seconds."""
        return 5  # Should take about 5 seconds

    def get_progress_info(self) -> Dict[str, Any]:
        """Get progress information during execution."""
        return {
            'current_phase': 'processing',
            'completion_percentage': 0,
            'estimated_time_remaining': self.estimate_duration()
        }

# Plugin registration function
def register_plugin():
    """Register this plugin with the system."""
    from src.plugin_system import get_plugin_manager

    plugin_manager = get_plugin_manager()
    plugin_instance = SampleWorkflowStepPlugin()

    return plugin_manager.registry.register_plugin(plugin_instance.get_info())

# Make plugin discoverable
PLUGIN_CLASS = SampleWorkflowStepPlugin
PLUGIN_INFO = SampleWorkflowStepPlugin().get_info()

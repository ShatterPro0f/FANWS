"""
pytest tests for enhanced plugin system with validation and threading
"""

import pytest
import tempfile
import shutil
import threading
import time
import json
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import types
import concurrent.futures

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.plugins.plugin_system import (
    PluginInterface, PluginRegistry, PluginInfo, PluginType, PluginStatus,
    PluginValidationResult, WorkflowStepPlugin, ContentGeneratorPlugin,
    ExportFormatPlugin, TextProcessorPlugin
)


class MockPlugin(PluginInterface):
    """Mock plugin for testing"""

    def __init__(self, should_fail_init=False, should_timeout=False):
        self.should_fail_init = should_fail_init
        self.should_timeout = should_timeout
        self.initialized = False
        self.cleaned_up = False
        # Bind test_method to the instance so tests can delattr() on the instance
        func = getattr(self.__class__, 'test_method', None)
        if func is not None:
            self.test_method = types.MethodType(func, self)

    def get_info(self) -> PluginInfo:
        return PluginInfo(
            name="mock_plugin",
            version="1.0.0",
            author="Test Author",
            description="Mock plugin for testing",
            plugin_type=PluginType.CONTENT_GENERATOR,
            api_version="1.0.0"
        )

    def initialize(self, config):
        if self.should_fail_init:
            raise Exception("Initialization failed")
        self.initialized = True
        return True

    def cleanup(self):
        self.cleaned_up = True
        return True

    def get_required_methods(self):
        return ['get_info', 'initialize', 'cleanup', 'test_method']

    def get_required_dependencies(self):
        return ['os', 'sys']  # Common dependencies that should exist

    def test_method(self):
        if self.should_timeout:
            time.sleep(40)  # Timeout after 30 seconds
        return "test_result"

    # Type-specific methods for ContentGenerator plugins used in tests
    def generate_content(self, prompt: str, context: dict) -> str:
        return f"generated for: {prompt}"

    def get_supported_types(self) -> list:
        return ["text"]


class BadMockPlugin:
    """Plugin that doesn't implement PluginInterface"""

    def __init__(self):
        pass

    def some_method(self):
        return "bad_plugin"


class TestPluginValidationResult:
    """Test PluginValidationResult dataclass"""

    def test_validation_result_creation(self):
        """Test creating validation result"""
        result = PluginValidationResult(is_valid=True)

        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []
        assert result.missing_methods == []
        assert result.missing_dependencies == []
        assert result.security_issues == []

    def test_validation_result_with_errors(self):
        """Test validation result with errors"""
        result = PluginValidationResult(
            is_valid=False,
            errors=["Missing method", "Invalid config"],
            warnings=["Deprecated feature"],
            missing_methods=["required_method"],
            missing_dependencies=["missing_package"],
            security_issues=["Unsafe operation"]
        )

        assert result.is_valid is False
        assert len(result.errors) == 2
        assert len(result.warnings) == 1
        assert len(result.missing_methods) == 1
        assert len(result.missing_dependencies) == 1
        assert len(result.security_issues) == 1


class TestPluginInterface:
    """Test enhanced PluginInterface"""

    def test_plugin_interface_required_methods(self):
        """Test getting required methods"""
        plugin = MockPlugin()
        required = plugin.get_required_methods()

        assert 'get_info' in required
        assert 'initialize' in required
        assert 'cleanup' in required

    def test_plugin_interface_dependency_check(self):
        """Test dependency checking"""
        plugin = MockPlugin()

        # Test existing dependencies
        assert plugin._check_dependency('os') is True
        assert plugin._check_dependency('sys') is True

        # Test non-existing dependency
        assert plugin._check_dependency('non_existent_module_12345') is False

    def test_plugin_environment_validation(self):
        """Test plugin environment validation"""
        plugin = MockPlugin()
        result = plugin.validate_environment()

        assert isinstance(result, PluginValidationResult)
        # Should be valid since MockPlugin has all required methods and dependencies
        assert result.is_valid is True

    def test_plugin_validation_missing_methods(self):
        """Test validation with missing methods"""
        plugin = MockPlugin()

        # Remove a required method from both the class and instance temporarily
        orig_class = getattr(MockPlugin, 'test_method', None)
        orig_inst = getattr(plugin, 'test_method', None)
        try:
            if hasattr(MockPlugin, 'test_method'):
                delattr(MockPlugin, 'test_method')
            if hasattr(plugin, 'test_method'):
                try:
                    delattr(plugin, 'test_method')
                except Exception:
                    # Some Python objects disallow deleting bound attributes
                    pass

            result = plugin.validate_environment()
            assert result.is_valid is False
            assert 'test_method' in result.missing_methods
        finally:
            if orig_class is not None:
                setattr(MockPlugin, 'test_method', orig_class)
            if orig_inst is not None:
                try:
                    setattr(plugin, 'test_method', orig_inst)
                except Exception:
                    pass

    def test_plugin_run_in_thread(self):
        """Test running plugin method in thread"""
        plugin = MockPlugin()

        def test_function(x, y):
            return x + y

        future = plugin.run_in_thread(test_function, 5, 3)
        result = future.result(timeout=5)

        assert result == 8


class TestPluginRegistry:
    """Test enhanced PluginRegistry"""

    @pytest.fixture
    def registry(self):
        """Create plugin registry for testing"""
        return PluginRegistry()

    @pytest.fixture
    def valid_plugin_info(self):
        """Create valid plugin info for testing"""
        return PluginInfo(
            name="test_plugin",
            version="1.0.0",
            author="Test Author",
            description="Test plugin description",
            plugin_type=PluginType.CONTENT_GENERATOR,
            api_version="1.0.0",
            dependencies=["os", "sys"],
            file_path="/fake/path/plugin.py"
        )

    def test_registry_initialization(self, registry):
        """Test registry initialization"""
        assert isinstance(registry.plugins, dict)
        assert isinstance(registry.loaded_plugins, dict)
        assert isinstance(registry.plugin_types, dict)
        assert isinstance(registry.listeners, dict)
        # Check that _lock is an RLock instance using type comparison
        assert type(registry._lock).__name__ == 'RLock'

    def test_register_valid_plugin(self, registry, valid_plugin_info):
        """Test registering a valid plugin"""
        with patch.object(registry, '_validate_plugin_info', return_value=True):
            result = registry.register_plugin(valid_plugin_info)

            assert result is True
            assert valid_plugin_info.name in registry.plugins
            assert valid_plugin_info.name in registry.plugin_types[PluginType.CONTENT_GENERATOR]

    def test_register_invalid_plugin(self, registry):
        """Test registering an invalid plugin"""
        invalid_info = PluginInfo(
            name="",  # Invalid empty name
            version="1.0.0",
            author="Test Author",
            description="Test plugin",
            plugin_type=PluginType.CONTENT_GENERATOR,
            api_version="1.0.0"
        )

        result = registry.register_plugin(invalid_info)
        assert result is False

    def test_unregister_plugin(self, registry, valid_plugin_info):
        """Test unregistering a plugin"""
        with patch.object(registry, '_validate_plugin_info', return_value=True):
            registry.register_plugin(valid_plugin_info)

            result = registry.unregister_plugin(valid_plugin_info.name)
            assert result is True
            assert valid_plugin_info.name not in registry.plugins

    def test_validate_plugin_instance(self, registry, valid_plugin_info):
        """Test validating plugin instance"""
        good_plugin = MockPlugin()
        bad_plugin = BadMockPlugin()

        # Test valid plugin
        assert registry.validate_plugin_instance(good_plugin, valid_plugin_info) is True

        # Test invalid plugin
        assert registry.validate_plugin_instance(bad_plugin, valid_plugin_info) is False

    def test_execute_plugin_safely(self, registry):
        """Test safe plugin execution"""
        plugin = MockPlugin()
        registry.loaded_plugins['test_plugin'] = plugin

        # Test successful execution
        result = registry.execute_plugin_safely('test_plugin', 'test_method')
        assert result == "test_result"

    def test_execute_plugin_safely_timeout(self, registry):
        """Test safe plugin execution with timeout"""
        plugin = MockPlugin(should_timeout=True)
        registry.loaded_plugins['test_plugin'] = plugin

        # Test timeout
        with pytest.raises(TimeoutError):
            registry.execute_plugin_safely('test_plugin', 'test_method')

    def test_execute_plugin_safely_nonexistent(self, registry):
        """Test safe execution of non-existent plugin"""
        with pytest.raises(ValueError):
            registry.execute_plugin_safely('nonexistent_plugin', 'some_method')

    def test_dependency_validation(self, registry):
        """Test dependency validation"""
        plugin_info = PluginInfo(
            name="dep_test",
            version="1.0.0",
            author="Test",
            description="Test",
            plugin_type=PluginType.CONTENT_GENERATOR,
            api_version="1.0.0",
            dependencies=["os", "sys", "non_existent_module_12345"]
        )

        result = registry._validate_plugin_dependencies(plugin_info)
        assert result is False  # Should fail due to missing dependency

    def test_dependency_format_validation(self, registry):
        """Test different dependency formats"""
        # Test pip dependency (mock)
        with patch('pkg_resources.get_distribution'):
            assert registry._check_dependency_available('pip:requests') is True

        # Test python version dependency
        assert registry._check_dependency_available('python:3.6') is True

        # Test module dependency
        assert registry._check_dependency_available('os') is True

    def test_version_comparison(self, registry):
        """Test version comparison"""
        assert registry._compare_versions('3.8', '3.6') is True
        assert registry._compare_versions('3.6', '3.8') is False
        assert registry._compare_versions('3.8.5', '3.8.0') is True

    def test_file_checksum_calculation(self, registry, temp_dir):
        """Test file checksum calculation"""
        test_file = os.path.join(temp_dir, "test.py")
        with open(test_file, 'w') as f:
            f.write("# Test plugin content")

        checksum = registry._calculate_file_checksum(test_file)
        assert isinstance(checksum, str)
        assert len(checksum) == 64  # SHA256 hex length

    def test_thread_safety(self, registry, valid_plugin_info):
        """Test thread safety of registry operations"""
        results = []
        errors = []

        def register_plugin_thread():
            try:
                with patch.object(registry, '_validate_plugin_info', return_value=True):
                    result = registry.register_plugin(valid_plugin_info)
                    results.append(result)
            except Exception as e:
                errors.append(e)

        def list_plugins_thread():
            try:
                plugins = registry.list_plugins()
                results.append(len(plugins))
            except Exception as e:
                errors.append(e)

        # Create multiple threads
        threads = []
        for i in range(5):
            if i % 2 == 0:
                thread = threading.Thread(target=register_plugin_thread)
            else:
                thread = threading.Thread(target=list_plugins_thread)
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join(timeout=5)

        # Check no errors occurred
        assert len(errors) == 0

    def test_event_listeners(self, registry, valid_plugin_info):
        """Test event listener system"""
        events_received = []

        def event_handler(plugin_name):
            events_received.append(plugin_name)

        registry.add_listener('plugin_registered', event_handler)

        with patch.object(registry, '_validate_plugin_info', return_value=True):
            registry.register_plugin(valid_plugin_info)

        assert len(events_received) == 1
        assert events_received[0] == valid_plugin_info.name

    def test_plugin_info_validation_comprehensive(self, registry):
        """Test comprehensive plugin info validation"""
        # Test invalid version format
        invalid_info = PluginInfo(
            name="test",
            version="invalid_version",
            author="Test",
            description="Test",
            plugin_type=PluginType.CONTENT_GENERATOR,
            api_version="1.0.0"
        )
        assert registry._validate_plugin_info(invalid_info) is False

        # Test API version mismatch
        invalid_info.version = "1.0.0"
        invalid_info.api_version = "2.0.0"
        assert registry._validate_plugin_info(invalid_info) is False

    @patch('src.plugins.plugin_system.importlib.util.spec_from_file_location')
    def test_load_plugin_instance_file_not_found(self, mock_spec, registry):
        """Test loading plugin when file doesn't exist"""
        plugin_info = PluginInfo(
            name="missing_plugin",
            version="1.0.0",
            author="Test",
            description="Test",
            plugin_type=PluginType.CONTENT_GENERATOR,
            api_version="1.0.0",
            file_path="/non/existent/path.py"
        )

        result = registry._load_plugin_instance(plugin_info)
        assert result is None

    def test_find_plugin_class(self, registry):
        """Test finding plugin class in module"""
        # Create mock module
        mock_module = Mock()
        mock_module.__name__ = "test_module"

        # Create mock plugin class
        class TestPluginClass(PluginInterface):
            def get_info(self):
                return PluginInfo(
                    name="test", version="1.0", author="test",
                    description="test", plugin_type=PluginType.CONTENT_GENERATOR,
                    api_version="1.0.0"
                )
            def initialize(self, config):
                return True
            def cleanup(self):
                return True

        TestPluginClass.__module__ = "test_module"

        # Mock inspect.getmembers
        with patch('inspect.getmembers', return_value=[('TestPluginClass', TestPluginClass)]):
            plugin_info = PluginInfo(
                name="test", version="1.0", author="test",
                description="test", plugin_type=PluginType.CONTENT_GENERATOR,
                api_version="1.0.0"
            )

            result = registry._find_plugin_class(mock_module, plugin_info)
            assert result is TestPluginClass


class TestPluginTypeSpecificValidation:
    """Test validation for specific plugin types"""

    def test_workflow_step_plugin_validation(self):
        """Test WorkflowStepPlugin specific validation"""

        class TestWorkflowPlugin(WorkflowStepPlugin):
            def get_info(self):
                return PluginInfo(
                    name="workflow_test", version="1.0", author="test",
                    description="test", plugin_type=PluginType.WORKFLOW_STEP,
                    api_version="1.0.0"
                )

            def initialize(self, config):
                return True

            def cleanup(self):
                return True

            def execute(self):
                return {"status": "completed"}

            def validate_prerequisites(self):
                return True

            def get_step_name(self):
                return "test_step"

        registry = PluginRegistry()
        plugin = TestWorkflowPlugin()
        plugin_info = plugin.get_info()

        assert registry.validate_plugin_instance(plugin, plugin_info) is True

    def test_content_generator_plugin_validation(self):
        """Test ContentGeneratorPlugin specific validation"""

        class TestContentPlugin(ContentGeneratorPlugin):
            def get_info(self):
                return PluginInfo(
                    name="content_test", version="1.0", author="test",
                    description="test", plugin_type=PluginType.CONTENT_GENERATOR,
                    api_version="1.0.0"
                )

            def initialize(self, config):
                return True

            def cleanup(self):
                return True

            def generate_content(self, prompt, context):
                return "Generated content"

            def get_supported_types(self):
                return ["story", "character"]

        registry = PluginRegistry()
        plugin = TestContentPlugin()
        plugin_info = plugin.get_info()

        assert registry.validate_plugin_instance(plugin, plugin_info) is True


class TestPluginSecurityAndSafety:
    """Test plugin security and safety features"""

    def test_plugin_execution_isolation(self):
        """Test that plugin execution is isolated"""

        class DangerousPlugin(PluginInterface):
            def get_info(self):
                return PluginInfo(
                    name="dangerous", version="1.0", author="test",
                    description="test", plugin_type=PluginType.CONTENT_GENERATOR,
                    api_version="1.0.0"
                )

            def initialize(self, config):
                return True

            def cleanup(self):
                return True

            def dangerous_method(self):
                # Simulate dangerous operation
                raise Exception("Dangerous operation failed")

        registry = PluginRegistry()
        plugin = DangerousPlugin()
        registry.loaded_plugins['dangerous'] = plugin

        # Should catch and handle the exception
        with pytest.raises(Exception):
            registry.execute_plugin_safely('dangerous', 'dangerous_method')

        # Plugin should be marked as error
        if 'dangerous' in registry.plugins:
            assert registry.plugins['dangerous'].status == PluginStatus.ERROR

    def test_plugin_timeout_protection(self):
        """Test protection against runaway plugins"""

        class SlowPlugin(PluginInterface):
            def get_info(self):
                return PluginInfo(
                    name="slow", version="1.0", author="test",
                    description="test", plugin_type=PluginType.CONTENT_GENERATOR,
                    api_version="1.0.0"
                )

            def initialize(self, config):
                return True

            def cleanup(self):
                return True

            def slow_method(self):
                time.sleep(35)  # Exceeds 30 second timeout
                return "done"

        registry = PluginRegistry()
        plugin = SlowPlugin()
        registry.loaded_plugins['slow'] = plugin

        # Should timeout
        with pytest.raises(TimeoutError):
            registry.execute_plugin_safely('slow', 'slow_method')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

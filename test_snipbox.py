#!/usr/bin/env python3
"""
Test suite for SnipBox Plugin

Run with: python3 test_snipbox.py
"""

import unittest
import os
import json
import tempfile
import sys
from pathlib import Path

# Mock Terminator's plugin system
class MockPluginBase:
    pass

sys.modules['terminatorlib'] = type(sys)('terminatorlib')
sys.modules['terminatorlib.plugin'] = type(sys)('terminatorlib.plugin')
sys.modules['terminatorlib.plugin'].Plugin = MockPluginBase

# Import the plugin
sys.path.insert(0, os.path.dirname(__file__))
from snipbox import SnipBoxPlugin


class TestSnipBoxPlugin(unittest.TestCase):
    """Test cases for SnipBoxPlugin"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, 'snippets.json')
        self.plugin = SnipBoxPlugin()

    def tearDown(self):
        """Clean up after tests"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_plugin_initialization(self):
        """Test that plugin initializes correctly"""
        self.assertIsNotNone(self.plugin)
        self.assertEqual(self.plugin.capabilities, ['terminal_menu'])
        self.assertIsInstance(self.plugin.snippets, dict)

    def test_available_export(self):
        """Test that AVAILABLE is properly exported"""
        import snipbox
        self.assertIn('SnipBoxPlugin', snipbox.AVAILABLE)

    def test_plugin_name(self):
        """Test that PLUGIN_NAME is correct"""
        import snipbox
        self.assertEqual(snipbox.PLUGIN_NAME, 'SnipBox')

    def test_default_snippets_structure(self):
        """Test that default snippets have correct structure"""
        self.assertIsInstance(self.plugin.snippets, dict)
        # Should have at least one category
        self.assertGreater(len(self.plugin.snippets), 0)

    def test_default_snippets_content(self):
        """Test that default snippets contain expected data"""
        # Check that at least one category exists
        self.assertGreater(len(self.plugin.snippets), 0, "No snippet categories found")

        # Check first category has valid structure
        for category, snippets_dict in self.plugin.snippets.items():
            self.assertIsInstance(snippets_dict, dict)
            # Each category should have name-command pairs
            for name, command in snippets_dict.items():
                self.assertIsInstance(name, str)
                self.assertIsInstance(command, str)
                self.assertGreater(len(name), 0, f"Empty name in {category}")
                self.assertGreater(len(command), 0, f"Empty command for {name}")
            break  # Only check first category

    def test_snippet_structure_validation(self):
        """Test that all snippets follow correct structure"""
        for category, snippets_dict in self.plugin.snippets.items():
            self.assertIsInstance(category, str)
            self.assertIsInstance(snippets_dict, dict)
            for name, command in snippets_dict.items():
                self.assertIsInstance(name, str)
                self.assertIsInstance(command, str)

    def test_callback_method_exists(self):
        """Test that callback method exists"""
        self.assertTrue(hasattr(self.plugin, 'callback'))
        self.assertTrue(callable(self.plugin.callback))

    def test_execute_snippet_method_exists(self):
        """Test that execute_snippet method exists"""
        self.assertTrue(hasattr(self.plugin, 'execute_snippet'))
        self.assertTrue(callable(self.plugin.execute_snippet))

    def test_show_manager_method_exists(self):
        """Test that show_manager method exists"""
        self.assertTrue(hasattr(self.plugin, 'show_manager'))
        self.assertTrue(callable(self.plugin.show_manager))

    def test_load_snippets_method_exists(self):
        """Test that load_snippets method exists"""
        self.assertTrue(hasattr(self.plugin, 'load_snippets'))
        self.assertTrue(callable(self.plugin.load_snippets))

    def test_snippets_json_valid(self):
        """Test that the default snippets.json is valid JSON"""
        config_path = os.path.expanduser('~/.config/terminator/snippets.json')
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    self.assertIsInstance(data, dict)
                except json.JSONDecodeError:
                    self.fail("snippets.json is not valid JSON")


class TestSnipBoxIntegration(unittest.TestCase):
    """Integration tests for the plugin"""

    def setUp(self):
        """Set up test fixtures"""
        self.plugin = SnipBoxPlugin()

    def test_plugin_has_consistent_state(self):
        """Test that plugin maintains consistent state"""
        initial_snippets = self.plugin.snippets.copy()
        # Reload snippets
        self.plugin.load_snippets()
        # Should be consistent
        self.assertEqual(initial_snippets, self.plugin.snippets)

    def test_no_empty_categories(self):
        """Test that there are no empty snippet categories"""
        for category, snippets in self.plugin.snippets.items():
            self.assertGreater(len(snippets), 0,
                               f"Category '{category}' is empty")

    def test_no_empty_commands(self):
        """Test that all commands are non-empty"""
        for category, snippets in self.plugin.snippets.items():
            for name, command in snippets.items():
                self.assertGreater(len(command), 0,
                                   f"Command '{name}' in '{category}' is empty")


def run_tests():
    """Run all tests and return results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSnipBoxPlugin))
    suite.addTests(loader.loadTestsFromTestCase(TestSnipBoxIntegration))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)

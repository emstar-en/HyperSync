"""
Tests for CLI list command
"""

import unittest
import subprocess
import json

class TestCLIList(unittest.TestCase):
    """Test cases for list command."""

    def test_list_core_tier(self):
        """Test listing CORE tier mechanisms."""
        result = subprocess.run(
            ['python', 'cli/consensus/list.py', 'CORE', '--format', 'json'],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['tier_id'], 'CORE')

    def test_list_invalid_tier(self):
        """Test with invalid tier."""
        result = subprocess.run(
            ['python', 'cli/consensus/list.py', 'INVALID'],
            capture_output=True,
            text=True
        )
        self.assertNotEqual(result.returncode, 0)

if __name__ == '__main__':
    unittest.main()

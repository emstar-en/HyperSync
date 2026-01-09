"""
Tests for CLI select command
"""

import unittest
import subprocess
import json

class TestCLISelect(unittest.TestCase):
    """Test cases for select command."""

    def test_select_valid_mechanism(self):
        """Test selecting valid mechanism."""
        result = subprocess.run(
            ['python', 'cli/consensus/select.py', 'raft', 'PRO', '--format', 'json'],
            capture_output=True,
            text=True
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data['status'], 'success')

    def test_select_invalid_mechanism(self):
        """Test selecting invalid mechanism."""
        result = subprocess.run(
            ['python', 'cli/consensus/select.py', 'invalid', 'PRO'],
            capture_output=True,
            text=True
        )
        self.assertNotEqual(result.returncode, 0)

if __name__ == '__main__':
    unittest.main()

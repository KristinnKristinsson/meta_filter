import unittest
import tempfile
import os
import json
from pathlib import Path
from sweep import sweep_directory, save_log, LOG_PATH
from comment import add_comment
from view import load_log

class TestView(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_file_path = Path(self.test_dir.name) / "test_example.py"
        self.test_code = (
            "# @issue style: Consider renaming for clarity\n"
            "def x():\n"
            "    return 42\n"
        )
        with open(self.test_file_path, 'w') as f:
            f.write(self.test_code)

        # Sweep and comment
        issues = sweep_directory(self.test_dir.name)
        save_log(issues)
        self.issue_id = issues[0]['id']
        add_comment(self.issue_id, "AI:StyleBot", "Consider renaming 'x' to something more descriptive.")

    def tearDown(self):
        self.test_dir.cleanup()
        if LOG_PATH.exists():
            os.remove(LOG_PATH)

    def test_view_log_structure(self):
        log = load_log()
        self.assertEqual(len(log), 1)
        issue = log[0]
        self.assertEqual(issue['id'], self.issue_id)
        self.assertEqual(issue['tag'], 'style')
        self.assertEqual(issue['status'], 'unresolved')
        self.assertTrue(issue['code'].startswith('def x'))
        self.assertEqual(len(issue['comments']), 1)
        self.assertEqual(issue['comments'][0]['author'], "AI:StyleBot")


if __name__ == '__main__':
    unittest.main()

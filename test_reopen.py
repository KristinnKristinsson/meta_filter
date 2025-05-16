import unittest
import tempfile
import os
import json
from pathlib import Path
from sweep import sweep_directory, save_log, LOG_PATH
from resolve import resolve_issue
from reopen import reopen_issue

class TestReopen(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_file_path = Path(self.test_dir.name) / "reopen_test.py"
        self.test_code = (
            "# @issue logic: Ensure output is always a string\n"
            "def stringify(x):\n"
            "    return str(x)\n"
        )
        with open(self.test_file_path, 'w') as f:
            f.write(self.test_code)

        issues = sweep_directory(self.test_dir.name)
        save_log(issues)
        self.issue_id = issues[0]['id']

        # Resolve the issue first
        resolve_issue(self.issue_id, "Fixer", "Confirmed str() covers all expected inputs.")

    def tearDown(self):
        self.test_dir.cleanup()
        if LOG_PATH.exists():
            os.remove(LOG_PATH)

    def test_reopen_resolved_issue(self):
        reopen_issue(self.issue_id, "Reopener", "Edge case discovered where input is None.")
        with open(LOG_PATH, 'r') as f:
            log = json.load(f)

        issue = next((item for item in log if item['id'] == self.issue_id), None)
        self.assertIsNotNone(issue)
        self.assertEqual(issue['status'], 'unresolved')
        self.assertTrue(any("Reopened" in c['text'] for c in issue['comments']))


if __name__ == '__main__':
    unittest.main()

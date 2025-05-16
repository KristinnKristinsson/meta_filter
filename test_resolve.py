import unittest
import tempfile
import os
import json
from pathlib import Path
from sweep import sweep_directory, save_log, LOG_PATH
from resolve import resolve_issue

class TestResolve(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_file_path = Path(self.test_dir.name) / "resolve_test.py"
        self.test_code = (
            "# @issue test: Verify resolution mechanism\n"
            "def test_case():\n"
            "    return True\n"
        )
        with open(self.test_file_path, 'w') as f:
            f.write(self.test_code)

        # Sweep and save initial log
        issues = sweep_directory(self.test_dir.name)
        save_log(issues)
        self.issue_id = issues[0]['id']

    def tearDown(self):
        self.test_dir.cleanup()
        if LOG_PATH.exists():
            os.remove(LOG_PATH)

    def test_resolve_issue(self):
        resolve_issue(self.issue_id, "HumanTester", "Confirmed logic is sound.")
        with open(LOG_PATH, 'r') as f:
            log = json.load(f)

        issue = next((item for item in log if item['id'] == self.issue_id), None)
        self.assertIsNotNone(issue)
        self.assertEqual(issue['status'], 'resolved')
        self.assertTrue(any("Resolved" in c['text'] for c in issue['comments']))


if __name__ == '__main__':
    unittest.main()

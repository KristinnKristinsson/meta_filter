import unittest
import tempfile
import os
import json
from pathlib import Path
from sweep import sweep_directory, save_log, LOG_PATH
from comment import add_comment

class TestComment(unittest.TestCase):

    def setUp(self):
        # Setup a temporary directory and file
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_file_path = Path(self.test_dir.name) / "testfile.py"
        self.test_code = (
            "# @issue bug: Needs to handle negative numbers\n"
            "def abs_val(x):\n"
            "    return x if x >= 0 else -x\n"
        )
        with open(self.test_file_path, 'w') as f:
            f.write(self.test_code)

        # Sweep and save initial issues
        issues = sweep_directory(self.test_dir.name)
        save_log(issues)
        self.issue_id = issues[0]['id']

    def tearDown(self):
        self.test_dir.cleanup()
        if LOG_PATH.exists():
            os.remove(LOG_PATH)

    def test_add_comment_to_issue(self):
        add_comment(self.issue_id, "AI:BugBot", "Consider what happens if input is None")
        with open(LOG_PATH, 'r') as f:
            log = json.load(f)

        issue = next((item for item in log if item['id'] == self.issue_id), None)
        self.assertIsNotNone(issue)
        self.assertEqual(len(issue['comments']), 1)
        comment = issue['comments'][0]
        self.assertEqual(comment['author'], "AI:BugBot")
        self.assertIn("input is None", comment['text'])
        self.assertIn("timestamp", comment)


if __name__ == '__main__':
    unittest.main()

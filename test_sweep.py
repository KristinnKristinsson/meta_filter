import unittest
import tempfile
import os
import json
from pathlib import Path
from sweep import sweep_directory, load_existing_log, save_log, LOG_PATH

class TestSweep(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory and file
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_file_path = Path(self.test_dir.name) / "example.py"
        self.test_code = (
            "# @issue perf: This loop might be slow on large input\n"
            "def calculate():\n"
            "    for i in range(1000000):\n"
            "        print(i)\n"
            "\n"
            "# @issue bug: Handle division by zero\n"
            "def buggy():\n"
            "    return 10 / 0\n"
        )
        with open(self.test_file_path, 'w') as f:
            f.write(self.test_code)

    def tearDown(self):
        self.test_dir.cleanup()
        if LOG_PATH.exists():
            os.remove(LOG_PATH)

    def test_sweep_extracts_issues(self):
        issues = sweep_directory(self.test_dir.name)
        self.assertEqual(len(issues), 2)

        perf_issue = issues[0]
        bug_issue = issues[1]

        self.assertEqual(perf_issue['tag'], 'perf')
        self.assertIn('slow', perf_issue['issue'])
        self.assertTrue(perf_issue['code'].startswith('def calculate'))
        self.assertEqual(perf_issue['status'], 'unresolved')

        self.assertEqual(bug_issue['tag'], 'bug')
        self.assertIn('division by zero', bug_issue['issue'])
        self.assertTrue(bug_issue['code'].startswith('def buggy'))

    def test_log_persistence(self):
        issues = sweep_directory(self.test_dir.name)
        save_log(issues)
        loaded = load_existing_log()
        self.assertEqual(len(loaded), 2)
        self.assertEqual(loaded[0]['id'], issues[0]['id'])


if __name__ == '__main__':
    unittest.main()

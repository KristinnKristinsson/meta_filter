import argparse
import json
from pathlib import Path
from datetime import datetime

LOG_PATH = Path(".codeforum/discussion_log.json")


def load_log():
    if LOG_PATH.exists():
        with open(LOG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print("No discussion log found.")
        return []


def list_issues(simplified=False):
    log = load_log()
    if not log:
        return

    for issue in log:
        print("=" * 60)
        print(f"ID:       {issue['id']} ({issue['short_id']})")
        print(f"File:     {issue['file']}")
        print(f"Line:     {issue['line']}")
        print(f"Tag:      {issue['tag']}")
        print(f"Issue:    {issue['issue']}")
        print(f"Status:   {issue['status']}")
        if not simplified:
            print(f"Code:\n{issue['code']}")
            print("Comments:")
            for comment in issue.get('comments', []):
                print(f"  - [{comment['author']}] {comment['text']} ({comment['timestamp']})")
        print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="View code issues and discussion threads.")
    parser.add_argument("--simple", action="store_true", help="Show simplified view (no code or comments)")
    args = parser.parse_args()
    list_issues(simplified=args.simple)


if __name__ == '__main__':
    main()

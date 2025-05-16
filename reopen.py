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


def save_log(log):
    with open(LOG_PATH, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2)


def reopen_issue(issue_id, reopener, reason):
    log = load_log()
    found = False
    for entry in log:
        if entry['id'] == issue_id:
            if entry['status'] != 'resolved':
                print(f"Issue '{issue_id}' is not resolved.")
                return
            entry['status'] = 'unresolved'
            entry.setdefault('comments', []).append({
                "author": reopener,
                "text": f"Reopened: {reason}",
                "timestamp": datetime.now().strftime('%y/%m/%d %H:%M:%S')
            })
            found = True
            break
    if not found:
        print(f"Issue ID '{issue_id}' not found.")
        return

    save_log(log)
    print(f"Issue '{issue_id}' reopened.")


def main():
    parser = argparse.ArgumentParser(description="Reopen a previously resolved issue.")
    parser.add_argument("issue_id", help="ID of the issue to reopen")
    parser.add_argument("--by", required=True, help="Name of the person or AI reopening the issue")
    parser.add_argument("--reason", required=True, help="Reason for reopening the issue")

    args = parser.parse_args()
    reopen_issue(args.issue_id, args.by, args.reason)


if __name__ == '__main__':
    main()

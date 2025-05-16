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


def resolve_issue(issue_id, resolver, summary):
    log = load_log()
    found = False
    for entry in log:
        if entry['id'] == issue_id:
            if entry['status'] == 'resolved':
                print(f"Issue '{issue_id}' is already resolved.")
                return
            entry['status'] = 'resolved'
            entry.setdefault('comments', []).append({
                "author": resolver,
                "text": f"Resolved: {summary}",
                "timestamp": datetime.now().strftime('%y/%m/%d %H:%M:%S')
            })
            found = True
            break
    if not found:
        print(f"Issue ID '{issue_id}' not found.")
        return

    save_log(log)
    print(f"Issue '{issue_id}' marked as resolved.")


def main():
    parser = argparse.ArgumentParser(description="Resolve an issue in the code discussion log.")
    parser.add_argument("issue_id", help="ID of the issue to resolve")
    parser.add_argument("--by", required=True, help="Name of the person or AI resolving the issue")
    parser.add_argument("--summary", required=True, help="Resolution summary or explanation")

    args = parser.parse_args()
    resolve_issue(args.issue_id, args.by, args.summary)


if __name__ == '__main__':
    main()

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
        print("No log file found. Run sweep first.")
        return []

def save_log(log):
    with open(LOG_PATH, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2)

def add_comment(issue_id_or_short_id, author, text):
    log = load_log()
    found = False
    for entry in log:
        if entry['id'] == issue_id_or_short_id or entry.get('short_id') == issue_id_or_short_id:
            comment = {
                "author": author,
                "text": text,
                "timestamp": datetime.now().strftime('%y/%m/%d %H:%M:%S')
            }
            entry.setdefault('comments', []).append(comment)
            found = True
            break
    if not found:
        print(f"Issue ID '{issue_id_or_short_id}' not found.")
        return

    save_log(log)
    print(f"Comment added to issue '{issue_id_or_short_id}'.")

def main():
    parser = argparse.ArgumentParser(description="Add a comment to a code issue.")
    parser.add_argument("issue_id", help="ID of the issue to comment on")
    parser.add_argument("-a", "--author", required=True, help="Author of the comment")
    parser.add_argument("-m", "--text", required=True, help="Text of the comment")

    args = parser.parse_args()
    add_comment(args.issue_id, args.author, args.text)

if __name__ == '__main__':
    main()

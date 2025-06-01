import json
from pathlib import Path
from datetime import datetime

# Load discussion log
LOG_PATH = Path(".codeforum/discussion_log.json")
OUTPUT_PATH = Path("threads/code_threads_log.txt")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

def load_log():
    if LOG_PATH.exists():
        with open(LOG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def format_thread(issue):
    header = f"### {issue.get('tag', 'issue').upper()}: {issue.get('issue', '')}\n"
    meta = (
        f"**File**: `{issue.get('file', '')}`  \n"
        f"**Line**: {issue.get('line', '')}  \n"
        f"**Short ID**: `{issue.get('short_id', '')}`  \n"
        f"**Status**: {issue.get('status', '')}\n\n"
    )
    code_block = f"```python\n{issue.get('code', '').strip()}\n```\n\n"
    
    comments = sorted(issue.get('comments', []), key=lambda c: c.get('timestamp', ''))
    thread_lines = ["**Discussion:**"]
    for comment in comments:
        author = comment.get("author", "Unknown")
        timestamp = comment.get("timestamp", "")
        text = comment.get("text", "")
        thread_lines.append(f"**{timestamp} – {author}**:\n*{text}*")

    thread = "\n\n".join(thread_lines)
    return f"{header}\n{meta}{code_block}{thread}\n\n{'-'*80}\n"

def save_log(issues):
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        for issue in issues:
            f.write(format_thread(issue))

issues = load_log()
save_log(issues)

"Thread log saved to threads/code_threads_log.txt"

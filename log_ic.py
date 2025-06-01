import json
import os
from pathlib import Path
from unique_id import generate_short_id, get_max_short_id_from_log

LOG_PATH = Path(".codeforum/discussion_log.json")

# Directory prep
LOG_PATH.parent.mkdir(exist_ok=True)


def load_existing_log():
    if LOG_PATH.exists():
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_log(log):
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)

def merge_logs(existing, new):
    existing_ids = {item['id'] for item in existing}
    merged = existing[:]

    max_short_id = get_max_short_id_from_log()

    for issue in new:
        if issue['id'] not in existing_ids:
            issue['short_id'] = generate_short_id(existing_max=max_short_id)
            max_short_id += 1
            merged.append(issue)

    return merged
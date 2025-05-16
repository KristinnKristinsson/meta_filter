import string
import json
from pathlib import Path

LOG_PATH = Path(".codeforum/discussion_log.json")

CHARS = string.digits + string.ascii_uppercase
BASE = len(CHARS)

def base36_encode(n):
    s = []
    while n:
        n, r = divmod(n, BASE)
        s.append(CHARS[r])
    return ''.join(reversed(s)).rjust(4, '0')

def base36_decode(s):
    return sum(CHARS.index(c) * (BASE ** i) for i, c in enumerate(reversed(s)))

def get_max_short_id_from_log():
    if LOG_PATH.exists():
        with open(LOG_PATH, 'r', encoding='utf-8') as f:
            try:
                issues = json.load(f)
                return max((base36_decode(issue['short_id']) for issue in issues if 'short_id' in issue), default=-1)
            except Exception:
                return -1
    return -1

def generate_short_id(existing_max=None):
    if existing_max is None:
        existing_max = get_max_short_id_from_log()
    next_num = existing_max + 1
    return base36_encode(next_num)

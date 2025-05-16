import json
import os
from datetime import datetime
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv

from comment import add_comment
from sweep import load_existing_log, save_log

# Load API key from .env
load_dotenv()
client = OpenAI()

LOG_PATH = Path(".codeforum/discussion_log.json")


def get_ai_comment(code, issue_text):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a code reviewer. Keep your comments short, practical, and accurate."},
            {"role": "user", "content": f"The following issue has been raised:\n\n{issue_text}\n\nHere is the code:\n\n{code}\n\nPlease provide a concise code review comment."}
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content.strip()


def auto_comment():
    log = load_existing_log()
    updated = False

    for entry in log:
        if entry["status"] == "unresolved":
            existing_ai_comments = [
                c for c in entry["comments"] if c["author"].startswith("AI:")
            ]
            if not existing_ai_comments:
                print(f"[AI] Commenting on: {entry['short_id']} — {entry['issue']}")
                ai_comment = get_ai_comment(entry["code"], entry["issue"])
                add_comment(entry["short_id"], author="AI:AutoReviewer", text=ai_comment)
                updated = True

    if updated:
        print("AI comments added to unresolved issues.")
    else:
        print("No unresolved issues without AI comments.")


if __name__ == "__main__":
    auto_comment()

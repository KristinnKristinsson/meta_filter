import json
import os
import re
from datetime import datetime
from pathlib import Path
import time
import string

from openai import OpenAI
from dotenv import load_dotenv
from log_ic import load_existing_log, save_log, merge_logs
from unique_id import generate_short_id, base36_decode

CODE_DIR = Path("src")  # or wherever your source files are

SUPPORTED_EXTENSIONS = [".py"]
DEF_PATTERN = re.compile(r"^\s*def\s+\w+\s*\(.*")

# # Load API Key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError("OPENAI_API_KEY not found in environment. Check your .env file.")

client = OpenAI(api_key=api_key)


def extract_function_blocks(filepath):
    """Extracts function blocks from a file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    functions = []
    i = 0
    while i < len(lines):
        if DEF_PATTERN.match(lines[i]):
            start = i
            indent_level = len(lines[i]) - len(lines[i].lstrip())
            i += 1
            while i < len(lines):
                line = lines[i]
                if line.strip() == "":
                    i += 1
                    continue
                curr_indent = len(line) - len(line.lstrip())
                if curr_indent <= indent_level:
                    break
                i += 1
            func_code = ''.join(lines[start:i])
            functions.append((start + 1, func_code))
        else:
            i += 1
    return functions

def analyze_function_with_ai(code, retries=2, delay=1):
    system_prompt = (
        "You are a strict and detail-oriented Python code reviewer.\n\n"
        "You must raise exactly one issue per function if any potential concern exists — even if minor — and you must return ONLY a valid JSON object in this format:\n\n"
        "{\n"
        '  "tag": "bug" | "perf" | "style" | "arch" | "logic",\n'
        '  "message": "<brief summary>",\n'
        '  "explanation": "<1-3 sentence explanation>"\n'
        "}\n\n"
        "If and only if there are truly zero issues, return:\n"
        '{ "tag": null }'
    )

    user_prompt = f"Here is the function:\n\n{code}"

    for attempt in range(retries + 1):
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
            )

            raw = response.choices[0].message.content.strip()
            print(f"[AI RESPONSE]\n{raw}\n")

            # Try to correct malformed JSON with a loose eval or reformat
            if not raw.startswith("{"):
                raw = raw[raw.find("{"):]

            result = json.loads(raw)

            # Make sure it's a structured response
            if isinstance(result, dict) and "tag" in result:
                return result if result["tag"] else None

        except json.JSONDecodeError as e:
            print(f"[JSON ERROR] Attempt {attempt+1}: {e}")
        except Exception as e:
            print(f"[API ERROR] Attempt {attempt+1}: {e}")

        if attempt < retries:
            print(f"[Retrying in {delay}s...]\n")
            time.sleep(delay)

    return None

def make_issue_entry(filepath, line_num, code, tag, message, explanation, short_id):
    return {
        "id": f"{filepath.name}#func_{line_num}",
        "short_id": short_id,
        "file": str(filepath),
        "line": line_num,
        "tag": tag,
        "issue": message,
        "code": code.strip(),
        "status": "unresolved",
        "comments": [
            {
                "author": "AI:AutoDiscover",
                "timestamp": datetime.now().strftime("%y/%m/%d %H:%M:%S"),
                "text": explanation
            }
        ]
    }

existing_log = load_existing_log()

def inject_issue_comment(filepath, line_num, tag, message):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    comment = f"# @issue {tag}: {message}\n"

    # Insert the comment line above the function definition
    insert_idx = line_num - 1
    while insert_idx > 0 and lines[insert_idx].strip() == "":
        insert_idx -= 1

    lines.insert(insert_idx, comment)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)



# Main sweep logic
# def ai_discover_codebase(directory = CODE_DIR, inject=False):
#     short_id = generate_short_id()
#     all_issues = []
#     issue_count = 0
#     injections = []
#     for filepath in directory.rglob("*"):
#         if filepath.suffix in SUPPORTED_EXTENSIONS:
#             function_blocks = extract_function_blocks(filepath)
#             for line_num, code in function_blocks:
#                 result = analyze_function_with_ai(code)
#                 if result and result.get("tag"):
#                     if inject:
#                         injections.append((filepath, line_num, result["tag"], result["message"]))
                    
#                     issue = make_issue_entry(filepath, line_num, code, result["tag"], result["message"], result["explanation"], short_id)
#                     all_issues.append(issue)
#                     issue_count += 1
#                     short_id = generate_short_id(base36_decode(short_id))


#     if all_issues:
#         if inject:
#             for filepath, line_num, tag, message in sorted(injections, key=lambda x: -x[1]):
#                 inject_issue_comment(filepath, line_num, tag, message)
#         existing = load_existing_log()
#         existing_ids = {i['id'] for i in existing}
#         new_issues = [i for i in all_issues if i['id'] not in existing_ids]
#         full_log = existing + new_issues
#         save_log(full_log)
#         return f"Discovered and logged {len(new_issues)} new AI-raised issue(s)."
#     return "No new issues discovered."

def ai_discover_codebase(directory = CODE_DIR):
    injections = []

    for filepath in directory.rglob("*.py"):
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        function_blocks = extract_function_blocks(filepath)

        for line_num, code in function_blocks:
            # Check for @issue tag in lines above the function
            start = line_num - 4 if line_num >= 4 else 0
            header_context = ''.join(lines[start:line_num]).lower()

            if "@issue" in header_context:
                print(f"[SKIP] Function at {filepath.name}:{line_num} already has an @issue tag.")
                continue

            result = analyze_function_with_ai(code)
            if result and result.get("tag"):
                injections.append((filepath, line_num, result["tag"], result["message"]))

    # Inject from bottom up
    for filepath, line_num, tag, message in sorted(injections, key=lambda x: -x[1]):
        inject_issue_comment(filepath, line_num, tag, message)

    return f"Injected {len(injections)} issues into source files."


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI-based code review and tagging tool.")
    parser.add_argument("directory", type=str, help="Target directory to scan")
    # parser.add_argument("--inject", action="store_true", help="Inject @issue comments into code (DANGEROUS!)")
    args = parser.parse_args()
    code_dir = Path(args.directory)
    print(f"Scanning directory: {code_dir.resolve()}")
    ai_discover_codebase(code_dir)
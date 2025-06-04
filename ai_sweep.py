import json
import os
import re
from datetime import datetime
from pathlib import Path
import time
import string

from openai import OpenAI
import httpx
from dotenv import load_dotenv
from log_ic import load_existing_log, save_log, merge_logs
from unique_id import generate_short_id, base36_decode

CODE_DIR = Path("src")  # or wherever your source files are

SUPPORTED_EXTENSIONS = [".py"]
#DEF_PATTERN = re.compile(r"^\s*def\s+\w+\s*\(.*")
DEF_PATTERN = re.compile(r"^\s*def\s+\w+\s*\(.*\):")

# # Load API Key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise RuntimeError("OPENAI_API_KEY not found in environment. Check your .env file.")

client = OpenAI(
    api_key=api_key,
    timeout=httpx.Timeout(timeout=60.0, connect=10.0, read=30.0, write=10.0))


def extract_function_blocks(filepath):
    """
    Extract all top-level function blocks from a Python file.

    Returns a list of tuples:
        (line_number_of_def, function_code_string)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    functions = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if DEF_PATTERN.match(line):
            start = i
            indent_level = len(line) - len(line.lstrip())
            i += 1

            # Capture until next function or dedent
            while i < len(lines):
                next_line = lines[i]
                if next_line.strip() == "":
                    i += 1
                    continue
                current_indent = len(next_line) - len(next_line.lstrip())
                if current_indent <= indent_level and DEF_PATTERN.match(next_line):
                    break
                i += 1

            func_code = ''.join(lines[start:i])
            functions.append((start + 1, func_code))  # Line numbers are 1-based
        else:
            i += 1

    return functions

def find_function_line(issue_line, function_blocks):
    for i, (start, _) in enumerate(function_blocks):
        end = function_blocks[i + 1][0] if i + 1 < len(function_blocks) else float('inf')
        if start <= issue_line < end:
            return start
    return None

from typing import List, Tuple, Dict


def match_issues_to_functions(issues, function_blocks):
    matched = []

    normalized_blocks = []
    for line_num, code in function_blocks:
        header = code.strip().splitlines()[0]
        if header.startswith("def "):
            name = header.split("(")[0].replace("def", "").strip()
            normalized_blocks.append((line_num, name, code))

    for issue in issues:
        issue_line = issue.get("line")
        issue_name = issue.get("function", "").strip()
        tag = issue.get("tag")
        message = issue.get("message")

        best_match = None
        for func_line, func_name, _ in normalized_blocks:
            if issue_name == func_name:
                best_match = (func_line, tag, message)
                break
            # loose match fallback if name fails
            elif abs(issue_line - func_line) <= 2:
                best_match = (func_line, tag, message)

        if best_match:
            matched.append(best_match)

    return matched


def analyze_file_with_ai(file_contents, filename, retries=3):
    system_prompt = f"""
You are a senior Python code reviewer.

Review the entire file {filename}. For each function, suggest at most one issue if applicable. Be pedantic and optimize where possible. 
Use the following strict JSON format for each issue you find:
{{
  "function": "<name of the function>",
  "line": <line number where the function starts>,
  "tag": "bug" | "perf" | "style" | "arch" | "logic",
  "message": "<brief summary of the issue>"
}}
Return a JSON array of issue objects. Do not return anything else.
""".strip()
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": file_contents}
                ],
                temperature=0.3,
            )
            return json.loads(response.choices[0].message.content.strip())
        except Exception as e:
            print(f"[Attempt {attempt+1}] API call failed: {e}")
            time.sleep(2)
    return None

existing_log = load_existing_log()

def inject_issue_comment(filepath, line_num, tag, message):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    comment = f"# @issue {tag}: {message}\n"

    if line_num > len(lines):
        print(f"[WARNING] line number {line_num} is beyond file length {len(lines)} for {filepath.name}")
        line_num = len(lines)

    insert_idx = max(0, line_num - 1)
    lines.insert(insert_idx, comment)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def ai_discover_path(path):
    path = Path(path)

    if path.is_file():
        return ai_discover_file(path)
    elif path.is_dir():
        return ai_discover_directory(path)
    else:
        raise ValueError(f"Invalid path: {path}")

def ai_discover_directory(directory_path):
    injected_total = 0
    for filepath in Path(directory_path).rglob("*.py"):
        result = ai_discover_file(filepath)
        print(result)
        injected_total += int(result.split()[1])  # crude way to parse count
    return f"Injected a total of {injected_total} issues across the directory."

def ai_discover_file(filepath):
    filepath = Path(filepath)

    with open(filepath, 'r', encoding='utf-8') as f:
        file_lines = f.readlines()
        file_contents = ''.join(file_lines)

    function_blocks = extract_function_blocks(filepath)
    issues = analyze_file_with_ai(file_contents, filepath.name)
    print(json.dumps(issues, indent=2))
    if not issues:
        return f"No issues detected in {filepath.name}"

    matched_issues = match_issues_to_functions(issues, function_blocks)

    injections = []
    for line_num, tag, message in matched_issues:
        if line_num > 1 and "@issue" in file_lines[line_num - 2].lower():
            print(f"[SKIP] {filepath.name}:{line_num} already has an @issue")
            continue
        injections.append((filepath, line_num, tag, message))

    for filepath, line_num, tag, message in sorted(injections, key=lambda x: -x[1]):
        inject_issue_comment(filepath, line_num, tag, message)

    return f"Injected {len(injections)} issue(s) into {filepath.name}"



if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI code reviewer with inline annotations.")
    parser.add_argument("path", help="Path to a Python file or directory.")
    args = parser.parse_args()

    ai_discover_path(args.path)
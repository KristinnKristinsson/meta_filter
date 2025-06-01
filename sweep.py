import os
import re
import json
from pathlib import Path
from log_ic import load_existing_log, save_log, merge_logs

# Config
ISSUE_PATTERN = re.compile(r"@issue\s+(\w+):\s*(.*)")
DEF_PATTERN = re.compile(r"^\s*def\s+\w+\s*\(.*\):")
SUPPORTED_EXTENSIONS = ['.py']
LOG_PATH = Path(".codeforum/discussion_log.json")

def find_issues_in_file(filepath):
    issues = []
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for idx, line in enumerate(lines):
        match = ISSUE_PATTERN.search(line.strip())
        if match:
            tag, message = match.groups()

            # Look ahead to see if the next non-empty, non-comment line is a function definition
            func_start_idx = None
            for look_ahead_idx in range(idx + 1, len(lines)):
                next_line = lines[look_ahead_idx].strip()
                if next_line and not next_line.startswith('#'):
                    if DEF_PATTERN.match(next_line):
                        func_start_idx = look_ahead_idx
                    break

            if func_start_idx is not None:
                code_context = extract_function_block(lines, func_start_idx)
                issue_id = f"{filepath.name}#func_{func_start_idx+1}"
            else:
                code_context = extract_code_context(lines, idx)
                issue_id = f"{filepath.name}#line_{idx+1}"

            issues.append({
                "id": issue_id,
                "file": str(filepath),
                "line": idx + 1,
                "tag": tag,
                "issue": message.strip(),
                "code": code_context,
                "status": "unresolved",
                "comments": []
            })
    return issues

def extract_code_context(lines, index, context_size=3):
    start = max(index - context_size, 0)
    end = min(index + context_size + 1, len(lines))
    return ''.join(lines[start:end]).strip()

def extract_function_block(lines, start_index):
    func_lines = []
    indent_level = len(lines[start_index]) - len(lines[start_index].lstrip())
    for i in range(start_index, len(lines)):
        line = lines[i]
        if line.strip() == '':
            func_lines.append(line)
            continue
        curr_indent = len(line) - len(line.lstrip())
        if i == start_index or curr_indent > indent_level:
            func_lines.append(line)
        else:
            break
    # Normalize and return
    cleaned_lines = [line.rstrip() for line in func_lines]
    return '\n'.join(cleaned_lines).strip()

def sweep_directory(directory):
    all_issues = []
    for root, _, files in os.walk(directory):
        for file in files:
            filepath = Path(root) / file
            if filepath.suffix in SUPPORTED_EXTENSIONS:
                issues = find_issues_in_file(filepath)
                all_issues.extend(issues)
    return all_issues

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print("""
Usage: python sweep.py <directory>

Scans Python files in the given directory for @issue comments.
Each @issue should follow this format:
    # @issue <tag>: <description>

The tool captures either the entire function (if the issue is above a def)
or a local context window (if inline), and logs each issue in:
    .codeforum/discussion_log.json

Example:
    python sweep.py src/

Tags might include: bug, logic, perf, style, arch, algo, etc.
""")
        sys.exit(1)

    code_dir = Path(sys.argv[1])
    new_issues = sweep_directory(code_dir)
    existing_log = load_existing_log()
    updated_log = merge_logs(existing_log, new_issues)
    save_log(updated_log)

    print(f"Logged {len(new_issues)} new issue(s). Total issues: {len(updated_log)}")

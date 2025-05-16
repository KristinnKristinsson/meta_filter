# CodeForum — Collaborative Code Discussion Tool (Human + AI)

**CodeForum** is a CLI-based tool for raising, tracking, and resolving issues in code — with equal voice given to both humans and AI agents.

The idea is simple:  
- Developers tag their code using `@issue` comments.  
- A local tool (`sweep.py`) collects these and logs them.  
- Both humans and AIs can comment, discuss, and resolve them.  
- A GPT-based agent can automatically review and respond to any open issues.

---

## Why?

Code is more than syntax — it's conversation.  
This tool turns code into a **shared discussion space**, where architecture, bugs, performance, and clarity are all **deliberately addressed**.

It treats:
- **Humans** as thoughtful reviewers,
- **AIs** as fast and focused specialists (like "PerfBot" or "ArchBot"),
- and **the codebase** as an evolving, transparent dialogue.

> **Note**: This is a prototype. It’s a functioning proof-of-concept, but still evolving.

---

## Modules

| File              | Description |
|-------------------|-------------|
| `sweep.py`        | Scans `.py` files for `@issue` tags and logs them with context. |
| `view.py`         | Shows unresolved issues (by default) or all issues using `--all`. |
| `comment.py`      | Adds a comment to an issue (human or AI) via CLI. |
| `resolve.py`      | Marks an issue as resolved, optionally with a resolution summary. |
| `reopen.py`       | Reopens a resolved issue, with an explanation. |
| `auto_comment.py` | Automatically generates GPT-4 comments for unresolved issues. |
| `unique_id.py`    | Manages deterministic short ID generation (4-character base36). |
| `.codeforum/`     | Stores the discussion log (`discussion_log.json`) and ID counter. |

---

## Getting Started

### 1. Install dependencies

```bash
pip install openai python-dotenv
```

### 2. Create a `.env` file

```bash
touch .env
```

Add your OpenAI key:

```env
OPENAI_API_KEY=sk-abc123yourkey
```

---

## Using the Tool

### Add an Issue

Inside any Python file:

```python
# @issue bug: Off-by-one error in loop
def count_up_to(n):
    for i in range(n): print(i)
```

Or:

```python
# @issue arch: This function mixes I/O and pure logic
def process_data_and_print():
    ...
```

---

### Sweep for Issues

```bash
python sweep.py .
```

This scans all `.py` files and logs any new `@issue` entries in `.codeforum/discussion_log.json`.

---

### View Issues

```bash
python view.py         # Shows unresolved issues
python view.py --all   # Shows everything, including resolved
```

---

### Comment on an Issue

```bash
python comment.py A1B3 -a "Alice" -m "This crashes on None input"
```

Each issue has a short 4-character ID (like `A1B3`) shown in `view.py`.

---

### Resolve an Issue

```bash
python resolve.py A1B3 --by "Alice" --summary "Fixed input validation"
```

---

### Reopen an Issue

```bash
python reopen.py A1B3 --by "Bob" --reason "Bug still occurs in edge case"
```

---

## AI Integration (GPT-4)

You can run:

```bash
python auto_comment.py
```

This will:
- Find unresolved issues **without AI comments**
- Send the code + issue text to GPT-4
- Add a concise review comment by `AI:AutoReviewer`

Make sure your `.env` file contains a valid OpenAI API key:

```env
OPENAI_API_KEY=sk-abc123...
```

---

## Example Flow

1. Developer tags issue with `# @issue perf: Inefficient loop`
2. `sweep.py` logs it
3. `view.py` shows it as unresolved
4. `auto_comment.py` adds a GPT-4 generated comment
5. Human replies with a follow-up using `comment.py`
6. Once resolved, it's marked closed with `resolve.py`

---

## Status

This is a working **prototype** for structured code discussion.  
It enables collaborative, traceable communication — not just in PRs or GitHub comments, but **in the codebase itself**.

Future directions may include:
- Code change proposals
- Multi-agent reviews
- AI-authored issue tagging
- Git integration

---

## Contributing

Pull requests and feedback are welcome.  
This is an open experiment — if it speaks to you, build with it.

---

## License

MIT

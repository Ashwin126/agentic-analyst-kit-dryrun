"""Hook for the reviewer subagent: it may write only runs/telco/review.md, plus scratch files in /tmp.
Every other write inside the project (analysis, briefs, data, config) is blocked, from file tools,
shell commands, or scripts it writes to /tmp. Exit code 2 blocks the action and shows the message to Claude.
Checks are line by line: a line that writes something and names a protected folder is blocked."""
import json, re, sys

REVIEW = "runs/telco/review.md"
PROTECTED = re.compile(r"(^|[\s\"'/=(])(runs|briefs|data|\.claude)/|\bCLAUDE\.md\b")
WRITES = re.compile("|".join([
    r">>?",                                                      # shell redirect
    r"\b(rm|mv|truncate|touch|tee|shred|unlink|rmdir|cp|rsync|install|ln|dd)\b",
    r"\b(sed|perl|ruby)\b.*\s-i",                                # in-place edit
    r"\.to_(csv|parquet|excel|json|pickle|feather|sql)\(",
    r"\.savefig\(",
    r"\bopen\([^)]*[\"'][rb]?[wax+]",
    r"\b(os\.(remove|unlink|rename|replace)|shutil\.\w+)\(",
    r"\.(write_text|write_bytes|unlink|rename|replace|touch|mkdir)\(",
    r"\bjson\.dump\(",
]))
GIT_WRITES = re.compile(r"\bgit\s+(add|commit|push|checkout|switch|reset|restore|stash|rm|mv|merge|rebase|apply)\b")

def blocked(why):
    print(f"Blocked: the reviewer may not change the analysis ({why}). Write only {REVIEW}; "
          "put scratch scripts and their outputs in /tmp.", file=sys.stderr)
    sys.exit(2)

def check_text(text):
    for line in re.split(r"\n|;|&&|\|\||\|(?!\|)", text.replace("\\", "/")):  # one shell step at a time
        if GIT_WRITES.search(line):
            blocked("git commands that change the repo")
        if WRITES.search(line) and PROTECTED.search(line.replace(REVIEW, "")):
            blocked(f"this line writes into the project: {line.strip()[:120]}")

event = json.load(sys.stdin)
tool = event.get("tool_name", "")
tool_input = event.get("tool_input", {})

if tool in ("Edit", "MultiEdit", "NotebookEdit"):
    blocked("edit tools are not allowed")

if tool == "Write":
    path = str(tool_input.get("file_path", "")).replace("\\", "/")
    if path.endswith("/" + REVIEW) or path == REVIEW:
        sys.exit(0)
    if path.startswith("/tmp/"):
        check_text(str(tool_input.get("content", "")))   # scratch script must not write into the project
        sys.exit(0)
    blocked(f"write to {path}")

if tool == "Bash":
    check_text(str(tool_input.get("command", "")))

sys.exit(0)

#!/usr/bin/env python3
"""
PostToolUse hook — fires after every Bash tool call.

When the command is `git push` or `git merge`, prompts the Supervisor
to run the diff-driven memory-update pass on the two-tier memory system.

Triggers: git push, git merge (and git pull, which internally runs git merge)
Does not fire: any other Bash command, and — since T095 — not a command that
merely *writes about* one of those in a heredoc body.
"""
import json
import os
import re
import sys

# `strip_heredoc_bodies` (T095 defect C). This hook had the same defect as the
# merge gate and was found the same way: writing `tasks/TASK_GUIDE_T095.md` — a
# `cat > file` heredoc with no git command anywhere on the line — made this hook
# demand a memory-update pass for a git operation that never happened. Same
# cause, so the same fix, from the same module rather than a second copy.
#
# The guard degrades in the OPPOSITE direction to `pre_bash_block_unsafe_merge`'s
# identically-shaped import, and deliberately so. That hook blocks pushes, so an
# unavailable resolver must become a block. This one is advisory: it prompts, it
# never gates. Losing the helper here can only cost a spurious memory-update
# prompt on a heredoc — the exact pre-T095 behaviour — whereas raising would
# leave the Supervisor with no prompt at all after a real push, which is the
# failure that actually loses information. So it falls back to the identity.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))
try:
    from shell_data import strip_heredoc_bodies  # noqa: E402
except Exception:  # pragma: no cover - exercised via subprocess test
    def strip_heredoc_bodies(command):
        return command

GIT_MEMORY_PATTERNS = [
    r"\bgit\s+push\b",
    r"\bgit\s+merge\b",
    r"\bgit\s+pull\b",   # git pull runs git merge internally
]

MEMORY_UPDATE_PROMPT = """
[hook:post_bash] Git operation detected — memory update required.

Run the diff-driven memory-update pass now:
1. Run: git diff HEAD~1 --name-only
2. Grep memory/decisions.md, memory/glossary.md, memory/learnings.md for any reference to the changed files
3. Update matched entries in place (fix stale facts, expand with new context)
4. Append any new decisions or learnings from this session to the appropriate cold file
5. Summarize new/changed entries as one-liners in memory/MEMORY.md (keep hot tier ≤50,000 characters total)

Routing: architectural/infra decisions → decisions.md | biz terms/domain models → glossary.md | patterns/gotchas/spec clarifications → learnings.md

NOTE: the cold-tier files (decisions.md, glossary.md, learnings.md) are git-tracked. Commit this pass — writing the files to disk is not sufficient. Only memory/event-trace/ is local-only (gitignored).
""".strip()


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if event.get("tool_name") != "Bash":
        sys.exit(0)

    command = event.get("tool_input", {}).get("command", "")

    # Classify the command, not the data it carries (T095 defect C). A heredoc
    # body is content being written to a file, so a `git push` inside one is a
    # mention. Only terminated bodies are stripped, and only up to their
    # terminator, so a real `git push` on the same command line still prompts.
    if not any(re.search(p, strip_heredoc_bodies(command)) for p in GIT_MEMORY_PATTERNS):
        sys.exit(0)

    # Plain stdout from a PostToolUse hook only reaches the debug log.
    # additionalContext is the documented way to inject the prompt into
    # the model's context next to the tool result.
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": MEMORY_UPDATE_PROMPT,
        }
    }))


main()

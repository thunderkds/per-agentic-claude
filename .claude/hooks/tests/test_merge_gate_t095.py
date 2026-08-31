#!/usr/bin/env python3
"""T095 — the merge gate's three defects, one file.

  * **Defect A** — `has_filled_verify_row()` resolved the Evidence section under
    the *main checkout's* `tasks/` only, but Stage 3 writes
    `TASK_REVIEW_Txxx.md` in the agent's worktree, on the task branch. Every
    worktree-isolated task therefore read as `(no evidence row)`.
  * **Defect B** — the block message and the quoted-invocation comment both
    prescribed `CLAUDE_ACTIVE_TASK=Txxx <command>`, which T047 measured as
    non-functional (a hook is a *sibling* process of the tool call).
  * **Defect C** — the gate classified a command by its **data**: a `cat > file`
    heredoc whose body contained `git push` was blocked as a push.

Every fixture here is **constructed**. Nothing reads the live board, the live
`tasks/` directory, or the machine's real `git worktree list` — a test that did
would pass or fail depending on which worktrees happen to exist today.

Run with: python3 -m pytest .claude/hooks/tests/test_merge_gate_t095.py -v
"""
import io
import json
import os
import sys
import tempfile
import types

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK_PATH = os.path.join(HOOKS_DIR, "pre_bash_block_unsafe_merge.py")
sys.path.insert(0, os.path.join(HOOKS_DIR, "lib"))

from shell_data import strip_heredoc_bodies  # noqa: E402


def load_hook_module(path, name):
    """Load a hook without running its bottom-of-file `main()` — same technique
    as `test_merge_gate_evidence.py`, which explains why it is necessary."""
    source = open(path).read()
    marker = "\nmain()"
    assert marker in source, f"{path} no longer ends in a bare main() call"
    module = types.ModuleType(name)
    module.__file__ = path
    exec(compile(source.replace(marker, "\n"), path, "exec"), module.__dict__)
    return module


merge_gate = load_hook_module(HOOK_PATH, "merge_gate_t095")


# ---------------------------------------------------------------------------
# Constructed fixtures
# ---------------------------------------------------------------------------

KANBAN_READY_FOR_REVIEW = """# PROJECT_KANBAN

### Todo

### In Progress

### Ready for Review
- [ ] **T900** — fixture task | common-infrastructure | C2 | Risk: Medium | P0

### Done
"""

# The post-T064 guide shape: the Evidence heading is vacated to a pointer, so
# resolution has to fall through to the review file.
GUIDE_WITH_VACATED_EVIDENCE = """# TASK_GUIDE - T900

### Evidence

> Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T900.md`.

---
"""

REVIEW_WITH_FILLED_VERIFY_ROW = """# TASK_REVIEW - T900

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| Verification command run | ☑ pass | 707 passed |
| verify | ☑ pass | verify skill run, feature confirmed working — pass |
"""

PYTEST_TRACE_RECORD = json.dumps({
    "timestamp": "2026-08-31T00:00:00+00:00",
    "tool_name": "Bash",
    "summary": json.dumps({"command": "python3 -m pytest .claude/hooks/tests/ -q"})[:300],
    "is_error": False,
})

HEREDOC_MENTIONING_A_PUSH = (
    "cat > notes.md <<'EOF'\n"
    "This document explains why the gate blocks a git push.\n"
    "EOF\n"
)


class GateFixture:
    """A main checkout and a stand-in worktree, both constructed on disk, with
    the hook module's module-level paths pointed at them.

    The worktree is a plain directory, not a real `git worktree`: the gate is
    handed its `tasks/` path through the `tasks_dir` parameter, so the test
    exercises the resolution logic without depending on git or on this machine's
    actual worktree list.
    """

    def __init__(self, review_in_worktree=True, review_in_main=False):
        self.root = tempfile.mkdtemp(prefix="t095_gate_")
        self.main_tasks = os.path.join(self.root, "main", "tasks")
        self.worktree_tasks = os.path.join(self.root, "wt-t900", "tasks")
        self.trace_dir = os.path.join(self.root, "main", "memory", "event-trace")
        for path in (self.main_tasks, self.worktree_tasks, self.trace_dir):
            os.makedirs(path)

        self._write(self.main_tasks, "TASK_GUIDE_T900.md", GUIDE_WITH_VACATED_EVIDENCE)
        self._write(self.worktree_tasks, "TASK_GUIDE_T900.md", GUIDE_WITH_VACATED_EVIDENCE)
        if review_in_worktree:
            self._write(self.worktree_tasks, "TASK_REVIEW_T900.md", REVIEW_WITH_FILLED_VERIFY_ROW)
        if review_in_main:
            self._write(self.main_tasks, "TASK_REVIEW_T900.md", REVIEW_WITH_FILLED_VERIFY_ROW)

        self.kanban = os.path.join(self.root, "PROJECT_KANBAN.md")
        with open(self.kanban, "w") as f:
            f.write(KANBAN_READY_FOR_REVIEW)
        with open(os.path.join(self.trace_dir, "T900.jsonl"), "w") as f:
            f.write(PYTEST_TRACE_RECORD + "\n")

        self._saved = (merge_gate.KANBAN, merge_gate.TASKS_DIR, merge_gate.TRACE_DIR)
        merge_gate.KANBAN = self.kanban
        merge_gate.TASKS_DIR = self.main_tasks
        merge_gate.TRACE_DIR = self.trace_dir

    @staticmethod
    def _write(directory, name, text):
        with open(os.path.join(directory, name), "w") as f:
            f.write(text)

    @property
    def search_dirs(self):
        """What the live gate builds from `git worktree list --porcelain`:
        the main checkout first, then each worktree."""
        return [self.main_tasks, self.worktree_tasks]

    def cleanup(self):
        merge_gate.KANBAN, merge_gate.TASKS_DIR, merge_gate.TRACE_DIR = self._saved
        import shutil

        shutil.rmtree(self.root, ignore_errors=True)


def run_gate(command, fixture, worktree_dirs=None):
    """Drive the hook's real `main()` over a constructed event, returning the
    block `reason` or None when the gate stayed silent.

    `worktree_dirs` stands in for the live `git worktree list` enumeration, so
    the fixture's directories are what the gate resolves evidence across.
    """
    event = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    saved_stdin, saved_stdout = sys.stdin, sys.stdout
    saved_enumerator = getattr(merge_gate, "worktree_tasks_dirs", None)
    sys.stdin = io.StringIO(event)
    sys.stdout = io.StringIO()
    if worktree_dirs is not None:
        merge_gate.worktree_tasks_dirs = lambda: list(worktree_dirs)
    try:
        try:
            merge_gate.main()
        except SystemExit:
            pass
        printed = sys.stdout.getvalue().strip()
    finally:
        sys.stdin, sys.stdout = saved_stdin, saved_stdout
        if saved_enumerator is not None:
            merge_gate.worktree_tasks_dirs = saved_enumerator
    if not printed:
        return None
    return json.loads(printed)["reason"]


# ---------------------------------------------------------------------------
# Defect C — a heredoc body is data, not a command (AC7)
# ---------------------------------------------------------------------------

def test_heredoc_body_mentioning_a_push_is_not_treated_as_a_push():
    """AC7: the exact command that was rejected while writing this task's own
    guide — a file write, no git command outside the heredoc body."""
    fixture = GateFixture()
    try:
        assert run_gate(HEREDOC_MENTIONING_A_PUSH, fixture, worktree_dirs=[]) is None
    finally:
        fixture.cleanup()


def test_heredoc_body_mentioning_a_merge_is_not_treated_as_a_merge():
    command = "cat > notes.md <<EOF\nThe Supervisor will git merge this branch later.\nEOF\n"
    fixture = GateFixture()
    try:
        assert run_gate(command, fixture, worktree_dirs=[]) is None
    finally:
        fixture.cleanup()


# ---------------------------------------------------------------------------
# Defect C — anti-evasion (AC8). The highest-consequence direction in this file:
# an over-stripping fix silently disarms the gate.
# ---------------------------------------------------------------------------

def test_real_push_after_the_heredoc_terminator_is_still_blocked():
    """AC8: stripping stops at the terminator, so the `; git push` after it is
    still command text. Without this the fix becomes a way to smuggle a push."""
    fixture = GateFixture()
    try:
        reason = run_gate(
            HEREDOC_MENTIONING_A_PUSH + "; git push origin fix/t900",
            fixture,
            worktree_dirs=[],
        )
        assert reason is not None and "Pipeline gate failed" in reason
    finally:
        fixture.cleanup()


def test_real_push_before_the_heredoc_is_still_blocked():
    fixture = GateFixture()
    try:
        reason = run_gate(
            "git push origin fix/t900 && " + HEREDOC_MENTIONING_A_PUSH,
            fixture,
            worktree_dirs=[],
        )
        assert reason is not None and "Pipeline gate failed" in reason
    finally:
        fixture.cleanup()


def test_push_on_the_heredoc_header_line_is_still_blocked():
    """The header's own line stays command text — only the body is removed."""
    fixture = GateFixture()
    try:
        reason = run_gate(
            "git push && cat > notes.md <<'EOF'\nplain prose\nEOF\n",
            fixture,
            worktree_dirs=[],
        )
        assert reason is not None and "Pipeline gate failed" in reason
    finally:
        fixture.cleanup()


def test_unterminated_heredoc_body_is_not_stripped():
    """Fail-closed direction: with no terminator the body is left as command
    text and still scanned, so the gate over-blocks rather than under-blocks."""
    fixture = GateFixture()
    try:
        reason = run_gate("cat > notes.md <<'EOF'\ngit push origin main\n", fixture, worktree_dirs=[])
        assert reason is not None and "Pipeline gate failed" in reason
    finally:
        fixture.cleanup()


# --- strip_heredoc_bodies itself -------------------------------------------

def test_body_is_replaced_with_a_space_not_deleted():
    """Deleting the span could glue the surrounding words into a token that was
    never in the command — the same rule `QUOTED_SPAN_PATTERN` follows."""
    stripped = strip_heredoc_bodies("cat <<'E'\nbody\nE\npush")
    assert "body" not in stripped
    assert stripped == "cat <<'E'\n \npush"


def test_quoted_and_unquoted_terminators_both_match():
    for header in ("<<EOF", "<<'EOF'", '<<"EOF"', "<< EOF"):
        command = f"cat > f {header}\ngit push\nEOF\ntrue"
        assert "git push" not in strip_heredoc_bodies(command), header


def test_dash_form_allows_a_tab_indented_terminator():
    assert "git push" not in strip_heredoc_bodies("cat > f <<-EOF\ngit push\n\tEOF\ntrue")


def test_plain_form_does_not_end_at_an_indented_terminator():
    """`<<EOF` requires the terminator at column 0. Treating an indented line as
    a terminator would stop stripping early and resume scanning body text."""
    command = "cat > f <<EOF\nprose\n\tEOF\nmore prose\nEOF\ntrue"
    assert "prose" not in strip_heredoc_bodies(command)


def test_multiple_heredocs_are_each_stripped():
    command = "cat > a <<'E1'\ngit push\nE1\ncat > b <<'E2'\ngit merge\nE2\ntrue"
    stripped = strip_heredoc_bodies(command)
    assert "git push" not in stripped and "git merge" not in stripped


def test_here_string_is_not_mistaken_for_a_heredoc():
    """`<<<` has no body and no terminator; misreading it as a header would let
    the rest of the command line be swallowed."""
    command = "grep x <<< 'data'\ngit push"
    assert strip_heredoc_bodies(command) == command


def test_non_string_and_heredoc_free_input_pass_through():
    assert strip_heredoc_bodies(None) is None
    assert strip_heredoc_bodies("git push origin main") == "git push origin main"


# ---------------------------------------------------------------------------
# AC9 anti-vacuity — with the Defect C fix reverted, the heredoc write must go
# back to being blocked. A test that passes with and without the fix proves
# nothing.
# ---------------------------------------------------------------------------

def test_heredoc_allowance_depends_on_the_fix():
    fixture = GateFixture()
    saved = merge_gate.strip_heredoc_bodies
    try:
        assert run_gate(HEREDOC_MENTIONING_A_PUSH, fixture, worktree_dirs=[]) is None
        merge_gate.strip_heredoc_bodies = lambda command: command  # pre-T095 behaviour
        reverted = run_gate(HEREDOC_MENTIONING_A_PUSH, fixture, worktree_dirs=[])
        assert reverted is not None and "Pipeline gate failed" in reverted
    finally:
        merge_gate.strip_heredoc_bodies = saved
        fixture.cleanup()

#!/usr/bin/env python3
"""T095 (Supervisor-approved scope addition) — `post_bash_memory_update.py` had
the merge gate's defect C, in its own file.

The hook fires the diff-driven memory-update prompt when a Bash command looks
like `git push` / `git merge` / `git pull`. It searched the raw command string,
so a `cat > file` heredoc whose **body** mentioned one of those demanded a memory
pass for a git operation that never happened. Observed twice: while writing
`tasks/TASK_GUIDE_T095.md`, and again on this task's own commits.

Same cause as the merge gate's defect C — classifying a command by the data it
carries — so it reuses the same `lib/shell_data.strip_heredoc_bodies` rather than
growing a second copy of the logic.

The two hooks degrade in **opposite** directions when that import fails, which is
the property most worth protecting here: the merge gate blocks pushes, so an
unavailable resolver must become a block; this hook only ever prompts, so it
falls back to the pre-T095 raw-string behaviour. A hook that stays silent after a
real push loses information; one that over-prompts on a heredoc costs a
paragraph.

Run with: python3 -m pytest .claude/hooks/tests/test_memory_hook_heredoc_data.py -v
"""
import json
import os
import subprocess
import sys
import tempfile

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK_PATH = os.path.join(HOOKS_DIR, "post_bash_memory_update.py")

FOREIGN_CWD = tempfile.gettempdir()

HEREDOC_MENTIONING_A_PUSH = (
    "cat > notes.md <<'EOF'\n"
    "This guide explains why the Supervisor must git push the branch.\n"
    "EOF\n"
)


def run_hook(command, env=None):
    """Drive the real hook the way the harness does. True when it fired the
    memory-update prompt."""
    event = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    result = subprocess.run(
        [sys.executable, HOOK_PATH],
        input=event,
        capture_output=True,
        text=True,
        cwd=FOREIGN_CWD,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    assert "Traceback" not in result.stderr, result.stderr
    if not result.stdout.strip():
        return False
    payload = json.loads(result.stdout)
    return "additionalContext" in payload["hookSpecificOutput"]


# --- the defect ------------------------------------------------------------

def test_heredoc_body_mentioning_a_push_does_not_demand_a_memory_pass():
    """The exact command shape that fired it while writing this task's guide."""
    assert run_hook(HEREDOC_MENTIONING_A_PUSH) is False


def test_heredoc_body_mentioning_a_merge_does_not_demand_a_memory_pass():
    command = "cat > notes.md <<EOF\nThe Supervisor will git merge this branch.\nEOF\n"
    assert run_hook(command) is False


def test_heredoc_body_mentioning_a_pull_does_not_demand_a_memory_pass():
    command = "cat > notes.md <<EOF\nRun git pull before starting.\nEOF\n"
    assert run_hook(command) is False


# --- what must keep firing (the direction that loses information) ----------

def test_a_real_push_still_demands_a_memory_pass():
    assert run_hook("git push origin fix/t095-merge-gate") is True


def test_a_real_merge_still_demands_a_memory_pass():
    assert run_hook("git merge --no-ff fix/t095-merge-gate") is True


def test_a_real_push_after_a_heredoc_terminator_still_demands_a_memory_pass():
    """The anti-evasion shape, mirroring the merge gate's AC8: stripping stops
    at the terminator, so the command after it is still command text."""
    assert run_hook(HEREDOC_MENTIONING_A_PUSH + "; git push origin main") is True


def test_a_real_push_before_a_heredoc_still_demands_a_memory_pass():
    assert run_hook("git push origin main && " + HEREDOC_MENTIONING_A_PUSH) is True


def test_unterminated_heredoc_body_still_demands_a_memory_pass():
    """Fail-toward-prompting: with no terminator the body is left as command
    text, so the hook over-prompts rather than going silent."""
    assert run_hook("cat > notes.md <<'EOF'\ngit push origin main\n") is True


# --- the fallback direction ------------------------------------------------

def test_missing_helper_degrades_to_prompting_not_to_silence():
    """With `lib` unimportable, the hook must fall back to the pre-T095 raw
    string search — over-prompting on a heredoc, never silent on a real push.

    Forced by pointing the interpreter at an empty directory tree via a copy of
    the hook with no sibling `lib/`, which is what an incomplete install looks
    like.
    """
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "hooks"))
        stray = os.path.join(tmp, "hooks", "post_bash_memory_update.py")
        with open(HOOK_PATH, encoding="utf-8") as src, open(stray, "w", encoding="utf-8") as dst:
            dst.write(src.read())

        event = json.dumps({"tool_name": "Bash", "tool_input": {"command": "git push origin main"}})
        result = subprocess.run(
            [sys.executable, stray], input=event, capture_output=True, text=True, cwd=FOREIGN_CWD,
        )
        assert result.returncode == 0, result.stderr
        assert "Traceback" not in result.stderr, result.stderr
        assert "additionalContext" in result.stdout, (
            "a real push must still prompt when the helper is unavailable"
        )


# --- unchanged behaviour ---------------------------------------------------

def test_unrelated_command_stays_silent():
    assert run_hook("ls -la") is False


def test_non_bash_tool_is_ignored():
    event = json.dumps({"tool_name": "Read", "tool_input": {"file_path": "x"}})
    result = subprocess.run(
        [sys.executable, HOOK_PATH], input=event, capture_output=True, text=True, cwd=FOREIGN_CWD,
    )
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_unparsable_stdin_exits_zero_silently():
    """Only the shapes this hook actually guarantees today.

    **Pre-existing gap, deliberately not fixed here** (T095's approved scope was
    reusing the heredoc helper, nothing else): a payload that *parses* but is not
    an object — `[]` or `null` — reaches `event.get(...)` and raises
    `AttributeError`. `pre_bash_block_unsafe_merge.py` guards this with an
    explicit `isinstance(event, dict)` check; this hook has no equivalent. It is
    a PostToolUse hook, so the traceback does not fail the tool call — it just
    means no memory-update prompt on a malformed event. Reported to the
    Supervisor rather than folded in silently.
    """
    for payload in ("", "not json"):
        result = subprocess.run(
            [sys.executable, HOOK_PATH], input=payload, capture_output=True, text=True,
            cwd=FOREIGN_CWD,
        )
        assert result.returncode == 0, (payload, result.stderr)
        assert "Traceback" not in result.stderr, (payload, result.stderr)


# --- anti-vacuity ----------------------------------------------------------

def test_the_allowance_depends_on_the_fix():
    """The heredoc must go back to firing when the fix is not in effect.

    Without this, `test_heredoc_body_mentioning_a_push_does_not_demand_a_memory_pass`
    would pass just as well against a hook that never fires at all.

    The pre-T095 behaviour is exactly the fallback path: raw-string search over
    the unmodified command. So a copy of the hook with no sibling `lib/` — an
    incomplete install — reproduces it, and doing it this way keeps the probe
    alive after this change is committed. A probe pinned to `git show HEAD:...`
    would silently start skipping the moment HEAD carried the fix.
    """
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "hooks"))
        stray = os.path.join(tmp, "hooks", "post_bash_memory_update.py")
        with open(HOOK_PATH, encoding="utf-8") as src, open(stray, "w", encoding="utf-8") as dst:
            dst.write(src.read())

        def fired(command):
            event = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
            result = subprocess.run(
                [sys.executable, stray], input=event, capture_output=True, text=True,
                cwd=FOREIGN_CWD,
            )
            assert result.returncode == 0, result.stderr
            return "additionalContext" in result.stdout

        # Fallback active: the heredoc fires again (pre-T095 behaviour) — which
        # also proves the import really did fail, so the sibling assertion in
        # `test_missing_helper_degrades_to_prompting_not_to_silence` is testing
        # the fallback rather than the normal path.
        assert fired(HEREDOC_MENTIONING_A_PUSH) is True
        # ...while the installed hook, with `lib/` present, stays silent on it.
        assert run_hook(HEREDOC_MENTIONING_A_PUSH) is False

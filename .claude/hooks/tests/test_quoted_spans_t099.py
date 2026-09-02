#!/usr/bin/env python3
"""T099 — a quoted span is data or command text depending on what wraps it.

T095 taught both git hooks that a **heredoc body** is data. It left the
**quoted-span** form of the same defect live in both of them, and worse than the
registration recorded: `pre_bash_block_unsafe_merge.py` did not merely
over-prompt, it *blocked*. An ordinary `grep -r "git push" .claude/` was refused
outright whenever any task sat In Progress — precisely when an agent is most
likely to run it.

The tempting fix — reuse the merge gate's existing `QUOTED_SPAN_PATTERN`, which
already strips quoted spans one level down in `invokes_test_runner` — is wrong,
and wrong in the direction that matters. Measured before the fix:

    echo "... git push ..."          today=BLOCK   naive quoted-strip=ALLOW
    bash -c "git push origin main"   today=BLOCK   naive quoted-strip=ALLOW  <- REAL
    ssh box "cd /r && git push"      today=BLOCK   naive quoted-strip=ALLOW  <- REAL

A heredoc body can be classified by looking at itself; a quoted span cannot. It
is an argument, and whether the shell executes it is decided by the command it is
an argument to. So the classification looks **left**, at the wrapper, and every
uncertainty resolves toward *code* — the direction that over-blocks rather than
disarms.

The two anti-vacuity probes at the bottom are the load-bearing ones. One reverts
the fix and asserts AC1 goes red again; the other substitutes the naive strip and
asserts AC2 goes red. Without both, this file would pass against a fix that does
nothing and against a fix that opens the gate.

Every fixture here is **constructed**. Nothing reads the live board or the live
`tasks/` directory. The blocked phrases are assembled at runtime for a reason
that is itself the defect: a source file containing them verbatim cannot be
grepped or edited through a Bash call while the gate is armed.

Run with: python3 -m pytest .claude/hooks/tests/test_quoted_spans_t099.py -v
"""
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import types

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRE_HOOK = os.path.join(HOOKS_DIR, "pre_bash_block_unsafe_merge.py")
POST_HOOK = os.path.join(HOOKS_DIR, "post_bash_memory_update.py")
sys.path.insert(0, os.path.join(HOOKS_DIR, "lib"))

from shell_data import strip_heredoc_bodies, strip_quoted_spans  # noqa: E402

FOREIGN_CWD = tempfile.gettempdir()

# Assembled, never written literally — see the module docstring.
PUSH = "g" + "it p" + "ush"
MERGE = "g" + "it m" + "erge"
PULL = "g" + "it p" + "ull"


def load_hook_module(path, name):
    """Load a hook without running its bottom-of-file `main()`, the technique
    `test_merge_gate_evidence.py` introduced and `test_merge_gate_t095.py` reuses."""
    source = open(path).read()
    marker = "\nmain()"
    assert marker in source, f"{path} no longer ends in a bare main() call"
    module = types.ModuleType(name)
    module.__file__ = path
    exec(compile(source.replace(marker, "\n"), path, "exec"), module.__dict__)
    return module


merge_gate = load_hook_module(PRE_HOOK, "merge_gate_t099")


# ---------------------------------------------------------------------------
# Fixtures — one task In Progress, which is the condition the defect needs
# ---------------------------------------------------------------------------

KANBAN_IN_PROGRESS = """# PROJECT_KANBAN

### Todo

### In Progress
- [ ] **T900** — fixture task | common-infrastructure | C2 | Risk: Medium | P0

### Ready for Review

### Done
"""


class GateFixture:
    """A constructed board with a task In Progress, with the hook module's
    module-level paths pointed at it.

    `In Progress` rather than `Ready for Review` deliberately: that branch of
    `main()` blocks on the task's mere existence, with no evidence lookup at all,
    so what these tests measure is the push/merge *matcher* and nothing else.
    """

    def __init__(self):
        self.root = tempfile.mkdtemp(prefix="t099_gate_")
        self.tasks = os.path.join(self.root, "tasks")
        self.trace = os.path.join(self.root, "memory", "event-trace")
        os.makedirs(self.tasks)
        os.makedirs(self.trace)
        self.kanban = os.path.join(self.root, "PROJECT_KANBAN.md")
        with open(self.kanban, "w") as f:
            f.write(KANBAN_IN_PROGRESS)
        self._saved = (merge_gate.KANBAN, merge_gate.TASKS_DIR, merge_gate.TRACE_DIR)
        merge_gate.KANBAN = self.kanban
        merge_gate.TASKS_DIR = self.tasks
        merge_gate.TRACE_DIR = self.trace

    def cleanup(self):
        merge_gate.KANBAN, merge_gate.TASKS_DIR, merge_gate.TRACE_DIR = self._saved
        import shutil

        shutil.rmtree(self.root, ignore_errors=True)


def pre_blocks(command):
    """True when `pre_bash_block_unsafe_merge` refuses the command."""
    fixture = GateFixture()
    event = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    saved_stdin, saved_stdout = sys.stdin, sys.stdout
    saved_enumerator = merge_gate.worktree_tasks_dirs
    sys.stdin = io.StringIO(event)
    sys.stdout = io.StringIO()
    merge_gate.worktree_tasks_dirs = lambda: []
    try:
        try:
            merge_gate.main()
        except SystemExit:
            pass
        printed = sys.stdout.getvalue().strip()
    finally:
        sys.stdin, sys.stdout = saved_stdin, saved_stdout
        merge_gate.worktree_tasks_dirs = saved_enumerator
        fixture.cleanup()
    return bool(printed)


def post_fires(command, hook_path=POST_HOOK):
    """True when `post_bash_memory_update` demands a memory pass. Driven as a
    subprocess, which is how the harness runs it."""
    event = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    result = subprocess.run(
        [sys.executable, hook_path], input=event, capture_output=True,
        text=True, cwd=FOREIGN_CWD,
    )
    assert result.returncode == 0, result.stderr
    assert "Traceback" not in result.stderr, result.stderr
    if not result.stdout.strip():
        return False
    return "additionalContext" in json.loads(result.stdout)["hookSpecificOutput"]


# ---------------------------------------------------------------------------
# AC1 — a quoted span nothing will execute is data, in both hooks
# ---------------------------------------------------------------------------

DATA_SPANS = [
    'echo "remember to %s the branch before review"' % PUSH,
    'grep -r "%s" .claude/' % PUSH,
    """python3 -c "print('%s')" """ % PUSH,
    "echo 'the Supervisor will %s this later'" % MERGE,
    'grep -rn "%s" memory/ | wc -l' % MERGE,
    'rg --fixed-strings "%s origin main" docs/' % PUSH,
    'echo "run %s first"' % PULL,
]


def test_data_spans_are_not_blocked_by_the_merge_gate():
    """AC1: the live obstruction. Each of these was refused before T099, with a
    task In Progress — which is exactly when an agent runs them."""
    for command in DATA_SPANS:
        assert pre_blocks(command) is False, command


def test_data_spans_do_not_demand_a_memory_pass():
    """AC1, other hook: same commands, and no memory-update prompt for a git
    operation that never happened."""
    for command in DATA_SPANS:
        assert post_fires(command) is False, command


def test_the_guides_three_named_data_shapes_specifically():
    """AC1 names three by hand; they are asserted by name so a future edit to
    `DATA_SPANS` cannot quietly drop one of them."""
    for command in ('echo "…%s…"' % PUSH,
                    'grep -r "%s" .claude/' % PUSH,
                    """python3 -c "print('%s')" """ % PUSH):
        assert pre_blocks(command) is False, command
        assert post_fires(command) is False, command


# ---------------------------------------------------------------------------
# AC2 — a quoted span a wrapper will execute is code. The AC that makes the
# task non-trivial: a naive strip turns every one of these green-as-in-allowed.
# ---------------------------------------------------------------------------

CODE_SPANS = [
    'bash -c "%s origin main"' % PUSH,
    "sh -c '%s --no-ff feature/x'" % MERGE,
    'ssh box "cd /r && %s"' % PUSH,
    'zsh -c "%s origin main"' % PUSH,
    'bash -lc "%s origin main"' % PUSH,
    'docker exec ci "%s origin main"' % PUSH,
    'docker run --rm img sh -c "%s origin main"' % PUSH,
    'env GIT_SSH_COMMAND=ssh sh -c "%s origin main"' % PUSH,
]


def test_code_spans_are_still_blocked_by_the_merge_gate():
    """AC2: a real push wrapped in a shell-invoker is a real push."""
    for command in CODE_SPANS:
        assert pre_blocks(command) is True, command


def test_code_spans_still_demand_a_memory_pass():
    for command in CODE_SPANS:
        assert post_fires(command) is True, command


def test_a_wrapper_after_a_separator_still_applies():
    """Edge case: the wrapper is not at the head of the whole command."""
    for command in ('echo hi; bash -c "%s origin main"' % PUSH,
                    'cd /r && ssh box "%s"' % PUSH,
                    'true | bash -c "%s origin main"' % PUSH,
                    'x=$(bash -c "%s origin main")' % PUSH):
        assert pre_blocks(command) is True, command


def test_a_wrappers_other_quoted_arguments_do_not_shield_its_command():
    """Edge case from the guide: the first span is an ssh *option*, the second is
    the command. Both follow the wrapper, so both are kept — over-keeping, which
    is the safe side."""
    command = 'ssh -o "StrictHostKeyChecking=no" box "%s origin main"' % PUSH
    assert pre_blocks(command) is True
    assert post_fires(command) is True


def test_a_wrapper_in_an_earlier_segment_does_not_leak_into_a_later_one():
    """The wrapper's reach ends at the next command separator, so a genuine data
    span after a `bash -c` call is still data."""
    assert pre_blocks('bash -c "ls -la"; grep -r "%s" .claude/' % PUSH) is False


# ---------------------------------------------------------------------------
# AC3 — the control. An unquoted push has no span to classify at all.
# ---------------------------------------------------------------------------

def test_the_real_unquoted_push_still_blocks():
    assert pre_blocks("%s origin main" % PUSH) is True
    assert post_fires("%s origin main" % PUSH) is True


def test_the_real_unquoted_merge_and_rebase_still_block():
    assert pre_blocks("%s --no-ff feature/x" % MERGE) is True
    assert pre_blocks("git rebase -i HEAD~3") is True


def test_a_real_push_alongside_a_data_span_still_blocks():
    """Stripping a data span must not swallow the real command sharing the line."""
    assert pre_blocks('echo "about to ship" && %s origin main' % PUSH) is True
    assert pre_blocks('%s origin main && echo "done"' % PUSH) is True


# ---------------------------------------------------------------------------
# AC5 — composition order: the heredoc wins
# ---------------------------------------------------------------------------

HEREDOC_CARRYING_A_WRAPPED_PUSH = (
    "cat > notes.md <<'EOF'\n"
    "Then the Supervisor runs bash -c \"%s origin main\" to ship it.\n"
    "EOF\n" % PUSH
)


def test_a_heredoc_body_containing_a_wrapped_push_is_still_data():
    """AC5: the body is being written to a file regardless of what it says, so
    the heredoc strip must run first and remove the wrapper along with it."""
    assert pre_blocks(HEREDOC_CARRYING_A_WRAPPED_PUSH) is False
    assert post_fires(HEREDOC_CARRYING_A_WRAPPED_PUSH) is False


# A heredoc whose *header line* also carries a data command. Written this way on
# purpose: it is the shape that makes the composition order observable, because
# the quoted-span strip run first would take `'EOF'` along with `"writing notes"`
# and leave `<<` with no tag for the heredoc strip to recognise.
HEREDOC_BEHIND_A_DATA_COMMAND = (
    'echo "writing notes" > n.md <<\'EOF\'\n'
    "Then run %s origin main.\n"
    "EOF\n" % PUSH
)


def test_the_composition_order_is_the_one_that_produces_that():
    """The same assertion one level down, on the functions themselves, so a
    reversal of the order is caught even if a hook stops calling them."""
    assert not re.search(r"\b%s\b" % PUSH,
                         strip_quoted_spans(strip_heredoc_bodies(HEREDOC_CARRYING_A_WRAPPED_PUSH)))
    # Heredocs first: the body is data whatever it says, and the header survives
    # to be recognised.
    assert not re.search(r"\b%s\b" % PUSH,
                         strip_quoted_spans(strip_heredoc_bodies(HEREDOC_BEHIND_A_DATA_COMMAND)))
    # Reversed, the quoted-span strip eats the heredoc's own `'EOF'` tag, the
    # header stops parsing, and the body is scanned as command text.
    assert re.search(r"\b%s\b" % PUSH,
                     strip_heredoc_bodies(strip_quoted_spans(HEREDOC_BEHIND_A_DATA_COMMAND)))
    assert pre_blocks(HEREDOC_BEHIND_A_DATA_COMMAND) is False


def test_a_real_wrapped_push_after_the_heredoc_terminator_still_blocks():
    """Anti-evasion: the heredoc strip stops at its terminator, so a wrapper on
    the far side is still command text and its span is still kept."""
    command = HEREDOC_CARRYING_A_WRAPPED_PUSH + '; bash -c "%s origin main"' % PUSH
    assert pre_blocks(command) is True
    assert post_fires(command) is True


# ---------------------------------------------------------------------------
# AC7 — nesting, mixed quotes, unterminated quotes: all resolve toward code
# ---------------------------------------------------------------------------

def test_single_quoted_wrapper_argument_is_code():
    assert pre_blocks("bash -c '%s origin main'" % PUSH) is True


def test_a_wrapper_nested_inside_a_span_keeps_the_span():
    """A span whose own text carries a wrapper resolves toward code. This
    over-blocks `echo "bash -c '<push>'"`, which is genuinely data — telling that
    apart from a real nested invocation needs the shell parser `shell_data`
    exists to avoid, so the uncertainty resolves the safe way."""
    assert pre_blocks("""echo "bash -c '%s'" """ % PUSH) is True
    assert pre_blocks("""echo "ssh box '%s'" """ % PUSH) is True


def test_an_unterminated_quote_leaves_the_rest_alone():
    """A shell would treat the remainder as an open string, but guessing that
    hides whatever follows. Nothing after an unmatched quote is stripped."""
    assert pre_blocks('echo "%s origin main' % PUSH) is True
    assert pre_blocks("echo '%s origin main" % PUSH) is True
    assert post_fires('echo "%s origin main' % PUSH) is True


def test_mixed_quote_types_do_not_terminate_each_other():
    """A `'` inside a `"` span is ordinary text, so the span ends at its own
    closing `"` — not at the apostrophe."""
    assert strip_quoted_spans("""echo "don't %s yet" """ % PUSH).find(PUSH) == -1
    # And the same span handed to a wrapper survives intact.
    kept = strip_quoted_spans("""bash -c "cd /r; %s" """ % PUSH)
    assert PUSH in kept


def test_bash_dash_c_with_an_unquoted_command_is_unaffected():
    """Edge case: no span at all, so nothing is classified and the raw text is
    matched exactly as before."""
    assert pre_blocks("bash -c ls") is False
    assert pre_blocks("bash -c %s" % PUSH) is True


# ---------------------------------------------------------------------------
# AC4 — T095's behaviour is composed with, not replaced
# ---------------------------------------------------------------------------

HEREDOC_MENTIONING_A_PUSH = (
    "cat > notes.md <<'EOF'\n"
    "This guide explains why the Supervisor must %s the branch.\n"
    "EOF\n" % PUSH
)


def test_plain_heredoc_data_is_still_data():
    assert pre_blocks(HEREDOC_MENTIONING_A_PUSH) is False
    assert post_fires(HEREDOC_MENTIONING_A_PUSH) is False


def test_an_unterminated_heredoc_is_still_left_alone():
    """T095's rule, unchanged: no terminator means the body stays command text
    and the command over-blocks."""
    assert pre_blocks("cat > notes.md <<'EOF'\n%s origin main\n" % PUSH) is True


def test_the_quoted_heredoc_tag_is_not_mistaken_for_a_data_span():
    """`<<'EOF'` contains a quoted span. Stripping it must not disturb the
    heredoc handling that runs first, nor glue `<<` to the body."""
    assert pre_blocks(HEREDOC_MENTIONING_A_PUSH) is False
    assert pre_blocks("cat > n.md <<'EOF'\nhello\nEOF\n%s origin main" % PUSH) is True


# ---------------------------------------------------------------------------
# AC6 — the two importers keep their opposite guard directions
# ---------------------------------------------------------------------------

def _hook_copy_without_lib(source, tmp):
    """A copy of a hook with no sibling `lib/` — what an incomplete install
    looks like, and the only way to make the guarded import actually fail."""
    os.makedirs(os.path.join(tmp, "hooks"), exist_ok=True)
    stray = os.path.join(tmp, "hooks", os.path.basename(source))
    with open(source, encoding="utf-8") as src, open(stray, "w", encoding="utf-8") as dst:
        dst.write(src.read())
    return stray


def test_pre_bash_still_blocks_when_the_resolver_is_unavailable():
    """AC6: this hook gates, so an unavailable resolver must become a block —
    including now that it imports a second name from the same module."""
    with tempfile.TemporaryDirectory() as tmp:
        stray = _hook_copy_without_lib(PRE_HOOK, tmp)
        event = json.dumps({"tool_name": "Bash", "tool_input": {"command": "ls"}})
        result = subprocess.run([sys.executable, stray], input=event,
                                capture_output=True, text=True, cwd=FOREIGN_CWD)
        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        assert payload["decision"] == "block"
        assert "Evidence resolver unavailable" in payload["reason"]


def test_post_bash_still_falls_back_to_prompting_when_the_resolver_is_unavailable():
    """AC6, opposite direction: this hook only prompts, so losing the helpers
    costs a spurious prompt — never silence on a real push."""
    with tempfile.TemporaryDirectory() as tmp:
        stray = _hook_copy_without_lib(POST_HOOK, tmp)
        assert post_fires("%s origin main" % PUSH, hook_path=stray) is True
        # Pre-fix behaviour restored, not a crash: the data span over-prompts.
        assert post_fires('grep -r "%s" .claude/' % PUSH, hook_path=stray) is True


def test_the_two_hooks_still_guard_in_opposite_directions():
    """Stated as one assertion, because the property is the *pair*, not either
    half — a future refactor that unifies them would erase it silently."""
    with tempfile.TemporaryDirectory() as tmp:
        pre = _hook_copy_without_lib(PRE_HOOK, tmp)
        post = _hook_copy_without_lib(POST_HOOK, tmp)
        event = json.dumps({"tool_name": "Bash", "tool_input": {"command": "ls"}})
        pre_out = subprocess.run([sys.executable, pre], input=event, capture_output=True,
                                 text=True, cwd=FOREIGN_CWD).stdout
        post_out = subprocess.run([sys.executable, post], input=event, capture_output=True,
                                  text=True, cwd=FOREIGN_CWD).stdout
        assert json.loads(pre_out)["decision"] == "block"   # gates: fail closed
        assert post_out.strip() == ""                       # advisory: fail quiet on a non-git cmd


# ---------------------------------------------------------------------------
# `strip_quoted_spans` itself — the properties inherited from T095
# ---------------------------------------------------------------------------

def test_a_stripped_span_is_replaced_with_a_space_not_deleted():
    """T095's rule, inherited: deleting can glue two words into a token that was
    never in the command."""
    assert "ab" not in strip_quoted_spans('echo a"x"b')
    assert strip_quoted_spans('echo a"x"b') == "echo a b"


def test_non_strings_and_quote_free_input_pass_through_unchanged():
    for value in (None, 123, ["%s" % PUSH], "", "%s origin main" % PUSH, "ls -la"):
        assert strip_quoted_spans(value) == value


def test_it_never_raises_on_hostile_input():
    """It runs before every Bash call in the repo, so a traceback here breaks all
    work — the reason `strip_heredoc_bodies` carries the same promise."""
    for value in ('"', "'", '""', "'''", '"a\'b"c\'', '"' * 50, "a" * 5000 + '"'):
        strip_quoted_spans(value)


# ---------------------------------------------------------------------------
# AC8 — anti-vacuity. Both probes are mandatory: without them this file would
# pass against a fix that does nothing AND against a fix that opens the gate.
# ---------------------------------------------------------------------------

def test_ac1_goes_red_when_the_fix_is_reverted():
    """Probe 1 — revert in place. With `strip_quoted_spans` back to the identity
    (pre-T099 behaviour), the data spans must be refused again. A test that
    passes with and without the fix proves nothing."""
    command = 'grep -r "%s" .claude/' % PUSH
    saved = merge_gate.strip_quoted_spans
    try:
        assert pre_blocks(command) is False
        merge_gate.strip_quoted_spans = lambda command: command
        assert pre_blocks(command) is True, (
            "AC1 passes even with the fix reverted — the test is vacuous"
        )
    finally:
        merge_gate.strip_quoted_spans = saved


def test_ac2_goes_red_under_the_naive_quoted_span_strip():
    """Probe 2 — substitute the wrong fix. Swapping in the unconditional
    `QUOTED_SPAN_PATTERN` strip (the obvious fix the guide warns about) must let
    a real wrapped push through. This is what proves the wrapper-awareness is
    load-bearing rather than decoration."""
    naive = lambda command: merge_gate.QUOTED_SPAN_PATTERN.sub(" ", command)  # noqa: E731
    saved = merge_gate.strip_quoted_spans
    try:
        for command in ('bash -c "%s origin main"' % PUSH,
                        'ssh box "cd /r && %s"' % PUSH,
                        "sh -c '%s --no-ff feature/x'" % MERGE):
            assert pre_blocks(command) is True, command
            merge_gate.strip_quoted_spans = naive
            assert pre_blocks(command) is False, (
                "the naive strip is expected to disarm the gate here; if it does "
                "not, this probe is not measuring what it claims"
            )
            merge_gate.strip_quoted_spans = saved
    finally:
        merge_gate.strip_quoted_spans = saved


def test_the_naive_strip_would_also_disarm_the_memory_hook():
    """The same substitution one level down, covering the second hook without a
    second monkeypatch seam — it is the function, not the hook, that decides."""
    naive = re.compile(r"\"[^\"]*\"|'[^']*'")
    for command in ('bash -c "%s origin main"' % PUSH, 'ssh box "cd /r && %s"' % PUSH):
        assert re.search(r"\b%s\b" % PUSH, strip_quoted_spans(command)), command
        assert not re.search(r"\b%s\b" % PUSH, naive.sub(" ", command)), command


# ---------------------------------------------------------------------------
# The DIRECTION itself, not the enumerated shapes. T099's first round passed
# every test above while `eval "<push>"`, `su user -c "<push>"` and
# `perl -e "system('<push>')"` all went from BLOCK to allow, because it
# enumerated the wrappers to KEEP and let anything unlisted fall through to the
# strip. Enumerating shapes can only ever catch the shapes someone thought of;
# these three tests assert the default, so an unrecognised command is covered
# whether or not anybody names it.
# ---------------------------------------------------------------------------

UNRECOGNISED_WRAPPERS = [
    'eval "%s origin main"' % PUSH,
    'su user -c "%s origin main"' % PUSH,
    """perl -e "system('%s')" """ % PUSH,
    'ruby -e "%s origin main"' % PUSH,
    'node -e "%s origin main"' % PUSH,
    'nohup bash "%s origin main"' % PUSH,
    'flock /tmp/l "%s origin main"' % PUSH,
    'setsid "%s origin main"' % PUSH,
    'watch "%s origin main"' % PUSH,
    'script -c "%s origin main" /dev/null' % PUSH,
    'chroot /r "%s origin main"' % PUSH,
    'stdbuf -o0 "%s origin main"' % PUSH,
]


def test_an_unrecognised_wrapper_resolves_toward_code():
    """None of these is enumerated anywhere in `shell_data`. Every one must
    still block, because *not being enumerated* is what decides it."""
    for command in UNRECOGNISED_WRAPPERS:
        assert PUSH in strip_quoted_spans(command), command
        assert pre_blocks(command) is True, command
        assert post_fires(command) is True, command


def test_a_command_nobody_has_ever_heard_of_still_keeps_its_span():
    """The direction stated at its most general: an invented command name cannot
    be on any list, so its span must survive. This is the assertion whose absence
    let the first round ship — it fails the moment the default flips to strip."""
    for name in ("frobnicate", "zzq-runner", "xyzzy --exec", "\u00e9t\u00e9-run", "a" * 40):
        command = '%s "%s origin main"' % (name, PUSH)
        assert PUSH in strip_quoted_spans(command), command
        assert pre_blocks(command) is True, command


def test_only_the_enumerated_data_commands_can_ever_strip_a_span():
    """The inverse, stated structurally: a span is stripped **only** behind a
    name in `DATA_COMMAND_PATTERN`. Asserted against the pattern itself so a
    future edit that widens the list has to change this test deliberately."""
    import shell_data

    for name in ("echo", "printf", "grep", "egrep", "fgrep", "rg", "ag",
                 "python3 -c", "python -c"):
        assert PUSH not in strip_quoted_spans('%s "%s"' % (name, PUSH)), name
        assert shell_data.DATA_COMMAND_PATTERN.search(name), name
    # And the executor override keeps `python -c` honest: a span that reaches
    # back out to the shell is code again even behind a listed data command.
    reaching_out = """python3 -c "import os; os.system('%s origin main')" """ % PUSH
    assert PUSH in strip_quoted_spans(reaching_out)
    assert pre_blocks(reaching_out) is True

#!/usr/bin/env python3
"""Separating a shell command's *data* from the command itself (T095 defect C).

A hook that decides "is this a push?" by searching the command string treats
everything the command carries as command text. A `cat > file <<'EOF' … EOF`
write whose **body** contains the words `git push` is therefore classified as a
push, and blocked — a misclassification of a write as a push, not a fail-closed
judgement about an ambiguous push. It was found by writing
`tasks/TASK_GUIDE_T095.md`: a heredoc with no git command anywhere on the line,
rejected by the merge gate it was documenting.

`pre_bash_block_unsafe_merge.py` already draws exactly this line one level down,
for the *evidence* matcher: ``QUOTED_SPAN_PATTERN`` exists because "quoted spans
are data, not commands". Heredoc bodies are the same category, so they are
handled the same way, with the same two rules copied deliberately:

* **Replaced with a space, never deleted.** Deleting a span can glue the two
  words either side of it into a token that was never in the command — the exact
  way a data-stripping fix turns into a spurious invocation.
* **Not a shell parser** (Simplicity First). Header recognition and terminator
  matching only. A real tokenizer is the rabbit hole this file exists to avoid.

**Fail-closed direction.** Everything here can only ever cause the caller to see
*less* command text, so every uncertainty resolves toward stripping *less*:

* Only the span from the header's own line-end to the terminator line is
  removed. Anything after the terminator is still command text and is still
  scanned — that is what keeps ``cat > f <<'E' … E`` followed by ``; git push``
  a blocked push rather than a way to smuggle one past the gate.
* An **unterminated** heredoc is left entirely alone. A shell would consume the
  rest of the input as body, so stripping it would arguably be accurate — but
  being wrong in that direction hides a real invocation, while being wrong in
  this direction can only over-block. Over-blocking is recoverable; a silently
  disarmed gate is not.

Shared rather than private to the merge gate because the same misclassification
was observed the same day in ``post_bash_memory_update.py``, which demanded a
memory pass for a push that never happened after matching a push string inside a
heredoc body. Both hooks import from here: the memory hook since ``00c54c6`` on
T095's own branch, the merge gate since T095 landed.


Quoted spans, and why they are not heredoc bodies (T099)
--------------------------------------------------------

T095 fixed the heredoc form of the defect and left the **quoted-span** form
live in both hooks: ``grep -r "git push" .claude/`` was refused outright by the
merge gate whenever any task sat In Progress — which is exactly when an agent is
most likely to run it.

The tempting fix is to reuse ``QUOTED_SPAN_PATTERN`` — the merge gate already
strips quoted spans one level down, in ``invokes_test_runner``. **That fix is
wrong, and it fails in the dangerous direction.** Measured before this module
was touched:

.. code-block:: text

    echo "... git push ..."          today=BLOCK   naive quoted-strip=ALLOW
    bash -c "git push origin main"   today=BLOCK   naive quoted-strip=ALLOW  <- a REAL push
    ssh box "cd /r && git push"      today=BLOCK   naive quoted-strip=ALLOW  <- a REAL push

The asymmetry is the whole point. A heredoc body has a *syntactic* destination:
``<<'EOF' … EOF`` is text being fed to a redirection, so the shell will never
execute it, whatever it says — it can be classified by looking at itself. A
quoted span has no destination of its own. It is an argument, and whether the
shell executes it is decided entirely by the command it is an argument to:
``echo "git push"`` prints those bytes, ``bash -c "git push"`` runs them.
Nothing *inside* the span tells the two apart, so a quoted span can only be
classified by looking **left**, at the command it belongs to.

``invokes_test_runner`` gets away with the unconditional strip because its
failure direction is the opposite one: it proves a runner *was* invoked, so a
false negative reads as "not verified" and the gate refuses the merge. In a
push matcher a false negative reads as "not a push" and the gate steps aside.
Same pattern, opposite consequence — which is why ``strip_quoted_spans`` is a
second function here rather than a second call site for the first one.

The direction rule from the heredoc half is inherited unchanged: every
uncertainty resolves toward treating a span as **code** (strip less, block
more). An unrecognised command, a nested executor, an unterminated quote — each
keeps the span. Over-blocking is recoverable and an operator sees it happen; a
silently disarmed gate is neither.

**That rule is enforced by which list is enumerated, and T099's first round
enumerated the wrong one.** It listed the *wrappers* — an allowlist of spans to
KEEP — so a wrapper nobody had thought of fell through to the strip and its push
became invisible to the gate. The module said the opposite ("a wrapper missing
from this list over-blocks — the recoverable direction"); the code under it
under-blocked, and Stage 5 measured `eval "git push"`, `su user -c "git push"`
and `perl -e "system('git push')"` all flipping BLOCK -> allow. The documented
invariant contradicting the code is how the gap survived review, so it is
recorded here rather than quietly corrected.

The enumeration is therefore inverted: ``DATA_COMMAND_PATTERN`` lists the
commands after which a span is *data*, and everything not on it is code. An
addition to that list is the only way to widen what the gate ignores, which
makes the fail-open direction reviewable in one place instead of unbounded.
"""
import re

# The `<<` / `<<-` header and the terminator word it declares. The word may be
# quoted (`<<'EOF'`, `<<"EOF"`) — which changes expansion inside the body, not
# which word ends it — so the quotes are matched and discarded.
#
# `<<<` is a *here-string*, not a heredoc: it has no body and no terminator, and
# the negative lookahead keeps it out rather than letting `<<` match its first
# two characters and then mis-read the rest of the line as a header.
HEREDOC_HEADER_PATTERN = re.compile(
    r"<<(?!<)(?P<dash>-?)\s*(?P<quote>['\"]?)(?P<tag>[A-Za-z_][A-Za-z0-9_]*)(?P=quote)"
)


def _terminator_pattern(tag, allow_leading_tabs):
    """The line that ends a heredoc: the tag alone on its own line.

    ``<<-`` (and only ``<<-``) permits leading **tabs** before the terminator,
    which is the whole point of that form. Plain ``<<`` does not, so a line
    reading ``  EOF`` does not end it — matching the shell rather than guessing
    keeps the stripped span identical to the one the shell would consume.
    """
    lead = "[\t]*" if allow_leading_tabs else ""
    return re.compile(rf"^{lead}{re.escape(tag)}[ \t]*$", re.MULTILINE)


def strip_heredoc_bodies(command):
    """Replace every terminated heredoc body in `command` with a single space.

    Returns `command` unchanged for non-strings and for anything with no `<<`
    in it. Never raises: callers run before every Bash call in the repo.
    """
    if not isinstance(command, str) or "<<" not in command:
        return command

    pieces = []
    pos = 0
    while True:
        header = HEREDOC_HEADER_PATTERN.search(command, pos)
        if not header:
            break
        # The body starts after the header's line, so the rest of that line
        # (redirections, a second heredoc header, `&& cmd`) stays command text.
        body_start = command.find("\n", header.end())
        if body_start == -1:
            break  # header with no body on this command — nothing to strip
        terminator = _terminator_pattern(
            header.group("tag"), allow_leading_tabs=bool(header.group("dash"))
        ).search(command, body_start + 1)
        if not terminator:
            break  # unterminated: strip nothing, keep scanning the raw text
        pieces.append(command[pos:body_start + 1])
        pieces.append(" ")
        pos = terminator.end()

    if not pieces:
        return command
    pieces.append(command[pos:])
    return "".join(pieces)


# --- Quoted spans: code, unless a known data command precedes them (T099) ---

# Commands after which a quoted argument is **data** — the only way a span gets
# stripped. This is an allowlist of exceptions to a keep-everything default, and
# that direction is the whole point: a command missing from this list keeps its
# spans, so the gate over-blocks, which an operator sees and can work around. A
# command wrongly *added* here silently disarms the gate for every span that
# follows it, which nobody sees. Add to this list only with that asymmetry in
# mind.
#
# Deliberately short. `echo`/`printf` cannot execute their arguments at all, and
# the `grep` family plus `rg`/`ag` only match against them. `python -c` is the
# one entry that does execute its span, and it is here because AC1 requires it;
# it can only execute *Python*, never shell, and a span that reaches back out to
# the shell is caught by ``SPAN_EXECUTOR_PATTERN`` below.
# Anchored at the segment's start, and that anchoring is load-bearing (Stage 4).
# An unanchored search matched a data word appearing anywhere in the prefix, so
# `ssh echo.example.com "<push>"`, `ssh -o "LogLevel=echo" box "<push>"` and any
# host whose name merely contains `echo`/`ag`/`rg` stripped the span and waved a
# real push through — the same fail-open shape as round 1, one level down. A data
# command only makes its arguments data when it is the command *being run*, so
# only leading whitespace and `VAR=value` assignments may precede it. A data
# command behind `sudo`/`time`/`xargs` is therefore kept, which over-blocks: the
# recoverable side, per this module's direction rule.
#
# The leading-path clause is restricted to path characters rather than `\S*`,
# and that restriction is load-bearing too (round 3). `\S*/` could backtrack
# *over* the assignment clause and eat an assignment's own `VAR=` as if it were
# a directory, so `X=/bin/echo sh -c "<push>"` read as "the command is echo" and
# stripped the span off a real `sh -c`. Any first token merely *containing*
# `/echo` was enough. Excluding `=` and the quote characters keeps a path a path.
DATA_COMMAND_PATTERN = re.compile(
    r"\s*(?:[A-Za-z_]\w*=\S*\s+)*"
    r"(?:[\w.\-/]*/)?"
    r"(?:"
    r"echo\b"
    r"|printf\b"
    r"|[ef]?grep\b"
    r"|rg\b"
    r"|ag\b"
    r"|python[0-9.]*\s+-[A-Za-z]*c\b"
    r")"
)

# Text that, appearing **inside** a span, drags it back to code even when a data
# command precedes it: `echo "bash -c '…'"` is genuinely data, but telling that
# apart from a real nested invocation needs the shell parser this module exists
# to avoid, so the uncertainty resolves the safe way. The `system(`/`popen(`/
# `subprocess` clause is what keeps `python -c` in the list above honest.
SPAN_EXECUTOR_PATTERN = re.compile(
    r"(?:^|[^\w./-])(?:"
    r"\w*sh\s+-[A-Za-z]*c\b"
    r"|ssh\b"
    r"|eval\b"
    r"|docker\s+(?:exec|run)\b"
    r")"
    # No left-boundary guard on these: they are usually reached through an
    # attribute (`os.system(`, `subprocess.run(`), so requiring a non-word
    # character before them would miss exactly the spelling that appears.
    r"|(?:system|popen|spawn\w*|exec\w*)\s*\("
    r"|subprocess\b"
)

# Where a shell starts a new command, so a data command seen earlier stops
# applying. `$(` and a backtick open a fresh command context for the same reason.
SEGMENT_BOUNDARY_PATTERN = re.compile(r"[;&|\n]|\$\(|`")


def strip_quoted_spans(command):
    """Replace every quoted span that is **data** with a single space.

    The default is **keep**. A span is treated as command text unless a command
    known to do nothing but print or match its arguments — see
    ``DATA_COMMAND_PATTERN`` — appears earlier in the same command segment. So:

    * ``grep -r "git push" .claude/`` and ``echo "… git push …"`` are data and
      the span is removed;
    * ``bash -c "git push"``, ``ssh box "cd /r && git push"``, and equally
      ``eval "git push"``, ``su user -c "git push"``, ``perl -e "system(…)"`` or
      any wrapper nobody has thought of yet keep their span and still block.

    That direction is the correction T099's second round exists to make. The
    first round enumerated the *wrappers* instead — an allowlist of spans to
    keep — which meant an unrecognised wrapper had its span stripped and its
    push waved through. Unknown must resolve toward **code**, because
    over-blocking is recoverable and an operator sees it happen, while a
    silently disarmed gate is neither. ``test_quoted_spans_t099.py`` pins that
    direction itself, not just the enumerated shapes.

    A span whose own text carries an executor (``SPAN_EXECUTOR_PATTERN``) is
    kept even behind a data command — over-blocking, the safe side.

    An **unterminated** quote ends the scan: the rest of the command is left
    exactly as it arrived. A shell would treat it as an open string, but
    guessing that hides whatever follows, and this module never strips on a
    guess.

    **Compose it after** ``strip_heredoc_bodies``, never before. A heredoc body
    is data regardless of what it contains, so a body carrying
    ``bash -c "git push"`` must already be gone. The reverse order also lets a
    quoted span swallow a heredoc's own header. Both hooks call
    ``strip_quoted_spans(strip_heredoc_bodies(command))``; a single combined
    helper was considered and rejected, because each hook's stripping has to
    stay separately substitutable for the anti-vacuity tests that revert one at
    a time.

    Returns `command` unchanged for non-strings and for anything with no quote
    character in it. Never raises: callers run before every Bash call in the repo.
    """
    if not isinstance(command, str) or ('"' not in command and "'" not in command):
        return command

    pieces = []
    emitted = 0        # end of the text already copied into `pieces`
    segment_start = 0  # start of the current command segment
    i = 0
    while i < len(command):
        char = command[i]
        if char in "\"'":
            close = command.find(char, i + 1)
            if close == -1:
                break  # unterminated - strip nothing further
            span = command[i:close + 1]
            if (DATA_COMMAND_PATTERN.match(command[segment_start:i])
                    and not SPAN_EXECUTOR_PATTERN.search(span)):
                pieces.append(command[emitted:i])
                pieces.append(" ")
                emitted = close + 1
            i = close + 1
            continue
        boundary = SEGMENT_BOUNDARY_PATTERN.match(command, i)
        if boundary:
            segment_start = boundary.end()
            i = boundary.end()
            continue
        i += 1

    if not pieces:
        return command
    pieces.append(command[emitted:])
    return "".join(pieces)

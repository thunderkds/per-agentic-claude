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
classified by looking **left**, at its wrapper.

``invokes_test_runner`` gets away with the unconditional strip because its
failure direction is the opposite one: it proves a runner *was* invoked, so a
false negative reads as "not verified" and the gate refuses the merge. In a
push matcher a false negative reads as "not a push" and the gate steps aside.
Same pattern, opposite consequence — which is why ``strip_quoted_spans`` is a
second function here rather than a second call site for the first one.

The direction rule from the heredoc half is inherited unchanged: every
uncertainty resolves toward treating a span as **code** (strip less, block
more). An unknown wrapper, a nested wrapper, an unterminated quote — each keeps
the span. Over-blocking is recoverable and an operator sees it happen; a
silently disarmed gate is neither.
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


# --- Quoted spans: data, unless a wrapper will execute them (T099) ----------

# Prefixes after which a quoted span is *command text*, not data. Deliberately
# short and deliberately incomplete (Simplicity First): the default is "do not
# strip", so a wrapper missing from this list over-blocks — the recoverable
# direction — while a wrapper wrongly *added* would be the disarming one.
#
# `\w*sh\s+-[A-Za-z]*c` covers `sh -c`, `bash -c`, `zsh -c` and the `-lc`
# /`-ec` cluster forms in one clause rather than enumerating shells. `env` and
# other leading assignments need no clause of their own: `env FOO=1 sh -c "…"`
# still contains `sh -c` before its span.
WRAPPER_PATTERN = re.compile(
    r"(?:^|[^\w./-])(?:"
    r"\w*sh\s+-[A-Za-z]*c\b"
    r"|ssh\b"
    r"|docker\s+(?:exec|run)\b"
    r")"
)

# Where a shell starts a new command, so a wrapper seen earlier stops applying.
# `$(` and a backtick open a fresh command context for the same reason.
SEGMENT_BOUNDARY_PATTERN = re.compile(r"[;&|\n]|\$\(|`")


def strip_quoted_spans(command):
    """Replace every quoted span that is **data** with a single space.

    A span is kept — treated as command text — when either:

    * a shell-invoking wrapper appears earlier in the same command segment, so
      the span is the thing that wrapper will run (``bash -c "git push"``,
      ``ssh box "cd /r && git push"``); or
    * a wrapper appears *inside* the span itself. ``echo "bash -c 'git push'"``
      is genuinely data, and keeping it only over-blocks — but distinguishing it
      from a real nested invocation needs the shell parser this module exists to
      avoid, so the nested case resolves toward code like every other
      uncertainty here.

    A wrapper's *other* arguments are kept too, by construction: in
    ``ssh -o "StrictHostKeyChecking=no" box "git push"`` both spans follow
    ``ssh`` in the same segment, so both survive. That is over-keeping, and over-
    keeping is the safe side.

    An **unterminated** quote ends the scan: the rest of the command is left
    exactly as it arrived. A shell would treat it as an open string, but guessing
    that hides whatever follows, and this module never strips on a guess.

    **Compose it after** ``strip_heredoc_bodies``, never before. A heredoc body
    is data regardless of what it contains, so a body carrying ``bash -c "git
    push"`` must already be gone — otherwise the wrapper *inside* that body
    keeps a span that is being written to a file. The reverse order also lets a
    quoted span swallow a heredoc's own header. Both hooks call
    ``strip_quoted_spans(strip_heredoc_bodies(command))``; a single combined
    helper was considered and rejected, because each hook's stripping has to stay
    separately substitutable for the anti-vacuity tests that revert one at a time.

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
                break  # unterminated — strip nothing further
            span = command[i:close + 1]
            if not (WRAPPER_PATTERN.search(command[segment_start:i])
                    or WRAPPER_PATTERN.search(span)):
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


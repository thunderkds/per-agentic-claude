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
heredoc body. That hook is untouched here (out of scope); this module is where
its fix would come from.
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

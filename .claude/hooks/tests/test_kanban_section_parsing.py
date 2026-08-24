#!/usr/bin/env python3
"""Regression tests for the T045 fix: `find_kanban_section` (pre_agent_validate_guide.py)
and `tasks_in_section` (pre_bash_block_unsafe_merge.py) must anchor their terminating
`###` lookahead to line start, not match a literal `###` quoted inside a row's text.

Reproduces the real 2026-07-23 defect: T039's Done row quoted the phrase
`` `### Hard-Stop Gates` `` while summarizing that task's review findings, which
truncated the Done section right there — every row below it (T042, T038, T022, ...)
became invisible to both hooks. See memory/learnings.md: "Never quote a `###`
heading inside a KANBAN row."

Run with: python3 -m pytest .claude/hooks/tests/test_kanban_section_parsing.py -v
"""
import importlib.util
import os
import re
import sys
import types

HOOKS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(HOOKS_DIR))

VALIDATE_GUIDE_PATH = os.path.join(HOOKS_DIR, "pre_agent_validate_guide.py")
BLOCK_MERGE_PATH = os.path.join(HOOKS_DIR, "pre_bash_block_unsafe_merge.py")


def _load(path, name):
    """pre_agent_validate_guide.py is import-safe (main() is guarded by
    `if __name__ == "__main__"`)."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_bare_main_hook(path, name):
    """pre_bash_block_unsafe_merge.py ends in a bare `main()` call (no
    __main__ guard), which would block on stdin at import time. Strip only
    that trailing call — same pattern as test_merge_gate_evidence.py."""
    source = open(path).read()
    marker = "\nmain()"
    assert marker in source, f"{path} no longer ends in a bare main() call"
    module = types.ModuleType(name)
    module.__file__ = path
    exec(compile(source.replace(marker, "\n"), path, "exec"), module.__dict__)
    return module


validate_guide = _load(VALIDATE_GUIDE_PATH, "pre_agent_validate_guide")
block_merge = _load_bare_main_hook(BLOCK_MERGE_PATH, "pre_bash_block_unsafe_merge")


# --- Fixture reproducing the real 2026-07-23 board shape ---------------------------
# T039's Done row (verbatim, from git history at dd76c96) quotes `### Hard-Stop Gates`
# inline. T042, T038 follow it in the same Done section — the real board also has
# T022 further down, but two is enough to prove "everything below the quote vanishes".

FIXTURE_KANBAN = """# PROJECT_KANBAN.md

## Board

### Todo
- [ ] **T043** — Fix trace/step-limit task attribution | Common-Infrastructure-Agent | C2 | Risk: Medium | P0

### In Progress
- [ ] **T050** — In-flight task | Backend-Implementer | C1 | Risk: Low | P1

### Ready for Review

### Done
- [x] **T039** — Dedup the `## Skills vs Agents` section in CLAUDE.md — Stage 4: 1 P0 (false `verify` Evidence claim) + 2 P1 (AC5 checksum was vacuous — `^## ` couldn't match the real `### Hard-Stop Gates` H3, so both sides extracted empty strings and compared equal) | C2 | Completed: 2026-07-23
- [x] **T042** — Fix post_write_register_task.py Complexity/Risk/Priority extraction | C1 | Completed: 2026-07-21
- [x] **T038** — Fix setup.sh piped curl \\| sh install | C2 | Completed: 2026-07-19
- [x] **T044** — Hook lifecycle & evidence integrity. Two follow-ups carried elsewhere: **T043** (trace attribution) and **T050** (token-audit window). | C2 | Completed: 2026-07-24

### Closed (investigated, will not do)
- [~] **T081** — *(SUPERSEDED 2026-08-21 by T085, which fixes both rows at source)* | C1

## Blocked

_None currently._
"""


def _write_fixture_kanban(monkeypatch, module, text):
    """Point module.KANBAN at a temp file with the given text (does not touch
    the real PROJECT_KANBAN.md)."""
    import tempfile

    fd, path = tempfile.mkstemp(suffix=".md")
    with os.fdopen(fd, "w") as f:
        f.write(text)
    monkeypatch.setattr(module, "KANBAN", path)
    return path


# --- AC2 (validate_guide): every row survives a `###`-quoting Done row -------------

def test_find_kanban_section_survives_inline_hash_quote(monkeypatch):
    path = _write_fixture_kanban(monkeypatch, validate_guide, FIXTURE_KANBAN)
    try:
        assert validate_guide.find_kanban_section("T039") == "Done"
        assert validate_guide.find_kanban_section("T042") == "Done"
        assert validate_guide.find_kanban_section("T038") == "Done"
    finally:
        os.remove(path)


# --- AC3: generalization — `#`, `##`, `####` inline must not truncate either ------

def test_find_kanban_section_survives_various_inline_hash_counts(monkeypatch):
    fixture = FIXTURE_KANBAN.replace(
        "T039**",
        "T039** — mentions #hashtag, ## two, #### four,"
    )
    path = _write_fixture_kanban(monkeypatch, validate_guide, fixture)
    try:
        assert validate_guide.find_kanban_section("T039") == "Done"
        assert validate_guide.find_kanban_section("T042") == "Done"
        assert validate_guide.find_kanban_section("T038") == "Done"
    finally:
        os.remove(path)


# --- AC4: positive — real section boundaries are unchanged, no false-negative ------

def test_find_kanban_section_todo_never_resolves_as_done(monkeypatch):
    path = _write_fixture_kanban(monkeypatch, validate_guide, FIXTURE_KANBAN)
    try:
        assert validate_guide.find_kanban_section("T043") == "Todo"
        assert validate_guide.find_kanban_section("T050") == "In Progress"
        assert validate_guide.find_kanban_section("T999") is None
    finally:
        os.remove(path)


def test_find_kanban_section_on_real_current_board():
    r"""AC4: the actual live PROJECT_KANBAN.md — every task resolves to its
    true section (no regression on the real file)."""
    kanban_path = os.path.join(ROOT, "PROJECT_KANBAN.md")
    with open(kanban_path) as f:
        text = f.read()
    done_ids = re.findall(r"- \[x\] \*\*(T\d+)\*\*", text)
    assert done_ids, "fixture assumption broken: no Done tasks found on real board"
    for tid in done_ids:
        assert validate_guide.find_kanban_section(tid) == "Done", tid


# --- AC6: negative — empty / missing / malformed board still behaves as before -----

def test_find_kanban_section_missing_file(monkeypatch):
    monkeypatch.setattr(validate_guide, "KANBAN", os.path.join(ROOT, "no-such-file.md"))
    assert validate_guide.find_kanban_section("T001") is None


def test_find_kanban_section_empty_file(monkeypatch):
    path = _write_fixture_kanban(monkeypatch, validate_guide, "")
    try:
        assert validate_guide.find_kanban_section("T001") is None
    finally:
        os.remove(path)


# --- AC5 (block_merge): tasks_in_section returns the complete set -------------------

def _tasks_in_section_impl(kanban_text, section_title):
    """block_merge.tasks_in_section is a closure defined inside main(); exercise
    the same regex logic directly against fixture text the way main() would."""
    m = re.search(
        rf"### {re.escape(section_title)}\n(.*?)(?=^###|\Z)", kanban_text,
        re.DOTALL | re.MULTILINE,
    )
    if not m:
        return []
    block = m.group(1).strip()
    return [
        re.search(r"\*\*(T\d+)\*\*", line).group(1)
        for line in block.splitlines()
        if line.strip().startswith("- ") and re.search(r"\*\*(T\d+)\*\*", line)
    ]


def test_tasks_in_section_survives_inline_hash_quote_in_earlier_section():
    """The merge-gate half: an inline `###` in an *earlier* section (Done, which
    comes before In Progress in board order in some layouts) must not swallow a
    later section's rows. Uses a fixture where Done (with the quote) appears
    before In Progress."""
    fixture = """# PROJECT_KANBAN.md

### Done
- [x] **T039** — mentions `### Hard-Stop Gates` inline | C2 | Completed: 2026-07-23
- [x] **T042** — later Done row | C1 | Completed: 2026-07-21

### In Progress
- [ ] **T050** — should still be found | Backend-Implementer | C1 | Risk: Low | P1
- [ ] **T051** — also found | Backend-Implementer | C1 | Risk: Low | P1
"""
    assert _tasks_in_section_impl(fixture, "In Progress") == ["T050", "T051"]
    assert _tasks_in_section_impl(fixture, "Done") == ["T039", "T042"]


def test_tasks_in_section_on_real_pre_bash_block_unsafe_merge_module():
    """Confirms the actual module source (not the reimplementation above) now
    uses the anchored, MULTILINE pattern — reading the source is the only way
    to check the closure without invoking the full hook's stdin protocol."""
    with open(BLOCK_MERGE_PATH) as f:
        src = f.read()
    assert "re.MULTILINE" in src
    assert "(?=^###|\\Z)" in src


# --- AC7: pre_agent_validate_guide.py's existing tests still pass unchanged --------
# (exercised by running the full suite in Verification Command, not duplicated here)


# --- T093 AC3: a bold cross-reference from another row must never win --------------

def test_find_kanban_section_ignores_bold_cross_reference_from_another_row(monkeypatch):
    """T093: FIXTURE_KANBAN's Done row **T044** bold-references **T043** (Todo) and
    **T050** (In Progress) in its prose — the exact live shape that made
    find_kanban_section('T091') return 'Done' while T091 sat in Todo (T090's Done row
    contained `split out as **T091**`). A task's section is the section of the row
    that *is* that task, never of a row that merely mentions it."""
    path = _write_fixture_kanban(monkeypatch, validate_guide, FIXTURE_KANBAN)
    try:
        assert validate_guide.find_kanban_section("T044") == "Done"
        assert validate_guide.find_kanban_section("T043") == "Todo"
        assert validate_guide.find_kanban_section("T050") == "In Progress"
    finally:
        os.remove(path)


# --- T093 M3: real section moves must still be seen (no over-anchoring) ------------

def test_find_kanban_section_follows_a_row_moved_between_sections(monkeypatch):
    """T093 M3: anchoring must key off the row's own ID *within whichever section the
    row sits in* — moving a row's text verbatim from Todo into Done must change the
    answer. A fix that hardcoded 'Todo' for T043 would pass AC3 and fail here."""
    moved = FIXTURE_KANBAN.replace(
        "- [ ] **T043** — Fix trace/step-limit task attribution | Common-Infrastructure-Agent | C2 | Risk: Medium | P0\n",
        "",
    ).replace(
        "### Done\n",
        "### Done\n- [ ] **T043** — Fix trace/step-limit task attribution | Common-Infrastructure-Agent | C2 | Risk: Medium | P0\n",
    )
    assert "**T043**" in moved.split("### Done")[1], "M3 mutation did not land"
    path = _write_fixture_kanban(monkeypatch, validate_guide, moved)
    try:
        assert validate_guide.find_kanban_section("T043") == "Done"
    finally:
        os.remove(path)


# --- T093 AC6: `### Closed` resolution is decided, not incidental ------------------

def test_find_kanban_section_resolves_closed_rows_as_closed(monkeypatch):
    """T093 AC6 — DECIDED: a `- [~]` row under `### Closed` resolves to "Closed",
    not None.

    Rationale: find_kanban_section's only consumer is the `Depends on:` advisory. A
    dependency that was investigated and closed "will not do" is a real, actionable
    signal — "currently 'Closed' (not Done). Confirm this is intentional" is accurate,
    whereas None emits "not found anywhere ... check for a typo", which is false: the
    task exists and was deliberately closed. Returning Closed also requires the anchor's
    checkbox class to carry `[~]` (AC5), which is what mutation M5 falsifies.
    """
    path = _write_fixture_kanban(monkeypatch, validate_guide, FIXTURE_KANBAN)
    try:
        assert validate_guide.find_kanban_section("T081") == "Closed"
    finally:
        os.remove(path)


def test_find_kanban_section_closed_body_stops_at_the_next_h2(monkeypatch):
    """T093 edge case: `### Closed` is followed by `## Blocked` (an H2, not an H3), so a
    `###`-only lookahead would run Closed's body to end-of-file and swallow every later
    section. Any row parked under `## Blocked` must not be reported as Closed."""
    fixture = FIXTURE_KANBAN.replace(
        "_None currently._",
        "- [ ] **T077** — parked pending an upstream decision | C1",
    )
    assert "**T077**" in fixture, "mutation did not land"
    path = _write_fixture_kanban(monkeypatch, validate_guide, fixture)
    try:
        assert validate_guide.find_kanban_section("T077") is None
        assert validate_guide.find_kanban_section("T081") == "Closed"
    finally:
        os.remove(path)


# --- T093 AC4: the live board, every ID that OWNS a row ---------------------------

def _owning_rows_on_live_board():
    """Independent, line-scoped reading of the live board: for each ID that owns a row,
    the section heading it actually sits under. Deliberately NOT reusing
    find_kanban_section — this is the oracle it is checked against."""
    kanban_path = os.path.join(ROOT, "PROJECT_KANBAN.md")
    with open(kanban_path) as f:
        lines = f.read().splitlines()
    section = None
    owned = []
    for line in lines:
        h2 = re.match(r"^## +(.+?)\s*$", line)
        h3 = re.match(r"^### +(\S+(?: \S+)*?)(?: \(.*\))?\s*$", line)
        if h3:
            section = h3.group(1)
            continue
        if h2:
            section = None
            continue
        m = re.match(r"^- \[[ x~]\] \*\*(T\d+)\*\*", line)
        if m:
            owned.append((m.group(1), section))
    return owned


def test_find_kanban_section_on_real_current_board():
    r"""AC4: the actual live PROJECT_KANBAN.md — **every** Txxx that owns a row (not only
    `- [x]` ones) must resolve to the section it is really in. The pre-T093 version of
    this test collected `- \[x\] \*\*(T\d+)\*\*` only, so a Todo row shadowed by a bold
    mention inside a Done row was the one case it could not see — and it stayed green
    *because* the bug's wrong answer was 'Done'."""
    owned = _owning_rows_on_live_board()
    assert owned, "fixture assumption broken: no owning rows found on real board"
    assert any(sec == "Done" for _, sec in owned), "no Done rows found on real board"
    assert any(sec == "Todo" for _, sec in owned), "no Todo rows found on real board"
    for tid, section in owned:
        resolved = validate_guide.find_kanban_section(tid)
        assert resolved == section, (
            f"{tid} owns a row under '{section}' on PROJECT_KANBAN.md but "
            f"find_kanban_section() resolved it to '{resolved}' — a row's section must "
            f"come from the row that IS that task, not from another row mentioning it"
        )


def test_live_board_still_carries_a_bold_cross_reference(monkeypatch):
    """T093 standing regression witness: the fix makes bold cross-references harmless, so
    the board keeps them. If this ever fails, someone un-bolded them again — the T093
    workaround — and the test above stopped exercising the real hazard."""
    kanban_path = os.path.join(ROOT, "PROJECT_KANBAN.md")
    with open(kanban_path) as f:
        lines = f.read().splitlines()
    cross = [
        line for line in lines
        if re.match(r"^- \[[ x~]\] \*\*T\d+\*\*", line)
        and len(set(re.findall(r"\*\*(T\d+)\*\*", line))) > 1
    ]
    assert cross, (
        "no board row bold-references another task any more — if that was a deliberate "
        "un-bolding, it is T093's workaround returning; the anchored resolver makes it "
        "unnecessary"
    )


# --- T093 AC8 / M4: pin tasks_in_section's first-match-per-line property -----------

def test_tasks_in_section_takes_only_the_first_bold_id_per_line():
    """T093 AC8: the blast-radius investigation exempted pre_bash_block_unsafe_merge.py
    from this task on the grounds that tasks_in_section() scopes to a line and takes the
    **first** bold ID on it — a row's own ID is always first, so prose cross-references
    later on the same line cannot win. Pinned here rather than trusted."""
    fixture = """# PROJECT_KANBAN.md

### In Progress
- [ ] **T050** — in flight; supersedes **T039** and unblocks **T042** | C1 | Risk: Low | P1

### Done
- [x] **T039** — earlier work | C2 | Completed: 2026-07-23
- [x] **T042** — earlier work | C1 | Completed: 2026-07-21
"""
    assert _tasks_in_section_impl(fixture, "In Progress") == ["T050"]
    assert _tasks_in_section_impl(fixture, "Done") == ["T039", "T042"]



def test_find_kanban_section_ignores_a_section_heading_quoted_in_a_row(monkeypatch):
    r"""T093, found while implementing: absorbing a heading's trailing qualifier
    (`### Closed (investigated, will not do)`) means the heading pattern no longer
    requires a newline immediately after the section name — so it must be anchored to
    line start on the *heading* side too (`^###`). The live T093 row quotes
    `` `### Closed` `` inside its prose; unanchored, that row was matched as the Closed
    heading and the section body was read from its own text. This is T045's defect
    class on the opposite side of the regex."""
    fixture = FIXTURE_KANBAN.replace(
        "- [ ] **T043** — Fix trace",
        "- [ ] **T043** — decide how `### Closed` rows resolve. Fix trace",
    )
    assert "`### Closed`" in fixture, "mutation did not land"
    path = _write_fixture_kanban(monkeypatch, validate_guide, fixture)
    try:
        assert validate_guide.find_kanban_section("T081") == "Closed"
        assert validate_guide.find_kanban_section("T043") == "Todo"
    finally:
        os.remove(path)

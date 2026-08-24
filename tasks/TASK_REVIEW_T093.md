# TASK_REVIEW — T093: Anchor the board section resolver to a row's own ID

> Sibling of `tasks/TASK_GUIDE_T093.md`. Everything here is **filled by the reviewer at Stage
> 4/5** — it is deliberately NOT in the guide, because the implementing agent re-reads the guide on
> every turn and never fills these two sections.
>
> Consumers resolve each section **guide first, this file second** (`.claude/hooks/lib/guide_sections.py`):
> a legacy guide that still carries these sections inline keeps working unchanged, and a stray
> review file can never override an inline section.

---

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_kanban_section_parsing.py` — 7 new tests: `..._ignores_bold_cross_reference_from_another_row` (AC3), `..._follows_a_row_moved_between_sections` (M3), `..._resolves_closed_rows_as_closed` (AC6), `..._closed_body_stops_at_the_next_h2`, `..._ignores_a_section_heading_quoted_in_a_row`, `test_find_kanban_section_on_real_current_board` **rewritten** to iterate every owning row (AC4), `test_live_board_still_carries_a_bold_cross_reference`, `test_tasks_in_section_takes_only_the_first_bold_id_per_line` (AC8). `FIXTURE_KANBAN` gained the shadowing hazard, a `### Closed` section and a `## Blocked` section |
| Verification command run | ☑ pass | `python3 -m pytest .claude/hooks/tests/ tests/ -q` → `726 passed in 9.40s` (719 baseline + 7 new, 0 regressions — AC10). Both paths; bare `pytest tests/ -q` collects 8 |
| Negative cases hold | ☑ pass | **All 5 mutation controls run, each confirmed landed (`git diff --stat` / `grep`) before its verdict.** **M1** (load-bearing): the two un-boldings from `30ae3d6`/`e7945eb` restored → pre-fix `find_kanban_section('T091')`/`('T092')` returned `Done` while both sat in Todo **with all 719 tests green**; post-fix both return `Todo`, 726 green. **M2** (revert the anchor to `f"**{task_ref}**" in body`) → **RED**, 4 tests incl. the AC3 fixture test and the AC4 live-board test, the latter naming the task and both sections: `T091 owns a row under 'Todo' … resolved it to 'Done'`. **M3** (drop `Done` from the section list) → **RED**, incl. `..._follows_a_row_moved_between_sections`, so that test is not vacuous. **M4** (helper takes the *last* bold ID per line) → **RED**, pinning `tasks_in_section`'s first-match property. **M5** (delete `[~]` from the checkbox class) → **RED**, incl. the AC6 Closed assertion. Also: `T999` → `None`, missing/empty board → `None` (pre-existing tests, still green). **AC9** — the `Depends on:` advisory re-exercised directly: not-Done dep → `\"…currently 'Todo' (not Done)…\"`, unknown dep → `\"…not found anywhere…\"`, Done dep → no warning |
| verify | ☐ pass / ☐ fail / ☐ N/A | [what was observed — must literally state "pass" or "fail" here too, e.g. "skill run, feature confirmed working — pass": the merge gate scans this Notes column for the word "pass", not just the Result column] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed: `find_kanban_section()` and its single consumer, the `Depends on:` advisory at `pre_agent_validate_guide.py:99`. Skipped by design: `pre_bash_block_unsafe_merge.py` — **AC7 verified, `git diff main -- .claude/hooks/pre_bash_block_unsafe_merge.py` is empty**; its `tasks_in_section()` was pinned by test rather than edited |
| **AC8 pin reaches production, not a copy (Stage 4 P2 — fixed)** | ☑ pass | As delivered, AC8's test called `_tasks_in_section_impl`, a hand-copy of the regex logic living in this test file, so the merge-gate exemption AC8 exists to pin was still *trusted*, not pinned. Fixed by extracting the real `tasks_in_section` closure from `pre_bash_block_unsafe_merge.py` by AST and exec'ing it (the closure is inside `main()`, so this is the only route that avoids the hook's stdin protocol). **Control run by the Supervisor, mutation confirmed landed (`grep -c re.findall` → 1): breaking the real closure's first-match property (`re.search` → `re.findall(...)[-1]`) turns 2 tests RED, while the copy-based helper returns `['T001']` and stays blind — the real-closure pin returns `['T002']` and catches it.** That side-by-side is the evidence the P2 was real rather than stylistic. `pre_bash_block_unsafe_merge.py` reverted and re-confirmed byte-identical to `main` (AC7 intact) |
| Full smoke suite still green (no regression) | ☑ pass | 726 passed, 0 failed. The 4 pre-existing T045 tests in this file are unchanged and green |
| Security review (Medium risk — mandatory) | ☑ pass | Scoped manually to `main..fix/t093-impl` (not the built-in `origin/HEAD` diff — 8 recorded over-scope incidents in this repo). Surface is one pure, read-only function. **0 findings.** Probes run against the live module: (a) `task_ref` stays `re.escape`d — `T.*`, `T001|T002`, `T(`, `T[0-9]{3}` all return `None` rather than matching or raising, and the caller already constrains it to `T\\d{3}`; (b) board text cannot forge a section — a Done row quoting `` `- [x] **T002**` `` inline and an indented `- [ ] **T003**` sub-bullet both fail to shadow the real Todo rows, which is a **fail-open gate hardened**, not merely unchanged; (c) no ReDoS — a 40,000-row pathological board resolves in 0.40s; (d) fail-open preserved — missing/unreadable board still returns `None` and never blocks a spawn; (e) no `subprocess`/`eval`/`exec`/network/write in the file |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | No UI component — a Python hook function and its tests |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | No UI component |
| **UI: Responsiveness at target viewports** | ☑ N/A | No UI component |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**: Captured `2026-08-24T09:08:57Z` on branch `fix/t093-impl`, **before any implementation
commit**, with the two un-boldings from `30ae3d6` restored (M1) so the live board carries the shape
that actually broke — `**T091**`/`**T092**` bold inside T090's Done row:

```
$ date -u +"BEFORE captured %Y-%m-%dT%H:%M:%SZ"
BEFORE captured 2026-08-24T09:08:57Z

$ python3 -c '<load .claude/hooks/pre_agent_validate_guide.py, call find_kanban_section>'
find_kanban_section('T090') -> 'Done'
find_kanban_section('T091') -> 'Done'     # WRONG — T091 is in Todo
find_kanban_section('T092') -> 'Done'     # WRONG — T092 is in Todo
find_kanban_section('T093') -> 'Todo'
find_kanban_section('T081') -> None       # ### Closed — undecided, not designed
find_kanban_section('T074') -> None

$ python3 -m pytest .claude/hooks/tests/ tests/ -q
719 passed in 9.81s
```

Both halves matter: two Todo tasks resolve as `Done` purely because another row mentions them in
bold, **and the full 719-test suite is green while it happens** — the fixture omits the hazard and
the live-board test iterates `- [x]` rows only, so neither test can see it.

**AFTER**: Captured `2026-08-24T09:13:57Z`, same commands, same board — the cross-references are
**still bold** (left that way deliberately, as a standing regression witness):

```
$ date -u +"AFTER captured %Y-%m-%dT%H:%M:%SZ"
AFTER captured 2026-08-24T09:13:57Z

$ python3 -c '<load .claude/hooks/pre_agent_validate_guide.py, call find_kanban_section>'
find_kanban_section('T090') -> 'Done'
find_kanban_section('T091') -> 'Todo'      # was 'Done'
find_kanban_section('T092') -> 'Todo'      # was 'Done'
find_kanban_section('T093') -> 'Todo'
find_kanban_section('T081') -> 'Closed'    # was None — AC6, now decided
find_kanban_section('T074') -> 'Closed'    # was None

$ python3 -m pytest .claude/hooks/tests/ tests/ -q
726 passed in 9.40s
```

**DELTA**: A task's board section is now read from the row that *is* that task (`^- [ x~] **Txxx**`),
so writing a completion note that bold-references a follow-up no longer makes that follow-up read as
`Done` to the spawn-time `Depends on:` advisory — and `### Closed` rows now resolve to `"Closed"`
instead of silently to `None`.

**WITNESS**: Implemented and run by `common-infrastructure` in worktree `wt-t093` on
`fix/t093-impl`, 2026-08-24 09:08–09:14Z. **Independent re-run of M1 and M2 by the Supervisor is
still outstanding** — the guide requires it and this row must not be read as satisfying it.
Trace attribution note: `memory/event-trace/T093.jsonl` covers only the tail of the session — see
the Evidence table's scope row.

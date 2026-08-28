# TASK_REVIEW — T094: The hook suite is red on v2's first commit — three failures, two unrelated causes

> Sibling of `tasks/TASK_GUIDE_T094.md`. Everything here is **filled by the reviewer at Stage
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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_kanban_section_parsing.py` — 3 tests added: `test_cross_section_hazard_resolves_to_the_owning_row` (AC4, pins T093's regression on `HAZARD_BOARD`), `test_pre_t093_resolver_fails_the_cross_section_hazard` (AC4/AC9 anti-vacuity: the pre-T093 resolver answers `Done` for a task owning a Todo row), `test_live_board_checks_pass_on_a_drained_board` (AC2, runs the two real live-board test functions against `DRAINED_BOARD`). Suite: `697 passed in 8.76s` |
| Verification command run | ☑ pass | `python3 -m pytest .claude/hooks/tests/ -q` → `697 passed`; `python3 -m pytest tests/test_provider_adapters.py -q` → `11 passed`; template char count → `3512` (AC6 bound: ≤ 3526). Full BEFORE/AFTER in the Demonstration below |
| Negative cases hold | ☑ pass | **AC9** (Group B is load-bearing): guard reverted to T091's text (3,717 chars) → `AssertionError: c-infra: 10,327 -> 10,518 chars — grew past its T082 floor.` / `assert 10518 <= 10327`, `1 failed, 3 passed`; restored to 3,512 immediately after. **AC4** (Group A is load-bearing): `_pre_t093_find_kanban_section(HAZARD_BOARD, "T900")` returns `Done` while the current resolver returns `Todo` — asserted in-suite, so the fixture cannot silently stop reproducing the defect. **AC8**: `git diff` against `test_agent_guide_dedup.py`, `tests/test_provider_adapters.py`, `PROJECT_KANBAN.md`, `pre_agent_validate_guide.py`, `pre_bash_block_unsafe_merge.py` is empty — 0 lines; `T082_BASELINE_REF` and `AC7_ROLE_BASELINE` untouched |
| verify | ☑ pass | Run by the user 2026-08-27. Runtime surface: `pre_agent_validate_guide.py` driven as a PreToolUse hook (JSON event on stdin, as `settings.json` invokes it) — not via import. **5 probes:** real T094 spawn → clean allow; `TASK_GUIDE_T999.md` → correct `decision: block`; prose-only `T999` → silent allow (structural-vs-prose holds at the CLI); **T093 hazard rebuilt live** (Done row reading `split out as **T900**` while T900 owns a Todo row, spawning a task with `Depends on: T900`) → resolved `'Todo' (not Done)`, i.e. the defect stays caught at the production surface; **drained board** (Todo + In Progress empty) → no crash, correct `not found anywhere on PROJECT_KANBAN.md`. Separately, the guide's Trap was closed by observation: T094 moved off Todo to genuinely drain the live board, fixed test file re-run → `19 passed`. Worktree restored clean after every probe. **Verdict: PASS.** Limitation recorded: no live sub-agent was spawned, so the compressed Staleness Guard was verified as text an agent would receive, not as observed agent behaviour |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed: the 2 changed files + their consumers. `general-agent-template.md` is read by `tests/test_provider_adapters.py` and `test_agent_guide_dedup.py` (both re-run, green); `test_kanban_section_parsing.py` has no callers. Skipped: the rest of the repo, untouched by the diff. `code-review` → 0 P0/P1, 4 P2/P3 all applied in `c148b7e`. `security-review` → 0 findings (diff is one test file + one doc file, both hard-excluded categories; no hook or gate logic changed) |
| Full smoke suite still green (no regression) | ☑ pass | `.claude/hooks/tests/`: `697 passed` (from `3 failed, 691 passed` at the guide's baseline). `tests/`: `40 passed`. Both after the final commit |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | Pure-backend task: the diff is one pytest file and one agent-guide markdown file. There is no UI component, no rendered surface, and the TASK_GUIDE carries no UI/Design AC section |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | Same — no tokens, colors, or typography are touched by a test-suite fix and a prose compression |
| **UI: Responsiveness at target viewports** | ☑ N/A | Same — nothing in this task renders at any viewport |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**: real, timestamped run of the guide's Verification Command against the unmodified
worktree at `04c8f7e` (working tree clean except this untracked review file), captured before any
implementation commit exists:

```
$ git status --porcelain
?? tasks/TASK_REVIEW_T094.md
$ date -u +%Y-%m-%dT%H:%M:%SZ
2026-08-25T04:48:49Z
$ git rev-parse --short HEAD
04c8f7e

$ python3 -m pytest .claude/hooks/tests/ -q
...
E       AssertionError: no board row in an earlier-scanned section bold-references a task owning a
E       row in a later-scanned one (e.g. a Done row naming a Todo follow-up) - if that was a
E       deliberate un-bolding, it is T093's workaround returning; the anchored resolver makes it
E       unnecessary, and removing it blinds test_find_kanban_section_on_real_current_board to the
E       defect T093 fixed
E       assert []

.claude/hooks/tests/test_kanban_section_parsing.py:397: AssertionError
=========================== short test summary info ============================
FAILED .claude/hooks/tests/test_agent_guide_dedup.py::test_ac7_per_role_loaded_size_is_strictly_lower_than_baseline[c-infra]
FAILED .claude/hooks/tests/test_kanban_section_parsing.py::test_live_board_still_carries_a_cross_section_bold_reference
2 failed, 692 passed in 9.20s

$ python3 -m pytest tests/test_provider_adapters.py -q
...........                                                              [100%]
11 passed in 0.02s

$ python3 -c "print(len(open('.claude/agents/general-agent-template.md').read()))"
3717
```

**Trap already fired — read with the above.** The guide records *three* failures; this baseline
shows *two*. The missing one is `test_find_kanban_section_on_real_current_board`, and it is not
fixed: commit `04c8f7e` (`plan(T094)`) registered T094's own Todo row on `PROJECT_KANBAN.md`, which
re-populated the Todo section and turned that test green with no code change — exactly the
documented Trap. It will go red again the moment the board drains. Per the guide it is **not**
accepted as the fix; AC2 proves the real fix against a drained-board fixture instead.

A pre-registration capture (`04c8f7e~1`) was attempted via `git archive` into a scratch tree and
discarded as invalid, not quoted here: the extracted tree has no `.git`, so the ~30 tests that read
baselines via `git show <sha>:<path>` fail spuriously (32 failed / 661 passed) — noise, not signal.
The board file itself was left untouched (`PROJECT_KANBAN.md` is a Files-Must-NOT-Touch entry).

**AFTER**: the same Verification Command, post-change, at `c148b7e`:

```
$ date -u +%Y-%m-%dT%H:%M:%SZ
2026-08-25T04:54:48Z

$ python3 -m pytest .claude/hooks/tests/ -q
........................................................................ [ 92%]
.................................................                        [100%]
697 passed in 8.76s

$ python3 -m pytest tests/test_provider_adapters.py -q
...........                                                              [100%]
11 passed in 0.01s

$ python3 -c "print(len(open('.claude/agents/general-agent-template.md').read()))"
3512
```

697, not the guide's predicted 694: 694 collected at baseline (3 failed + 691 passed), plus the
three new tests this task adds (`test_cross_section_hazard_resolves_to_the_owning_row`,
`test_pre_t093_resolver_fails_the_cross_section_hazard`,
`test_live_board_checks_pass_on_a_drained_board`). The fourth change is a rename, and the deleted
duplicate was never collected — Python bound only the second definition — so neither moves the
count.

**DELTA**: `.claude/hooks/tests/` is green on v2 and stays green when the board drains, so every
subsequent v2 task's "Full smoke suite still green" Evidence row now means something instead of
being false-or-blocked — and the two board tests no longer have to be re-reddened by the ordinary
act of finishing all open work.

**WITNESS**: run by the implementing Common-Infrastructure agent in worktree
`/home/hungnguyenhuu/workspace/pets/wt-t094` on 2026-08-25 (UTC timestamps above, `date -u` inline
with each capture). **No independent witness yet** — and the event trace does not supply one:
`memory/event-trace/T094.jsonl` contains exactly one entry, the Supervisor's `Write` of the guide at
`2026-08-25T04:36:04Z`. None of this session's commands appear in it, even though
`.claude/hooks/.state/active_task` was set to T094 before the first test run, so the trace hook is
not capturing this worktree's tool calls. Independent confirmation is Stage 5's `/verify`, which
only the user can run.

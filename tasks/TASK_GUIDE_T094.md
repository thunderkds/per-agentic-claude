# TASK_GUIDE — T094: The hook suite is red on v2's first commit — three failures, two unrelated causes
**Date**: 2026-08-25
**Complexity Level**: C2
**Risk Level**: Medium
**Priority**: P0
**Assigned agent**: Common-Infrastructure-Agent
**Agent guide**: `.claude/agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

Before writing any code:
1. Read `PROJECT_SPEC.md`
2. Read `memory/MEMORY.md`
3. Read this file completely
4. Read `.claude/agents/common-infrastructure.md`
5. Note the **Complexity Level** above and apply the matching process from the Complexity matrix in your role guide
6. C2 task, multi-file: read `memory/codebase-map.md`
7. Read `memory/learnings.md` — specifically the T075 entry ("the budget test was coupled to the file being nearly full") and the "a negative-grep test free-passes when its file list is wrong" entry. Defect group A below is the **same defect class as T075**; the prior fix is your pattern reference.

---

## Requirement (Pillar 1 — Adapt the requirement)

User request, 2026-08-25, verbatim:

> "yes, fix the red suite as v2's first task"

Context: v2 was branched from `main` to become the working branch while `main` stays frozen as the
user's live v1 install (see `memory/decisions.md`, 2026-08-25). Running the hook suite on v2's first
commit found it already red — inherited from `main`, not introduced by v2:

```
$ python3 -m pytest .claude/hooks/tests/ -q
3 failed, 691 passed in 9.12s
FAILED test_agent_guide_dedup.py::test_ac7_per_role_loaded_size_is_strictly_lower_than_baseline[c-infra]
FAILED test_kanban_section_parsing.py::test_find_kanban_section_on_real_current_board
FAILED test_kanban_section_parsing.py::test_live_board_still_carries_a_cross_section_bold_reference
```

**Restated intent**:
> Return `.claude/hooks/tests/` to green on v2, fixing each failure at its real cause rather than at
> the assertion, so that every subsequent v2 task's "Full smoke suite still green" Evidence row means
> something. A red baseline makes that row either false or permanently blocked.

The three failures have **two unrelated causes**. They are one task because they share one
deliverable — a green suite — and each fix is small; they are kept as separate AC groups because
conflating them is how one gets fixed and the other gets rationalised.

### Defect group A — two Kanban tests are coupled to the live board's contents

`test_kanban_section_parsing.py` asserts against the real `PROJECT_KANBAN.md`. The board is now
fully drained (T091/T092/T093 all closed; Todo and In Progress both empty), so:

- `test_find_kanban_section_on_real_current_board` fails on
  `AssertionError: no Todo rows found on real board` — its own fixture-assumption guard, firing
  correctly.
- `test_live_board_still_carries_a_cross_section_bold_reference` fails with
  `assert []` — it requires a Done row that bold-references a task owning a row in a later-scanned
  section, and with no Todo rows there can be no such pair.

Neither failure indicates the T093 fix regressed. `find_kanban_section()` is fine. The tests
encoded an incidental property of the data file — that the board always has work on it — as a
precondition. This is exactly T075: a test coupled to a file's transient fullness, broken by the
ordinary operation that empties it.

**Trap, read this before touching anything.** Registering T094 itself puts a Todo row on the board,
which makes both tests go green **without fixing anything**. That green is an artifact of this
task's own bookkeeping and will go red again the moment the board drains. Do not accept it as the
fix, and do not report it as evidence. Prove the fix by running the tests against a **drained-board
fixture**, not against the live file in its current state.

Also found while diagnosing, in scope for this task: `test_kanban_section_parsing.py` defines
`test_find_kanban_section_on_real_current_board` **twice** — once at line 139 (the T045 version,
matching only `- [x]` rows) and again at line 349 (the T093 version). Python binds the second, so
the T045 version is dead code that has never run since T093 landed and silently never will. It must
not be left in place.

### Defect group B — T091 grew the shared agent template past c-infra's pinned budget floor

`test_ac7_per_role_loaded_size_is_strictly_lower_than_baseline[c-infra]` fails:

```
AssertionError: c-infra: 10,327 -> 10,518 chars — grew past its T082 floor.
```

Measured cause, confirmed:

| File | at `ebb2958` (the T082 floor) | now | delta |
|---|---|---|---|
| `.claude/agents/general-agent-template.md` | 3,526 | 3,717 | **+191** |
| `.claude/agents/common-infrastructure.md` | 6,801 | 6,801 | 0 |

`git log ebb2958..HEAD -- .claude/agents/general-agent-template.md` returns exactly T091's two
commits (`bbfd0f0`, `3b036e1`). T091's Staleness Guard rewrite added 191 characters to the
**shared** template, which is loaded alongside every role guide; `common-infrastructure.md` is the
smallest role guide and the only pair sitting close enough to its floor to breach. The test worked
as designed and caught a real per-spawn context regression that T091's own review did not.

This is a genuine budget breach, not a stale baseline. The test comment above `AC7_ROLE_BASELINE`
is explicit that a blanket re-pin "would have made the next role to breach invisible" — and this
breach is precisely that next one. Re-pinning `T082_BASELINE_REF` forward to absorb it repeats the
mistake T082's Stage 4 review already caught once, and the assertion message anticipates the
temptation by name: *"Report the real number rather than reframing the criterion."*

**Out of scope**:
- Any change to `find_kanban_section()` or `tasks_in_section()` themselves — they are correct; T093
  and T045 fixed them and those fixes stand.
- Any change to the *meaning* of the Staleness Guard. T091's content fix (naming `CLAUDE.md` as the
  source, naming both adapters, naming the conformance test) is correct and must survive intact —
  this task may only make it shorter, never less accurate or less complete.
- The other test directory, `tests/` — not implicated; leave it alone.
- Behavioural skill evals (the originally-proposed v2 first task). Separate concern, not started.

**Requirement Refs**: none — this is a defect registered from a live suite run, not a PRD feature.
`PRD.md` has no FR covering the repo's own test health.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (Supervisor, 2026-08-25)
- [x] Domain terms align with `PROJECT_SPEC.md` — "budget floor", "live board", "fixture assumption" all pre-existing
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] Requirement Refs: none exist, and none are needed (defect task)

---

## Dependencies & Reachability

**Depends on**: `None` — both defects are already present on the current commit.

**Entry point**: `python3 -m pytest .claude/hooks/tests/ -q`

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | `python3 -m pytest .claude/hooks/tests/ -q` exits 0 with zero failures | "fix the red suite" |
| 2 | Both Kanban tests pass against a **drained-board fixture** (no Todo rows, no In Progress rows), proving the fix is not the T094 row's side effect | Group A + the Trap |
| 3 | Both Kanban tests still pass against the live board **as it is today** (with the T094 Todo row present) | Group A, no regression |
| 4 | The defect T093 fixed is still caught: a fixture board where a Done row bold-references a Todo task must still make the relevant test fail if `find_kanban_section` is reverted to its pre-T093 form | Group A — the fix must not be "delete the assertion" |
| 5 | `test_kanban_section_parsing.py` defines `test_find_kanban_section_on_real_current_board` exactly once; whichever coverage the removed duplicate carried is preserved (the T045 version's `- [x]`-only sweep is a strict subset of the T093 version's, so verify rather than assume) | Group A, dead-code finding |
| 6 | `.claude/agents/general-agent-template.md` is ≤ 3,526 characters (its `ebb2958` size), restoring c-infra below its floor | Group B |
| 7 | The Staleness Guard section still names `CLAUDE.md` as the mirrored source, **both** adapter paths (`AGENTS.md` and `.cursor/rules/agent-base.mdc`), and `tests/test_provider_adapters.py` — i.e. `tests/test_provider_adapters.py` stays green, all 11 of its tests | Out of scope: T091's meaning survives |
| 8 | `T082_BASELINE_REF` and `AC7_ROLE_BASELINE` are unchanged — the breach is fixed by shrinking the file, not by moving the floor | Group B, explicit |
| 9 | Negative: with the shortened guard text reverted to T091's version, AC7[c-infra] goes red again — proving AC6's fix is load-bearing and not a measurement artifact | Group B, anti-vacuity |

---

## Evaluation & Acceptance

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | Full hook suite, current worktree | 694 passed, 0 failed | automated test |
| 2 | A fixture `PROJECT_KANBAN.md` with a populated Done section and an empty Todo and In Progress | Both Kanban tests pass | automated test |
| 3 | Same fixture, but `find_kanban_section` monkeypatched to its pre-T093 first-match-wins form | The cross-section test fails | automated test (anti-vacuity probe) |
| 4 | `general-agent-template.md` reverted to HEAD's version | AC7[c-infra] fails at 10,518 | manual probe, output pasted |
| 5 | `tests/test_provider_adapters.py` after the guard is shortened | 11 passed | automated test |

### Verification Command (exact, runnable)

```bash
python3 -m pytest .claude/hooks/tests/ -q && \
python3 -m pytest tests/test_provider_adapters.py -q && \
python3 -c "print(len(open('.claude/agents/general-agent-template.md').read()))"
```

Expected: `694 passed`, then `11 passed`, then an integer ≤ `3526`.

### Evidence (filled by reviewer at Stage 4/5)

> Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T094.md`.

---

## Demonstration

> See `tasks/TASK_REVIEW_T094.md`.

---

## Approach

**Pattern reference**: `.claude/hooks/tests/test_memory_channel_and_budget.py` — this is the file
T075 fixed for the identical defect class (a test coupled to a data file's transient fullness). Read
how it decoupled: the assertion moved onto a constructed fixture, and the live-file check became a
separate, weaker sanity assertion that cannot fail on ordinary content change. Imitate that split.

**Vital slice**: the two Kanban tests' fixture decoupling — that is the recurring failure mode and
the one that will break again next time the board drains. Group B is a two-line content edit.

**Cut list**:
- No sweep of the other 29 test files for the same coupling pattern. Two instances are known and
  fixed here; a systematic audit is a separate task if the pattern recurs a third time.
- No new lint or hook to prevent live-file coupling generally. Premature — three occurrences (T075,
  and this task's two) is not yet a pattern worth automating against.

**Recommended approach.**

*Group A.* Build a drained-board fixture (Done rows present, Todo and In Progress empty, plus one
Done row bold-referencing a Todo-owning task for the cross-section case) and point both failing
tests at it. The live board keeps a check, but a weakened one: assert only that every task **that
does own a row** resolves to that row's real section — which is vacuously true on an empty board and
strictly meaningful on a populated one. That preserves the regression value on a real board without
requiring the board to be in any particular state. Delete the shadowed line-139 duplicate after
confirming its assertion is a subset of line 349's (AC5).

*Group B.* Shorten the Staleness Guard by ≥191 characters without dropping any of the four things
T091 put in it. Its current form is six lines of prose that restate the adapter contract; the
content requirement is that a maintainer editing `CLAUDE.md`'s non-negotiables learns (a) both
adapters mirror it, (b) their two paths, (c) the test enforces it. That is compressible to roughly
half the prose. Verify with AC7 and AC9, not by eye.

Do **not** attempt Group B by trimming a different part of the shared template — the +191 is
T091's and the budget conversation belongs where the growth happened.

---

## Edge Case Checklist

- [ ] The T094 Todo row makes both Group A tests green without any code change — do not mistake this for the fix (AC2 exists to catch it)
- [ ] Deleting the line-139 duplicate silently removes coverage the line-349 version does not have — verify subset before deleting, don't assume (AC5)
- [ ] Shortening the guard drops one of the two adapter paths, or the test name — `tests/test_provider_adapters.py` goes red and catches it (AC7)
- [ ] Shortening the guard to ≤3,526 by deleting content rather than compressing it: the guard's line budget is separately capped at ≤8 non-blank lines by `test_provider_adapters.py`, so both bounds must hold at once
- [ ] The drained-board fixture is written to a real path inside the repo and left behind, or written to a tracked file — use `tmp_path`/monkeypatch as the surrounding tests already do (see T059: a test that wrote to a tracked repo file destroyed data in a worktree)
- [ ] Fixing the cross-section test by deleting its assertion — it exists to keep the T093 regression detectable (AC4)
- [ ] `git show ebb2958:<path>` is the baseline reader; character counts must be `.decode('utf-8')`-based, not byte-based (the existing comment at `baseline_loaded_chars` explains why — em dashes and `≤` inflate bytes ~4%)

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `.claude/hooks/tests/test_kanban_section_parsing.py` | Decouple the two failing tests from live-board contents via a drained-board fixture; remove the shadowed duplicate at line 139 |
| `.claude/agents/general-agent-template.md` | Compress the `## Staleness Guard` section by ≥191 chars, preserving all of T091's content |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/hooks/pre_agent_validate_guide.py` | `find_kanban_section()` is correct; T093 fixed it. The bug is in the tests |
| `.claude/hooks/pre_bash_block_unsafe_merge.py` | Same — `tasks_in_section()` is not implicated |
| `.claude/hooks/tests/test_agent_guide_dedup.py` | The AC7 assertion and its baselines are correct and must stay untouched (AC8). Fix the file it measures, not the measurement |
| `tests/test_provider_adapters.py` | It is the oracle for AC7 of this task; changing it would let the guard rewrite mark its own homework |
| `PROJECT_KANBAN.md` | Supervisor-owned. Do not add, remove, or reorder rows to influence a test result |

---

## Test Plan

1. **Red first.** Run the verification command on an unmodified worktree; paste the 3 failures.
2. Group A: write the drained-board fixture and the anti-vacuity probe (Success Criterion 3) — probe
   red against pre-T093 behaviour — *before* changing the two tests.
3. Group A: repoint the tests; confirm green against both the fixture and the live board.
4. Group A: confirm the duplicate's assertion is a subset of the survivor's, then delete it; suite green.
5. Group B: compress the guard; run AC6 (char count), AC7 (`test_provider_adapters.py`), AC9 (revert probe).
6. Full run: `python3 -m pytest .claude/hooks/tests/ -q` and `python3 -m pytest tests/ -q`, both green.

---

## Completion Checklist

- [ ] Implementation done
- [ ] Self-review: `Skill({ skill: "code-review" })` run
- [ ] Security review: `Skill({ skill: "security-review" })` run (Medium risk — required)
- [ ] Lint passes
- [ ] Tests written AND pass — output pasted into `tasks/TASK_REVIEW_T094.md`'s Evidence table (Hard-Stop Gate 5)
- [ ] `Skill({ skill: "verify" })` run
- [ ] `memory/MEMORY.md` updated (if new patterns or feedback learned)
- [ ] Supervisor notified: task ready for Stage 4 review

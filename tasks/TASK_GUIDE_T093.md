# TASK_GUIDE — T093: Anchor the board section resolver to a row's own ID
**Date**: 2026-08-24
**Complexity Level**: C2
**Risk Level**: Medium
**Priority**: P2
**Assigned agent**: Common-Infrastructure-Agent
**Agent guide**: `.claude/agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

Before writing any code:
1. Read `PROJECT_SPEC.md`
2. Read `memory/MEMORY.md`
3. Read this file completely
4. Read `.claude/agents/common-infrastructure.md`
5. Note the **Complexity Level** (C2) and apply the matching process from the Complexity matrix in your role guide
6. **C2 — read `memory/codebase-map.md`** for directory layout and blast-radius hotspots

---

## Requirement (Pillar 1 — Adapt the requirement)

> "give it its own row" — user, 2026-08-24, on a defect the Supervisor surfaced while reconciling the
> board, having introduced one instance of it in the same session.

`find_kanban_section()` (`.claude/hooks/pre_agent_validate_guide.py:35`) searches board sections in the
fixed order `Done, Ready for Review, In Progress, Todo` and returns on the first section whose body
contains the literal `**Txxx**` anywhere. Board rows routinely bold-reference *other* tasks —
completion notes name their follow-ups, superseded rows name their successor — so **a Todo task
bold-referenced from a Done row resolves as `Done`**, first match winning.

Observed live, twice, not theorised:
- T090's merged body contains `split out as **T091**`. Once T090 moved to Done,
  `find_kanban_section("T091")` returned `Done` while T091 sat in Todo.
- The Supervisor's own T090 completion note reproduced it for `**T092**` in the same commit.

Both were un-bolded at the call site. That is a **workaround, not a fix**: the next completion note
that bolds a follow-up ID reintroduces it, and nothing prevents that.

**Restated intent**:
> A task's board section is determined by the row that *is* that task, never by another row that
> merely mentions it — and the tests must be able to fail when that stops being true.

### Blast radius — investigated at Stage 2, and it narrows the task

The T093 board row flagged, as an open question to check rather than an assumption, whether the merge
gate consumes the same shadowed answer — which would be P0-shaped. **It was checked before this guide
was written, and the answer is no. Priority stays P2.** Recorded here with the reasoning so the
implementer does not re-derive it, and so a wrong conclusion is falsifiable rather than invisible:

- **`find_kanban_section()` has exactly one consumer**: the `Depends on:` advisory at
  `pre_agent_validate_guide.py:99`. It is explicitly **non-blocking** (the guide's own Dependencies
  section says so). So the live impact of shadowing is a **fail-open advisory**: a dependency that is
  really Todo reads as `Done`, the "not Done — confirm this is intentional" warning never fires, and
  the spawn proceeds silently. Real, and quiet, but advisory.
- **`tasks_in_section()` in `pre_bash_block_unsafe_merge.py:279` is a different function and is not
  vulnerable to this.** It splits the section body into lines, keeps only lines whose strip starts with
  `- `, and takes `re.search`'s **first** `**(T\d+)**` on each. A row's own ID is always the first bold
  ID on its line, so prose cross-references later in the same line cannot win. The merge gate is sound
  here. **Do not "fix" it** — changing it is out of scope (see Files Must NOT Touch).
- One residual in `tasks_in_section()` worth an assertion but **not** a behaviour change: a sub-bullet
  line beginning `- ` inside `In Progress`/`Ready for Review` that mentions a bold ID would be counted
  as a task in that section. That fails **closed** (a spurious merge blocker), which is the safe
  direction, and no such line exists on the board today (`In Progress` body is currently `\n\n`).

**Out of scope**:
- Any behaviour change to `pre_bash_block_unsafe_merge.py`. It is correct here; the investigation above
  is the evidence, and re-opening it would be an orthogonal edit (Karpathy: Surgical Changes).
- Un-bolding more cross-references on the board. That is the workaround this task replaces.
- Any new hook, any change to `.claude/settings.json`.
- Making `Depends on` blocking. It is advisory by an explicit T017 decision; this task fixes *what the
  advisory computes*, never *whether it blocks*.

**Requirement Refs**: **N/A — `PRD.md` does not exist in this repo** (it is an artifact the kit
generates in downstream projects at Phase 0). Traceability is to the user request above and to the two
observed live instances, both named at file-and-line. Do not fabricate an FR-NNN.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (Supervisor, 2026-08-24)
- [x] Domain terms align with `PROJECT_SPEC.md` — no new term introduced
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] Requirement Refs recorded N/A with a written reason rather than fabricated

---

## Dependencies & Reachability

**Depends on**: `None`.

**Entry point**: `find_kanban_section` — called at `.claude/hooks/pre_agent_validate_guide.py:99`.

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | `find_kanban_section()` matches only a row's **own** ID — the match is anchored to the start of a list-item line, e.g. `^- \[[ x~]\] \*\*Txxx\*\*` — so a bold mention in another row's prose can never determine a section | "determined by the row that *is* that task" |
| 2 | Against the **live** board, `T091`, `T092`, `T093` resolve to `Todo` and `T090` to `Done`, with the two un-boldings from `30ae3d6`/`e7945eb` **restored to bold first** so the fix is proven against the shape that actually broke | "un-bolding is a workaround, not a fix" |
| 3 | `FIXTURE_KANBAN` gains a Done row that bold-references a Todo task; the fixture test asserts that Todo task still resolves to `Todo` | The hazard is absent from today's fixture |
| 4 | `test_find_kanban_section_on_real_current_board` iterates **every** `Txxx` that owns a row on the live board — not only `- [x]` ones — and asserts each resolves to the section it is actually in | The live-board test is blind to shadowed Todo rows by construction |
| 5 | The checkbox class in the anchor covers `[ ]`, `[x]` and `[~]`, since `### Closed` uses `[~]` (T081, T074, T072) | Observed board syntax |
| 6 | `### Closed` resolution is **decided and asserted**, not left incidental: either it returns `"Closed"` or it returns `None`, with a one-line rationale in the test's docstring | "undecided rather than designed" |
| 7 | `pre_bash_block_unsafe_merge.py` is **byte-identical to `main`** | Out of scope |
| 8 | A test asserts `tasks_in_section()`'s first-match-per-line property directly, so the reasoning that exempted the merge gate is pinned rather than trusted | Blast-radius investigation above |
| 9 | The `Depends on` advisory still emits its warning for a genuinely-not-Done dependency, and still emits the "not found anywhere" warning for an unknown ID | No regression in the one consumer |
| 10 | Full suite green: 719 baseline + new tests, 0 regressions | Hard-Stop Gate 5 |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | Live board, post-fix | `T090`→Done, `T091`/`T092`/`T093`→Todo | automated test |
| 2 | **M1 (load-bearing)** — re-bold `split out as T091` to `**T091**` in T090's Done row, then run the suite | **RED before the fix, GREEN after.** This is the only control that proves the fix addresses the real defect rather than the symptom the un-bolding hid. Run it in both directions and record both | automated test, run and reverted |
| 3 | **M2** — revert `find_kanban_section` to the unanchored `f"**{task_ref}**" in body` form, fixture and live tests unchanged | Both the new fixture test (AC3) and the widened live-board test (AC4) go **RED**. If either stays green it is not covering the defect | automated test, run and reverted |
| 4 | **M3** — move a Todo row into `### Done` on a fixture without changing its text | That task resolves `Done` — the fix must not over-anchor into ignoring real section moves | automated test |
| 5 | **M4** — a fixture `In Progress` row whose prose bold-references a Done task | `tasks_in_section("In Progress")` returns the row's **own** ID only (AC8) | automated test |
| 6 | **M5** — delete the `[~]` alternative from the anchor's checkbox class | The Closed-section assertion (AC6) goes RED | automated test, run and reverted |
| 7 | `git diff main -- .claude/hooks/pre_bash_block_unsafe_merge.py` | Empty output | command |

> Every mutation must be confirmed to have **landed** (`git diff --stat` non-empty, or `grep` the
> mutated string) **before** its RED/GREEN verdict is recorded. T083 had a control reported as
> non-reproducible when the `sed` had simply matched nothing, and this repo carries 6 recorded
> "a checkmark is a claim, not a fact" incidents. The Supervisor will independently re-run **M1 and M2**.

### Verification Command (exact, runnable)

```bash
python3 -m pytest .claude/hooks/tests/ tests/ -q
```

> Both paths. Bare `pytest tests/ -q` collects **8** tests, not 719 — the harness suite is under
> `.claude/hooks/tests/`, which pytest skips because `.claude` is hidden.

### Evidence (filled by reviewer at Stage 4/5)

> Filled at Stage 4/5 in `tasks/TASK_REVIEW_T093.md`, copied from `templates/TASK_REVIEW_template.md`.

---

## Demonstration

> See `tasks/TASK_REVIEW_T093.md`.

---

## Approach

**Pattern reference**: `.claude/hooks/pre_bash_block_unsafe_merge.py:279` (`tasks_in_section`) — the
function in this repo that already solves this exact problem correctly, by scoping to a line and taking
the first bold ID on it. Imitate its line-scoped discipline; do not copy its body.

**Vital slice**: the anchored regex in `find_kanban_section()`, plus the two test corrections (AC3
fixture hazard, AC4 widened iteration). Those three are the whole defect.

**Cut list** (cuts, not deferrals):
- No refactor to share one parser between the two hooks. They are ~10 lines each with different return
  shapes; a shared helper is the abstraction Simplicity First rejects, and it would couple a spawn-time
  advisory to a merge-time gate.
- No board linter forbidding bold cross-references. The fix makes them harmless; a linter would police
  a style that no longer matters.
- No change to the section search order. Anchoring makes order irrelevant for correct boards, and
  changing both at once means a failure cannot be attributed to either.
- No `Ready for Review` / `Blocked` / `Stage Tracker` handling beyond what exists.

**On AC2 — restore the bold before proving the fix.** The tempting shortcut is to run the new tests
against today's already-un-bolded board and call it green. That would prove nothing: the board no
longer contains the shape that broke. The un-boldings must be reverted, the failure reproduced, and
the fix shown to hold **with the cross-references bold**, which is also how the board will look again
the next time anyone writes a completion note.

---

## Edge Case Checklist

- [ ] A row's own ID is not always at a fixed offset — `- [ ] **T093** —` and `- [~] **T081** — *(SUPERSEDED…`
      differ. Anchor on the checkbox pattern, not a character count.
- [ ] `### Closed` sits **after** `## Blocked`/`## Stage Tracker` in file order but is still a `###`
      section; the existing `(?=^###|\Z)` lookahead stops at the next `###`, so verify the Closed body
      is captured as intended rather than assumed.
- [ ] A section heading appearing inside a row's prose (an inline `### quote`) already has two tests
      (`:91`, `:103`) — do not regress them; they exist because this parser has been broken this way
      before.
- [ ] `T999`/unknown IDs must still return `None`, and a missing or empty board must still return
      `None` (`:143`, `:148`).
- [ ] The live-board test widened by AC4 will fail loudly the next time a row is misfiled. That is the
      point, but confirm the failure message names the task and both sections, or a future maintainer
      will read it as flaky.
- [ ] Do not assume `- [x]` implies Done after this change — T081 is `- [~]` in Closed, and the
      existing test asserting "every `[x]` resolves to Done" must stay true.

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `.claude/hooks/pre_agent_validate_guide.py` | Anchor `find_kanban_section()`'s match to a row's own ID; decide Closed per AC6 |
| `.claude/hooks/tests/test_kanban_section_parsing.py` | Fixture gains the shadowing hazard (AC3); live-board test iterates every owning ID (AC4); Closed assertion (AC6); `tasks_in_section` first-match pin (AC8) |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.claude/hooks/pre_bash_block_unsafe_merge.py` | AC7 byte-identity. Investigated and found correct — editing it is an orthogonal change to a merge gate |
| `PROJECT_KANBAN.md` | Except the temporary M1 re-bold, which is a control and is reverted. The board is not the fix |
| `.claude/settings.json` | No hook wiring changes |
| `memory/*.md` | Supervisor-only writes (Memory Write Protocol) |

> If you believe one of these must change, **stop and report to the Supervisor** before touching it.
> T090's implementer touched a Must-NOT-Touch file for a defensible reason; the narrow form was
> accepted, but the acceptable path was disclosure first, not a good reason found afterwards.

---

## Test Plan

1. Restore the two un-boldings (`**T091**` in T090's row, `**T092**` in its completion note).
2. Widen the live-board test (AC4) and add the fixture hazard (AC3). Observe **RED**, with the failure
   naming a Todo task resolving as Done — this is the defect reproduced, and it must be seen before the
   fix, not after.
3. Anchor the regex. Observe GREEN.
4. Run M2–M5, confirming each mutation **landed** before recording its verdict, reverting each.
5. Decide and assert Closed (AC6) with the rationale in the docstring.
6. `python3 -m pytest .claude/hooks/tests/ tests/ -q` → 719 + new, 0 regressions.
7. `git diff main -- .claude/hooks/pre_bash_block_unsafe_merge.py` → empty.
8. Leave the cross-references **bold** in the final state. If the fix is right they are harmless, and
   leaving them bold is the standing regression witness.

---

## Completion Checklist

- [ ] Implementation done
- [ ] Self-review: `Skill({ skill: "code-review" })` run
- [ ] Security review: `Skill({ skill: "security-review" })` run — **mandatory, Medium risk**. Scope it
      manually to `main..<branch>`; the built-in diffs the checked-out branch against `origin/HEAD` and
      has pulled in unrelated work **8 times** in this repo (T071 record)
- [ ] Lint passes
- [ ] Tests written AND pass — output pasted into `tasks/TASK_REVIEW_T093.md`'s Evidence table (Hard-Stop Gate 5)
- [ ] UI/Design Evidence rows: **☐ N/A** — no UI component (UI/Design AC section deleted per Hard-Stop Gate 6)
- [ ] `Skill({ skill: "verify" })` run by the **user** — the Supervisor cannot run it
- [ ] `memory/MEMORY.md` updated by the Supervisor
- [ ] Supervisor notified: task ready for Stage 4 review

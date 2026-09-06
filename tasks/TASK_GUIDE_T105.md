# TASK_GUIDE — T105: Main's shellcheck gate is red, and one of its suppressions names a check that no longer fires
**Date**: 2026-09-06
**Complexity Level**: C1
**Risk Level**: Low
**Priority**: P0
**Assigned agent**: Common-Infrastructure-Agent
**Agent guide**: `agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

Before writing any code:
1. Read `PROJECT_SPEC.md`
2. Read `memory/MEMORY.md`
3. Read this file completely
4. Read `agents/common-infrastructure.md`
5. Note the **Complexity Level** above and apply the matching process from the Complexity matrix in your role guide.
6. C1 / two known files — `memory/codebase-map.md` is not required.

---

## Requirement (Pillar 1 — Adapt the requirement)

User request, 2026-09-06, verbatim:

> "the shellcheck install scripts on the main is fail, check and fix, supervisro"

**Restated intent**:
> CI's `Shellcheck install scripts` step exits 1 on `main`. Make that exact command exit 0 by
> correcting the four reported findings at their source, without weakening the gate and without
> changing what any of the scripts actually do.

**Measured baseline** (Supervisor, shellcheck 0.11.0, CI's exact argument list):

```
scripts/smoke-install.sh:36            SC2329 (info)  cleanup() is never invoked
tests/test_harness_projection.sh:299   SC2181 (style) check exit code directly, not $?
tests/test_harness_projection.sh:385   SC2012 (info)  use find instead of ls
tests/test_harness_projection.sh:386   SC2012 (info)  use find instead of ls
EXIT=1
```

Shellcheck exits 1 on info/style severity, so all four are gate-failing even though none is a
warning or error.

**Root cause, per finding — read this before touching anything:**

- `scripts/smoke-install.sh:35` **already carries** `# shellcheck disable=SC2317` with the comment
  "cleanup is invoked indirectly via the EXIT trap". That reasoning is still correct; the code is
  not. Shellcheck split the trap-invoked-function case out of SC2317 into the newer **SC2329**, so
  the directive now suppresses a check that no longer fires and the live one lands unsuppressed.
  Nothing in this repo changed — the apt shellcheck in `ubuntu-latest` rolled forward under it.
- SC2181 and SC2012 are long-standing checks against `tests/test_harness_projection.sh`, last
  touched 2026-08-31 (T097). That half has plausibly been red since then. **Unconfirmed**: `gh` is
  not authenticated in the Supervisor's environment, so CI run history was not read. Do not repeat
  this as measured fact.

**Out of scope**:
- Pinning the shellcheck version in `.github/workflows/ci.yml`. Explicitly decided by the user on
  2026-09-06: keep CI on apt's shellcheck so new checks keep surfacing, accepting that a future
  roll-forward can break `main` the same way. Do not touch `ci.yml`.
- The other 16 `*.sh` files in the repo. CI lints exactly five; widening the argument list is a
  different task.
- Any behavioural change to `smoke-install.sh` or `test_harness_projection.sh`. This task changes
  how the code reads to a linter, never what it does.

**Requirement Refs**: `None — corrective maintenance on the CI gate, not a PRD feature.`

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (Supervisor; baseline reproduced locally before writing this guide)
- [x] Domain terms align with `PROJECT_SPEC.md` — no new terminology introduced
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] Requirement Refs: none claimed, so nothing to verify in `PRD.md`

---

## Dependencies & Reachability

**Depends on**: `None`

**Entry point**: `shellcheck -x setup.sh update.sh scripts/validate.sh scripts/smoke-install.sh tests/test_harness_projection.sh`
> The literal command in `.github/workflows/ci.yml:19`. This task's whole surface is that line's exit code.

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | CI's exact shellcheck command exits 0 with no output on all five files | "make that exact command exit 0" |
| 2 | `scripts/smoke-install.sh`'s trap-cleanup suppression names the code that actually fires, and keeps a comment stating why the function is reachable | root cause 1 — the stale `SC2317` directive |
| 3 | `tests/test_harness_projection.sh:299` checks the command's outcome directly rather than via `$?`, and the AC6 empty-`--harness` assertions still pass and still fail on a regression | root cause 2 — SC2181 without weakening the test |
| 4 | The two `ls -1` comparisons no longer trip SC2012, and AC9 still compares the same two sets in the same sorted order | root cause 3 — SC2012 without changing what AC9 asserts |
| 5 | `bash tests/test_harness_projection.sh` and `sh scripts/smoke-install.sh` both still pass — no behavioural change | "without changing what any of the scripts actually do" |
| 6 | No finding is silenced by a blanket file-level `disable`, a `--severity` raise, or removal of a file from the lint list | "without weakening the gate" |

---

## Evaluation & Acceptance

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | shellcheck 0.11.0, CI's five-file argument list | exit 0, empty stdout | automated test (`tests/test_shellcheck_clean.sh`) |
| 2 | shellcheck absent from PATH | exit non-zero with an explicit "cannot verify" message — never a silent skip-as-pass | automated test |
| 3 | `bash tests/test_harness_projection.sh` after the edits | same pass/fail summary as before the change | automated test |
| 4 | `sh scripts/smoke-install.sh` after the edits | passes; temp target still removed on exit | automated test |

> **Oracle authorship (Gate 5)**: the Supervisor specifies the oracle above; the agent writes
> `tests/test_shellcheck_clean.sh` to it. Success Criterion 2 is not optional — a test that
> silently passes when its tool is missing is the "invisible off switch" failure already recorded
> in `memory/learnings.md`. Make absence loud.

### Verification Command (exact, runnable)

```bash
bash tests/test_shellcheck_clean.sh \
  && bash tests/test_harness_projection.sh \
  && sh scripts/smoke-install.sh
```

### Evidence (filled by reviewer at Stage 4/5)

> Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T105.md`, copied from
> `templates/TASK_REVIEW_template.md`. Not done until every row has pasted output.

---

## Demonstration

> See `tasks/TASK_REVIEW_T105.md`.

---

## Approach

**Pattern reference**: `scripts/smoke-install.sh:35` — a targeted, single-code `# shellcheck disable=` carrying a
one-line comment that states *why* the code is a false positive here. That is this repo's existing
convention for a justified suppression; imitate its shape, and note that its content is precisely
what has gone stale.

**Vital slice**: `None — four findings and one oracle is the whole surface.`

**Cut list**: `None — nothing was cut.`

Fix each finding at the level it actually occurs, preferring a real code change where one is
clean and a narrow justified suppression only where the linter is genuinely wrong:

1. **SC2329** — the linter is wrong; `cleanup` is reachable via `trap ... EXIT`. Keep a suppression,
   but make it name the code that fires. Prefer keeping both codes on the directive
   (`disable=SC2317,SC2329`) so the line stays correct across shellcheck versions, and update the
   comment to say the same thing.
2. **SC2181** — the linter is right. `run_setup` is called in an if/else and its status then read
   from `$?`. Restructure so the outcome is captured at the call (assign the status to a variable
   in each branch, or invert so the command is tested directly). Do not change which condition
   counts as pass and which as fail — AC6 asserts a *non-zero* exit is correct behaviour.
3. **SC2012 (×2)** — the linter is technically right and the fix is cheap. These list skill
   directory names under a fixture. Either replace with a `find`-based listing that yields the same
   newline-separated, `LC_ALL=C`-sorted basenames, or keep `ls -1` behind a narrow per-line
   `disable=SC2012` justified by the fact that the names are repo-controlled skill slugs. Prefer the
   `find` rewrite; if it changes the sorted output in any way, fall back to the justified
   suppression and say so in the review.

Then write `tests/test_shellcheck_clean.sh` as the local mirror of the CI step. Do **not** add it as
a new CI step — CI already runs shellcheck directly, and a second step asserting the same thing is
duplication.

---

## Edge Case Checklist

- [ ] The `find` rewrite must produce **basenames**, not paths — `ls -1` inside a `cd` yields bare names; a naive `find` yields `./name`. AC9 compares two such listings against each other, so a path-prefix change on one side silently breaks the comparison.
- [ ] `find` recurses by default; the originals list one level. Bound the depth or AC9 will compare a tree against a flat list.
- [ ] The `grep -v '^oversize-skill$'` filter anchors on a bare name; it stops matching if the listing gains a prefix.
- [ ] `LC_ALL=C sort` ordering must survive the rewrite — `find` does not sort.
- [ ] SC2181's restructure must not swallow a non-zero status under `set -e`, and must keep the two `--harness` empty forms distinguishable in the failure message.
- [ ] `tests/test_shellcheck_clean.sh` must not itself trip shellcheck if it is ever added to the lint list.
- [ ] Removing a finding by deleting the code that triggers it is not a fix — the AC6 and AC9 assertions must still be present and still meaningful afterward.

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `scripts/smoke-install.sh` | Correct the stale `SC2317` directive at line 35 to cover `SC2329`; update its comment |
| `tests/test_harness_projection.sh` | Line 299: check `run_setup`'s outcome directly. Lines 385–386: remove the SC2012 trigger without changing AC9's comparison |
| `tests/test_shellcheck_clean.sh` | **New.** Runs CI's exact shellcheck command, asserts exit 0, fails loudly if shellcheck is absent |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `.github/workflows/ci.yml` | Version pinning explicitly ruled out by the user; the lint argument list must stay exactly as-is so AC1 measures the real gate |
| `setup.sh`, `update.sh`, `scripts/validate.sh` | In the lint list and already clean — no reason to edit them |
| `PROJECT_KANBAN.md` | Supervisor-owned. An agent editing the board is the self-certification failure recorded for T102/T104 |

---

## Test Plan

1. Establish the red baseline: run the Verification Command's first line before any edit and confirm it fails with the four findings above.
2. Fix the findings one at a time, re-running shellcheck after each so every edit is attributable.
3. Run `bash tests/test_harness_projection.sh` and compare its pass/fail summary against a pre-change run — the counts must be identical.
4. Run `sh scripts/smoke-install.sh` and confirm it still passes and still cleans up its temp target.
5. Paste real output — not a summary of it — into `tasks/TASK_REVIEW_T105.md`.

---

## Completion Checklist

- [ ] Implementation done
- [ ] Self-review: `Skill({ skill: "code-review" })` run
- [ ] Security review — N/A (Low risk, no product code, no data handling)
- [ ] Lint passes (this task *is* the lint gate)
- [ ] Tests written AND pass — output pasted into `tasks/TASK_REVIEW_T105.md`'s Evidence table (Hard-Stop Gate 5)
- [ ] UI/Design Evidence rows marked ☐ N/A — pure shell/CI task, no UI component (Hard-Stop Gate 6)
- [ ] `Skill({ skill: "verify" })` run — user-invoked
- [ ] `memory/MEMORY.md` updated (if new patterns learned)
- [ ] Supervisor notified: task ready for Stage 4 review

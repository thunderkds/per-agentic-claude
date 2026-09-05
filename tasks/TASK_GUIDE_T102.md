# TASK_GUIDE — T102: The v2 baseline is red and the board says it is green

**Date**: 2026-09-05
**Complexity Level**: C1
**Risk Level**: Low
**Priority**: P1
**Assigned agent**: Common-Infrastructure-Agent
**Agent guide**: `agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

Before writing any code:
1. Read `PROJECT_SPEC.md`
2. Read `memory/MEMORY.md`
3. Read this file completely
4. Read `agents/common-infrastructure.md`
5. C1 — apply the C1 row of the Complexity matrix in your role guide.
6. Not required (C1, four known files): `memory/codebase-map.md`

---

## Requirement (Pillar 1 — Adapt the requirement)

From `PROJECT_KANBAN.md` T102, registered 2026-09-04 out of T101's Stage 4 and Stage 5: a clean
`v2` checkout returns `6 failed, 837 passed`, while the board's Todo session-handoff note dated
2026-08-31 still asserts *"v2 is clean and green"*. Four halves, found together, all falsifying the
same board claim.

**Restated intent**:
> Make the `v2` baseline actually green and make every place that describes that baseline — the
> handoff note and the site footer — state what is true, so the next session's baseline check is
> against a board that is not lying to it.

**Out of scope** (explicitly NOT this task):
- Half (a), the `memory/MEMORY.md` hot-tier budget breach. It is fixed by `/compact-memory`, which
  is **user-invocable only**, and `compact-memory`'s own rule is *move syntheses down, never shorten
  them*. The Supervisor must not silently shrink entries. The user runs it; this task inherits the
  result. **Decided with the user 2026-09-05.**
- Re-slimming `README.md` or moving T097's `--harness` block to the site. **The user chose to raise
  the cap** (see AC1) — do not relitigate, and do not delete README content to "help".
- T085's still-open finding that `[site](site/index.html)` does not render on GitHub.
- Any content change to `site/index.html` beyond the two footer directory names.

**Requirement Refs**: none — this is a board-and-baseline correctness task, not a PRD feature.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the KANBAN row and the user's 2026-09-05 decisions (Supervisor)
- [x] Domain terms align with `PROJECT_SPEC.md` — "hot tier", "canon", "drift test" all used as defined
- [x] Every Acceptance Criterion traces to a lettered half of the T102 row
- [x] No `PRD.md` refs claimed

---

## Dependencies & Reachability

**Depends on**: User-run `/compact-memory` — the 5 hot-tier failures cannot go green without it.
AC6 (whole suite green) is blocked until it has run; AC1–AC5 are not.

**Entry point**: `test_readme_is_at_most_60_lines` — the failing test whose rename is the task's
most grep-able artifact. Also `tests/test_site_content.py` and `PROJECT_KANBAN.md` line 14.

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | `tests/test_readme_slim.py`'s line cap is **75**, and the test's name states 75 rather than 60 (a test named `..._at_most_60_lines` that asserts 75 is a lie in the name). `README.md` is unmodified — `git diff --stat` lists no `README.md` | (b), user's decision |
| 2 | The other four tests in `test_readme_slim.py` are byte-unchanged | (b), Surgical Changes |
| 3 | The Todo session-handoff note in `PROJECT_KANBAN.md` no longer claims v2 is "clean and green" with the stale 707/40/41 counts; it states the measured post-task result and the date it was measured | (c) |
| 4 | `site/index.html`'s footer names the directories `tests/test_site_content.py` actually resolves — plain-root `agents/` and `skills/`, not `.claude/` | (d) |
| 5 | A new drift test asserts the footer's claimed directories **derived from `test_site_content.py`'s own `AGENTS_DIR`/`SKILLS_DIR` at test time**, not hardcoded. A hardcoded literal is the vacuous-assertion shape this repo has hit ten times — it must re-trip automatically if the canon moves again | (d), T101 M3 pattern |
| 6 | `python3 -m pytest tests/ .claude/hooks/tests/ -q` → **0 failed**, after the user's `/compact-memory` | (a)+(b), the board claim itself |
| 7 | No pre-existing test is modified except `test_readme_slim.py`'s cap test (AC1) | Surgical Changes |

---

## Evaluation & Acceptance

### Success Criteria (observable, pass/fail)

| # | Given | Expect | How it's checked |
|---|-------|--------|------------------|
| 1 | `README.md` at its current 73 lines | The cap test passes | automated test |
| 2 | **Mutation control M1** — append 3 filler lines to `README.md` (→76) | The cap test goes **RED** naming 76 > 75 | automated, must be observed RED then reverted |
| 3 | **Mutation control M2** — edit the footer to say `.claude/` again | The new AC5 drift test goes **RED** | automated, must be observed RED then reverted |
| 4 | **Mutation control M3** — change `AGENTS_DIR` in `test_site_content.py` to `ROOT/.claude/agents` | The AC5 test goes **RED** *without the footer changing*, proving it reads the source and not a literal | automated, must be observed RED then reverted |
| 5 | The handoff note after the edit | Contains no "clean and green" claim and no `707`/`40`/`41` counts | `grep` |

> M3 is the load-bearing one. M2 alone passes on a test that hardcodes `agents/`; only M3
> distinguishes a derived assertion from a literal one.

### Verification Command (exact, runnable)

```bash
cd "$(git rev-parse --show-toplevel)" && \
python3 -m pytest tests/ .claude/hooks/tests/ -q 2>&1 | tail -3 && \
echo "--- AC1 cap ---" && grep -n "75" tests/test_readme_slim.py && wc -l README.md && \
echo "--- AC3 handoff ---" && grep -c "clean and green" PROJECT_KANBAN.md && \
echo "--- AC4 footer ---" && sed -n '560,564p' site/index.html && \
echo "--- AC7 scope ---" && git diff --name-only
```

### Evidence

> Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T102.md`.

---

## Approach

**Pattern reference**: `tests/test_site_content.py` — T101's three drift tests derive expected
values from source at test time (`VALID_HARNESSES`, the cap in `lib/harness-fetch.sh`, on-disk
`SKILL.md` sizes). AC5's test belongs in that file and must be built the same way: import or
re-resolve `AGENTS_DIR`/`SKILLS_DIR`, then assert the footer names the basenames those paths yield.

**Vital slice**: AC5's derived footer test — it is the only new *guard*; everything else is a
one-value correction that stays correct on its own.

**Cut list**:
- No test for the handoff note's content. A prose note is edited by humans each session; pinning
  it would fail on every legitimate handoff.
- No sweep of the other `60`-line mentions in historical `tasks/TASK_GUIDE_T085.md` and the review
  files — those record what was true when written and are the audit trail. Only the live test moves.

**Why raise the cap rather than re-slim** (user's decision, recorded so it is not relitigated):
T085 slimmed the README to 55 lines; T097's `--harness` documentation is what pushed it to 73. That
is a real feature earning real space, so the 60 was the stale value, not the content. 75 gives two
lines of headroom over today's 73 — deliberately tight, because a cap with slack stops being a cap.

---

## Edge Case Checklist

- [ ] The cap test's **name** is part of the fix. Leaving `test_readme_is_at_most_60_lines` while
      changing the constant to 75 produces a test whose name misstates what it enforces — the exact
      class of defect (c) exists to fix.
- [ ] Do not renumber or reflow `README.md` while "checking" the count — AC1 requires it untouched.
- [ ] The footer sentence appears once (`site/index.html:562-563`) and wraps across two lines;
      a single-line `grep`/`sed` replacement will miss it.
- [ ] `test_site_content.py` may already assert on footer text for the `v1 release` string T101
      locked (AC8 of T101). Do not disturb that assertion.
- [ ] AC6 will still show 5 failures if `/compact-memory` has not been run. Report that as
      **blocked on the user**, never as a pass, and never by editing `memory/MEMORY.md` to fit.

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `tests/test_readme_slim.py` | Cap 60 → 75; rename the test to match; assertion message updated |
| `site/index.html` | Footer: `.claude/` → the plain-root `agents/` and `skills/` canon (2 lines) |
| `tests/test_site_content.py` | **New test** — footer directories derived from `AGENTS_DIR`/`SKILLS_DIR` |
| `PROJECT_KANBAN.md` | Handoff note corrected; T102 row updated through the stages |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `README.md` | AC1 — the cap moves, the content does not |
| `memory/MEMORY.md` | Half (a) is the user's `/compact-memory`, not a silent shrink |
| `tasks/TASK_GUIDE_T085.md`, `tasks/TASK_REVIEW_T*.md` | Audit trail — they record what was true when written |
| The `v1 release` footer string and the `/main/setup.sh` install URL | T101 AC8 scope locks, still in force |

---

## Test Plan

1. Capture the baseline first: `pytest tests/ .claude/hooks/tests/ -q | tail -3` → expect
   `6 failed, 837 passed`. Paste it. A task about a mis-stated baseline may not start by assuming one.
2. AC1/AC2: change the cap, run `pytest tests/test_readme_slim.py -q` → 5 passed.
3. Run M1, observe RED, paste, revert.
4. AC4/AC5: fix the footer, write the derived test, run M2 and M3, observe both RED, paste, revert.
5. AC3: correct the handoff note.
6. AC6: full suite. If only the 5 hot-tier failures remain, stop and report **blocked on
   `/compact-memory`** — do not touch `memory/MEMORY.md`.

---

## Completion Checklist

- [ ] Implementation done
- [ ] `Skill({ skill: "code-review" })` run
- [ ] security-review — N/A (Low risk; test constants, one HTML footer, one board note; no runtime path)
- [ ] Tests written AND pass — output pasted into `tasks/TASK_REVIEW_T102.md` (Hard-Stop Gate 5)
- [ ] M1/M2/M3 each observed RED and pasted (a new test never seen RED is not evidence)
- [ ] `Skill({ skill: "verify" })` run by the user
- [ ] `memory/MEMORY.md` updated
- [ ] Supervisor notified: ready for Stage 4

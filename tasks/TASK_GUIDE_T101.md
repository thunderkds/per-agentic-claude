# TASK_GUIDE — T101: Reconcile README and site with what v2 actually shipped
**Date**: 2026-09-04
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
5. Note the **Complexity Level** above and apply the matching process from the Complexity matrix in your role guide
6. C1 task, but it spans two documentation surfaces plus a test file — read `docs/ddr/0007-canonical-skills-and-agents-at-plain-root.md` and `docs/claude-md/folder-structure.md` before editing, because they are the authority for the facts you are correcting

---

## Requirement (Pillar 1 — Adapt the requirement)

User request, 2026-09-04, verbatim intent:
> "checking all update from v2 branch with the main, update the README, the site also, for the
> information update if any"

**Restated intent** (Supervisor's interpretation):
> `main..v2` is 90 commits (T094–T100) and `main` is 0 behind. Three of those tasks changed
> user-facing behaviour. The Install and Update-flow sections of the site already document T097
> correctly. Four other places still describe the pre-T096/T097 world and are now factually wrong
> or materially incomplete. Correct exactly those four, and add drift tests so the same four
> cannot silently re-rot — `tests/test_site_content.py` did not catch any of them.

**Scope decisions locked by the user at Stage 2** (do not re-litigate):
- Document the v2 code **as it is**. Do **not** change the `curl` install URL — it points at
  `main` deliberately, because `main` is the user's live v1 install. Retargeting the installer is a
  release decision, not a docs fix.
- Leave the site footer's `v1 release` string alone, for the same reason.
- One task, not split per-surface.

**Out of scope** (explicitly NOT this task):
- Changing any install URL, or the footer release label (user decision above).
- The pre-existing T085 finding that `[site](site/index.html)` links do not render on GitHub. Real,
  recorded, release-blocking, and **not** this task — it needs a deployed URL, which is operator work.
- Any change to `setup.sh`, `update.sh`, `MANIFEST`, or hook code. This task documents shipped
  behaviour; it does not alter it.
- Documenting T098/T099/T100. They changed no user-facing doc surface (update.sh harness detection,
  hook quoted-span classification, the Response Standard). Verified, not assumed.

**Requirement Refs**: none — this is corrective documentation against merged tasks
(T096/DDR-0007, T097), not a new PRD feature.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (Supervisor; scope questions answered by the user 2026-09-04)
- [x] Domain terms align with the project's language — "canon", "projection", "harness" all used as DDR-0007 and T097 define them
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] Requirement Refs: N/A, recorded above with reason

---

## Dependencies & Reachability

**Depends on**: None — T096 and T097 are both merged into `v2`; this documents them after the fact.

**Entry point**: `Repository layout` — the site section id/heading whose table carries the wrong
canon paths. Grep-able in `site/index.html`.

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | The site's `Repository layout` table lists `skills/` and `agents/` at plain root as the canonical locations, and states that `.claude/skills` and `.claude/agents` are **relative symlinks** onto them | F1 — T096/DDR-0007 |
| 2 | The word `symlink` appears on the site page at least once (it appears **0** times today) | F1 |
| 3 | The site's `Options` table contains a `--harness` row naming the valid values `claude` and `codex` | F2 — T097 |
| 4 | The site's `Providers` section states that Codex executes kit skills by name, and names the **8 KB body cap** and the four skills skipped by it (`bugfix`, `craft-spawn-prompt`, `diagnose`, `write-better-skill`) | F3 — T097 |
| 5 | The site's `Providers` section no longer claims non-Claude providers get no Skill tooling at all; the remaining gap is stated accurately (hooks, `Agent()` spawns, and the review/verify/ship skills built on them stay Claude-only) | F3 |
| 6 | `README.md` line 11 references `agents/general-agent-template.md` (canon), not `.claude/agents/...` | F4 |
| 7 | New tests in `tests/test_site_content.py` fail if AC1, AC3, or AC4's facts are removed from the page | drift-proofing |
| 8 | The `curl` install URL in both `README.md` and `site/index.html` still contains `/main/setup.sh`, byte-unchanged; the footer still reads `v1 release` | user scope lock |
| 9 | No file outside the four in *Files to Change* is modified | Surgical Changes |

---

## Evaluation & Acceptance

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | The edited `site/index.html` | `grep -c 'symlink'` ≥ 1; `grep -c '8 KB'` ≥ 1 | automated test |
| 2 | The edited page's Options table | contains a row whose first cell is `--harness` | automated test |
| 3 | **Mutation control M1** — delete the `skills/` plain-root row from the layout table | the new AC1 test goes **RED**; restore, GREEN | manual, re-run by Supervisor at Stage 4 |
| 4 | **Mutation control M2** — delete the `8 KB` sentence from Providers | the new AC4 test goes **RED**; restore, GREEN | manual, re-run by Supervisor at Stage 4 |
| 5 | Whole suite after the change | all pre-existing `tests/` and `.claude/hooks/tests/` pass; **zero** pre-existing tests modified | automated test |
| 6 | `git diff --stat main..HEAD -- README.md site/index.html` after edit | install URL lines unchanged (AC8) | manual grep |

> **M1 and M2 are mandatory, not optional.** This repo has now recorded a double-digit count of
> assertions that were satisfied by a page that never contained the fact in the first place. A new
> test that has never been observed RED is not evidence. Paste both transitions.

### Verification Command (exact, runnable)

```bash
cd "$(git rev-parse --show-toplevel)" && \
  python3 -m pytest tests/ .claude/hooks/tests/ -q 2>&1 | tail -5 && \
  echo "--- AC8 scope lock ---" && \
  grep -c '/main/setup.sh' README.md site/index.html && \
  grep -c 'v1 release' site/index.html
```

### Evidence (filled by reviewer at Stage 4/5)

> Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T101.md`, copied from
> `templates/TASK_REVIEW_template.md`.

---

## Demonstration

> See `tasks/TASK_REVIEW_T101.md`.

---

## UI / Design Acceptance Criteria

> `site/index.html` is a rendered page, so this section stays. The change is **content-only** —
> new table rows and prose inside existing components. No new component, no token change, no
> layout system change. Verify that and nothing more; do not redesign anything.

### 1. Visual Regression

| Screen / Component | Verification method | Expected result |
|-------------------|---------------------|-----------------|
| `Repository layout` table | Open the page in a browser; compare against the pre-change render | Two added rows adopt the existing table styling; no column overflow, no horizontal scroll on the page body |
| `Options` table | Same | Added `--harness` row matches sibling rows exactly |

### 2. Design-System Compliance

| Criterion | Verification method | Expected result |
|-----------|---------------------|-----------------|
| Colors match existing tokens | No new CSS; reuse existing table/`<code>` classes | Zero new CSS rules added — assert by diffing the `<style>` block |
| Typography matches spec | Inherited from existing table markup | No inline `style=` attributes introduced |
| Spacing / layout matches spec | Inherited | No change to the `<style>` block |

### 3. Layout / Responsiveness

| Viewport | Verification method | Expected result |
|----------|---------------------|-----------------|
| Mobile (320–480px) | Browser devtools at 375px | Tables remain readable within their existing overflow container; page body does not scroll horizontally |
| Tablet (768px) | Devtools | Nav collapse behaviour unchanged |
| Desktop (1024px+) | Devtools | Unchanged from pre-edit render apart from the added rows |

> `test_no_external_assets` already guards asset loading — do not add any image, font, or CDN
> reference to satisfy any row above.

---

## Approach

**Pattern reference**: `tests/test_site_content.py` — specifically `_word_present()` and
`test_every_wired_hook_appears_in_hook_table()`. Imitate them exactly: exact-token presence checks
rather than naive substring matching, and where possible derive the expected value **from the
source of truth at test time** rather than hardcoding it in the test.

For AC4's four skipped skills, prefer deriving the list from the real cap rather than pasting four
names into the test: `setup.sh`/`MANIFEST` carry the Codex projection rule, and the cap is a real
number applied to real files. If deriving it proves fragile, hardcoding is acceptable **only** with
a one-line comment saying why — a hardcoded list that drifts is exactly the failure this task exists
to fix.

**Vital slice**: the four factual corrections (F1–F4) plus the three tests that pin them.

**Cut list**:
- No rewrite of the Providers section's prose beyond the two sentences that are wrong.
- No new site section for T096; the existing layout table is the right home.
- No test for AC6 (the README canon path) — `scripts/test-claude-md-refs.sh` already validates
  referenced paths resolve; adding a second checker would be this repo's second instrument for one
  fact. Check that the existing script still passes instead.

**Reasoning.** All four findings share one root cause: `tests/test_site_content.py` drift-tests
*rosters* (skills, agents, hooks, packs — all currently correct) but nothing about paths, options,
or provider capability. So the roster tests stayed green through T096 and T097 while the surrounding
prose went stale. Fixing the text without extending the test surface would leave the same hole open
for T101's own corrections.

---

## Edge Case Checklist

- [ ] `test_readme_promised_topics_are_on_the_page()` couples README wording to site content — changing README line 11 or any site heading may trip it. Run it before assuming your edit is isolated.
- [ ] `test_every_nav_link_resolves_to_a_section_id()` and `test_every_section_has_a_nav_link()` are bidirectional. If you add a section (you should not need to), you must add a nav link.
- [ ] The layout table currently has no `skills/`/`agents/` rows at all — this is an **addition plus a correction**, not a find-and-replace. Blindly rewriting `.claude/skills/` → `skills/` would lose the fact that the symlink exists and is load-bearing.
- [ ] `.claude/skills` and `.claude/agents` are **relative** (`-> ../skills`). CLAUDE.md calls absolutising them a violation. Do not describe them as absolute or as copies.
- [ ] Codex gets **no** agent guides — `MANIFEST:25` says so explicitly (`agents` has no `codex=` pair). Do not imply Codex receives the agent roster.
- [ ] HTML-escape anything you add: the page uses `&lt;name&gt;` for angle brackets in the Options table.
- [ ] Do not "fix" the `site/index.html` links or the footer while you are in the file. Both are explicitly out of scope and AC8 tests for it.

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `site/index.html` | Layout table: add `skills/` + `agents/` canon rows, correct the two `.claude/*` rows to name them as relative symlinks. Options table: add `--harness` row. Providers: correct the Codex capability claim, add the 8 KB cap and the four skipped skills. |
| `README.md` | Line 11: `.claude/agents/general-agent-template.md` → `agents/general-agent-template.md` |
| `tests/test_site_content.py` | Three new drift tests pinning AC1, AC3, AC4 |
| `tasks/TASK_REVIEW_T101.md` | New, from `templates/TASK_REVIEW_template.md` |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `setup.sh`, `update.sh`, `MANIFEST` | This task documents shipped behaviour; changing it would invalidate the docs being written |
| `lib/harness-fetch.sh`, any `.claude/hooks/**` | Out of scope; no hook behaviour is in question |
| `CLAUDE.md`, `docs/claude-md/folder-structure.md`, `docs/ddr/0007-*.md` | These are the **source of truth** you are correcting the site *against*. If you believe one of them is wrong, STOP and tell the Supervisor — do not edit it to match the site |
| Any existing test in `tests/` or `.claude/hooks/tests/` | AC7 adds tests; modifying an existing one to pass is the failure mode, not the fix |
| `PROJECT_KANBAN.md` | Supervisor-owned |

---

## Test Plan

1. Run the full suite first and record the **baseline** count. Do not skip this — every "+N new
   tests, 0 regressions" claim in this repo is only meaningful against a recorded baseline.
2. Write the three new tests **first** and watch them fail against the current page (they must,
   since the facts are absent — this is the natural red phase, and it is free evidence).
3. Make the four content corrections. Tests go green.
4. Run M1 and M2. Paste both RED transitions and the restore.
5. Re-run the full suite plus `scripts/validate.sh` and `scripts/test-claude-md-refs.sh`.
6. Open `site/index.html` in a browser at 375px and 1280px for the UI rows above.

---

## Completion Checklist

- [ ] Implementation done
- [ ] Self-review: `Skill({ skill: "code-review" })` run
- [ ] Security review: N/A — Low risk, documentation and test-only, no runtime path touched (record this reason, do not leave the row blank)
- [ ] Lint passes (`scripts/validate.sh`)
- [ ] Tests written AND pass — output pasted into `tasks/TASK_REVIEW_T101.md`'s Evidence table (Hard-Stop Gate 5)
- [ ] M1 and M2 mutation controls observed RED and restored, both pasted
- [ ] UI/Design Evidence rows filled (Hard-Stop Gate 6) — content-only change, but all three rows need a result or a justified N/A
- [ ] `Skill({ skill: "verify" })` — **user-run only**; ask the Supervisor to request it
- [ ] Supervisor notified: task ready for Stage 4 review

# TASK_GUIDE — T104: The site advertises v1 on the eve of a v2.0.0 release

**Date**: 2026-09-05
**Complexity Level**: C0
**Risk Level**: Low
**Priority**: P0 (blocks the v2.0.0 release)
**Assigned agent**: Common-Infrastructure-Agent
**Agent guide**: `agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

1. Read `PROJECT_SPEC.md`
2. Read `memory/MEMORY.md`
3. Read this file completely
4. Read `agents/common-infrastructure.md`
5. C0 — smallest correct change, no brainstorm, no decomposition.

---

## Requirement (Pillar 1 — Adapt the requirement)

The `ship` pass for v2.0.0 found `site/index.html` still calls itself v1 in two places. T101
deliberately left these alone, recording them as a **release decision** rather than a docs fix. The
user made that decision on 2026-09-05: update them.

**Restated intent**:
> The public page must name the release it actually ships with, and a test must derive that version
> from the release record so the next release cannot leave the page behind again.

**Out of scope**:
- Any other content on the page. Two version strings and one new test, nothing else.
- The `curl` install URL (`/main/setup.sh`) — still correct, still T101's scope lock.
- Creating a `VERSION` file or any new version-tracking mechanism. `RUNBOOK.md`'s Release Log is
  already the record; use it, do not invent a second source of truth.

### Requirement Fidelity Gate

- [x] Restated intent confirmed against the user's 2026-09-05 decision (Supervisor)
- [x] Every AC traces to that decision
- [x] No `PRD.md` refs claimed

---

## Dependencies & Reachability

**Depends on**: None. `RUNBOOK.md`'s `v2.0.0` row already exists (commit `b955654`).

**Entry point**: `site/index.html` line 180 (`supervisor kit &middot; v1`) and line 562
(`personal-agentic-claude — v1 release`).

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to |
|---|----------------------|-----------|
| 1 | `site/index.html:180` names the shipping version, not `v1` | the decision |
| 2 | `site/index.html:562`'s footer names the shipping version, not `v1 release` | the decision |
| 3 | A new test asserts both strings match the **newest version in `RUNBOOK.md`'s Release Log table**, parsed at test time — never a hardcoded `v2.0.0` literal | recurrence guard |
| 4 | The footer's existing claim about `agents/`/`skills/` (T102 AC4) is unchanged and its test still passes | Surgical Changes |
| 5 | The `curl` install URL is byte-unchanged in `site/index.html` and `README.md` | T101 AC8 scope lock |
| 6 | Full suite green: `python3 -m pytest tests/ .claude/hooks/tests/ -q` → 0 failed | Gate 5 |

---

## Evaluation & Acceptance

### Success Criteria

| # | Given | Expect | How checked |
|---|-------|--------|-------------|
| 1 | The page after the edit | AC3's test passes | automated |
| 2 | **M1** — add a `v2.1.0` row to `RUNBOOK.md`'s Release Log, page untouched | AC3's test goes **RED** naming v2.1.0 | automated, must be observed RED then reverted |
| 3 | **M2** — revert one of the two page strings to `v1`, RUNBOOK untouched | AC3's test goes **RED** | automated, observed RED then reverted |

> **M1 is load-bearing.** M2 alone passes on a test that hardcodes `v2.0.0`. Only M1 proves the
> expected value is parsed from the Release Log at test time. A test never observed RED is not
> evidence — and in T102 the equivalent control was lost once and shipped vacuous.

### Verification Command

```bash
cd "$(git rev-parse --show-toplevel)" && \
python3 -m pytest tests/ .claude/hooks/tests/ -q 2>&1 | tail -3 && \
echo "--- AC1/AC2 ---" && grep -n 'supervisor kit' site/index.html && sed -n '560,564p' site/index.html && \
echo "--- AC5 lock ---" && grep -c '/main/setup.sh' site/index.html README.md && \
echo "--- scope ---" && git diff --name-only
```

### Evidence

> Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T104.md`.

---

## UI / Design Acceptance Criteria

### 1. Visual Regression

| Screen / Component | Verification method | Expected result |
|---|---|---|
| Sidebar version badge + page footer | headless Chrome DOM capture at 1280px, compared against the pre-change capture | only the version text differs; no layout shift |

### 2. Design-System Compliance

| Criterion | Verification method | Expected result |
|---|---|---|
| Colors / typography / spacing | none needed — text content only, inheriting existing styles | no token, font or spacing change in the diff |

### 3. Layout / Responsiveness

| Viewport | Verification method | Expected result |
|---|---|---|
| Mobile (375px) | headless Chrome, check the badge and footer do not wrap or overflow | no horizontal overflow |
| Desktop (1280px) | headless Chrome DOM + screenshot | badge and footer render on one line each |

> `v2.0.0` is 2 characters longer than `v1`; the responsiveness row is the reason that matters.

---

## Approach

**Pattern reference**: `tests/test_site_content.py`'s
`test_footer_names_the_directories_it_is_actually_drift_tested_against` (T102) and
`test_readme_step_limit_default_matches_hook_source` (T085) — both derive the expected value from a
live source at test time rather than hardcoding it. AC3's test belongs in that file and must be
built the same way: parse the Release Log table, take the newest row's version, assert the page
names it.

**Vital slice**: AC3's derived test. The two string edits are trivial and stay correct on their own;
the test is the only part that prevents the third occurrence.

**Cut list**: no `VERSION` file, no version-bump script, no CI check. `RUNBOOK.md` already records
releases and this is a personal toolkit — a second source of truth would be the thing that drifts.

---

## Edge Case Checklist

- [ ] "Newest row" is the **last** data row of the Release Log table, not the first — rows are
      appended chronologically (v1.0.0, v1.1.0, v2.0.0). Sorting by string would put v1.1.0 last.
- [ ] The sidebar renders `&middot;` as an HTML entity and is lowercase (`supervisor kit · v1`);
      the footer is prose (`— v1 release`). Two different shapes: do not assume one replacement
      pattern covers both.
- [ ] Do not match the bare token `v1` with a loose regex — `v1` appears inside other words and in
      the `v1.1.0` runbook references. Anchor to the two known contexts.
- [ ] `_page_text()` in `test_site_content.py` may strip tags; check whether the version text
      survives that helper before asserting against it.

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `site/index.html` | 2 lines — sidebar badge (180) and footer version (562) |
| `tests/test_site_content.py` | **New test** — page version derived from RUNBOOK's newest Release Log row |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `RUNBOOK.md` | It is the source of truth this test reads; editing it to fit is the T102 breach |
| `README.md` | Not in scope; carries no version string |
| The `/main/setup.sh` URL anywhere | T101 AC8 scope lock, still in force |

---

## Test Plan

1. Capture the baseline: full suite → expect `844 passed`. Paste it.
2. Write AC3's test first and watch it **fail** against the un-edited page.
3. Make the two string edits; test passes.
4. Run M1 and M2, observe each RED, paste, revert.
5. Full suite + the UI checks from the UI/Design section above.

---

## Completion Checklist

- [ ] Implementation done
- [ ] `Skill({ skill: "code-review" })` run
- [ ] security-review — N/A (Low risk, two text strings and one read-only test)
- [ ] Tests written AND pass — pasted into `tasks/TASK_REVIEW_T104.md` (Gate 5)
- [ ] M1/M2 each observed RED and pasted
- [ ] UI Evidence rows filled (Gate 6) — this task has a UI component
- [ ] `Skill({ skill: "verify" })` run by the user
- [ ] Supervisor notified: ready for Stage 4

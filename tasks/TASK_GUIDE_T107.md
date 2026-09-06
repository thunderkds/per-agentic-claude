# TASK_GUIDE — T107: The kit answers to two different names depending on which surface you land on
**Date**: 2026-09-06
**Complexity Level**: C1
**Risk Level**: Low
**Priority**: P2
**Assigned agent**: Common-Infrastructure-Agent
**Agent guide**: `agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

1. Read `PROJECT_SPEC.md`  2. Read `memory/MEMORY.md`  3. Read this file completely
4. Read `agents/common-infrastructure.md`  5. C1 — `memory/codebase-map.md` not required.

---

## Requirement (Pillar 1 — Adapt the requirement)

User decision, 2026-09-06, in response to the Supervisor asking which name is canonical:

> "Easy Kit"

**Restated intent**:
> **Easy Kit** is the product's name. Make every surface say so, so a reader who clicks from the
> README to the site does not appear to land on a different product.

**Measured baseline** (Supervisor, 2026-09-06 — grep, not recollection):

| Surface | Says | |
|---|---|---|
| `site/index.html:6,213` | **Easy Kit** | already correct — do not touch |
| `README.md:1` | Supervisor Agent Deployment System | H1 |
| `PROJECT_SPEC.md:12` | Supervisor Agent Deployment System | `- **Name**:` field |
| `setup.sh:2` | Supervisor Agent Deployment System | header comment |
| `update.sh:2` | Supervisor Agent Deployment System | header comment |

**Out of scope**:
- `site/index.html` — already canonical.
- The GitHub repo name, the remote URL, and the install one-liner's path
  (`raw.githubusercontent.com/thunderkds/personal-agentic-claude/...`). Renaming a repo breaks every
  existing install's update path. **Not this task; not without an explicit user decision.**
- `tasks/`, `memory/`, `RUNBOOK.md` release rows and any other historical record. Past entries said
  what they said; rewriting history to match a later rename destroys the audit trail.
- Any user-facing behaviour. This is naming only.

**Requirement Refs**: `None — product naming decision.`

### Requirement Fidelity Gate
- [x] Restated intent confirmed — the user answered a direct either/or with "Easy Kit"
- [x] Baseline grepped in the repo before this guide was written
- [x] Every AC traces to the Requirement
- [x] No Requirement Refs claimed

---

## Dependencies & Reachability

**Depends on**: T106 — both edit `README.md`; T106 must merge first or this conflicts on line 1.

**Entry point**: `README.md`

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to |
|---|----------------------|-----------|
| 1 | `README.md`'s H1 is **Easy Kit** | the decision |
| 2 | `PROJECT_SPEC.md`'s `- **Name**:` field is **Easy Kit** | the decision |
| 3 | `setup.sh` and `update.sh` header comments say **Easy Kit** | the decision |
| 4 | No occurrence of "Supervisor Agent Deployment System" remains outside `tasks/`, `memory/`, and historical `RUNBOOK.md` rows | "every surface" |
| 5 | The repo name, remote URL and install one-liner are byte-identical to before | Out of scope — the install path must not break |
| 6 | `sh scripts/validate.sh`, `sh scripts/smoke-install.sh` and `sh tests/test_readme_current.sh` all still pass | no behavioural change |

---

## Evaluation & Acceptance

### Success Criteria

| # | Given | Expect | How checked |
|---|-------|--------|-------------|
| 1 | `grep -rn "Supervisor Agent Deployment System"` excluding tasks/, memory/, RUNBOOK.md, .git/ | no matches | automated |
| 2 | `grep -c "personal-agentic-claude" setup.sh update.sh README.md` | unchanged from pre-edit count | automated — guards AC5 |
| 3 | the three suites above | all pass | automated |

### Verification Command

```bash
sh scripts/validate.sh && sh scripts/smoke-install.sh && sh tests/test_readme_current.sh \
  && ! grep -rn "Supervisor Agent Deployment System" . \
       --include='*.md' --include='*.html' --include='*.json' --include='*.sh' \
     | grep -v '^\./\.git/' | grep -v '^\./tasks/\|^\./memory/\|^\./RUNBOOK.md'
```

### Evidence
> Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T107.md`.

---

## Approach

**Pattern reference**: `None — a four-site string replacement with no comparable prior art in this repo.`
**Vital slice**: `None — four edits are the whole surface.`
**Cut list**: the repo/remote rename, deliberately deferred (see Out of scope).

Do not sed the whole tree. Edit the four named locations by hand and re-grep. A blanket
find-and-replace would reach `tasks/` and `memory/`, which AC4 explicitly protects.

---

## Edge Case Checklist

- [ ] "Easy Kit" must not be shortened, hyphenated, or lowercased inconsistently — match `site/index.html`'s exact casing.
- [ ] `setup.sh`/`update.sh` line 2 is a comment; confirm nothing parses it (grep the test suites for the string before editing).
- [ ] `PROJECT_SPEC.md`'s Name field may be referenced by a template or hook — grep before editing.
- [ ] Do not touch the `personal-agentic-claude` slug anywhere; it is the install path, not the product name.
- [ ] The README H1 change lands on line 1 — rebase on merged T106 first, don't resolve a conflict by hand.

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `README.md` | H1 → Easy Kit |
| `PROJECT_SPEC.md` | Name field → Easy Kit |
| `setup.sh`, `update.sh` | header comment → Easy Kit |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `site/index.html` | already canonical |
| `tasks/**`, `memory/**`, `RUNBOOK.md` release rows | historical record; rewriting it destroys the audit trail |
| anything containing `personal-agentic-claude` | that is the install path, not the name |

---

## Test Plan

1. Record the pre-edit `personal-agentic-claude` occurrence counts (AC5 guard).
2. Edit the four locations by hand.
3. Run the Verification Command; paste real output into `tasks/TASK_REVIEW_T107.md`.
4. Re-check the AC5 counts are unchanged.

---

## Completion Checklist

- [ ] Implementation done
- [ ] Self-review: `Skill({ skill: "code-review" })` run
- [ ] Security review — N/A (Low risk, naming only)
- [ ] Tests pass — output pasted into `tasks/TASK_REVIEW_T107.md` (Hard-Stop Gate 5)
- [ ] UI/Design Evidence rows ☐ N/A — no UI component (Hard-Stop Gate 6)
- [ ] `Skill({ skill: "verify" })` run — user-invoked
- [ ] Supervisor notified: ready for Stage 4 review

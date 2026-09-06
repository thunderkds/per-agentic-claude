# TASK_GUIDE — T106: The README never caught up with v2 — it names no version, and it sells a Codex install without saying four skills are missing there
**Date**: 2026-09-06
**Complexity Level**: C1
**Risk Level**: Low
**Priority**: P1
**Assigned agent**: Common-Infrastructure-Agent
**Agent guide**: `agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

1. Read `PROJECT_SPEC.md`
2. Read `memory/MEMORY.md`
3. Read this file completely
4. Read `agents/common-infrastructure.md`
5. C1 — `memory/codebase-map.md` not required.

---

## Requirement (Pillar 1 — Adapt the requirement)

User request, 2026-09-06, verbatim:

> "check the task from version 2 with version 1 and make sure we update the README for latest"

**Restated intent**:
> Reconcile `README.md` against what v2.0.0 actually shipped, so a reader landing on it can tell
> which release they are looking at and is not surprised by a functional gap the README currently
> omits.

**Measured baseline** (Supervisor, 2026-09-06 — verified in the repo, not inferred):

`git diff v1..HEAD --stat -- README.md` → **19 insertions, 1 deletion**, across a release that
`RUNBOOK.md:208` records as **BREAKING** and spanning T086, T089, T090–T104. T101 (`b6b51a0`) did
reconcile the README's *mechanics* — `--harness`, plain-root canon, symlinks, the update
re-derivation rule are all present and correct. Four gaps survived it:

| # | Gap | Evidence |
|---|---|---|
| 1 | README names no version at all | 0 version strings in 73 lines; `site/index.html` names `v2.0.0`; `RUNBOOK.md:208` records the release |
| 2 | Invites `--harness codex` (lines 44–45) but never says four skills are skipped there | `lib/harness-fetch.sh:180` — "Codex caps a skill body at 8 KB. An oversize skill is SKIPPED". Measured 2026-09-06: `bugfix` 10173 B, `craft-spawn-prompt` 10109 B, `diagnose` 13548 B, `write-better-skill` 14568 B |
| 3 | Line 3 frames the kit as "for Claude Code" | v2's headline is multi-harness; adapters appear only in passing at line 14 |
| 4 | Lines 19–20 carry a live TODO: "the operator fills in the deployed `.vercel.app` URL here once T084's deploy is run" | T084 is merged; no `.vercel.app` URL exists anywhere in the repo |

**Gap 2 is the one that costs a user something.** The other three are accuracy; this one is a
silent functional gap — a Codex user follows the README's own instruction and ends up without four
skills, with nothing in the README to explain why.

**Out of scope**:
- `site/index.html` — T104 already made it name `v2.0.0`. Do not edit it.
- Re-documenting mechanics T101 already covered correctly (`--harness`, canon layout, symlinks,
  update re-derivation). Read them, do not rewrite them.
- Raising or changing the 8 KB cap, or shortening the four oversize skills to fit. This task
  *documents* the gap; closing it is a different task.
- `CLAUDE.md`, `docs/MULTI_AGENT.md`. `RUNBOOK.md` may be touched **only** to record the deployed site URL (AC7).

**Requirement Refs**: `None — documentation reconciliation, not a PRD feature.`

### Requirement Fidelity Gate

- [x] Restated intent confirmed by the Supervisor; all four gaps reproduced in the repo before this guide was written
- [x] Domain terms align with `PROJECT_SPEC.md` — no new terminology
- [x] Every Acceptance Criterion traces to a line in the Requirement
- [x] Requirement Refs: none claimed

---

## Dependencies & Reachability

**Depends on**: `None`

**Entry point**: `README.md`
> The file itself is the surface — it is what a first-time reader meets before installing anything.

---

## Site URL — supplied and verified

`https://personal-agentic-claude.vercel.app/` — supplied by the user 2026-09-06 and **verified live by the
Supervisor before this guide was updated**: HTTP 200, 31112 bytes, and the served HTML is byte-identical to
this repo's `site/index.html` (so the deploy is not stale). Use it verbatim. Do not invent or alter it.

Record it in `RUNBOOK.md`'s "Deploying the landing site" section too (AC7). The URL existing nowhere in the
repo is what forced a round-trip to the user on this task; writing it down once ends that.

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | README names the current release (`v2.0.0`), and the named version matches `RUNBOOK.md`'s newest release row | gap 1 — "update the README for latest" |
| 2 | README states that a Codex install skips skills whose body exceeds Codex's 8 KB cap, names the four currently affected, and says they are genuinely unavailable rather than truncated | gap 2 |
| 3 | The opening framing reflects multi-harness support (Claude Code, Codex, Cursor) rather than Claude Code alone, without inflating what the adapters actually do | gap 3 |
| 4 | Every `site/index.html` repo-relative link in the README points at `https://personal-agentic-claude.vercel.app/`, and the stale "once T084's deploy is run" TODO is gone | gap 4 |
| 7 | `RUNBOOK.md`'s landing-site section records the deployed URL | the URL was findable nowhere in the repo |
| 5 | An automated test asserts AC1 and AC2 and fails when either drifts | Gate 5; and the recurrence risk below |
| 6 | Nothing T101 documented correctly is rewritten, and no claim is added that the repo does not support | "Out of scope" |

---

## Evaluation & Acceptance

### Success Criteria

| # | Given | Expect | How checked |
|---|-------|--------|-------------|
| 1 | `README.md` after the change | contains the same version string as `RUNBOOK.md`'s newest release row | automated test |
| 2 | A skill's body pushed over 8 KB (or an oversize one shrunk under it) | the test FAILS, naming the skill whose README listing is now wrong | automated test — the negative case |
| 3 | `README.md` after the change | names all four current oversize skills in its Codex section | automated test |
| 4 | A reader following the Codex install line | learns, from the README alone, that four named skills will not exist in that install | manual read |

> **The negative case (SC2) is the whole point of the test.** A test that only confirms today's four
> names would itself be an expiring measurement — the exact failure mode recorded three times in
> `memory/learnings.md` and again this session at T105. **Derive the oversize set from the cap in
> `lib/harness-fetch.sh` and compare it to what the README lists.** Do not hardcode the four names in
> the test.

### Verification Command

```bash
bash tests/test_readme_current.sh
```

### Evidence

> Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T106.md`.

---

## Approach

**Pattern reference**: `scripts/test-claude-md-refs.sh` — this repo's existing shape for a test that
checks documentation against the repo it describes. Imitate its structure and failure output.

**Vital slice**: the four gaps plus the drift test.
**Cut list**: `None — nothing was cut.`

Keep the README's existing character: it is deliberately a short front door that defers detail to the
site. Do **not** grow it into a manual. Gap 2 needs roughly a sentence and a four-item list; gaps 1
and 3 are a line each.

---

## Edge Case Checklist

- [ ] The four oversize skills are a *measurement taken 2026-09-06*. Any skill edit changes the set — this is precisely why AC5's test must derive it, not restate it.
- [ ] The cap is overridable at install time via `HARNESS_SKILL_BODY_CAP` (`lib/harness-fetch.sh:185`), and `0` disables the check. The README's claim should describe the default without implying the cap is immutable.
- [ ] Read the cap out of `lib/harness-fetch.sh` rather than hardcoding `8192` in the test, so the test survives a cap change.
- [ ] Skill bodies are measured in bytes, not characters — a multibyte character counts for more than one. Use `wc -c`, never `wc -m`.
- [ ] Don't state or imply the four skills are truncated in Codex. They are **skipped**; the distinction is the whole user-facing point.
- [ ] Version comparison must not be fooled by `v2.0.0` matching inside a longer string, or by RUNBOOK rows being newest-first vs oldest-first — check which.

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `README.md` | Name the release; add the Codex skip note with its four skills; widen the opening framing; replace the three `site/index.html` links + drop the T084 TODO |
| `RUNBOOK.md` | Record the deployed site URL in the landing-site section (AC7) — that section only |
| `tests/test_readme_current.sh` | **New.** Derives the oversize set and the current version from the repo, asserts the README matches both |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `site/index.html` | T104 already made it name v2.0.0 |
| `lib/harness-fetch.sh` | This task documents the cap, never changes it |
| `PROJECT_KANBAN.md` | Supervisor-owned |

---

## Test Plan

1. Confirm the four gaps in the current README before editing.
2. Write `tests/test_readme_current.sh` first; watch it fail against the unedited README (red).
3. Edit the README; watch it pass (green).
4. Run the negative case: temporarily pad a small skill past 8 KB and confirm the test fails naming that skill; revert.
5. Paste real output — not a summary — into `tasks/TASK_REVIEW_T106.md`.

---

## Completion Checklist

- [ ] Implementation done
- [ ] Self-review: `Skill({ skill: "code-review" })` run
- [ ] Security review — N/A (Low risk, documentation + one test script)
- [ ] Lint passes — if `tests/test_readme_current.sh` is added to CI's shellcheck list, it must be clean (see T105's follow-up 1: that list is hardcoded in two places)
- [ ] Tests written AND pass — output pasted into `tasks/TASK_REVIEW_T106.md` (Hard-Stop Gate 5)
- [ ] UI/Design Evidence rows ☐ N/A — documentation task, no UI component (Hard-Stop Gate 6)
- [ ] `Skill({ skill: "verify" })` run — user-invoked
- [ ] Supervisor notified: ready for Stage 4 review

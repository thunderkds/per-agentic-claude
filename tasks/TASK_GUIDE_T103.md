# TASK_GUIDE — T103: Inline the Response Standard into CLAUDE.md so it reaches the Supervisor
**Date**: 2026-09-04
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
5. Read `memory/learnings.md`'s entry *"A pointer in CLAUDE.md to a non-injected file does not bind
   the Supervisor"* — it is the measured account of the defect and the authority for this task
6. Read `agents/general-agent-template.md`'s `## Response Standard` — the rules you are relocating

---

## Requirement (Pillar 1 — Adapt the requirement)

User report, 2026-09-04:
> "as I saw, the update from task 100 does not work as expected, the response still unreachable"

Clarified with the user: replies are still too dense to follow; the T100 standard is not taking
effect on the Supervisor.

**Restated intent**:
> T100's six Response Standard rules are correct and stay exactly as written. Their **delivery
> channel to the Supervisor** is what failed. `CLAUDE.md` currently says *"`agents/general-agent-
> template.md`'s `## Response Standard` binds the Supervisor too: read it and apply it to your own
> replies"* — a rule whose activation depends on the Supervisor performing an unenforced act
> (opening a file the harness does not auto-inject). Move the rules themselves into `CLAUDE.md`,
> which **is** auto-injected, and pin that with a test so the next edit cannot silently revert it to
> a pointer.

**The evidence this is real, not inferred.** Across the T101 session the Supervisor violated at least
three of the six rules repeatedly — 2-column status tables (against *"a table only to compare on 3+
dimensions, never to lay out one thing"*), re-listing the same open items in four consecutive replies
(against *"don't re-list open items your last reply listed"*), and narrating what it had just read.
It had **not opened `general-agent-template.md` at any point** in that session; it opened the file
only after the user complained.

**Third occurrence of one defect class**: T041 named reachability, T066 stated it as *"already
covered must mean reaches-the-context"*, and T082's Stage 5 **measured** a pointer in a non-injected
file losing its binding and fixed it by keeping the rule in `CLAUDE.md`. T100 re-introduced that
shape for its Supervisor half.

**Why T100's verify did not catch it** (do not repeat this method): it ran at the agent-config
surface — a sub-agent in a worktree against a control on the base branch. Sub-agents receive
`general-agent-template.md` as their **system prompt**, so the rules genuinely bound there. The
Supervisor's own session was never the surface, and it is the *only* surface where the pointer form
and the inlined form differ.

**Out of scope**:
- Rewording any of the six rules. They are not the defect. Relocate them verbatim.
- The four role guides. Sub-agents already receive the standard correctly via the template.
- A general sweep for other pointer-shaped rules in `CLAUDE.md`. The user chose the narrow fix;
  recorded as a cut, and a candidate follow-up row if this class recurs a fourth time.
- `## Supervisor Communication Style`'s self-monitoring / `compact-advisor` paragraph — untouched.

---

## Dependencies & Reachability

**Depends on**: None.

**Entry point**: `## Response Standard` — the heading, which must after this task appear in
`CLAUDE.md` as well as in `agents/general-agent-template.md`.

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|---|---|
| 1 | `CLAUDE.md` contains all six rule lines of the Response Standard verbatim, not a pointer to them | the defect |
| 2 | The sentence *"read it and apply it to your own replies"* (and any equivalent instruction telling the Supervisor to go open the template) is **gone** from `CLAUDE.md` | a pointer is what failed |
| 3 | `agents/general-agent-template.md` still carries the standard unchanged — sub-agents keep their working channel | out-of-scope lock |
| 4 | The six rule lines in `CLAUDE.md` are **byte-identical** to those in the template | no drift between two copies |
| 5 | A test asserts AC1 and AC4 by reading both files at test time and comparing, so the two cannot drift and the check cannot go vacuous | user chose "+ a test" |
| 6 | A test asserts AC2 — that `CLAUDE.md` does not merely point | prevents silent regression to a pointer |
| 7 | `tests/test_response_standard.py`'s docstring claim *"the one file every sub-agent **and the Supervisor** reach"* is corrected — it is the premise that was false | the wrong premise, fixed at source |
| 8 | `test_agent_guide_dedup.py`'s `T070_BASELINE_REF` is repointed to this task's own `CLAUDE.md` edit commit, with a comment explaining why, matching the convention T071/T082/T096/T100 each followed | AC5 pin is red-by-construction otherwise |
| 9 | The four role guides are byte-unchanged | out-of-scope lock |
| 10 | Full suite: no pre-existing test modified except the two named in AC7/AC8, and the 6 known pre-existing failures (T102) are unchanged in name and count | Surgical Changes |

---

## Evaluation & Acceptance

### Success Criteria

| # | Given | Expect | How checked |
|---|---|---|---|
| 1 | The edited `CLAUDE.md` | contains all six rule lines, byte-identical to the template's | automated test |
| 2 | `CLAUDE.md` | contains no "read it and apply it"-style instruction for this standard | automated test |
| 3 | **M1** — revert `CLAUDE.md`'s section to the pointer form | the AC1/AC2 tests go **RED**; restore, GREEN | manual, re-run by Supervisor |
| 4 | **M2** — change one word in `CLAUDE.md`'s copy of a rule line so the two files disagree | the AC4 drift test goes **RED**; restore, GREEN | manual, re-run by Supervisor |
| 5 | **M3** — delete the `## Response Standard` heading from the template | the AC3 test goes **RED** (the sub-agent channel must stay pinned too); restore | manual, re-run by Supervisor |
| 6 | Full suite | 6 failed / 836+ passed — same 6 pre-existing names as T102 | automated |

> M1–M3 are mandatory. **M2 and M3 matter as much as M1**: a test that only checks `CLAUDE.md`
> contains the rules would pass on a repo where the template lost them (breaking sub-agents) or
> where the two copies have quietly diverged. Pin all three directions, as T101's round 2 did.

### Verification Command

```bash
cd "$(git rev-parse --show-toplevel)" && python3 -m pytest tests/ .claude/hooks/tests/ -q 2>&1 | tail -3
```

### Evidence

> Filled at Stage 4/5 in `tasks/TASK_REVIEW_T103.md`.

---

## Demonstration

> See `tasks/TASK_REVIEW_T103.md`. This task changes no executable code, so BEFORE is the verbatim
> current text of `CLAUDE.md`'s `## Supervisor Communication Style` opening paragraph.

---

## Approach

**Pattern reference**: `tests/test_response_standard.py` — it already reads the probe string **out of
the template at test time** and asserts the probe still exists before using it, precisely so the
guard cannot go vacuous. Extend that file in that style rather than starting a new one.

**Vital slice**: replacing the pointer sentence in `CLAUDE.md` with the six rules, plus the three
tests pinning it.

**Cut list**: the sweep for other pointer-shaped rules (user's choice); any rewording of the rules.

**The one real hazard.** `CLAUDE.md` is pinned byte-identical to a baseline commit by
`test_agent_guide_dedup.py` (AC5, `T070_BASELINE_REF`, currently `c87097e` = T100's own edit commit).
Editing `CLAUDE.md` makes that assertion red **by construction**. The established convention — followed
by T071, T082, T096 and T100, each documented in that file's comment block — is to repoint the ref to
your own edit commit and add a comment saying what changed and why. **Repoint, never delete, and do
not touch the assertion body.** You cannot know your own commit hash before committing, so: commit the
`CLAUDE.md` change first, then repoint in a second commit naming the first.

---

## Edge Case Checklist

- [ ] `test_response_standard_is_not_duplicated_into_the_role_guides` checks the **four role guides**, not `CLAUDE.md` — verified at Stage 2, so inlining here does not collide with it. Confirm that still holds rather than assuming it.
- [ ] Do not add the rules to any role guide; that test would correctly go red.
- [ ] The `## Supervisor Communication Style` section also carries the "not short by default" sentence and the audit-trail carve-out. Both stay — the rules govern replies only, never KANBAN rows, Evidence, memory or commit messages.
- [ ] Keep the compact-advisor paragraph and its blockquote intact.
- [ ] AC4 compares rule lines across two files: strip trailing whitespace consistently or the byte-identity check will fail on invisible differences.
- [ ] `CLAUDE_LEGACY.md` has a documented sync policy for new gates. Check whether it carries this section; if it does, decide explicitly and record the decision either way rather than silently skipping it.

---

## Files to Change (Predicted)

| File | Change |
|---|---|
| `CLAUDE.md` | `## Supervisor Communication Style`: replace the pointer sentence with the six rules verbatim |
| `tests/test_response_standard.py` | Add AC1/AC2/AC4 tests; correct the false docstring premise (AC7) |
| `.claude/hooks/tests/test_agent_guide_dedup.py` | Repoint `T070_BASELINE_REF` + comment (AC8) — this line only |
| `tasks/TASK_REVIEW_T103.md` | New, from the template |
| `CLAUDE_LEGACY.md` | Only if the edge-case check finds it carries this section |

## Files Must NOT Touch

| File | Reason |
|---|---|
| `agents/general-agent-template.md` | The sub-agent channel works; AC3 pins it byte-unchanged |
| `agents/{backend,frontend,qa,common-infrastructure}.md` | AC9 |
| Any other test | AC10 |
| `PROJECT_KANBAN.md` | Supervisor-owned |

---

## Test Plan

1. Record the baseline suite count first.
2. Write the three tests, watch AC1/AC2/AC4 fail against the current `CLAUDE.md`.
3. Make the edit. Commit it. Repoint `T070_BASELINE_REF` in a second commit.
4. Run M1, M2, M3. Paste all three RED transitions and the restores.
5. Full suite; confirm the 6 pre-existing failures are unchanged in name and count.

---

## Completion Checklist

- [ ] Implementation done
- [ ] `Skill({ skill: "code-review" })` run
- [ ] Security review: N/A — Low risk, documentation and test-only, no runtime path (record the reason)
- [ ] `scripts/validate.sh` passes
- [ ] Tests written AND pass — output pasted into `tasks/TASK_REVIEW_T103.md`
- [ ] M1, M2, M3 observed RED and restored, all three pasted
- [ ] UI/Design AC section deleted — pure-documentation task, all three UI Evidence rows ☐ N/A
- [ ] `Skill({ skill: "verify" })` — **user-run only**
- [ ] Supervisor notified: ready for Stage 4

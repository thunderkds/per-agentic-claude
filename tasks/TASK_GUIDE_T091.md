# TASK_GUIDE — T091: Staleness Guard names the wrong source and misses the Cursor adapter
**Date**: 2026-08-24
**Complexity Level**: C0
**Risk Level**: Low
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
5. Note the **Complexity Level** above (C0) and apply the matching process from the Complexity matrix in your role guide
6. C0, two known files — `memory/codebase-map.md` is **not** required.

Also read before editing: `tests/test_provider_adapters.py` (its module docstring states the SC4
derive-at-test-time rule this task must not violate) and `docs/ddr/` DDR-0006 (the primary/adapter
mandate that made the guard wrong).

---

## Requirement (Pillar 1 — Adapt the requirement)

From `PROJECT_KANBAN.md` T091, registered 2026-08-24 from T090's Stage 4 code-review (P2,
confidence 100, verified by reading the file):

> `.claude/agents/general-agent-template.md:58-62` states root `AGENTS.md` is *"a thin mirror of
> **this file's** Base Rules for non-Claude CLIs"* and instructs maintainers editing the template or
> the four role guides to check `AGENTS.md` is still accurate. **Both halves are now wrong.**
> (1) After T090 the adapters mirror `CLAUDE.md`'s non-negotiables — the four Karpathy principle
> names, the six Hard-Stop Gate titles, the untrusted-content rule and "no TASK_GUIDE = no work" —
> **not** the template's Base Rules; the guard therefore sends a maintainer to audit the wrong
> source, and an edit to `CLAUDE.md` (the channel that actually feeds the adapters) triggers no
> guard at all. (2) The guard names only `AGENTS.md`; `.cursor/rules/agent-base.mdc`, shipped by
> T090 and equally required per DDR-0006, has **no** staleness guard whatsoever.
>
> Scope is the guard's five lines: correct the source it names, add the Cursor adapter, and point
> maintainers at the conformance test as the real enforcement. Do **not** re-expand the guard into
> a second sync policy — `CLAUDE_LEGACY.md` at 629 hand-synced lines is what that becomes. Consider
> asserting the guard's own accuracy in `test_provider_adapters.py`, since an unenforced staleness
> note is exactly what this row is about.

**Restated intent** (Supervisor's interpretation, in the project's domain language):
> Rewrite the Staleness Guard so it describes the post-T090 reality — the adapters mirror
> `CLAUDE.md`'s non-negotiables, there are two of them, and `tests/test_provider_adapters.py` is
> what actually enforces the sync — and add a conformance test so the guard's own accuracy is
> mechanically enforced rather than trusted.

**Out of scope** (what this task explicitly does NOT do):
- Changing the content of `AGENTS.md` or `.cursor/rules/agent-base.mdc` — they are correct today.
- Changing `CLAUDE.md`, the four role guides, or the template's Base Rules / Output Requirements.
- Adding a sync *policy* (a checklist, a procedure, a mirrored rule list) anywhere. The guard stays
  a short pointer; the test is the enforcement.
- Adding a third adapter or any new provider channel.
- Touching `CLAUDE_LEGACY.md`.

**Requirement Refs**: none — this is a defect row registered from T090's Stage 4 review, not a
`PRD.md` feature. Traceability is to `PROJECT_KANBAN.md` T091 and DDR-0006.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (Supervisor, from the T091 KANBAN row; user approved starting T091 on 2026-08-24)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary — "adapter", "primary", "non-negotiables" are DDR-0006's terms, used here unchanged
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] Requirement Refs: N/A (defect row) — coverage is against the KANBAN row's stated scope

---

## Dependencies & Reachability

**Depends on**: `None` — T090 (which created the condition) is merged and Done.

**Entry point**: `## Staleness Guard` — the literal heading in
`.claude/agents/general-agent-template.md`; also the string the new test greps for.

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | The Staleness Guard section names `CLAUDE.md` as the source the adapters mirror, and no longer claims they mirror this file's Base Rules | "the adapters mirror `CLAUDE.md`'s non-negotiables … not the template's Base Rules" |
| 2 | The Staleness Guard section names both adapter paths: `AGENTS.md` and `.cursor/rules/agent-base.mdc` | "The guard names only `AGENTS.md`; `.cursor/rules/agent-base.mdc` … has no staleness guard whatsoever" |
| 3 | The Staleness Guard section names `tests/test_provider_adapters.py` as the mechanism that actually enforces the sync | "point maintainers at the conformance test as the real enforcement" |
| 4 | The rewritten Staleness Guard section is at most 8 lines of body text (was 5) — it did not become a second sync policy | "Do not re-expand the guard into a second sync policy" |
| 5 | A new test in `tests/test_provider_adapters.py` asserts AC1–AC4 against the live template file, deriving the adapter paths from the existing `ADAPTERS` mapping rather than hardcoding them | "Consider asserting the guard's own accuracy in `test_provider_adapters.py`"; SC4 derive-at-test-time rule |
| 6 | The new test FAILS against the pre-fix guard text and PASSES against the fixed text (proven by pasted red-then-green output) | Hard-Stop Gate 5; "A green suite is not evidence when both tests look away" (learnings) |
| 7 | The full existing suite still passes — no adapter content changed, no other test disturbed | Out-of-scope list |

---

## Evaluation & Acceptance

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | The template's Staleness Guard section as it stands before this task | New test fails, naming the missing Cursor adapter / wrong source | automated test, run on stashed pre-fix text |
| 2 | The rewritten Staleness Guard section | New test passes; all four AC1–AC4 assertions green | automated test |
| 3 | Hypothetical: guard rewritten but `.cursor/rules/agent-base.mdc` omitted | New test fails on the adapter-coverage assertion | automated test (AC5 derives paths from `ADAPTERS`, so removing an adapter path from the guard is caught) |
| 4 | Guard rewritten to 20 lines of sync procedure | New test fails the ≤8-line assertion | automated test |

### Verification Command (exact, runnable)

```bash
python3 -m pytest tests/test_provider_adapters.py -q
```

Full-suite check for AC7:

```bash
python3 -m pytest tests/ -q
```

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T091.md`.

---

## Demonstration

> **Moved.** See `tasks/TASK_REVIEW_T091.md`.

---

## Approach

**Pattern reference**: `tests/test_provider_adapters.py` — imitate its structure exactly: a
`_`-prefixed reader helper, `_normalize()` for newline-safe prose comparison, values derived from
the live file at test time (never a hardcoded copy), and one assertion message per failure that
names the file and what was missing.

**Vital slice**: the guard's own five lines plus one new test function. **Cut list**: no
CONTRIBUTING-style sync doc; no guard blocks added to the four role guides; no pre-commit hook.

Recommended approach:

1. Rewrite `## Staleness Guard` in `.claude/agents/general-agent-template.md` so it says, in ≤8
   lines: the two adapters mirror `CLAUDE.md`'s non-negotiables (not this file's Base Rules); edits
   to those non-negotiables in `CLAUDE.md` are what require an adapter update; and
   `tests/test_provider_adapters.py` enforces this mechanically — run it rather than auditing by eye.
2. Add `test_staleness_guard_describes_the_real_adapter_contract()` to
   `tests/test_provider_adapters.py`. Extract the `## Staleness Guard` section from the template
   with a regex anchored on the heading (stop at the next `##` or EOF), then assert: it mentions
   `CLAUDE.md`; it mentions every path in `ADAPTERS`; it mentions `test_provider_adapters.py`; its
   body is ≤8 non-blank lines; and it does **not** contain the stale phrase describing the adapters
   as a mirror of *this file's* Base Rules.
3. Prove red-then-green: run the new test against the current (pre-fix) guard text first and paste
   the failure, then against the fixed text.

Why P2 and not higher (this reasoning must survive into review): `tests/test_provider_adapters.py`
already enforces the actual `CLAUDE.md`↔adapter sync mechanically, so the Staleness Guard is
redundant belt-and-braces, not the load-bearing mechanism it was before T090.

---

## Edge Case Checklist

- [ ] The stale-phrase negative assertion must not be so literal that any rewording passes it, nor so
      loose that the corrected text trips it — assert on the specific claim ("this file's Base Rules"
      as the mirrored source), not on the word "Base Rules" alone
- [ ] The section-extraction regex must stop at the next heading, not swallow the rest of the file —
      otherwise the ≤8-line assertion is measured against the wrong text and always fails/always passes
- [ ] `.cursor/rules/agent-base.mdc` contains a `.` and `/`; ensure the path match is a plain
      substring check, not a regex where the dot is a wildcard that would match a near-miss path
- [ ] Line counting must ignore blank lines and the heading itself, and be stated in the assertion
      message so a future maintainer knows what the budget covers
- [ ] The template file is auto-loaded into agent context — keep the rewrite terse; a bloated guard
      costs every spawn (T066 dedup precedent)
- [ ] Do not "improve" the surrounding Output Requirements / Non-negotiables prose while in the file

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `.claude/agents/general-agent-template.md` | Rewrite the `## Staleness Guard` section (currently lines 58–62): correct the mirrored source to `CLAUDE.md`, name both adapters, point at the conformance test |
| `tests/test_provider_adapters.py` | Add one test asserting the guard's own accuracy (AC1–AC4), deriving adapter paths from the existing `ADAPTERS` mapping |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `CLAUDE.md` | Primary source; this task fixes a pointer at it, not its content |
| `AGENTS.md` | Adapter content is correct post-T090 and out of scope |
| `.cursor/rules/agent-base.mdc` | Same — correct today; only the guard's awareness of it is broken |
| `.claude/agents/{common-infrastructure,backend,frontend,qa}.md` | The four role guides are not part of the guard's five-line scope |
| `CLAUDE_LEGACY.md` | Explicitly named in the row as the anti-pattern this task must not reproduce |
| `PROJECT_KANBAN.md` | Supervisor-only; the Supervisor closes the row at Stage 5 |
| `memory/**` | Supervisor-only per the Memory Write Protocol |

---

## Test Plan

1. **Red**: with the current guard text in place, run
   `python3 -m pytest tests/test_provider_adapters.py -q` after adding the new test. It must fail,
   and the failure message must name the specific defect (wrong source / missing Cursor adapter).
   Paste this output.
2. **Green**: apply the guard rewrite; re-run the same command. All tests pass. Paste this output.
3. **Regression**: `python3 -m pytest tests/ -q` — full suite green (AC7). Paste the summary line.
4. **Negative probe (AC5/SC3)**: temporarily delete `.cursor/rules/agent-base.mdc` from the guard
   text, confirm the test goes red, restore. Report the observed failure in the review file — this
   is what proves the assertion is not vacuous.

---

## Completion Checklist

- [ ] Implementation done
- [ ] Self-review: `Skill({ skill: "code-review" })` run
- [ ] Security review: N/A — Low risk, docs + test only
- [ ] Lint passes
- [ ] Tests written AND pass — red-then-green output pasted into `tasks/TASK_REVIEW_T091.md`'s Evidence table (Hard-Stop Gate 5)
- [ ] `Skill({ skill: "verify" })` run (user-invoked) — guard text confirmed accurate against the live adapters
- [ ] UI Evidence rows: ☐ N/A × 3 — no UI component in this task (docs + test only)
- [ ] `memory/MEMORY.md` updated (Supervisor, diff-driven pass at Stage 5)
- [ ] Supervisor notified: task ready for Stage 4 review

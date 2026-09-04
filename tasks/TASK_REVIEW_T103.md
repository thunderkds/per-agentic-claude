# TASK_REVIEW — T103: Inline the Response Standard into CLAUDE.md

> Sibling of `tasks/TASK_GUIDE_T103.md`. Everything here is **filled by the reviewer at Stage
> 4/5** — it is deliberately NOT in the guide, because the implementing agent re-reads the guide on
> every turn and never fills these two sections.
>
> Consumers resolve each section **guide first, this file second** (`.claude/hooks/lib/guide_sections.py`):
> a legacy guide that still carries these sections inline keeps working unchanged, and a stray
> review file can never override an inline section.

---

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_response_standard.py` — 3 new tests: `test_t103_ac1_ac4_claude_md_carries_the_six_rules_byte_identical_to_the_template` (AC1/AC4), `test_t103_ac2_claude_md_states_the_rules_it_does_not_merely_point` (AC2), `test_t103_ac3_template_still_carries_the_standard_for_sub_agents` (AC3). All read both files at test time; each has an explicit `len(...)==6` anti-vacuity guard. |
| Verification command run | ☑ pass | `python3 -m pytest tests/ .claude/hooks/tests/ -q` → `6 failed, 837 passed`. The 6 failures are the pre-existing T102 set (MEMORY.md hot-tier budget ×5, README ≤60 lines ×1) — unchanged in name and count from the baseline captured before any edit (`6 failed, 834 passed`; +3 = 2 new T103 tests + AC3 which pre-dated). |
| Negative cases hold | ☑ pass | M1/M2/M3 below — all three mutation directions observed RED then restored GREEN. |
| verify | ☐ N/A | Documentation + test-only change, no runtime code path. `verify` is user-run only (project rule); Supervisor to request `/verify` at Stage 5 if desired — **N/A pass**. |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed the 4 changed files (`git diff 70b4192..HEAD`): `CLAUDE.md`, `tests/test_response_standard.py`, `.claude/hooks/tests/test_agent_guide_dedup.py`, `tasks/TASK_REVIEW_T103.md`. No production code, no callers. `main...HEAD` deliberately not used (branch is far ahead of frozen `main`). |
| Full smoke suite still green (no regression) | ☑ pass | Same 6 pre-existing failures, 837 passed; `scripts/validate.sh` → PASS. |
| **UI: Visual regression (diff or verdict pasted)** | ☐ N/A | Pure-documentation task, no UI component. |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☐ N/A | Pure-documentation task, no UI component. |
| **UI: Responsiveness at target viewports** | ☐ N/A | Pure-documentation task, no UI component. |

### code-review (Stage 4) — findings

Run inline (C1, 4 files, no production code). Personas: correctness, testing, maintainability, standards, adversarial (>50 changed lines).

- **P0 / P1**: None.
- **P2**: None.
- **P3 (noted, no fix)**: (a) the compact-advisor paragraph was tightened rather than kept fully verbatim — the guide's edge-case checklist says "keep intact", but the blockquote and the `Skill()` call + two-meanings explanation are preserved, and the user approved the trim to fit the 200-line cap. (b) AC1/AC2 assert the rules exist somewhere in `CLAUDE.md`, not specifically under `## Supervisor Communication Style`; section placement is not an AC, so no guard added.
- Entry-point reachability (Phase 0.5): `Entry point: ## Response Standard` — grep of `CLAUDE.md` finds `### Response Standard` (heading) + the six rule lines. Reachable. No finding.

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE** (verbatim opening paragraph of `CLAUDE.md`'s `## Supervisor Communication Style`, as it
exists before the first implementation commit — captured 2026-09-04):

```
Chat replies are **not** short by default — the session that registered this rule ran 40+ lines,
stacked tables and three-option menus. `agents/general-agent-template.md`'s `## Response Standard`
binds the Supervisor too: read it and apply it to your own replies. It governs conversation only —
keep `PROJECT_KANBAN.md` rows, `TASK_GUIDE_Txxx.md` Evidence, `memory/decisions.md` and commit
messages fully detailed, since that is the audit trail and simplifying it loses real information.
```

The six rules are not in this file at all — they are only in `agents/general-agent-template.md`,
which the harness does not auto-inject into the Supervisor's session. Activation depends on the
Supervisor choosing to open that file.

**AFTER** (verbatim, `CLAUDE.md` lines 19–32 after the edit — commit `b1da25a`):

```
## Supervisor Communication Style

Chat replies are **not** short by default. The `## Response Standard` below governs the Supervisor's
own replies as well as sub-agents' — conversation only: `PROJECT_KANBAN.md` rows, `TASK_GUIDE_Txxx.md`
Evidence, `memory/decisions.md` and commit messages stay fully detailed, as the audit trail.

### Response Standard

- Lead with the answer or verdict; method and caveats come after.
- Asking for a decision: recommendation first, alternatives one line each.
- Cut sentences restating the question or narrating what you read.
- A table only to compare on 3+ dimensions, never to lay out one thing.
- Say what is blocked and what you need, not all you could do.
- Don't re-list open items your last reply listed; point back in a line.
```

The six lines are byte-identical to `agents/general-agent-template.md`'s `## Response Standard`
bullets (asserted by `test_t103_ac1_ac4...` reading both files at test time).

**DELTA**: The six Response Standard rules now live in `CLAUDE.md` itself (auto-injected every
session), so they reach the Supervisor with no unenforced "go open the template" step; three tests
pin the two copies against drift and pin the sub-agent channel too.

**WITNESS**: Implementation + M1/M2/M3 mutation controls + full-suite run performed by the T103
Common-Infrastructure sub-agent on 2026-09-04 (branch `fix/t103-response-standard-channel`, commits
`b1da25a` (CLAUDE.md + tests), `30627ac` (baseline-ref repoint)). `memory/event-trace/T103.jsonl` captured only the initial guide Read
(Bash-tool trace attribution is known-thin from a worktree — see MEMORY.md). **Independent witness
pending**: Supervisor to re-run the verification command at Stage 4/5 and record its own output here.

---

## Mutation controls (M1 / M2 / M3)

Baseline before any edit: `6 failed, 834 passed`. New T103 tests written first and watched fail
against the unedited `CLAUDE.md`:

```
FAILED tests/test_response_standard.py::test_t103_ac1_ac4_claude_md_carries_the_six_rules_byte_identical_to_the_template
FAILED tests/test_response_standard.py::test_t103_ac2_claude_md_states_the_rules_it_does_not_merely_point
2 failed, 3 passed         # AC3 already green (template unchanged); T100's two originals green
```

### M1 — revert `CLAUDE.md`'s section to the pointer form → AC1/AC2 RED

Mutation: replaced `### Response Standard` + the six bullets with
`See \`agents/general-agent-template.md\`'s \`## Response Standard\` — read it and apply it to your own replies.`

```
FAILED tests/test_response_standard.py::test_t103_ac1_ac4_claude_md_carries_the_six_rules_byte_identical_to_the_template
FAILED tests/test_response_standard.py::test_t103_ac2_claude_md_states_the_rules_it_does_not_merely_point
2 failed, 3 passed in 0.02s
```
Restore (`cp` from backup) → `5 passed in 0.01s`. GREEN.

### M2 — change one word in `CLAUDE.md`'s copy of a rule line → AC4 drift RED

Mutation: rule 1 in `CLAUDE.md` only, `"...come after."` → `"...come later."` (template unchanged).

```
FAILED tests/test_response_standard.py::test_t103_ac1_ac4_claude_md_carries_the_six_rules_byte_identical_to_the_template
1 failed, 4 passed in 0.02s
```
(AC2 stays green — the six rule lines are still present, they have merely drifted.) Restore → `5 passed`. GREEN.

### M3 — delete the `## Response Standard` heading from the template → AC3 RED

Mutation: `agents/general-agent-template.md`, `## Response Standard` → `## Response Standard (removed heading test)`.

```
FAILED tests/test_response_standard.py::test_t103_ac1_ac4_claude_md_carries_the_six_rules_byte_identical_to_the_template
FAILED tests/test_response_standard.py::test_t103_ac3_template_still_carries_the_standard_for_sub_agents
2 failed, 3 passed in 0.02s
```
AC3 catches the broken sub-agent channel (its `_rule_lines(template)` count drops to 0); AC1/AC4's
anti-vacuity guard (`len(template_rules) == 6`) also trips, as designed. Restore → `61 passed`
(with `test_agent_guide_dedup.py`). GREEN.

**Why M2 and M3 are not optional**: a test that only checked "`CLAUDE.md` contains the rules" would
stay green under M2 (two copies silently drifted) and under M3 (template lost the section, every
spawned sub-agent silently running without it). All three directions are pinned.

---

## Out-of-scope decision log

- **`CLAUDE_LEGACY.md`**: checked (`grep -n "Communication Style\|Response Standard\|short by
  default\|compact-advisor"` → no match). It does **not** carry the `## Supervisor Communication
  Style` section, so its documented "mirror new gates" sync policy does not apply here. No change.
- **`AGENTS.md` / `.cursor/rules/agent-base.mdc`**: neither carries this section; `test_provider_
  adapters.py` enforces only the Karpathy names, Hard-Stop Gate titles, untrusted-content rule and
  "no TASK_GUIDE = no work". No change.
- **`agents/general-agent-template.md` + 4 role guides**: byte-unchanged (AC3/AC9). The sub-agent
  channel already works.
- **Line budget**: `CLAUDE.md` is pinned `<= 200` lines by `test_vital_slice.py::test_ac11_line_cap`
  (a pre-existing test AC10 forbids modifying). The six rules + heading were absorbed by tightening
  the adjacent "Self-monitoring for context overwhelm" / compact-advisor prose in the same section;
  the blockquote and the compact-advisor `Skill()` call are kept verbatim. User approved this
  approach before implementation. Net line delta: 0.

---

## Stage 4 — code-review (Supervisor, 2026-09-04)

**0 P0 / 0 P1 / 1 P2 / 1 P3.** No merge-blocking finding. `security-review` not activated — Low risk,
documentation and test-only, no runtime path, no auth/input/secret/shell surface in the diff.

10/10 ACs verified independently, not read off the agent's report:

- **AC1/AC4** — the six rule lines in `CLAUDE.md` parse byte-identical to the template's (compared by
  extracting both at review time, not by eye).
- **AC3/AC9** — `agents/general-agent-template.md` and all four role guides **byte-unchanged** vs `v2`.
- **AC7** — the false docstring premise is corrected at source, and states plainly why the template is
  not "the one file every sub-agent and the Supervisor reach".
- **AC8** — `T070_BASELINE_REF` repointed `c87097e` -> `b1da25a` with the convention's comment block;
  assertion body untouched.
- **AC10** — exactly two test files touched, both sanctioned by AC7/AC8. `validate.sh` RC=0.
- Suite **837 passed / 6 failed**, failure set **byte-identical** to the `v2` baseline (T102). 0 regressions.

All three mutation controls re-run by the Supervisor rather than trusting the pasted transitions:

| Mutation | Result |
|---|---|
| **M1** — revert `CLAUDE.md`'s section to a pointer | **RED** ×2 — *"does not carry the six rule lines; a pointer is not enough for the Supervisor, whose session the harness does not auto-inject the template into"* |
| **M2** — desync one word (`verdict` -> `outcome`) between the two copies | **RED** — *"not byte-identical to the template's"* |
| **M3** — rename the heading in the template | **RED** ×2 — the sub-agent channel is pinned even while `CLAUDE.md` is correct |

M2 and M3 are the ones that matter beyond M1: without them this fix would stay green on a repo whose
two copies had silently drifted, or one where the template lost the section and every sub-agent was
broken while the Supervisor looked fine.

### P2 — Recommended (structural, not a defect in this diff)

**`CLAUDE.md` is now at exactly 200/200 lines against `LINE_CAPS` in `test_vital_slice.py` — zero
slack.** That cap is real and was already at 200 before this task, which is why the six new rule lines
**forced** compression of the adjacent Self-monitoring prose. The agent did not choose to touch
neighbouring text gratuitously; it had no other way to land the change, and it said so accurately in
its commit message. Recorded because the consequence outlives this task: **the next addition to
`CLAUDE.md` has nowhere to go**, and the file's own comment calls the cap *"a ceiling with slack,
never an equality… expected to be retired or repointed after review"*. It is now an equality. Either
the cap gets raised deliberately or the next content change silently pays for itself by deleting
something else. Own row, not this one.

### P3 — Optional

**The forced compression traded away two pieces of rationale, not just words.** Gone: *"the session
that registered this rule ran 40+ lines, stacked tables and three-option menus"* — the concrete
provenance for why replies are not short by default; and *"forcing a rigid checkpoint would make the
pipeline less flexible for no real gain"* — the reason the compaction check is a judgment call rather
than a trigger. Both are recoverable from git history and neither is load-bearing for behaviour, so
this is P3, not P2. Flagged because "compressed to fit a cap" is exactly how a *why* quietly becomes
a *what*.

### Outstanding

Stage 5 `/verify` only — user-run in this project. **The surface is a live Supervisor session**, not a
spawned sub-agent: T100 passed its verify at the agent-config surface precisely because sub-agents
were never the broken channel. The observable claim is that a Supervisor session which has **not**
opened `agents/general-agent-template.md` still has the six rules in context and follows them.

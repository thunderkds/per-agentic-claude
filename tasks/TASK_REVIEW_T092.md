# TASK_REVIEW — T092: [Short Title]

> Sibling of `tasks/TASK_GUIDE_T092.md`. Everything here is **filled by the reviewer at Stage
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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_spawn_prompt_cache_note.py` — 6 tests: AC1 conclusion, AC2 do-not+T069, AC3 DDR pointer, AC4 line-cap+no-heading, AC5/AC6 numeric-literal traceability, AC8 banned-word negative |
| Verification command run | ☑ pass | `python3 -m pytest .claude/hooks/tests/ tests/ -q` → `725 passed in 9.12s` (719 baseline + 6 new, 0 regressions) |
| Negative cases hold | ☑ pass | M1 (deleted DDR pointer) → RED naming missing pointer (AC3+AC6). M2 (number not in DDR, `~99.9%`) → RED naming unsourced literal. **M3 (load-bearing: mutated the DDR's own `~97%`→`~99.9%`, SKILL.md untouched)** → RED, proving the expectation is derived from DDR-0004 at test time, not hardcoded. M4 (inserted "budget") → RED on AC8. Line-cap padding, non-blank (+5 lines, 83 total) → RED on AC4 (+ incidental AC5 hit from digits in filler). Line-cap padding, blank-only (+6 blank lines, 84 total) → RED on AC4. Every mutation's landing was confirmed via `grep -c`/count before recording its verdict, and each was reverted from the same saved-good copy (`/tmp/.../SKILL.md.withpassage`) before the next, per the guide's mutation-control note |
| verify | ☑ pass | **`/verify` run by the user 2026-08-24 — pass.** Surface was **the agent**, not the markup: a skill-instruction change is only real if it reaches the reasoning of whoever runs the skill (T082 precedent). Identical prompt in both trees ordering the assembler to *"keep the spawn prompt as SHORT as possible… drop the memory reference and the orienting content"*. **Wired (this branch): kept every element**, citing this passage's own reasoning — *"spawn context is ~97% cache-read and trimming saves negligible real cost while risking dropped context (T069's failure mode)"*. **Unwired control (`wt-t093`, `grep -c cache` → 0): dropped BOTH the `memory/MEMORY.md` reference and the orienting content**, rationalising *"this spawn is realistically a resume/verify pass, not a cold start, so the full requirement restatement isn't load-bearing"*. **A genuine behavioural delta — and stronger than T082 got**, whose control refused the payloads unprompted, leaving that task's value documentation-only. Here the skill's pre-existing element table (which already lists elements 2 and 4 as mandatory) did **not** hold under a plausible cost argument; the passage did. Note the control's failure mode is a confident wrong inference from the guide's ticked Completion Checklist, not laziness |
| **AC9: README.md / site/index.html grepped for contradicting spawn-cost claims** | ☑ pass | Run by the **Supervisor at Stage 4**, not the implementer — this row was blank in the branch as delivered, which is the P1 finding. Command and raw counts, both zero: `grep -ciE "spawn.{0,30}(cost|token)|token.{0,30}(cost|budget)|cache" README.md` → **0**; same command against `site/index.html` → **0**. No contradicting spawn-cost or token-cost claim exists in either surface, so **no correction was needed and none was made**. Recorded because AC9 was written unconditional on purpose: the "check first" phrasing is the antipattern that let T085's P1b recur inside T090, and a measured 0 pasted here is a completed AC, whereas a silent absence is indistinguishable from the skip the AC exists to prevent |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed: `.claude/skills/craft-spawn-prompt/SKILL.md` (the +6-line passage only), new test file, `tasks/TASK_REVIEW_T092.md`. Confirmed untouched: `docs/ddr/0004-*.md` (AC5's source of truth — diff empty after all mutation reverts), `templates/TASK_GUIDE_template.md` and `.claude/hooks/post_tool_trace.py` (AC7, `git diff main` empty), `CLAUDE.md`, `memory/*.md`. Did not review unrelated skills/hooks outside this change's blast radius |
| Full smoke suite still green (no regression) | ☑ pass | Same `725 passed in 9.12s` run above covers the full suite, not just the new file |
| **UI: Visual regression (diff or verdict pasted)** | ☐ N/A | Pure-documentation/test change, no UI component (UI/Design AC section not applicable per Hard-Stop Gate 6, Completion Checklist) |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☐ N/A | Same reason |
| **UI: Responsiveness at target viewports** | ☐ N/A | Same reason |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**: Verbatim prior content of `.claude/skills/craft-spawn-prompt/SKILL.md`'s
`#### 3. Assemble the prompt` step (72-line file, no cache references — grep confirmed 2026-08-24),
captured before any implementation commit for this task:

```
#### 3. Assemble the prompt
Both shapes reuse the same checklist proven in `bugfix` Step 4; only element 2 and the presence of element 3 change:

| # | Element | Standard guide | Bugfix-flavored guide |
|---|---|---|---|
| 1 | Guide pointer | `tasks/TASK_GUIDE_Txxx.md` path | same |
| 2 | Orienting content | Guide's Restated Intent / Requirement section, verbatim | Confirmed Mental Model section, verbatim |
| 3 | First-action skill invocation | Only if the task explicitly requires one (e.g. `migration-safety` for schema work) — otherwise omit | `Skill({ skill: "diagnose" })` as the first action — always present |
| 4 | Memory reference | The **path** `memory/MEMORY.md`, with an instruction to read it in full. Do **not** paste its contents | same |
| 5 | Agent-guide pointer | `.claude/agents/<role>.md` from the guide's `**Agent guide**` field | same |
| 6 | Trace-attribution instruction | The active-task state-file line below, verbatim | same |
| 7 | Demonstration BEFORE-capture instruction | The BEFORE-capture line below, verbatim | same — for a bugfix guide, this is naturally satisfied by the Phase 1 repro loop the `diagnose` first action already builds; the instruction still restates the rule so the agent doesn't skip it under time pressure |

Any caller-supplied inputs (e.g. bugfix's fixed "invoke diagnose first" instruction) are accepted as parameters to this step, not re-derived.
```

**AFTER**: Same step, plus the new passage inserted after the pre-existing "Any caller-supplied
inputs..." sentence (line count 72 → 78, +6, no new heading):

```
Any caller-supplied inputs (e.g. bugfix's fixed "invoke diagnose first" instruction) are accepted as parameters to this step, not re-derived.

**Spawn-prompt size is not the cost lever (DDR-0004).** ~97% of injected context bills as a cache
read, so trimming it recovers roughly a tenth of its nominal token count — spawn **count**, not
size, is what costs. Do not trim guide refs, the `memory/MEMORY.md` path, or orienting content to
"save tokens": T069 showed that context does not arrive on its own. Numbers:
`docs/ddr/0004-uphold-hard-stop-gate-1-over-spawn-elimination.md`.
```

**DELTA**: A Supervisor running `craft-spawn-prompt` is now told, inside the skill itself, that
spawn-prompt size is ~free (cache read) and spawn count is the real cost lever — before this task
the finding lived only in a hook, a DDR, and two cold memory files, none of which is read while
assembling a spawn prompt.

**WITNESS**: Common-Infrastructure-Agent, T092, 2026-08-24T09:07:30Z–2026-08-24T09:11:20Z (session
event trace); Supervisor to independently re-run M3/M4 at Stage 4 per the guide's Evaluation note.

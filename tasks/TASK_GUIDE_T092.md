# TASK_GUIDE — T092: Carry the cache-read finding into `craft-spawn-prompt`
**Date**: 2026-08-24
**Complexity Level**: C1
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
5. Note the **Complexity Level** above and apply the matching process (brainstorm / decompose / verify depth / model) from the Complexity matrix in your role guide
6. C1 touching three known files — `memory/codebase-map.md` is optional here, not required

Also read before implementing, because the whole task is about their content reaching one place:
- `docs/ddr/0004-uphold-hard-stop-gate-1-over-spawn-elimination.md` (the source of the claim)
- `.claude/skills/craft-spawn-prompt/SKILL.md` (the destination, 72 lines today)

---

## Requirement (Pillar 1 — Adapt the requirement)

User request, 2026-08-24, verbatim in substance:

> "checking if we cover the cache in the kits" … *(on being shown the finding)* … "open a Stage 2 row for it"

The coverage check found this. Cache is covered **as measurement**, and covered well:

- `.claude/hooks/post_tool_trace.py:70-119` records `cache_creation_input_tokens`,
  `cache_read_input_tokens`, and the flattened `cache_creation_5m` / `cache_creation_1h` TTL tiers
  on every spawn record.
- T061's A/B (`memory/learnings.md:677`): arm B added **1,115 tokens of novel prompt text** and moved
  `cache_creation` by **−1**, because the spawn prompt is already inside the Supervisor's cached
  context before the agent starts, so nearly everything injected bills as a cache read.
- T067's first production telemetry: **83,802 tokens at 97.6% cache read**
  (`docs/ddr/0004-…:20`).
- DDR-0004's conclusion (`:81-82`): trimming injected context recovers roughly a tenth of its nominal
  token count, so spawn **count**, not spawn **size**, is the cost lever.

`.claude/skills/craft-spawn-prompt/SKILL.md` contains **zero** cache references — grep confirmed
2026-08-24. The finding lives in a hook, a DDR, and two cold memory files; none of those is read while
assembling a spawn prompt. The skill that most directly acts on the conclusion is the one place it
never reached.

**Restated intent** (Supervisor's interpretation, in the project's domain language):
> A Supervisor assembling a spawn prompt should be told, in the skill it is already running, that
> spawn-prompt size is not a cost lever and spawn count is — so it does not spend effort trimming
> guide refs, the memory path, or orienting content to "save tokens", recovering ~a tenth of a nominal
> count while losing exactly the context T069 proved does not arrive on its own.

**Value framing — state it plainly in the guide and do not overclaim it.** This task prevents wasted
optimization effort. It does not make anything faster, cheaper, or newly possible. A paragraph is the
right size of response to that; a section, a cost model, or an instrument is not.

**Out of scope** (what this task explicitly does NOT do):
- Any new hook, any new gate, any change to `.claude/settings.json`.
- Any token budget or cost field on `templates/TASK_GUIDE_template.md`.
- Any change to `post_tool_trace.py` or to what telemetry is recorded.
- Any re-measurement of cache behaviour — T061/T067 stand; this task transcribes, it does not verify.
- Any change to `docs/ddr/0004-*.md` itself. It is the source of truth here and must stay untouched,
  or the AC5 test is comparing a file against its own edited source.

**Requirement Refs**: **N/A — `PRD.md` does not exist in this repo**, and its absence is structural,
not an oversight: this repo *is* the kit, and `PRD.md` is an artifact the kit generates in downstream
projects at Phase 0. The requirement traces to the user request quoted above and to DDR-0004, both
named at file-and-line in the Acceptance Criteria. Do not invent an FR-NNN to fill the field.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (Supervisor, 2026-08-24 — the user read the
      finding as stated above and asked for a row on exactly it)
- [x] Domain terms align with `PROJECT_SPEC.md` glossary — `Cold-start cost`, `Token Audit Log` and
      `$ per completed task` are already locked there from DDR-0001; this task introduces **no new term**
      and must not coin one
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] Requirement Refs handled — recorded N/A with a written reason above rather than fabricated

---

## Dependencies & Reachability

**Depends on**: `None` — DDR-0004 and the telemetry it rests on are merged and on `main`.

**Entry point**: `craft-spawn-prompt` — the skill is invoked by name from `CLAUDE.md` Stage 3 and from
the `bugfix` skill's Step 4; that literal string is grep-able in both.

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | `.claude/skills/craft-spawn-prompt/SKILL.md` states the measured conclusion: spawn-prompt **size** is ~free because nearly all injected context bills as a cache read, and spawn **count** is the cost lever | "the skill that most directly acts on the conclusion is the one place it never reached" |
| 2 | The same passage carries an explicit **do-not** — do not trim guide refs, the `memory/MEMORY.md` path, or orienting content from a spawn prompt to save tokens — naming T069 as the reason context does not arrive on its own | Restated intent, "losing exactly the context T069 proved does not arrive on its own" |
| 3 | The passage points at `docs/ddr/0004-uphold-hard-stop-gate-1-over-spawn-elimination.md` **by filename** for the numbers, and does not restate the derivation | Value framing — "a paragraph is the right size of response" |
| 4 | The addition is **≤ 8 lines** net to `SKILL.md` (72 → ≤ 80), and adds no new `##`/`###` heading | Value framing; T071's +8-lines-per-guide precedent |
| 5 | A new test asserts every percentage- or token-count-shaped literal in the added passage **also appears in `docs/ddr/0004-*.md`**, reading that file at test time — never a hardcoded expected value | "no number quoted as a target"; T088 M3 / T090 SC4 pattern |
| 6 | The same test fails if the DDR pointer of AC3 is absent from `SKILL.md` | AC3 |
| 7 | `templates/TASK_GUIDE_template.md` and `.claude/hooks/post_tool_trace.py` are **byte-identical to `main`** | Out of scope list |
| 8 | The passage phrases every number as a **measurement with a date/task attribution**, never as a target, budget, threshold or goal — asserted negatively against the words `budget`, `target`, `limit`, `at most`, `should be under` within the added passage | "a number with no live instrument becomes a target" — T071, DDR-0001, DDR-0002, T063 |
| 9 | `README.md` and `site/index.html` are grepped for existing spawn-cost / token-cost claims, the counts are pasted into the review, and any claim found to contradict AC1 is corrected in the same task | The recorded "check first" antipattern — see Approach |
| 10 | Full suite green: 719 passed baseline + the new test(s), 0 regressions | Hard-Stop Gate 5 |

---

## Evaluation & Acceptance (How we know the agent worked correctly)

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | `SKILL.md` as shipped by this task | New test passes; `wc -l` ≤ 80; no new heading | automated test |
| 2 | **M1 (mutation control)** — delete the DDR filename pointer from `SKILL.md` | Test goes **RED**, naming the missing pointer | automated test, run and reverted |
| 3 | **M2 (mutation control)** — change a number in the added passage to one absent from DDR-0004 (e.g. `97.6%` → `99.9%`) | Test goes **RED**, naming the unsourced literal | automated test, run and reverted |
| 4 | **M3 (mutation control, load-bearing)** — leave `SKILL.md` untouched and change the number **in `docs/ddr/0004-*.md`** instead | Test goes **RED**. This is the only control that proves the expectation is derived from the DDR **at test time** rather than hardcoded; if this stays green the test is vacuous and AC5 is not met, whatever M2 did | automated test, run and reverted |
| 5 | **M4 (mutation control)** — insert the word `budget` into the added passage | AC8's negative assertion goes **RED** | automated test, run and reverted |
| 6 | Pad the added passage past the cap with **both blank and non-blank lines** | The ≤8-line assertion goes RED in both forms | automated test, run and reverted |
| 7 | `git diff main -- templates/TASK_GUIDE_template.md .claude/hooks/post_tool_trace.py` | Empty output | command |

> Every mutation above must be confirmed to have **landed** (`git diff --stat` non-empty, or `grep`
> the mutated string) **before** its RED/GREEN verdict is recorded. This repo has had a control
> reported as non-reproducible when the `sed` had simply matched nothing (T083), and has 6 recorded
> "a checkmark is a claim, not a fact" incidents. The Supervisor will independently re-run M3 and M4.

### Verification Command (exact, runnable)

```bash
python3 -m pytest .claude/hooks/tests/ tests/ -q
```

> Note the two paths. Bare `pytest tests/ -q` collects **8** tests, not 719 — the harness suite lives
> under `.claude/hooks/tests/`, which pytest skips because `.claude` is hidden. This exact mistake
> shipped in the T083 guide and would have let an agent report green having run no regression tests.

### Evidence (filled by reviewer at Stage 4/5)

> Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T092.md`, copied from
> `templates/TASK_REVIEW_template.md`.

---

## Demonstration

> See `tasks/TASK_REVIEW_T092.md`.

---

## Approach

**Pattern reference**: `tests/test_provider_adapters.py` — T090's conformance test, which derives its
expected strings from `CLAUDE.md` **at test time** instead of hardcoding a copy. AC5's test should
imitate that shape exactly, with `docs/ddr/0004-*.md` in the role `CLAUDE.md` plays there.

**Vital slice**: one short paragraph inside the existing `#### 3. Assemble the prompt` step of
`SKILL.md`, plus one test file. Step 3 is the placement, not step 1 or the Karpathy block, because
step 3 is where a Supervisor is actually deciding what to put in the prompt — which is the moment the
trimming temptation occurs. A rule placed where the temptation is not felt is a rule that is read and
not applied (T041 → T066 → T069, three recorded instances).

**Cut list** (deliberately not built — cuts, not deferrals):
- No `#### 7. Cost note` section. A new step implies a new action; there is no action here, only a
  constraint on an existing one.
- No cost model, no per-model pricing, no worked example.
- No token budget field on the TASK_GUIDE template.
- No assertion that the *Supervisor* obeyed the rule — unenforceable, and T091 is on the board for
  exactly the failure of writing an unenforced note.
- No backfill into `bugfix` Step 4. It delegates to this skill; duplicating the paragraph there would
  create the second source of truth `CLAUDE_LEGACY.md` (629 hand-synced lines) is the standing warning
  against.

**On AC9 — this is deliberately not conditional.** The obvious phrasing would be *"update `site/` only
if it already carries a spawn-cost claim — check first."* That exact shape is a recorded antipattern in
`memory/learnings.md`: T090's site row said "check first", the implementer checked correctly, measured
0, and left the site silent while `README.md` pointed at it as the full reference — which was T085's
P1b recurring in the same file for the same reason, caught by the user rather than by any gate. So AC9
mandates the grep **unconditionally** and makes its counts a review artifact. If the counts are 0, the
finding is "0, no contradiction, nothing to correct" — that is a completed AC, not a skipped one.

---

## Edge Case Checklist

- [ ] The `%` and comma-grouped forms differ between files (`97.6%` vs `~97%`, `83,802` vs `83802`).
      AC5's extractor must normalise, or it will fail on a faithful quotation and pass on an unfaithful
      one — the inversion that matters.
- [ ] `docs/ddr/0004-*.md` must be globbed, not hardcoded by full filename in the test's *reading* path,
      or a future DDR rename silently turns the test vacuous (file-not-found handled as "nothing to
      compare"). Fail loudly if the glob matches zero files.
- [ ] `test_skill_spec_conformance.py` caps `SKILL.md` at 500 lines — no conflict at 80, but run the
      full suite rather than assuming this is the only guard on this file.
- [ ] `test_skill_reference_pointers.py` exists and may assert on cross-skill references; a new
      filename pointer inside a SKILL.md could trip it. Check before assuming AC3 is free.
- [ ] The word `cache` already appears in `map-codebase/SKILL.md` only as `__pycache__`. Any repo-wide
      grep used as evidence must exclude that, or it will report false coverage.
- [ ] Do not let the passage read as if the pipeline should spawn fewer agents. DDR-0004 **upheld**
      Hard-Stop Gate 1 over spawn elimination — "spawn count is the lever" is a cost observation, not a
      licence to skip spawns, and a passage implying otherwise would contradict the DDR it cites.

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `.claude/skills/craft-spawn-prompt/SKILL.md` | +≤8 lines inside `#### 3. Assemble the prompt` — the conclusion, the do-not, the DDR pointer |
| `.claude/hooks/tests/test_spawn_prompt_cache_note.py` | New. AC5/AC6/AC8 assertions, expectations derived from `docs/ddr/0004-*.md` at test time |
| `README.md` / `site/index.html` | **Only if** AC9's grep finds a contradicting spawn-cost claim. Report the counts either way |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `docs/ddr/0004-uphold-hard-stop-gate-1-over-spawn-elimination.md` | The source of truth AC5 compares against. Editing it makes the test compare a file to its own edited source. M3 mutates it **temporarily** and reverts — that is the control, not a change |
| `templates/TASK_GUIDE_template.md` | AC7 byte-identity; explicit cut |
| `.claude/hooks/post_tool_trace.py` | AC7 byte-identity; telemetry is out of scope |
| `CLAUDE.md` | The rule belongs where the work happens, not in the always-injected file. Adding it here re-opens the size question T090 just closed |
| `memory/*.md` | Supervisor-only writes (Memory Write Protocol) |

> If you believe one of these must change, **stop and report to the Supervisor**. T090's implementer
> touched a Must-NOT-Touch file for a defensible reason and the narrow form was accepted — the
> acceptable path was disclosure first, not a good reason found afterwards.

---

## Test Plan

1. Write `test_spawn_prompt_cache_note.py` **first** and observe it RED against today's `SKILL.md`
   (which has zero cache references) — the red must name the missing passage, not error on import.
2. Add the passage to `SKILL.md`. Confirm GREEN.
3. Run M1–M4 and the two line-cap paddings (SC2–SC6), confirming each mutation **landed** before
   recording its verdict, and reverting each. M3 is the one that decides whether AC5 is real.
4. Run AC9's greps; paste raw counts into the review regardless of outcome.
5. `python3 -m pytest .claude/hooks/tests/ tests/ -q` → expect 719 + new, 0 regressions.
6. `git diff main -- templates/TASK_GUIDE_template.md .claude/hooks/post_tool_trace.py` → empty.

---

## Completion Checklist

- [ ] Implementation done
- [ ] Self-review: `Skill({ skill: "code-review" })` run
- [ ] Security review: **N/A** — Low risk, documentation plus one read-only test, no runtime code path
- [ ] Lint passes
- [ ] Tests written AND pass — output pasted into `tasks/TASK_REVIEW_T092.md`'s Evidence table (Hard-Stop Gate 5)
- [ ] UI/Design Evidence rows: **☐ N/A** — pure-documentation task, no UI component (UI/Design AC section deleted from this guide per Hard-Stop Gate 6)
- [ ] `Skill({ skill: "verify" })` run by the **user** — the Supervisor cannot run it
- [ ] `memory/MEMORY.md` updated by the Supervisor (if new patterns learned)
- [ ] Supervisor notified: task ready for Stage 4 review

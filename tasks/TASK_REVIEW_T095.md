# TASK_REVIEW — T095: The merge gate cannot see worktree evidence, prescribes a disproved remedy, and blocks writes whose data mentions a push

> Sibling of `tasks/TASK_GUIDE_T095.md`. Everything here is **filled by the reviewer at Stage
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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_merge_gate_t095.py` (37 tests) and `.claude/hooks/tests/test_memory_hook_heredoc_data.py` (13 tests, the Supervisor-approved `post_bash_memory_update.py` reuse) — 50 new tests, all against constructed fixtures. Defect A: AC1 (worktree-only evidence found, at the entry point and at `has_filled_verify_row`), AC2 (review file nowhere → still `(no evidence row)`), AC3 ×6 fail-closed inputs re-asserted with the worktree search path active, enumeration-failure degradation, porcelain parsing. Defect B: AC4, AC5 (both directions), AC6. Defect C: AC7, AC8 ×3 (after the terminator, before the heredoc, on the header line), unterminated-heredoc fail-closed, terminator forms, here-string, multi-heredoc. AC9 anti-vacuity: `test_worktree_evidence_resolution_depends_on_the_fix` and `test_heredoc_allowance_depends_on_the_fix` — each reverts its fix in-place and asserts the scenario goes red again. |
| Verification command run | ☑ pass | `python3 -m pytest .claude/hooks/tests/ -q && python3 -m pytest tests/ -q` → `757 passed in 8.99s` then `40 passed in 0.05s`. Baseline was 707 before T095 (AC10 asks for ≥697/≥707); +50 is exactly this task's new tests (37 for the three merge-gate defects, 13 for the Supervisor-approved `post_bash_memory_update.py` reuse), no pre-existing test changed. Earlier run at 2026-08-31T09:18:56Z, before the scope addition, showed `744 passed`. |
| Negative cases hold | ☑ pass | Fail-closed is the whole risk here and is asserted from three sides: AC3's six named inputs (missing guide, missing review file, unreadable file, absent Evidence section, unfilled row, template `☐ pass` placeholder) all return False *with* the worktree path active; every `git worktree list` failure mode (git absent, non-zero exit, exception) degrades to main-checkout-only, never to allow; and AC8's anti-evasion probe confirms a real `; git push` after a heredoc terminator still blocks. Both AC9 anti-vacuity probes go red on a reverted fix, so none of the above is vacuous. |
| verify | ☐ pass / ☐ fail / ☐ N/A | [what was observed — must literally state "pass" or "fail" here too, e.g. "skill run, feature confirmed working — pass": the merge gate scans this Notes column for the word "pass", not just the Result column] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☐ pass / ☐ fail | [what was reviewed vs. skipped, and why] |
| Full smoke suite still green (no regression) | ☑ pass | `tests/` 40 passed, unchanged. `.claude/hooks/tests/` 707 → 757, the delta being this task's own new tests only. |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | Pure-backend task: one Python hook, one new hook lib module, one test file. No UI component, no rendered surface. |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | Same reason — no UI surface in scope. |
| **UI: Responsiveness at target viewports** | ☑ N/A | Same reason — no UI surface in scope. |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**: Captured `2026-08-31T09:10:57Z` at HEAD `ce5c131` (`fix/t095-merge-gate`, no
implementation commit exists yet). The real hook is driven at its declared entry point —
`printf '%s' '<PreToolUse Bash event JSON>' | python3 .claude/hooks/pre_bash_block_unsafe_merge.py`
— against a constructed fixture repo (a git checkout with a real `git worktree`): board row **T900**
in Ready for Review, its guide's `### Evidence` section vacated to a T064 pointer, its filled
`☑ pass` verify row present **only** in `<worktree>/tasks/TASK_REVIEW_T900.md` on the task branch,
and a real non-error `pytest` trace record so only the evidence-row half of the gate is under test.

```
========================================================================
SCENARIO A+B - real push; evidence exists only in the worktree
------------------------------------------------------------------------
command sent:
git push origin fix/t900
--- hook exit: 0
--- hook stdout:
[hook:pre_bash] Pipeline gate failed — cannot push/merge:
  • Tasks in Ready for Review missing Stage 5 verify evidence: T900 (no evidence row)
Complete Stage 4 review and Stage 5 verify first.
  Note: a Bash command is attributed to a task only via CLAUDE_ACTIVE_TASK — run the task's verification command as `CLAUDE_ACTIVE_TASK=Txxx <command>` or no trace record is filed under it.

========================================================================
SCENARIO C - heredoc file write whose BODY mentions a push
------------------------------------------------------------------------
command sent:
cat > notes.md <<'EOF'
This document explains why the gate blocks a git push.
EOF

--- hook exit: 0
--- hook stdout:
[hook:pre_bash] Pipeline gate failed — cannot push/merge:
  • Tasks in Ready for Review missing Stage 5 verify evidence: T900 (no evidence row)
Complete Stage 4 review and Stage 5 verify first.
  Note: a Bash command is attributed to a task only via CLAUDE_ACTIVE_TASK — run the task's verification command as `CLAUDE_ACTIVE_TASK=Txxx <command>` or no trace record is filed under it.

========================================================================
SCENARIO C-anti-evasion - same heredoc, real push after the terminator
------------------------------------------------------------------------
command sent:
cat > notes.md <<'EOF'
This document explains why the gate blocks a git push.
EOF
; git push origin fix/t900
--- hook exit: 0
--- hook stdout:
[hook:pre_bash] Pipeline gate failed — cannot push/merge:
  • Tasks in Ready for Review missing Stage 5 verify evidence: T900 (no evidence row)
Complete Stage 4 review and Stage 5 verify first.
  Note: a Bash command is attributed to a task only via CLAUDE_ACTIVE_TASK — run the task's verification command as `CLAUDE_ACTIVE_TASK=Txxx <command>` or no trace record is filed under it.
```

All three defects reproduce in one capture:
- **Defect A** — scenario A+B blocks with the literal suffix `(no evidence row)` even though a
  filled `☑ pass` verify row exists in the worktree the push is coming from. `has_filled_verify_row`
  resolves under the main checkout's `tasks/` only, so evidence written where Stage 3 actually
  happens is invisible.
- **Defect B** — every block prints `a Bash command is attributed to a task only via
  CLAUDE_ACTIVE_TASK — run the task's verification command as CLAUDE_ACTIVE_TASK=Txxx <command>`,
  the mechanism `lib/task_context.py`'s docstring records as measured-dead (a hook is a *sibling*
  process of the tool call and never inherits the subshell's env). The word "only" is false: the
  state file is a second, working channel. Line 84's comment carries the same false premise.
- **Defect C** — scenario C is a `cat > notes.md` heredoc file write with **no git command anywhere
  outside the heredoc body**, yet the gate blocks it as a push: it classifies the command by the
  data the command carries. Scenario C-anti-evasion is the control the fix must not break — a real
  `; git push` after the terminator, which must keep blocking.

**AFTER**: Captured `2026-08-31T09:17:56Z` at HEAD `c8eb0fd`, same fixture, same entry point, same
three commands — plus three **control** scenarios run against the same fixture with the review file
deleted, so "the gate went quiet" can be told apart from "the gate stopped gating".

```
========================================================================
SCENARIO A+B - real push; evidence exists only in the worktree
------------------------------------------------------------------------
command sent:
git push origin fix/t900
--- hook exit: 0
--- hook stdout:
(silent — gate allowed)

========================================================================
SCENARIO C - heredoc file write whose BODY mentions a push
------------------------------------------------------------------------
command sent:
cat > notes.md <<'EOF'
This document explains why the gate blocks a git push.
EOF

--- hook exit: 0
--- hook stdout:
(silent — gate allowed)

========================================================================
SCENARIO C-anti-evasion - same heredoc, real push after the terminator
------------------------------------------------------------------------
--- hook exit: 0
--- hook stdout:
(silent — gate allowed)      [evidence is present, so there is nothing to block on]

========================================================================
SCENARIO A-control - no evidence anywhere; gate must still block (AC2)
------------------------------------------------------------------------
command sent:
git push origin fix/t900
--- hook exit: 0
--- hook stdout:
[hook:pre_bash] Pipeline gate failed — cannot push/merge:
  • Tasks in Ready for Review missing Stage 5 verify evidence: T900 (no evidence row)
Complete Stage 4 review and Stage 5 verify first.
  Note: if a task above is missing its trace record rather than its evidence row, attribute your Bash calls by writing the active-task state file first: `mkdir -p <main-checkout>/.claude/hooks/.state && printf '%s\n%s\n' "Txxx" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > <main-checkout>/.claude/hooks/.state/active_task` — using the literal absolute path of the main checkout (not $CLAUDE_PROJECT_DIR, which is empty inside a Bash tool call, and not a relative path, which resolves into your worktree). Valid for CLAUDE_ACTIVE_TASK_STATE_MAX_AGE_S seconds (default 6h). CLAUDE_ACTIVE_TASK=Txxx <command> does NOT work from inside a session: a hook is a sibling process of the tool call and never inherits its subshell (T047). The env var only takes effect when set before the session starts.

========================================================================
SCENARIO C-control - heredoc write, still not a push even with no evidence
------------------------------------------------------------------------
command sent:
cat > notes.md <<'EOF'
This document explains why the gate blocks a git push.
EOF

--- hook exit: 0
--- hook stdout:
(silent — gate allowed)

========================================================================
SCENARIO C-anti-evasion-control - real push after terminator, no evidence (AC8)
------------------------------------------------------------------------
command sent:
cat > notes.md <<'EOF'
This document explains why the gate blocks a git push.
EOF
; git push origin fix/t900
--- hook exit: 0
--- hook stdout:
[hook:pre_bash] Pipeline gate failed — cannot push/merge:
  • Tasks in Ready for Review missing Stage 5 verify evidence: T900 (no evidence row)
Complete Stage 4 review and Stage 5 verify first.
  Note: if a task above is missing its trace record rather than its evidence row, attribute your Bash calls by writing the active-task state file first: ... [full remedy as above]
```

Read against BEFORE, scenario by scenario:
- **Defect A (AC1)** — scenario A+B went from `T900 (no evidence row)` to silent. The filled
  `☑ pass` row is still only in the worktree, on the task branch; the gate now enumerates
  `git worktree list --porcelain` and finds it there. Note this scenario runs against a **real** git
  worktree, so it exercises the live enumeration, not the injected fixture list the unit tests use.
- **Defect A fail-closed (AC2)** — scenario A-control deletes that same file and the gate blocks
  again with the identical `(no evidence row)` suffix. Searching more places did not become a reason
  to skip the check.
- **Defect B (AC4/AC5)** — every block message now carries the state-file remedy with its
  absolute-path requirement, names `$CLAUDE_PROJECT_DIR` and relative paths as the two ways to get
  it wrong, and states plainly that `CLAUDE_ACTIVE_TASK=Txxx <command>` does not work from inside a
  session — while still crediting the env var in the one context where it does. The false "only" is
  gone. AC6's line-84 comment is corrected in the same terms.
- **Defect C (AC7)** — the heredoc write is silent in both passes, with evidence present and with it
  absent, so the allowance comes from recognising the body as data rather than from the gate having
  nothing to say.
- **Defect C anti-evasion (AC8)** — scenario C-anti-evasion-control is the one that matters: the
  same heredoc followed by a real `; git push` after the terminator still blocks. Stripping stops at
  the terminator the header declares, so the fix did not become a way to smuggle a push past the
  gate.

**AFTER (scope addition, Supervisor-approved 2026-08-31)**: `post_bash_memory_update.py` carried
the same defect C in its own file — it demanded a diff-driven memory pass for a git operation that
never happened, twice: while writing `tasks/TASK_GUIDE_T095.md`, and again on this task's own
commits. The Supervisor approved reusing `lib/shell_data.strip_heredoc_bodies` there. Captured
`2026-08-31T09:25:04Z`, driving both the pre-fix version (`git show HEAD:...`) and the fixed one
over the same three commands:

```
========================================================================
BEFORE (HEAD, pre-fix)
  heredoc write, body mentions a push, no git command on the line
    -> FIRES memory-update prompt
  a real push
    -> FIRES memory-update prompt
  heredoc write + a real push after the terminator
    -> FIRES memory-update prompt

========================================================================
AFTER  (working tree)
  heredoc write, body mentions a push, no git command on the line
    -> silent
  a real push
    -> FIRES memory-update prompt
  heredoc write + a real push after the terminator
    -> FIRES memory-update prompt
```

One line changed at the matcher plus a guarded import — no second copy of the stripping logic. The
guard degrades in the **opposite** direction to the merge gate's identically-shaped import, and
deliberately: the merge gate blocks pushes, so an unavailable resolver must become a block; this
hook only ever prompts, so it falls back to the pre-T095 raw-string search. A hook that goes silent
after a real push loses information; one that over-prompts on a heredoc costs a paragraph. Covered
by 13 tests in `.claude/hooks/tests/test_memory_hook_heredoc_data.py`, including the anti-evasion
shape, the unterminated-heredoc case, the fallback direction, and an anti-vacuity probe that replays
the heredoc against the pre-fix hook and asserts it fired.

**DELTA**: A Stage 5 push from a worktree now passes the merge gate on the evidence the agent
actually wrote in that worktree — no Supervisor hand-landing the review file on the integration
branch first, which is what T094, T096 and T097 each paid — a document that *discusses* pushing can
be written with a heredoc without being blocked as a push, and an operator who is blocked is handed
the attribution remedy that works instead of the one T047 measured as dead.

**WITNESS**: Implemented and captured by the Common-Infrastructure-Agent (T095) on 2026-08-31.
BEFORE `09:10:57Z` at `ce5c131`, AFTER `09:17:56Z` at `c8eb0fd`. The verification command's own run
is corroborated by a real, non-error `Bash` record in `memory/event-trace/T095.jsonl` at
`2026-08-31T09:18:56.726352+00:00`:
`{"command": "python3 -m pytest .claude/hooks/tests/ -q && python3 -m pytest tests/ -q", ...}`.

> **Attribution caveat for the reviewer — please read before merging.** That record is in the
> **worktree's** `memory/event-trace/`, not the main checkout's. This session's
> `$CLAUDE_PROJECT_DIR` is the worktree, so both `post_tool_trace.py` and `task_context.py` resolve
> their roots there; the state file written at the main-checkout absolute path (per the spawn
> prompt) was never read, and every call before this was diagnosed landed in the worktree's
> `_untagged.jsonl`. `memory/event-trace/` is gitignored, so the record does not travel with the
> branch. Independent Stage 5 `verify` is user-invoked anyway — running the verification command
> from the main checkout will file the corroborating record where the gate reads it. Details and
> the suggested follow-up are in the agent's report; the state file's anchoring is explicitly out of
> T095's scope, so nothing was changed about it here.

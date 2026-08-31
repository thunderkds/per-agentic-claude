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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☐ pass / ☐ fail | [test file path(s) — required before Done] |
| Verification command run | ☐ pass / ☐ fail | [paste actual output] |
| Negative cases hold | ☐ pass / ☐ fail | |
| verify | ☐ pass / ☐ fail / ☐ N/A | [what was observed — must literally state "pass" or "fail" here too, e.g. "skill run, feature confirmed working — pass": the merge gate scans this Notes column for the word "pass", not just the Result column] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☐ pass / ☐ fail | [what was reviewed vs. skipped, and why] |
| Full smoke suite still green (no regression) | ☐ pass / ☐ fail | |
| **UI: Visual regression (diff or verdict pasted)** | ☐ pass / ☐ fail / ☐ N/A | [screenshot path or LLM verdict — required for UI tasks, Hard-Stop Gate 6] |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☐ pass / ☐ fail / ☐ N/A | [method used + output] |
| **UI: Responsiveness at target viewports** | ☐ pass / ☐ fail / ☐ N/A | [viewports tested, any overflow findings] |

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

**AFTER**: [same command, post-change] OR [verbatim excerpt of the new content]

**DELTA**: [one sentence — what a user can now do that they could not before]

**WITNESS**: [who ran it and when — derived from `memory/event-trace/T095.jsonl`, never the
implementing agent alone]

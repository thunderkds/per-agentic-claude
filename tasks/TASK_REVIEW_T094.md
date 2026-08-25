# TASK_REVIEW — T094: The hook suite is red on v2's first commit — three failures, two unrelated causes

> Sibling of `tasks/TASK_GUIDE_T094.md`. Everything here is **filled by the reviewer at Stage
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

**BEFORE**: real, timestamped run of the guide's Verification Command against the unmodified
worktree at `04c8f7e` (working tree clean except this untracked review file), captured before any
implementation commit exists:

```
$ git status --porcelain
?? tasks/TASK_REVIEW_T094.md
$ date -u +%Y-%m-%dT%H:%M:%SZ
2026-08-25T04:48:49Z
$ git rev-parse --short HEAD
04c8f7e

$ python3 -m pytest .claude/hooks/tests/ -q
...
E       AssertionError: no board row in an earlier-scanned section bold-references a task owning a
E       row in a later-scanned one (e.g. a Done row naming a Todo follow-up) - if that was a
E       deliberate un-bolding, it is T093's workaround returning; the anchored resolver makes it
E       unnecessary, and removing it blinds test_find_kanban_section_on_real_current_board to the
E       defect T093 fixed
E       assert []

.claude/hooks/tests/test_kanban_section_parsing.py:397: AssertionError
=========================== short test summary info ============================
FAILED .claude/hooks/tests/test_agent_guide_dedup.py::test_ac7_per_role_loaded_size_is_strictly_lower_than_baseline[c-infra]
FAILED .claude/hooks/tests/test_kanban_section_parsing.py::test_live_board_still_carries_a_cross_section_bold_reference
2 failed, 692 passed in 9.20s

$ python3 -m pytest tests/test_provider_adapters.py -q
...........                                                              [100%]
11 passed in 0.02s

$ python3 -c "print(len(open('.claude/agents/general-agent-template.md').read()))"
3717
```

**Trap already fired — read with the above.** The guide records *three* failures; this baseline
shows *two*. The missing one is `test_find_kanban_section_on_real_current_board`, and it is not
fixed: commit `04c8f7e` (`plan(T094)`) registered T094's own Todo row on `PROJECT_KANBAN.md`, which
re-populated the Todo section and turned that test green with no code change — exactly the
documented Trap. It will go red again the moment the board drains. Per the guide it is **not**
accepted as the fix; AC2 proves the real fix against a drained-board fixture instead.

A pre-registration capture (`04c8f7e~1`) was attempted via `git archive` into a scratch tree and
discarded as invalid, not quoted here: the extracted tree has no `.git`, so the ~30 tests that read
baselines via `git show <sha>:<path>` fail spuriously (32 failed / 661 passed) — noise, not signal.
The board file itself was left untouched (`PROJECT_KANBAN.md` is a Files-Must-NOT-Touch entry).

**AFTER**: [same command, post-change] OR [verbatim excerpt of the new content]

**DELTA**: [one sentence — what a user can now do that they could not before]

**WITNESS**: [who ran it and when — derived from `memory/event-trace/Txxx.jsonl`, never the
implementing agent alone]

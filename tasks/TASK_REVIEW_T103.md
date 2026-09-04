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

**AFTER**: [verbatim excerpt of the new content — filled after the edit]

**DELTA**: The six Response Standard rules now live in `CLAUDE.md` itself (auto-injected every
session), so they reach the Supervisor with no unenforced "go open the template" step; three tests
pin the two copies against drift and pin the sub-agent channel too.

**WITNESS**: [who ran it and when — derived from `memory/event-trace/T103.jsonl`, never the
implementing agent alone]

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

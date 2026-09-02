# TASK_REVIEW — T100: One response standard for the Supervisor and every sub-agent

> Sibling of `tasks/TASK_GUIDE_T[NNN].md`. Everything here is **filled by the reviewer at Stage
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

**BEFORE** (verbatim prior content, captured 2026-09-02 before the first implementation commit):

`CLAUDE.md` lines 19-25 — `## Supervisor Communication Style`, opening paragraph:

```
## Supervisor Communication Style

The harness already keeps chat replies short and plain by default — no extra rule needed for that.
The one thing to guard against: don't let that brevity bleed into project artifacts. Keep
`PROJECT_KANBAN.md` rows, `TASK_GUIDE_Txxx.md` Evidence, `memory/decisions.md`, and commit messages
fully detailed — those are the audit trail, not conversation, and simplifying them loses real
information.
```

`agents/general-agent-template.md` — there is **no** `## Response Standard` section. Verbatim, the
file's complete section list before this task:

```
$ grep -n '^## ' agents/general-agent-template.md
9:## Base Rules (Inherited by All Sub-Agents)
33:## Search Before You Build
54:## Output Requirements (Every Task)
61:## Staleness Guard
```

`tests/` — no test asserts anything about a response standard:

```
$ grep -rl "Response Standard" tests/ CLAUDE.md agents/
(no matches)
```

**AFTER**: [same command, post-change] OR [verbatim excerpt of the new content]

**DELTA**: [one sentence — what a user can now do that they could not before]

**WITNESS**: [who ran it and when — derived from `memory/event-trace/Txxx.jsonl`, never the
implementing agent alone]

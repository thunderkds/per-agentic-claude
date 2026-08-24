# TASK_REVIEW — T090: Provider adapters — make "works with any provider" structurally true

> Sibling of `tasks/TASK_GUIDE_T090.md`. Everything here is **filled by the reviewer at Stage
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

**BEFORE**: Verbatim prior content, captured 2026-08-24T03:15Z before any implementation commit.

`AGENTS.md` (12 lines, entire file):
```
# AGENTS.md

This is a thin mirror for non-Claude agentic CLIs (Codex, etc.). `CLAUDE.md` and
`.claude/agents/` remain canonical — if anything here conflicts with those, they win.

Before any work:
- Read `PROJECT_SPEC.md`, your `tasks/TASK_GUIDE_Txxx.md`, and these base rules.
- Work only inside your assigned worktree; touch only the predicted files (Surgical Changes).
- Build test-first; a task is done only when its verification command passes.
- Stop and ask on any ambiguity — never guess.

See `docs/MULTI_AGENT.md` for full dispatch recipes and what does/doesn't port across CLIs.
```

`.cursor/rules/agent-base.mdc` — does not exist (`ls .cursor/rules/agent-base.mdc` returned "No such
file or directory"; no `.cursor/` directory exists in the repo at all).

`MANIFEST` — 6 non-comment lines, no `.cursor/rules` entry:
```
.claude/agents
.claude/skills
.claude/hooks
templates
docs/claude-md
AGENTS.md
```

`docs/MULTI_AGENT.md` (relevant excerpt, "Shared AGENTS.md" section): "It is **not required** for
the dispatch recipes above (the prompt already points at the guides) — it just removes repetition
and gives Cursor/Codex a default to fall back on. Keep it a thin mirror, not a second source of
truth." Its Cursor section only sketches `cursor-agent -p` dispatch and says mirroring
`.claude/agents/general-agent-template.md` into `.cursor/rules/agent-base.mdc` is a suggestion
("see below"), not a fact about an existing file.

`README.md` — carries no multi-provider claim beyond "A general-purpose multi-agent supervisor
framework for Claude Code." (line 3); no mention of Codex/Cursor/adapters anywhere in the file.

`tests/test_provider_adapters.py` — does not exist.

**AFTER**: [same command, post-change] OR [verbatim excerpt of the new content]

**DELTA**: [one sentence — what a user can now do that they could not before]

**WITNESS**: [who ran it and when — derived from `memory/event-trace/Txxx.jsonl`, never the
implementing agent alone]

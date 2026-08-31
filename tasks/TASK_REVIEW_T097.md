# TASK_REVIEW — T097: B2: Per-harness install projection and the AGENTS.md correction

> Sibling of `tasks/TASK_GUIDE_T097.md`. Everything here is **filled by the reviewer at Stage
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

**BEFORE**:

**(1) The `--harness` flag does not exist — throwaway repo, captured before any implementation commit:**

```
### BEFORE capture — T097 — host hungnguyenhuu-NUC11PAHi7 — UTC 2026-08-31T07:33:01Z
### repo HEAD under test: 6d43ada (no implementation commit exists)

$ cd /tmp/t097-before.O9920H && git init -q .   # throwaway repo
$ bash /home/hungnguyenhuu/workspace/pets/wt-t097/setup.sh --harness codex
[error] Unknown flag: --harness. Valid flags: --copy, --pack=<name>
exit=1

$ ls -la .codex/skills
ls: cannot access '.codex/skills': No such file or directory
exit=2

$ grep -c . MANIFEST-second-column  # no destination column exists today:
(no MANIFEST line has any second column)
```

**(2) A real Codex session cannot see any kit skill, and the `AGENTS.md` text that says so:**

```
### BEFORE (AC3, controlled probe) — UTC 2026-08-31T07:35:33Z — repo HEAD 6d43ada, no implementation commit
Three throwaway git repos, each containing ONE probe skill 'zzprobe-skills' in a different directory.
Command per repo: codex exec --sandbox read-only -C <repo> "List every skill available to you by name..."

/tmp/p-root    (skills/zzprobe-skills/SKILL.md)          -> imagegen, openai-docs, plugin-creator, skill-creator, skill-installer   [probe ABSENT]
/tmp/p-claude  (.claude/skills/zzprobe-skills/SKILL.md)  -> imagegen, openai-docs, plugin-creator, skill-creator, skill-installer   [probe ABSENT]
/tmp/p-codex   (.codex/skills/zzprobe-skills/SKILL.md)   -> imagegen, openai-docs, plugin-creator, skill-creator, skill-installer, zzprobe-skills   [probe FOUND]

Conclusion: Codex 0.149.1 discovers skills ONLY under .codex/skills. A kit install today writes
skills/ and .claude/skills -> neither is discovered, so no kit skill is available to Codex.

### BEFORE (Defect A) — verbatim AGENTS.md lines 29-33 at HEAD 6d43ada:
## What Codex cannot enforce here
Codex has no equivalent of Claude Code's hooks, skills, or `Skill`/`Agent` tooling. It cannot run
`code-review`, `security-review`, `verify`, `ship`, or `migration-safety`, and it does not get the
git-guardrails PreToolUse hook. Those stay on the Claude supervisor — see `docs/MULTI_AGENT.md`
("What does NOT port").
```

**AFTER**: [same command, post-change] OR [verbatim excerpt of the new content]

**DELTA**: [one sentence — what a user can now do that they could not before]

**WITNESS**: [who ran it and when — derived from `memory/event-trace/Txxx.jsonl`, never the
implementing agent alone]

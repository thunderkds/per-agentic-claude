# TASK_REVIEW — T106: [Short Title]

> Sibling of `tasks/TASK_GUIDE_T106.md`. Everything here is **filled by the reviewer at Stage
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

**BEFORE** (2026-09-06T00:00:00Z, captured before any T106 implementation commit — `git log -1` at
this point is `4617ac3 Release v2.0.0 — canon at plain root, per-harness install`, i.e. `README.md`
is unmodified from that commit):

Verbatim excerpt, `README.md` line 3 (opening framing — gap 3, gap 1):
```
A general-purpose multi-agent supervisor framework for Claude Code. Install once, deploy into any
```
(no version string appears anywhere in the file's 73 lines)

Verbatim excerpt, `README.md` lines 17-20 (site link + stale TODO — gap 4):
```
**Full reference** — architecture, the pipeline stages, packs, memory system, hooks table, custom
skills, and update flow — lives on the project site: [`site/index.html`](site/index.html)
*(repo-relative for now; the operator fills in the deployed `.vercel.app` URL here once T084's
deploy is run).*
```

Verbatim excerpt, `README.md` lines 44-45 (Codex install, no skip note — gap 2):
```
sh -c "$(curl -fsSL https://raw.githubusercontent.com/thunderkds/personal-agentic-claude/main/setup.sh)" -- --harness codex                    # Codex only
sh -c "$(curl -fsSL https://raw.githubusercontent.com/thunderkds/personal-agentic-claude/main/setup.sh)" -- --harness claude --harness codex   # both
```

Verbatim excerpt, `README.md` line 57 and line 73 (remaining `site/index.html` links):
```
[site](site/index.html) for the full Quick Start, Options table, and Update flow.
```
```
documented on the [site](site/index.html).
```

`RUNBOOK.md`'s "Deploying the landing site" section (lines 106-160) contains no `.vercel.app` URL
anywhere — confirmed via `grep -n "vercel.app" RUNBOOK.md` returning no matches before this task.

AC5's test run against the UNEDITED README, `sh tests/test_readme_current.sh`, real output:
```
FAIL: AC1: README does not mention 'v2.0.0' (RUNBOOK.md's newest release row)
PASS: AC2 setup: derived cap = 8192 bytes from lib/harness-fetch.sh
PASS: AC2 setup: derived oversize skill set = [bugfix craft-spawn-prompt diagnose write-better-skill]
FAIL: AC2: README must say oversize skills are SKIPPED (not truncated) for Codex
FAIL: AC2: README does not name currently-oversize skill 'bugfix'
FAIL: AC2: README does not name currently-oversize skill 'craft-spawn-prompt'
FAIL: AC2: README does not name currently-oversize skill 'diagnose'
FAIL: AC2: README does not name currently-oversize skill 'write-better-skill'

test_readme_current: FAILED
EXIT=1
```

**AFTER**: [same command, post-change] OR [verbatim excerpt of the new content]

**DELTA**: [one sentence — what a user can now do that they could not before]

**WITNESS**: [who ran it and when — derived from `memory/event-trace/Txxx.jsonl`, never the
implementing agent alone]

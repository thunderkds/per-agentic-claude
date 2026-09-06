# TASK_REVIEW — T107: [Short Title]

> Sibling of `tasks/TASK_GUIDE_T107.md`. Everything here is **filled by the reviewer at Stage
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

**BEFORE**: verbatim prior content of the changed lines, captured 2026-09-06 before any
implementation commit:

- `README.md:1` — `# Supervisor Agent Deployment System`
- `PROJECT_SPEC.md:12` — `- **Name**: Supervisor Agent Deployment System`
- `setup.sh:2` — `# setup.sh — Supervisor Agent Deployment System installer (direct-to-repo, ADR-0001)`
- `update.sh:2` — `# update.sh — Supervisor Agent Deployment System updater (direct-to-repo, ADR-0001)`
- `MANIFEST:1` — `# MANIFEST — Supervisor Agent Deployment System` (added after Supervisor
  correction — the guide's baseline grep filtered on `--include='*.md,*.html,*.json,*.sh'` and
  missed this extensionless file; confirmed safe to edit since MANIFEST's own header states
  "Lines starting with # are comments" and `setup.sh` parses paths, not the banner)

AC5 guard, pre-edit: `grep -rn "personal-agentic-claude" setup.sh update.sh README.md | wc -l` → `9`

**AFTER**: verbatim new content of the five changed lines:

- `README.md:1` — `# Easy Kit`
- `PROJECT_SPEC.md:12` — `- **Name**: Easy Kit`
- `setup.sh:2` — `# setup.sh — Easy Kit installer (direct-to-repo, ADR-0001)`
- `update.sh:2` — `# update.sh — Easy Kit updater (direct-to-repo, ADR-0001)`
- `MANIFEST:1` — `# MANIFEST — Easy Kit`

AC5 guard, post-edit: `grep -rn "personal-agentic-claude" setup.sh update.sh README.md | wc -l` → `9` — unchanged.

Corrected verification command (per Supervisor's amendment — extension filters dropped since they
hid MANIFEST; `command grep` used because this shell's `grep` is a `ugrep`-wrapping function that
drops the `./` prefix and makes the exclusion filter silently match nothing):

```
sh scripts/validate.sh && sh scripts/smoke-install.sh && sh tests/test_readme_current.sh \
  && ! command grep -rn "Supervisor Agent Deployment System" . \
       --exclude-dir=.git \
     | command grep -v '^\./tasks/\|^\./memory/\|^\./RUNBOOK.md\|^\./PROJECT_KANBAN.md'
```

Real output, 2026-09-06:
- `scripts/validate.sh` → `validate.sh: PASS`
- `scripts/smoke-install.sh` → `smoke-install.sh: PASS`
- `tests/test_readme_current.sh` → `test_readme_current: ALL PASS`
- Raw grep (pre-exclusion) matched only in `./PROJECT_KANBAN.md` (rows T107, T106 — historical
  registration text) and `./tasks/TASK_REVIEW_T107.md` / `./tasks/TASK_GUIDE_T107.md` (this task's
  own guide/review docs) — all protected paths.
- After the exclusion filter: zero lines remained (`grep` exit 1 = no match found).
- Overall command exit: `0` (PASS).

**DELTA**: [one sentence — what a user can now do that they could not before]

**WITNESS**: [who ran it and when — derived from `memory/event-trace/Txxx.jsonl`, never the
implementing agent alone]

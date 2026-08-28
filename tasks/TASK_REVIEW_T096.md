# TASK_REVIEW — T096 (B1): Relocate canonical `skills/` and `agents/` to plain root

**Task ID**: T096
**Branch**: `feat/t096-canon-plain-root`
**Agent**: Common-Infrastructure-Agent
**Guide**: `tasks/TASK_GUIDE_T096.md`
**Date**: 2026-08-28

---

## Guide defects found at intake (reported to Supervisor, work proceeded)

Recorded here because the guide's Requirement Fidelity Gate asserts facts that do not hold
against this tree. Neither defect changes the live surface being modified.

### D1 — `DDR-0007` does not exist

Mandatory Startup step 6 requires reading
`docs/ddr/0007-canonical-skills-and-agents-at-plain-root.md` **in full**, calling it "the decision
this task implements". The Fidelity Gate ticks "Requirement Refs resolve: `DDR-0007` exists on
disk". It does not exist — not in the worktree, and not on any local or remote branch:

```
$ ls docs/ddr/
0001-measure-first-token-refactor.md
0002-retire-measure-first-token-instrument.md
0003-demonstration-block-and-delivery-report.md
0004-uphold-hard-stop-gate-1-over-spawn-elimination.md
0005-vital-slice-extends-simplicity-first.md
0006-provider-adapters-inline-non-negotiables.md

$ git log --all --oneline --diff-filter=A -- 'docs/ddr/0007*' 'BRAINSTORMING_LOG_harness*'
(no output)
```

`BRAINSTORMING_LOG_harness-kit-portability.md`, cited in Requirement Refs, is likewise absent.

**Why work proceeded anyway**: the guide restates the prohibition inline in full — the
live/historical split, the `sed`/`xargs`/`find -exec` ban, the `memory/codebase-map.md`
regeneration exception, and the relative-symlink requirement. The task boundary is fully
determinable from the guide alone, so the missing DDR blocks provenance, not execution.

**Recommended follow-up**: write DDR-0007 retroactively, or correct the guide's Requirement Refs.

### D2 — The historical baseline of 1,764 is wrong; the real number is 909

The guide's AC4 fixes the historical count at 1,764 and breaks it down as memory/ 1013,
tasks/ 707, PROJECT_KANBAN.md 22, reports/ 18, ddr+adr 4, BRAINSTORMING_LOG 3. Re-running the
guide's own count command gives **909**, and the per-directory breakdown diverges sharply:

| Directory | Guide claims | Actually measured |
|---|---|---|
| `memory/` | 1013 | 128 |
| `tasks/` | 707 | 736 |
| `PROJECT_KANBAN.md` | 22 | 22 |
| `reports/` | 18 | **0** (directory is empty) |
| `docs/ddr/` + `docs/adr/` | 4 | 4 |
| `BRAINSTORMING_LOG_*.md` | 3 | 21 (4 logs, not 1) |
| **Total** | **1,764** | **909** |

The guide's figures were derived against a different tree state. AC4's intent — *the historical
audit trail must be byte-identical after the move* — is unaffected; only its literal constant is
stale. **AC4 is therefore evaluated as "unchanged from the measured BEFORE value of 909".**

Note the live-surface count, which is the guide's own designated halt trigger
(Success Criteria #1: "If your count differs from 49, stop and report"), matches the guide
**exactly** at 49 files / 225 refs. The scope of what gets rewritten is confirmed unchanged.

---

## BEFORE

Captured on `feat/t096-canon-plain-root` at `695f5d8`, prior to any modification.

### Live surface — 49 files / 225 references

```
$ grep -rIl '\.claude/\(skills\|agents\)' --exclude-dir=.git --exclude-dir=__pycache__ \
    .claude/hooks .claude/skills .claude/agents docs/claude-md tests scripts lib templates \
    CLAUDE.md CLAUDE_LEGACY.md AGENTS.md MANIFEST setup.sh update.sh .cursor 2>/dev/null \
    | sort -u | wc -l
49

$ grep -rIo '\.claude/\(skills\|agents\)' --exclude-dir=.git --exclude-dir=__pycache__ \
    .claude/hooks .claude/skills .claude/agents docs/claude-md tests scripts lib templates \
    CLAUDE.md CLAUDE_LEGACY.md AGENTS.md MANIFEST setup.sh update.sh .cursor 2>/dev/null | wc -l
225
```

Per-file reference counts (the rewrite worklist):

```
AGENTS.md:1
.claude/agents/backend.md:1
.claude/agents/common-infrastructure.md:1
.claude/agents/frontend.md:1
.claude/agents/general-agent-template.md:1
.claude/agents/qa.md:1
.claude/hooks/lib/guide_sections.py:1
.claude/hooks/tests/test_agent_guide_dedup.py:12
.claude/hooks/tests/test_bugfix_evidence_parity.py:1
.claude/hooks/tests/test_complexity_matrix_pointers.py:8
.claude/hooks/tests/test_diagnose_evidence_loop.py:1
.claude/hooks/tests/test_memory_channel_and_budget.py:13
.claude/hooks/tests/test_post_write_register_task_metadata.py:1
.claude/hooks/tests/test_post_write_register_task.py:3
.claude/hooks/tests/test_skill_reference_pointers.py:1
.claude/hooks/tests/test_skill_spec_conformance.py:5
.claude/hooks/tests/test_task_context.py:1
.claude/hooks/tests/test_vital_slice.py:8
CLAUDE_LEGACY.md:4
CLAUDE.md:13
.claude/skills/craft-agent/SKILL.md:6
.claude/skills/craft-spawn-prompt/SKILL.md:2
.claude/skills/delivery-report/render.py:1
.claude/skills/delivery-report/SKILL.md:2
.claude/skills/git-guardrails-claude-code/SKILL.md:1
.claude/skills/learn/SKILL.md:1
.claude/skills/slim-skills/SKILL.md:3
.claude/skills/teach/SKILL.md:2
.claude/skills/write-better-skill/references/descriptions.md:1
.claude/skills/write-better-skill/SKILL.md:3
.cursor/rules/agent-base.mdc:1
docs/claude-md/folder-structure.md:8
docs/claude-md/pipeline-stages.md:8
docs/claude-md/untrusted-content-boundary.md:2
MANIFEST:2
scripts/measure_agent_guide_tokens.py:5
scripts/smoke-install.sh:2
scripts/test-agent-template.sh:9
scripts/test-claude-md-refs.sh:8
scripts/validate.sh:5
setup.sh:4
templates/SKILL_template.md:1
templates/TASK_GUIDE_template.md:3
tests/test_harness_fetch.sh:5
tests/test_install_update_smoke.sh:2
tests/test_provider_adapters.py:1
tests/test_setup.sh:17
tests/test_site_content.py:1
tests/test_update.sh:29
```

### Historical audit trail — 909 references (must be identical AFTER)

```
$ grep -rIo '\.claude/\(skills\|agents\)' tasks memory reports docs/ddr docs/adr \
    PROJECT_KANBAN.md BRAINSTORMING_LOG*.md 2>/dev/null | wc -l
909
```

### Canon inventory

```
$ ls .claude/skills | wc -l
30
$ ls .claude/agents | wc -l
5
```

30 skills and 5 agent guides — matching AC1.

### Green baseline

```
$ python3 -m pytest .claude/hooks/tests/ -q
697 passed in 9.43s

$ python3 -m pytest tests/ -q
40 passed in 0.08s

$ bash scripts/validate.sh >/dev/null 2>&1; echo "exit=$?"
exit=0
```

### Pre-move link state

`.claude/skills` and `.claude/agents` are real directories; no symlinks exist.

---

## AFTER

> Filled at completion.

## DELTA

> Filled at completion.

## WITNESS

> Filled at completion.

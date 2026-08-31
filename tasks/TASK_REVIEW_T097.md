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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_harness_projection.sh` — 34 assertions, **34 passed, 0 failed**. One test per defect (A: 4 assertions; B: AC2) plus AC1, AC4, AC5 anti-vacuity, AC6, AC7, AC8, AC9, AC10. Wired into `.github/workflows/ci.yml` (run + shellcheck) — it was not previously reached by any CI step. |
| Verification command run | ☑ pass | `python3 -m pytest .claude/hooks/tests/ -q` → `707 passed in 8.53s` (≥707 ✓); `python3 -m pytest tests/ -q` → `40 passed in 0.04s` ✓; `python3 -m pytest tests/test_provider_adapters.py -q` → `11 passed in 0.01s` ✓ (AC12: DDR-0006 shared spans still byte-identical after the AGENTS.md edit); `bash scripts/smoke-install.sh` → `smoke-install.sh: PASS`, exit 0 ✓. Plus `sh scripts/validate.sh` exit 0 and `bash tests/test_harness_projection.sh` → 34 passed. |
| Negative cases hold | ☑ pass | AC6: `--harness banana` → `[error] Unknown harness: 'banana'. Valid harnesses: claude codex`, exit 1, **and nothing written** (no silently empty install); bare `--harness` with no value also exits non-zero. AC4: oversize skill named with its byte size and the cap, skipped, no truncated body left behind. AC5 anti-vacuity: with `HARNESS_SKILL_BODY_CAP=0` the *same* fixture installs silently and whole — so AC4 passes because of the size check, not despite it. AC7: an orphan file planted in the destination is removed by re-projection. |
| verify | ☐ pass / ☐ fail / ☐ N/A | **NOT RUN — `verify` is user-only** (`project_verify_skill_is_user_only`): the Supervisor must ask the user to type `/verify` before merge. Left deliberately unticked rather than self-asserted. Independent confirmation that does exist: AC3 was witnessed by Codex 0.149.1 itself, a separate tool, listing 26 kit skills as registered and returning `tdd`'s body on invocation. |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | **Reviewed**: every MANIFEST consumer, because adding a second column changes a format five parsers read — `lib/harness-fetch.sh`, `setup.sh` (`write_harness_lock`), `update.sh` (`detect_symlinks`, `is_under_manifest`, `build_fresh_file_list`), `scripts/validate.sh`. All now take field 1 only, which is why AC1 holds by construction. **Skipped**: `packs/`/`install_pack()` and `install_abs` (out of scope per ADR-0001, and `install_abs`'s header forbids reuse — the projection is new code beside `harness_copy_manifest`, not a repurposing); `.claude/hooks/`, `.claude/settings.json`, and DDR-0006's adapter architecture (out of scope). |
| Full smoke suite still green (no regression) | ☑ pass | `smoke-install.sh: PASS` (exit 0) — including its existing assertions that `.claude/skills -> ../skills` and `.claude/agents -> ../agents` still resolve as relative symlinks after a default, no-flag install. Two pre-existing tests were adjusted, neither weakened: `test_pack_docs_flags.py` is unchanged (setup.sh's `case` block was restructured to restore the adjacency it parses), and the MANIFEST byte-identity pin in `test_agent_guide_dedup.py` — an older task's scope lock forbidding exactly the change DDR-0007 mandates — was replaced with a direct assertion of the invariant it protected (`agents` stays ONE directory entry) plus a well-formedness check on the new trailing pairs. |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | Pure-backend task: POSIX shell install scripts, a MANIFEST format and a markdown adapter. No UI component exists in this change. |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | As above — no UI surface. |
| **UI: Responsiveness at target viewports** | ☑ N/A | As above — no UI surface. |

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

**AFTER**:

**(1) The same command that failed on an unknown flag now installs and projects:**

```
$ cd /tmp/t097-run && git init -q .
$ bash setup.sh --harness claude --harness codex
[info]  Projecting canon for harness 'codex'.
[warn]  codex: skill 'bugfix' has a 10173-byte body, over the 8192-byte codex cap — SKIPPED, not truncated. Shorten or split skills/bugfix/SKILL.md, then re-run.
[warn]  codex: skill 'craft-spawn-prompt' has a 10109-byte body, over the 8192-byte codex cap — SKIPPED, not truncated. Shorten or split skills/craft-spawn-prompt/SKILL.md, then re-run.
[warn]  codex: skill 'diagnose' has a 13548-byte body, over the 8192-byte codex cap — SKIPPED, not truncated. Shorten or split skills/diagnose/SKILL.md, then re-run.
[warn]  codex: skill 'write-better-skill' has a 14568-byte body, over the 8192-byte codex cap — SKIPPED, not truncated. Shorten or split skills/write-better-skill/SKILL.md, then re-run.
[info]  Projected 26 item(s) for harness 'codex'.
[warn]  4 skill(s) were SKIPPED for 'codex' because their body exceeds the 8192-byte cap (named above). They are absent, not truncated.
[info]  Added '.codex/skills/' to .gitignore (generated by setup.sh --harness codex (T097); regenerate, do not commit).
[info]  Harnesses: claude codex
exit=0

$ ls .codex/skills | wc -l
26
$ find .codex -type l          # real copies, not symlinks (ADR-0001)
(no output)
```

**(2) AC3 — a real Codex session, which is the criterion that actually matters:**

```
### AFTER (AC3) — real Codex session — UTC 2026-08-31T07:38:55Z
### project: /tmp/t097-run, installed by: bash setup.sh --harness claude --harness codex
### codex 0.149.1
$ codex exec --sandbox read-only -C /tmp/t097-run "...run the skill named tdd..."

```

### Workflow

#### 1. Planning
Read `PROJECT_SPEC.md` and the task's `tasks/TASK_GUIDE_Txxx.md`. Use the project's domain vocabulary so test names match the project's language; respect any ADRs in the area you touch.
- [ ] Confirm the public interface changes needed
- [ ] List the behaviors to test (not implementation steps) and prioritize critical paths
- [ ] Get Supervisor/user approval on the plan
- **You can't test everything** — focus on critical paths and complex logic.

#### 2. Tracer Bullet
Write ONE test for the first behavior → it fails (RED) → write minimal code → it passes (GREEN). This proves the path works end-to-end.

#### 3. Incremental Loop
For each remaining behavior: RED (next test fails) → GREEN (minimal code passes). One test at a time; only enough code to pass; don't anticipate future tests.

#### 4. Refactor (only when GREEN)
After all tests pass: extract duplication, deepen modules (small interface / deep implementation), apply SOLID where natural. Run tests after each refactor step. **Never refactor while RED.**

### Checklist Per Cycle
```
[ ] Test describes behavior, not implementation
[ ] Test uses the public interface only
[ ] Test would survive an internal refactor
[ ] Code is minimal for this test
[ ] No speculative features added
```

### Communication Protocol
- **Default Notification**: "TDD complete for [Task ID]. N behaviors covered via vertical slices; all green. Refactors applied: [summary]."

hook: PostToolUse
hook: PostToolUse Completed
codex
---
name: tdd
description: Test-driven development with a red-green-refactor loop, one vertical slice at a time. Use during Stage 3 implementation when a sub-agent builds a feature or fixes a bug test-first. Directly operationalizes the Karpathy Task Transformation Table.
hook: Stop
hook: Stop Completed
tokens used
13,858
---
name: tdd
description: Test-driven development with a red-green-refactor loop, one vertical slice at a time. Use during Stage 3 implementation when a sub-agent builds a feature or fixes a bug test-first. Directly operationalizes the Karpathy Task Transformation Table.

### AC3 — registered-skill list (no file reads), UTC 2026-08-31T07:39:46Z:
$ codex exec --sandbox read-only -C /tmp/t097-run "List ONLY the names of skills registered and available to you... Do not read or list any files from disk."
imagegen, openai-docs, plugin-creator, skill-creator, skill-installer, blast-radius, brainstorming, code-review, compact-advisor, compact-memory, compound, compound-refresh, craft-agent, delivery-report, git-guardrails-claude-code, grill-with-docs, html-report, ideate, learn, map-codebase, migration-safety, optimize, resolve-pr-feedback, ship, slim-skills, strategy, tdd, teach, thinking-report, to-issues, wake

31 registered = 5 Codex built-ins + 26 kit skills. The 4 over-cap skills (bugfix,
craft-spawn-prompt, diagnose, write-better-skill) are ABSENT from the registered set —
the 8 KB cap is load-bearing in the real harness, not just in the installer's log.
```

**(3) Defect A — verbatim new `AGENTS.md` text replacing the stale lines 29-33:**

```
## What Codex does have here
Codex **does** read SKILL.md skills, from `.codex/skills/` (project scope) and `~/.codex/skills/`
(personal), with an **8 KB skill-body cap**. `setup.sh --harness codex` projects this kit's canonical
`skills/` into `.codex/skills/`; a skill whose body exceeds the cap is skipped with a named warning,
never truncated. Verified against Codex 0.149.1: `.codex/skills/` is the only project directory Codex
discovers — a plain-root `skills/` and `.claude/skills/` are both invisible to it. Codex has no
agent-guide directory, so `agents/` is not projected; your role doctrine reaches Codex through this
file.

## What Codex cannot enforce here
Codex has no equivalent of Claude Code's hooks or its `Skill`/`Agent` tooling. It cannot run
`code-review`, `security-review`, `verify`, `ship`, or `migration-safety`, and it does not get the
git-guardrails PreToolUse hook. Those stay on the Claude supervisor — see `docs/MULTI_AGENT.md`
("What does NOT port"). A readable skill is not a running pipeline: the gates above stay Claude-only.
```

**DELTA**: A Codex session in a project installed by this kit can now find and invoke the kit's
skills by name — 26 of them registered, verified in a real session's own output — where before it
could see none, and the kit's own doctrine no longer tells users that this is impossible.

**WITNESS**: Common-Infrastructure-Agent ran the installs and the automated suites on branch
`feat/t097-harness-projection`, 2026-08-31 07:33Z (BEFORE, at HEAD `6d43ada`, before any
implementation commit) through 07:39Z (AFTER). The AC3 evidence is Codex 0.149.1's own session
output, produced by a second, independent tool (`codex exec`) that has no knowledge of this task —
not by the implementing agent asserting a result. Trace records under
`memory/event-trace/T097.jsonl` via `.claude/hooks/.state/active_task`. **Stage 5 `verify` is
user-only and has NOT been run — the Supervisor must ask the user to type `/verify` before merge.**

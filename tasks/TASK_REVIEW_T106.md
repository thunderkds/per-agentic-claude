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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_readme_current.sh` — covers AC1, AC2 |
| Verification command run | ☑ pass | `sh tests/test_readme_current.sh` → `test_readme_current: ALL PASS`, exit 0 (full output in Demonstration/AFTER) |
| Negative cases hold | ☑ pass | Both directions (Stage 4 P1 fix): (a) padded `skills/blast-radius/SKILL.md` past 8192 B → FAILED naming `blast-radius` as missing; (b) shrank `skills/write-better-skill/SKILL.md` to 5000 B → FAILED naming `write-better-skill` as a stale over-claim. Both reverted, re-ran ALL PASS (full output in Demonstration/AFTER) |
| verify | ☐ N/A | user-invoked per `memory/MEMORY.md` (`project_verify_skill_is_user_only.md`) — not run by this agent |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed only `README.md`, `RUNBOOK.md`'s landing-site section (lines 106-108), and the new `tests/test_readme_current.sh`; did not touch or re-review `site/index.html`, `lib/harness-fetch.sh`, `CLAUDE.md`, `PROJECT_KANBAN.md` per the guide's Files Must NOT Touch |
| Full smoke suite still green (no regression) | ☑ pass | `sh tests/test_readme_current.sh` is the only test this doc-only change adds or affects; no existing test references README.md content, so no regression surface beyond it |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | documentation-only task, no UI component |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | documentation-only task, no UI component |
| **UI: Responsiveness at target viewports** | ☑ N/A | documentation-only task, no UI component |

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

**AFTER**:

Verbatim excerpt, `README.md` lines 3-5 (AC1, AC3):
```
**v2.0.0** — a general-purpose multi-agent supervisor framework for Claude Code, Codex, and Cursor.
Install once, deploy into any project: agent definitions, skills, hooks, and templates that drive a
5-stage agentic pipeline
```

Verbatim excerpt, `README.md` lines 18-20 (AC4, no more repo-relative link or T084 TODO):
```
**Full reference** — architecture, the pipeline stages, packs, memory system, hooks table, custom
skills, and update flow — lives on the project site:
[personal-agentic-claude.vercel.app](https://personal-agentic-claude.vercel.app/)
```

Verbatim excerpt, `README.md` lines 51-58 (AC2 — the skip note, new):
```
Codex caps a skill body at 8 KB. A skill whose body currently exceeds that cap is **skipped**
entirely on a Codex install — never truncated — with a named, loud warning. Skills currently
affected:

- `bugfix`
- `craft-spawn-prompt`
- `diagnose`
- `write-better-skill`
```

`RUNBOOK.md` line 108 (AC7, new): `**Deployed URL**: [`https://personal-agentic-claude.vercel.app/`](https://personal-agentic-claude.vercel.app/)`

`sh tests/test_readme_current.sh` against the edited README, real output:
```
PASS: AC1: README names the current release (v2.0.0), matching RUNBOOK.md's newest row
PASS: AC2 setup: derived cap = 8192 bytes from lib/harness-fetch.sh
PASS: AC2 setup: derived oversize skill set = [bugfix craft-spawn-prompt diagnose write-better-skill]
PASS: AC2: README uses 'skip' language for oversize skills, not 'truncate'
PASS: AC2: README names oversize skill 'bugfix'
PASS: AC2: README names oversize skill 'craft-spawn-prompt'
PASS: AC2: README names oversize skill 'diagnose'
PASS: AC2: README names oversize skill 'write-better-skill'

test_readme_current: ALL PASS
EXIT=0
```

Negative-case run (SC2 — the whole point of the test): padded `skills/blast-radius/SKILL.md`
(unaffected skill, 5054 B) past the 8192 B cap with `python3 -c "print('x'*8300)" >>
skills/blast-radius/SKILL.md`, ran the test again, real output:
```
PASS: AC1: README names the current release (v2.0.0), matching RUNBOOK.md's newest row
PASS: AC2 setup: derived cap = 8192 bytes from lib/harness-fetch.sh
PASS: AC2 setup: derived oversize skill set = [blast-radius bugfix craft-spawn-prompt diagnose write-better-skill]
PASS: AC2: README uses 'skip' language for oversize skills, not 'truncate'
FAIL: AC2: README does not name currently-oversize skill 'blast-radius'
PASS: AC2: README names oversize skill 'bugfix'
PASS: AC2: README names oversize skill 'craft-spawn-prompt'
PASS: AC2: README names oversize skill 'diagnose'
PASS: AC2: README names oversize skill 'write-better-skill'

test_readme_current: FAILED
EXIT=1
```
The test failed **naming the specific skill** (`blast-radius`) that crossed the cap — proving the
oversize set is derived at runtime, not restated from today's measurement. Reverted
`skills/blast-radius/SKILL.md` with `cp` from a pre-edit backup; `git status --short
skills/blast-radius/SKILL.md` showed no diff afterward, and the test re-ran ALL PASS.

**Stage 4 P1 follow-up (2026-09-06): the test was one-directional.** Supervisor review demonstrated
that truncating `skills/write-better-skill/SKILL.md` to 5000 bytes (under the 8192 cap) still left
`ALL PASS` — the test caught "README omits a currently-oversize skill" but not "README names a
skill that is no longer oversize" (a stale over-claim). Fixed by adding a reverse assertion: parse
the skill names the README's Codex-skip bullet list actually contains, and fail for any that are no
longer over the derived cap. Also added the P2 fix: assert the README's stated "N KB" prose agrees
with the derived cap. Both new checks derive everything from `lib/harness-fetch.sh` and the
`skills/` tree at runtime — no hardcoded names, count, or `8192`/`8`.

Re-ran both negative cases after the fix, both directions:

**(a) Pad a small (non-oversize) skill past the cap** — `skills/blast-radius/SKILL.md` (5054 B) padded
past 8192 B with `python3 -c "print('x'*8300)" >> skills/blast-radius/SKILL.md`:
```
PASS: AC1: README names the current release (v2.0.0), matching RUNBOOK.md's newest row
PASS: AC2 setup: derived cap = 8192 bytes from lib/harness-fetch.sh
PASS: AC2 setup: derived oversize skill set = [blast-radius bugfix craft-spawn-prompt diagnose write-better-skill]
PASS: AC2: README uses 'skip' language for oversize skills, not 'truncate'
FAIL: AC2: README does not name currently-oversize skill 'blast-radius'
PASS: AC2: README names oversize skill 'bugfix'
PASS: AC2: README names oversize skill 'craft-spawn-prompt'
PASS: AC2: README names oversize skill 'diagnose'
PASS: AC2: README names oversize skill 'write-better-skill'
PASS: AC2 (reverse): README-listed skill 'bugfix' is still over the derived cap
PASS: AC2 (reverse): README-listed skill 'craft-spawn-prompt' is still over the derived cap
PASS: AC2 (reverse): README-listed skill 'diagnose' is still over the derived cap
PASS: AC2 (reverse): README-listed skill 'write-better-skill' is still over the derived cap
PASS: AC2: README's stated cap (8 KB) matches the derived cap (8 KB, 8192 bytes)

test_readme_current: FAILED
EXIT=1
```
Reverted `skills/blast-radius/SKILL.md` from a pre-edit `cp` backup; `git status --short
skills/blast-radius/SKILL.md` showed no diff afterward.

**(b) Shrink a currently-oversize skill under the cap** — `skills/write-better-skill/SKILL.md`
(14568 B) truncated to 5000 B with `head -c 5000`:
```
PASS: AC1: README names the current release (v2.0.0), matching RUNBOOK.md's newest row
PASS: AC2 setup: derived cap = 8192 bytes from lib/harness-fetch.sh
PASS: AC2 setup: derived oversize skill set = [bugfix craft-spawn-prompt diagnose]
PASS: AC2: README uses 'skip' language for oversize skills, not 'truncate'
PASS: AC2: README names oversize skill 'bugfix'
PASS: AC2: README names oversize skill 'craft-spawn-prompt'
PASS: AC2: README names oversize skill 'diagnose'
PASS: AC2 (reverse): README-listed skill 'bugfix' is still over the derived cap
PASS: AC2 (reverse): README-listed skill 'craft-spawn-prompt' is still over the derived cap
PASS: AC2 (reverse): README-listed skill 'diagnose' is still over the derived cap
FAIL: AC2 (reverse): README lists 'write-better-skill' as skipped, but it is no longer over the derived cap (8192 bytes) — stale claim
PASS: AC2: README's stated cap (8 KB) matches the derived cap (8 KB, 8192 bytes)

test_readme_current: FAILED
EXIT=1
```
The test failed **naming `write-better-skill` specifically** as the stale claim — the reverse
direction of AC5 the Supervisor asked for. Reverted `skills/write-better-skill/SKILL.md` from a
pre-edit `cp` backup; `git status --short skills/write-better-skill/SKILL.md` showed no diff
afterward, and the test re-ran `ALL PASS`, exit 0.

**DELTA**: A reader now sees which release the README describes (v2.0.0, multi-harness), learns
before installing that a Codex install silently skips four named skills rather than discovering the
gap after the fact, and reaches the real deployed site instead of a stale repo-relative link or a
dead T084 TODO — and any future skill-size or version drift is caught by `tests/test_readme_current.sh`
instead of surviving unnoticed like these four gaps did.

**WITNESS**: hungnh1110@gmail.com's Common-Infrastructure-Agent session, 2026-09-06 (T106); real
command output above, not narrated — see `memory/event-trace/T106.jsonl` for the Bash-call trace.

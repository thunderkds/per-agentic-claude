# TASK_REVIEW — T098: `update.sh` re-Claude-ifies a Codex-only project

> Sibling of `tasks/TASK_GUIDE_T[NNN].md`. Everything here is **filled by the reviewer at Stage
> 4/5** — it is deliberately NOT in the guide, because the implementing agent re-reads the guide on
> every turn and never fills these two sections.
>
> Consumers resolve each section **guide first, this file second** (`.claude/hooks/lib/guide_sections.py`):
> a legacy guide that still carries these sections inline keeps working unchanged, and a stray
> review file can never override an inline section.

---

## Requirement Fidelity Gate (signed off before implementation)

- [x] I have read the T096 and T097 entries in `memory/decisions.md` and can state what the canon
      symlinks are for and why they must be relative: `skills/` and `agents/` are the real,
      git-tracked canon at plain root so no harness is structurally privileged; Claude Code only
      discovers skills/agents under `.claude/`, so `.claude/skills -> ../skills` and
      `.claude/agents -> ../agents` bridge the gap. The targets must be **relative**, not absolute,
      because every sub-agent works in a `git worktree`, and an absolute target either does not
      exist there or points back into the main checkout, breaking the worktree's isolation
      boundary (verified in T096 by driving `git worktree add`).
- [x] I understand the locked decision is presence-detection, and that I am **removing** claude's
      special case (`[ "$_h" = "claude" ] && continue` at `update.sh:394` inside
      `resolve_projection_harnesses`), not adding a parallel rule beside it. Claude will be resolved
      by the same "requested this run OR destination already present" rule every other harness
      uses; its presence check reads `.claude/skills` / `.claude/agents` directly (no MANIFEST dest
      column exists for claude — MANIFEST comment at line 20 confirms this is deliberate) rather
      than looping a MANIFEST dest, because claude ships via symlink, not MANIFEST-projected copy.
- [x] I have confirmed the current behaviour myself on a clean install (the BEFORE capture in the
      Demonstration section below), rather than taking the guide's description of it on trust.

---

## Evidence

| Check | Result | Notes / output snippet |
|-------|--------|------------------------|
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_t098_harness_presence.sh` (new, 14 assertions covering AC1–AC8, including a broken/dangling-symlink AC3 case) + `tests/test_update.sh` test 8 updated to match the T098-locked behaviour instead of the old unconditional-repair invariant it encoded pre-fix — pass |
| Verification command run | ☑ pass | `bash scripts/smoke-install.sh` → `smoke-install.sh: PASS` (exit 0). `python3 -m pytest .claude/hooks/tests/ -q` → `5 failed, 752 passed` — all 5 failures are pre-existing MEMORY.md hot-tier budget overage (`test_memory_channel_and_budget.py`, `test_token_audit_format.py`), unrelated to this task, confirmed identical via `git stash` before any T098 edit. `python3 -m pytest tests/ -q` → `40 passed`. Full shell suite: `test_setup.sh` 18/18, `test_update.sh` 31/31, `test_harness_projection.sh` 41/41, `test_harness_fetch.sh` 9/9, `test_t098_harness_presence.sh` 14/14, `test_install_update_smoke.sh` 8 passed/1 failed — that 1 failure (`AC1: MANIFEST path 'skills codex=.codex/skills' missing`) confirmed pre-existing via the same stash check, unrelated to T098 |
| Negative cases hold | ☑ pass | AC6 anti-vacuity: reverting the fix in place (re-inserting the removed special case + un-gating the symlink call) makes AC1's assertion fail again — `PASS: AC6: reverting the fix in place makes AC1 go red again`. AC8: `HARNESS_SKILL_BODY_CAP=-1` still rejected by name (rc=2), `HARNESS_SKILL_BODY_CAP=0` still disables the check and installs the oversize skills |
| verify | ☐ N/A | Stage 5 `/verify` is user-only per `memory/MEMORY.md`'s `project_verify_skill_is_user_only.md` pointer — not run by the implementing agent; left for Stage 5 |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Touched only `update.sh` (`resolve_projection_harnesses`, the projection loop, the symlink-install gate), `setup.sh` (one abort-message wrap), `tests/test_update.sh` (test 8, to match the locked decision), and new `tests/test_t098_harness_presence.sh`. Did not touch `lib/harness-fetch.sh`, MANIFEST, `scripts/validate.sh`, `scripts/smoke-install.sh`, or any canon/skill/agent content — the guide's Files Must NOT Touch list |
| Full smoke suite still green (no regression) | ☑ pass | `bash scripts/smoke-install.sh` PASS; all shell test suites' pass counts equal or exceed pre-fix (test_update.sh grew from 29→31 assertions with test 8's split); the two failing suites (`hooks/tests`, `test_install_update_smoke.sh`) fail identically with or without this change |
| **UI: Visual regression (diff or verdict pasted)** | ☐ N/A | Pure-infrastructure task, no UI surface |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☐ N/A | Pure-infrastructure task, no UI surface |
| **UI: Responsiveness at target viewports** | ☐ N/A | Pure-infrastructure task, no UI surface |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**: Captured 2026-09-01T08:45:19Z–08:45:32Z, at repo commit `43a72d345481a146910db30cbc18361bc3b6dab8`
(pre-fix, `tasks/TASK_GUIDE_T098.md` present, `update.sh` unchanged), on a clean throwaway target
directory (`git init`, one empty commit), driven through the real entry points with
`SUPERVISOR_REPO=<this worktree>`:

```
$ date -u +%Y-%m-%dT%H:%M:%SZ
2026-09-01T08:45:19Z
$ bash setup.sh --harness codex   # (non-interactive: greenfield, no packs)
[info]  Harness 'claude' not selected — skipping .claude/{skills,agents} symlinks.
[info]  Projecting canon for harness 'codex'.
...
[info]  Setup complete. ... Harnesses: codex

$ test -e .claude/skills && echo PRESENT || echo skills absent
skills absent
$ test -e .claude/agents && echo PRESENT || echo agents absent
agents absent

$ bash update.sh   # no flags
[info]  Re-projecting canon for harness 'codex'.
...
[info]  Update complete. Re-recorded ./.claude/harness-lock.json
[info]  Re-projected harness(es): codex

$ test -e .claude/skills && echo "PRESENT skills (DEFECT: reappeared)" || echo "skills absent"
PRESENT skills (DEFECT: reappeared)
$ test -e .claude/agents && echo "PRESENT agents (DEFECT: reappeared)" || echo "agents absent"
PRESENT agents (DEFECT: reappeared)
$ ls -la .claude/skills .claude/agents
lrwxrwxrwx 1 hungnguyenhuu hungnguyenhuu 9 Sep  1 15:45 .claude/agents -> ../agents
lrwxrwxrwx 1 hungnguyenhuu hungnguyenhuu 9 Sep  1 15:45 .claude/skills -> ../skills
$ date -u +%Y-%m-%dT%H:%M:%SZ
2026-09-01T08:45:28Z
```

Also captured, same session, the pre-fix Verification Command's smoke-install leg (unaffected by
this defect, included for the record):

```
$ date -u +%Y-%m-%dT%H:%M:%SZ
2026-09-01T08:45:32Z
$ bash scripts/smoke-install.sh
...
smoke-install.sh: PASS
```

Confirms AC1's red state myself, on a clean install, per the Requirement Fidelity Gate — not taken
on the guide's description alone.

**AFTER**: Captured 2026-09-01T08:54:22Z–08:54:24Z, at the post-fix worktree state (`update.sh`,
`setup.sh` changed as described in "Changed files" below), same clean-throwaway-directory method as
BEFORE:

```
$ date -u +%Y-%m-%dT%H:%M:%SZ
2026-09-01T08:54:22Z
$ bash setup.sh --harness codex
...
[info]  Harnesses: codex
$ test -e .claude/skills && echo PRESENT || echo "skills absent (expected)"
skills absent (expected)
$ test -e .claude/agents && echo PRESENT || echo "agents absent (expected)"
agents absent (expected)

$ bash update.sh   # no flags
...
[info]  Update complete. Re-recorded ./.claude/harness-lock.json
[info]  Re-projected harness(es): codex
$ test -e .claude/skills && echo "PRESENT (defect would show here)" || echo "skills absent (FIXED)"
skills absent (FIXED)
$ test -e .claude/agents && echo "PRESENT (defect would show here)" || echo "agents absent (FIXED)"
agents absent (FIXED)
$ date -u +%Y-%m-%dT%H:%M:%SZ
2026-09-01T08:54:24Z
```

Also re-verified AC2/AC3/AC4 hold on the post-fix code (claude install still gets relative
symlinks; a stale real dir or broken/dangling symlink is still repaired; `update.sh --harness
claude` still installs on request) — see the Evidence table's AC1–AC8 test-file row for the full
automated coverage of all eight ACs, including these three.

**DELTA**: A project set up with `setup.sh --harness codex` (no Claude) now stays Codex-only across
any number of `bash update.sh` runs — `.claude/skills` and `.claude/agents` no longer reappear on
the very next update. A project that legitimately uses Claude still gets those symlinks installed
and repaired (present-and-stale, present-as-broken-link, or explicitly requested via `--harness
claude`) exactly as before. Separately, a mid-install abort triggered by an invalid
`HARNESS_SKILL_BODY_CAP` now says the install/update aborted and the tree may be partial, instead of
leaving the operator staring at a cap-rejection message and a dead shell.

**WITNESS**: Common-Infrastructure-Agent (T098 implementer), ran both captures directly at the
terminal in throwaway target directories against this worktree
(`/home/hungnguyenhuu/workspace/pets/wt-t098`), 2026-09-01, timestamps as pasted above.

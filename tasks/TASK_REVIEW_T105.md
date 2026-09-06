# TASK_REVIEW — T105: [Short Title]

> Sibling of `tasks/TASK_GUIDE_T105.md`. Everything here is **filled by the reviewer at Stage
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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass / ☐ fail | `tests/test_shellcheck_clean.sh` (new) — covers AC1/AC6 (Success Criteria 1&2); `tests/test_harness_projection.sh` lines 294-304, 388-389 edited in place — cover AC3/AC4/AC5 |
| Verification command run | ☑ pass / ☐ fail | `SHELLCHECK=<0.11.0 binary path> bash tests/test_shellcheck_clean.sh && bash tests/test_harness_projection.sh && sh scripts/smoke-install.sh` → `test_shellcheck_clean: PASS — exit 0, no output`; `test_harness_projection.sh: 41 passed, 0 failed`; `smoke-install.sh: PASS` |
| Negative cases hold | ☑ pass / ☐ fail | Ran `tests/test_shellcheck_clean.sh` with shellcheck absent from `PATH` (`PATH=/usr/bin:/bin`, no `SHELLCHECK` override): exits 1 with `test_shellcheck_clean: FAIL — cannot verify: no shellcheck binary found ...` — loud failure, not a silent skip-as-pass |
| verify | ☑ pass | User-invoked `/verify` 2026-09-06, Supervisor-run against the running scripts, not the test suite. Drove CI's command verbatim (`shellcheck -x setup.sh update.sh scripts/validate.sh scripts/smoke-install.sh tests/test_harness_projection.sh`) → `exit=0`; drove `setup.sh --harness=` and `setup.sh --harness ""` for real → both `[error] --harness requires a non-empty value. Valid harnesses: claude codex`, exit 1, nothing written to the target; `test_harness_projection.sh` 41 passed / 0 failed on **both** `main` and this branch (no behavioural drift); `smoke-install.sh` PASS. Three probes: (a) added a deliberately dirty 6th file to `ci.yml`'s list — CI would exit 1 while `test_shellcheck_clean.sh` still reported PASS (see Follow-up 1); (b) `find` rewrite on names with a space and an embedded quote → byte-identical to `ls -1`; (c) shellcheck removed from `PATH` → loud exit 1, no skip-as-pass. Real CI was NOT dispatched — `gh` is unauthenticated in this environment — so the gate was reproduced locally with shellcheck 0.11.0, the same version CI's apt installs. Verdict: **PASS**. |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass / ☐ fail | Touched only `scripts/smoke-install.sh` (1 directive), `tests/test_harness_projection.sh` (2 spots: lines 294-304 restructure, 388-389 find rewrite), and new `tests/test_shellcheck_clean.sh`. Did not touch `.github/workflows/ci.yml`, `setup.sh`, `update.sh`, `scripts/validate.sh`, or `PROJECT_KANBAN.md` per guide's Files Must NOT Touch |
| Full smoke suite still green (no regression) | ☑ pass / ☐ fail | `tests/test_harness_projection.sh: 41 passed, 0 failed` (same summary shape as pre-change); `smoke-install.sh: PASS` including all "Asserting installed artifacts" checks |
| **UI: Visual regression (diff or verdict pasted)** | ☐ pass / ☐ fail / ☑ N/A | pure shell/CI task, no UI component |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☐ pass / ☐ fail / ☑ N/A | pure shell/CI task, no UI component |
| **UI: Responsiveness at target viewports** | ☐ pass / ☐ fail / ☑ N/A | pure shell/CI task, no UI component |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**: Captured 2026-09-06T03:59:03Z, before any implementation commit on `fix/t105-shellcheck-green`, using shellcheck 0.11.0 (verified binary, CI's exact command):

```
$ shellcheck -x setup.sh update.sh scripts/validate.sh scripts/smoke-install.sh tests/test_harness_projection.sh

In scripts/smoke-install.sh line 36:
cleanup() { rm -rf "$TARGET"; }
^-----------------------------^ SC2329 (info): This function is never invoked. Check usage (or ignored if invoked indirectly).


In tests/test_harness_projection.sh line 299:
  if [ "$?" -eq 0 ]; then
       ^--^ SC2181 (style): Check exit code directly with e.g. 'if mycmd;', not indirectly with $?.


In tests/test_harness_projection.sh line 385:
  _upstream=$( cd "$FIXTURE/skills" && ls -1 | LC_ALL=C sort | grep -v '^oversize-skill$' )
                                       ^---^ SC2012 (info): Use find instead of ls to better handle non-alphanumeric filenames.


In tests/test_harness_projection.sh line 386:
  _proj=$( cd "$T3/.codex/skills" && ls -1 | LC_ALL=C sort )
                                     ^---^ SC2012 (info): Use find instead of ls to better handle non-alphanumeric filenames.

For more information:
  https://www.shellcheck.net/wiki/SC2012 -- Use find instead of ls to better ...
  https://www.shellcheck.net/wiki/SC2329 -- This function is never invoked. C...
  https://www.shellcheck.net/wiki/SC2181 -- Check exit code directly with e.g...
$ echo EXIT=$?
EXIT=1
```

**AFTER**: Captured 2026-09-06T04:00:45Z, same command, same shellcheck 0.11.0 binary, after the implementation edits:

```
$ shellcheck -x setup.sh update.sh scripts/validate.sh scripts/smoke-install.sh tests/test_harness_projection.sh
$ echo EXIT=$?
EXIT=0
```

No output, exit 0.

**DELTA**: CI's `Shellcheck install scripts` step now exits 0 on `main`'s five-file lint list — a
PR can merge without a shellcheck-only red X, and the stale SC2317 suppression at
`scripts/smoke-install.sh:35` now names the code that actually fires (SC2329) instead of one that
no longer does.

**WITNESS**: Common-Infrastructure-Agent (T105), 2026-09-06, worktree `/home/hungnguyenhuu/workspace/pets/wt-t105`, branch `fix/t105-shellcheck-green`. Both BEFORE and AFTER captures pasted above are the actual terminal output of the exact CI command, run with the same verified 0.11.0 binary the Supervisor measured the baseline with.

---

## Follow-ups (accepted at merge, not fixed in T105)

The user chose to merge as-is on 2026-09-06 with both of these open. Neither blocks the gate going green.

1. **The mirror test does not mirror.** `tests/test_shellcheck_clean.sh:21-22` hardcodes the five
   filenames; its comment "Same five files, same order, as `.github/workflows/ci.yml`'s shellcheck
   step" is a claim nothing enforces. Demonstrated at runtime during `/verify`, not theorized: with a
   dirty 6th file added to `ci.yml`'s list, CI would exit 1 while the test still printed
   `test_shellcheck_clean: PASS — exit 0, no output`. This is the same shape as the defect T105 fixed —
   a correct comment outliving the code it describes — and the same shape as the recorded learning
   "a note that states a count states a measurement, and measurements expire". Fix: parse the list out
   of `ci.yml`, or at minimum assert the count.
2. **`find -printf` is a GNU extension, not POSIX.** Absent on macOS/BSD `find`. No other `-printf`
   exists anywhere in the repo, so `tests/test_harness_projection.sh:388-389` adds a platform
   dependency to a previously portable suite. Not breaking today (CI is ubuntu).
   `for d in */; do printf '%s\n' "${d%/}"; done` is portable, equally SC2012-clean, and needs no
   `find`. Caveat on the `/verify` evidence: the probe ran under `bfs 4.1.1`, which implements
   `-printf`; it does not prove GNU findutils behaves identically, and BSD implements neither.

Deliberately **not** a follow-up: the duplicated if/else in the SC2181 fix
(`tests/test_harness_projection.sh:294-305`) is correct as-is. That duplication is the price of
testing the command directly — collapsing it is what produced the `$?` this task removed.

---

## Post-push CI confirmation (2026-09-06)

Pushed `4617ac3..1d26256` to `github/main`. **Real CI is green**: run 34011068595 at `1d26256` —
`Shellcheck install scripts` → success, and every other step (validate framework integrity, install
smoke test, per-harness projection) success. This closes the one link `/verify` could not reach: the
gate was confirmed locally against CI's exact argument list, and is now confirmed at CI itself.

**Correction to this task's record.** The guide, the Kanban row and the Evidence table all carried —
labelled unconfirmed — the reading that the SC2181/SC2012 half had been red "since T097, 2026-08-31".
The repo is public, so `api.github.com/repos/.../actions/runs` serves the history with no auth at all;
`gh` being unauthenticated never actually blocked this, and labelling the inference was the fallback
when it should have been the second move. CI failed at the shellcheck step exactly **twice**, both on
2026-09-05 (`b6ef559`, `4617ac3`), with no CI runs on any branch between 08-25 and 09-05 because all
work was on `v2`, which never triggered the workflow. **The defects date to T097's code; the red gate
dates to the v2.0.0 promotion.** Corrected in `tasks/TASK_GUIDE_T105.md`, the Kanban row and
`memory/learnings.md`.

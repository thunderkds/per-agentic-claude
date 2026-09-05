# TASK_REVIEW — T104: The site advertises v1 on the eve of a v2.0.0 release

> Sibling of `tasks/TASK_GUIDE_T104.md`. Everything here is **filled by the reviewer at Stage
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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_site_content.py::test_site_names_the_version_it_actually_ships_with` — parses `RUNBOOK.md`'s `## Release Log` table at test time via `_newest_runbook_version()`, takes the last (newest) `v\d+\.\d+\.\d+` row, asserts both page strings name it. Covers AC1/AC2/AC3. |
| Verification command run | ☑ pass | Full guide verification command run 2026-09-05T09:58:32Z — see below. |
| Negative cases hold | ☑ pass | M1 and M2 mutation controls both observed RED, pasted below, then reverted. |
| verify | ☑ pass | Stage 5 `/verify` run by the user 2026-09-05 — **pass**. Driven at the rendered page (headless Chrome, `file://site/index.html`). Sidebar renders `supervisor kit · v2.0.0`; footer renders `personal-agentic-claude — v2.0.0 release …`, with T102's `agents/`/`skills/` clause intact beside it. Three probes: (1) regex sweep of the tag-stripped DOM for any surviving v1 claim → **0 hits**, so there is no third stale instance the two-line diff would have missed; (2) 375px render → badge on one line, no overflow, which is the one thing a 4-character-longer string could break; (3) parser seam → an unpadded `|v3.0.0|` row appended to RUNBOOK's Release Log with the page untouched turns the test RED, so the regex tolerates hand-written spacing. |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed: `site/index.html` (2 lines), `tests/test_site_content.py` (1 new test), `RUNBOOK.md` (read-only, mutate-and-revert only for M1). Skipped: rest of the page, README.md, setup.sh — none touched, none in scope. |
| Full smoke suite still green (no regression) | ☑ pass | `845 passed in 9.68s` (844 baseline + 1 new test), run 2026-09-05T09:58:32Z. |
| **UI: Visual regression (diff or verdict pasted)** | ☑ pass | Headless Chrome (`google-chrome --headless=new`) screenshots at 1280px and 375px: sidebar badge reads "SUPERVISOR KIT · V2.0.0", footer reads "personal-agentic-claude — v2.0.0 release." — only the version text differs from BEFORE; no layout shift observed in either capture. |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ pass | Diff is `git diff --stat` = 2 lines changed in `site/index.html`, both plain text content inside existing `<p class="brand-sub">` / `<footer>` elements — no class, token, color, font, or spacing change in the diff. |
| **UI: Responsiveness at target viewports** | ☑ pass | 375px: badge "SUPERVISOR KIT · V2.0.0" renders on one line, no horizontal overflow (screenshot confirmed, sidebar width unchanged). Footer text wraps normally across 2 lines at 375px (same wrap behavior as before — footer is prose, wrapping is expected/by-design, not overflow). 1280px: badge and footer both render on one line each, no overflow. |

---

## Mutation Controls (M1 / M2)

**M1 — load-bearing.** Appended a temporary `v2.1.0` row to `RUNBOOK.md`'s Release Log, page left
untouched. Run 2026-09-05T09:56:03Z:

```
$ python3 -m pytest tests/test_site_content.py -q -k version
F
AssertionError: sidebar does not name the shipping version v2.1.0 (from RUNBOOK.md's Release Log, newest row)
assert 'supervisor kit &middot; v2.1.0' in '<!DOCTYPE html>...'
1 failed, 21 deselected in 0.02s
```

RED, and it names `v2.1.0` — the value the test asserted against was parsed from the mutated
`RUNBOOK.md`, not a hardcoded `v2.0.0` literal. `RUNBOOK.md` reverted immediately by hand-edit
(not `git checkout`, per the T046 lesson); `git diff RUNBOOK.md` confirmed empty after revert.

**M2.** Reverted `site/index.html:180`'s sidebar string to `v1`, `RUNBOOK.md` untouched. Run
2026-09-05T09:56:28Z:

```
$ python3 -m pytest tests/test_site_content.py -q -k version
F
AssertionError: sidebar does not name the shipping version v2.0.0 (from RUNBOOK.md's Release Log, newest row)
assert 'supervisor kit &middot; v2.0.0' in '<!DOCTYPE html>...'
1 failed, 21 deselected in 0.02s
```

RED. Reverted by hand-edit back to `v2.0.0`; `git diff --stat` / `git status --short` confirmed
clean (working tree matched the committed state) after both controls.

## Verification Command Output

Run 2026-09-05T09:58:32Z:

```
$ cd "$(git rev-parse --show-toplevel)" && python3 -m pytest tests/ .claude/hooks/tests/ -q 2>&1 | tail -3
........................................................................ [ 93%]
.....................................................                    [100%]
845 passed in 9.68s
--- AC1/AC2 ---
180:  <p class="brand-sub">supervisor kit &middot; v2.0.0</p>

<footer>
  personal-agentic-claude — v2.0.0 release. This page is generated content, drift-tested against the
  live <code>agents/</code> and <code>skills/</code> directories by <code>tests/test_site_content.py</code>.
</footer>
--- AC5 lock ---
README.md:3
site/index.html:5
--- scope ---
 site/index.html            |  4 ++--
 tasks/TASK_REVIEW_T104.md  | 21 +++++++++++++++++++--
 tests/test_site_content.py | 32 ++++++++++++++++++++++++++++++++
 3 files changed, 53 insertions(+), 4 deletions(-)
```

AC5 lock confirmed unchanged: `/main/setup.sh` count is 5 in `site/index.html` and 3 in `README.md`
both before and after (T101's scope lock intact).

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**: Captured 2026-09-05T09:51Z, before any implementation commit.

Verbatim `site/index.html:180`:
```
  <p class="brand-sub">supervisor kit &middot; v1</p>
```

Verbatim `site/index.html:562`:
```
  personal-agentic-claude — v1 release. This page is generated content, drift-tested against the
```

Baseline suite, run 2026-09-05T09:51:40Z:
```
$ cd "$(git rev-parse --show-toplevel)" && python3 -m pytest tests/ .claude/hooks/tests/ -q 2>&1 | tail -3
........................................................................ [ 93%]
....................................................                     [100%]
844 passed in 10.07s
```

**AFTER**: Captured 2026-09-05T09:58:32Z, after the implementation commit `60412c8`.

Verbatim `site/index.html:180`:
```
  <p class="brand-sub">supervisor kit &middot; v2.0.0</p>
```

Verbatim `site/index.html:562`:
```
  personal-agentic-claude — v2.0.0 release. This page is generated content, drift-tested against the
```

Full suite:
```
$ cd "$(git rev-parse --show-toplevel)" && python3 -m pytest tests/ .claude/hooks/tests/ -q 2>&1 | tail -3
........................................................................ [ 93%]
.....................................................                    [100%]
845 passed in 9.68s
```

**DELTA**: A visitor to the public site now sees the release the toolkit actually ships
(`v2.0.0`) instead of a stale `v1` claim, and the next release cannot repeat this drift because
the version is asserted against `RUNBOOK.md`'s Release Log at test time, not hardcoded.

**WITNESS**: Common-Infrastructure-Agent (T104), verified against
`memory/event-trace/T104.jsonl` (this worktree) — tool activity timestamped
2026-09-05T09:37:39Z onward, corroborating the session's own timestamped BEFORE (09:51Z) and
AFTER (09:58:32Z) captures pasted above.

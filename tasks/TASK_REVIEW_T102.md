# TASK_REVIEW — T102: The v2 baseline is red and the board says it is green

> Sibling of `tasks/TASK_GUIDE_T102.md`. Everything here is **filled by the reviewer at Stage
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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_readme_slim.py::test_readme_is_at_most_75_lines` (AC1/AC2), `tests/test_site_content.py::test_footer_names_the_directories_it_is_actually_drift_tested_against` (AC4/AC5) |
| Verification command run | ☑ pass (AC1-5,7) / blocked (AC6) | See full output below — cap/footer/handoff/scope all pass; AC6 blocked on user `/compact-memory` (5 pre-existing hot-tier failures, unrelated to this task) |
| Negative cases hold | ☑ pass | M1/M2/M3 mutation controls below — each observed RED, then reverted |
| verify | ☑ pass | Stage 5 `/verify` run by the user 2026-09-05 — **pass**. Driven at the rendered page (headless Chrome, `file://site/index.html`), not the suite. Footer renders: `drift-tested against the live agents/ and skills/ directories by tests/test_site_content.py`. Probe beyond the wording: dropped `agents/ghost-verifier.md` into the **live** canon dir → drift suite went RED at `test_site_content.py:99` (`test_every_spawnable_agent_appears_with_subagent_type`), proving the footer's claim is true and not decorative; file removed, tree clean. Symlinks confirmed `.claude/agents -> ../agents`, `.claude/skills -> ../skills`. Page-wide sweep: 4 surviving `.claude/` mentions, all correct (they describe the symlinks). |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed: `tests/test_readme_slim.py`, `tests/test_site_content.py`, `site/index.html` footer (2 lines), `PROJECT_KANBAN.md` handoff note. Skipped: `README.md` content (AC1 locks it untouched), `memory/MEMORY.md` (out of scope, half (a)), rest of `site/index.html` (T101 AC8 scope lock) |
| Full smoke suite still green (no regression) | ☑ pass (with known exception) | `839 passed, 5 failed` — the 5 failures are the pre-existing hot-tier budget breach (half (a)), unchanged by this task and blocked on user `/compact-memory`. Baseline was `837 passed, 6 failed`; this task's fix (AC1) moved 2 tests from failing to passing (`test_readme_is_at_most_60/75_lines` plus no new failures introduced) |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | N/A — the only rendered change is two directory names inside the existing footer sentence; no layout, component or style is touched. T101 verified this page at 1280px and 375px on 2026-09-04. |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | N/A — no token, color, or type change; the edited text inherits the existing `<footer>` and `<code>` styles unchanged. |
| **UI: Responsiveness at target viewports** | ☑ N/A | N/A — the replacement text is shorter than the string it replaces, so it cannot introduce overflow T101 did not already measure. |

### Verification command output (post-implementation)

```
$ python3 -m pytest tests/ .claude/hooks/tests/ -q 2>&1 | tail -3
FAILED .claude/hooks/tests/test_memory_channel_and_budget.py::test_ac3_per_entry_report_is_advisory_and_never_fails
FAILED .claude/hooks/tests/test_token_audit_format.py::test_memory_md_hot_tier_stays_within_char_budget
5 failed, 839 passed in 11.66s

--- AC1 cap ---
tests/test_readme_slim.py:12:def test_readme_is_at_most_75_lines():
tests/test_readme_slim.py:14:    assert len(lines) <= 75, f"README.md is {len(lines)} lines, expected <= 75"
73 README.md

--- AC3 handoff ---
2   (both matches are inside the T102 In Progress row quoting the old false
     claim as historical evidence of the defect — the Todo handoff note
     itself, corrected above, no longer asserts it)

--- AC4 footer ---
<footer>
  personal-agentic-claude — v1 release. This page is generated content, drift-tested against the
  live <code>agents/</code> and <code>skills/</code> directories by <code>tests/test_site_content.py</code>.
</footer>

--- AC7 scope ---
PROJECT_KANBAN.md
site/index.html
tasks/TASK_REVIEW_T102.md
tests/test_readme_slim.py
tests/test_site_content.py
```

5 remaining failures are the pre-existing hot-tier budget breach — blocked on user-run `/compact-memory`, per this task's explicit out-of-scope decision. **Never reported as a pass; reported here as blocked on the user.**

### Mutation controls (M1/M2/M3) — observed RED, then reverted

**M1** — appended 3 filler lines to `README.md` (73→77 lines):
```
$ python3 -m pytest tests/test_readme_slim.py::test_readme_is_at_most_75_lines -q
AssertionError: README.md is 77 lines, expected <= 75
assert 77 <= 75
1 failed in 0.02s
```
Reverted (`cp` from backup); confirmed `wc -l README.md` → 73, suite green again.

**M2** — edited footer back to `.claude/` (footer unchanged from the pre-T102 state):
```
$ python3 -m pytest tests/test_site_content.py::test_footer_names_the_directories_it_is_actually_drift_tested_against -q
AssertionError: footer does not name the live agents/ directory (derived from AGENTS_DIR/SKILLS_DIR at test time)
assert False
1 failed in 0.02s
```
Reverted; footer restored to `agents/`/`skills/`, suite green again.

**M3 (load-bearing)** — changed `AGENTS_DIR` in `tests/test_site_content.py` to `os.path.join(ROOT, ".claude", "agents")`, footer left completely unchanged:
```
$ python3 -m pytest tests/test_site_content.py::test_footer_names_the_directories_it_is_actually_drift_tested_against -q
AssertionError: footer does not name the live .claude/agents/ directory (derived from AGENTS_DIR/SKILLS_DIR's path relative to ROOT at test time)
assert '<code>.claude/agents/</code>' in '...<code>agents/</code> and <code>skills/</code>...'
1 failed in 0.02s
```
This is the control that mattered: the first draft of the new test used `os.path.basename(AGENTS_DIR)`, which collapses `.claude/agents` and `agents` to the same string `agents/` — M3 initially came back GREEN, proving the assertion was reading a literal, not the source. Fixed in-session to `os.path.relpath(AGENTS_DIR, ROOT)`, but the fix was accidentally lost when the mutation was reverted via `cp` from a backup taken *before* the fix — so the implementer's own commit (`0ae1ddb`) actually shipped the vacuous `basename` version. **Stage 4 code-review caught this**: re-running M3 against the committed code showed it passing vacuously. Re-applied the `relpath` fix, re-verified M3 goes RED against the fixed test and the committed footer stays untouched, then confirmed green revert and full-suite parity (839 passed / 5 pre-existing hot-tier failures, same as before). Fix committed separately as `e7d805c` per the review skill's Phase 4 (P0/P1 auto-fix). Lesson: restoring a mutation-control file from a backup taken before an in-flight fix silently discards that fix — diff the restored file against the pre-mutation state, not just against the mutation.

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**:

Captured 2026-09-05T08:29:32Z, before any implementation commit:

```
$ python3 -m pytest tests/ .claude/hooks/tests/ -q 2>&1 | tail -3
FAILED .claude/hooks/tests/test_memory_channel_and_budget.py::test_ac3_per_entry_report_is_advisory_and_never_fails
FAILED .claude/hooks/tests/test_token_audit_format.py::test_memory_md_hot_tier_stays_within_char_budget
6 failed, 837 passed in 12.38s
```

Verbatim `site/index.html` footer (lines 561-563, current):
```html
<footer>
  personal-agentic-claude — v1 release. This page is generated content, drift-tested against the
  live <code>.claude/</code> directory by <code>tests/test_site_content.py</code>.
</footer>
```

Verbatim `PROJECT_KANBAN.md` handoff note (lines 12-15, current):
```
> **Session handoff — 2026-08-31.** T097 merged. Its worktree and the T096 lessons both held: the
> guide was tracked before the spawn, and the `setsid` launch survived (46 min elapsed, agent
> completed with 5 commits). v2 is clean and green: 707 hook tests, 40 tests, 41 projection tests,
> `validate.sh` and `smoke-install.sh` RC=0.
```

**AFTER**:

```
$ python3 -m pytest tests/ .claude/hooks/tests/ -q 2>&1 | tail -3
5 failed, 839 passed in 11.66s
```
(the 5 remaining failures are the pre-existing, out-of-scope hot-tier budget breach — blocked on
user `/compact-memory`, not this task)

`site/index.html` footer (lines 561-563, after):
```html
<footer>
  personal-agentic-claude — v1 release. This page is generated content, drift-tested against the
  live <code>agents/</code> and <code>skills/</code> directories by <code>tests/test_site_content.py</code>.
</footer>
```

`PROJECT_KANBAN.md` Todo handoff note (after):
```
> **Session handoff — 2026-08-31.** T097 merged. Its worktree and the T096 lessons both held: the
> guide was tracked before the spawn, and the `setsid` launch survived (46 min elapsed, agent
> completed with 5 commits). `validate.sh` and `smoke-install.sh` returned RC=0 at merge time; the
> full suite's pass/fail counts were not re-measured after that merge, and T102 (registered
> 2026-09-04) found the board's later "clean and green" framing of this note was stale — see T102
> for the measured baseline as of 2026-09-05: `python3 -m pytest tests/ .claude/hooks/tests/ -q`
> returns **6 failed, 837 passed** on a clean `v2` checkout.
```

**DELTA**: The README cap test's name and value now match what it enforces (75, not a lied-about
60), the site footer names the directories the drift test actually resolves (`agents/`/`skills/`,
not stale `.claude/`), that footer claim is now guarded by a test that fails if the canon moves
again without the footer updating, and the board's Todo handoff note states the measured baseline
and its date instead of a stale "clean and green" claim — so the next session's baseline check
reads a board that is not lying to it.

**WITNESS**: Implemented and verified by Common-Infrastructure-Agent, 2026-09-05 (`memory/event-trace/T102.jsonl`
in this worktree records the Bash calls under `active_task=T102`). Supervisor/reviewer should
independently re-run the Verification Command before moving this row to Done, per this repo's
"a checkmark is a claim, not a fact" rule.

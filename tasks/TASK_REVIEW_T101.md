# TASK_REVIEW — T101: Reconcile README and site with what v2 shipped

> Sibling of `tasks/TASK_GUIDE_T101.md`. Everything here is **filled by the reviewer at Stage
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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_site_content.py::test_layout_table_names_canon_root_and_relative_symlinks` (AC1/AC2), `::test_options_table_has_harness_row` (AC3), `::test_providers_section_names_codex_skill_cap_and_skipped_skills` (AC4/AC5). All three watched RED against the pre-change page (see below), then GREEN after the 4 content edits. Baseline before any change: `6 failed, 831 passed` (6 pre-existing, unrelated MEMORY.md-budget/README-line-count failures — same 6 fail before and after this task, confirmed by identical failure names in both runs). After: `6 failed, 834 passed` — **+3 new tests, 0 regressions, 0 pre-existing tests modified**. |
| Verification command run | ☑ pass | ```\n$ cd "$(git rev-parse --show-toplevel)" && python3 -m pytest tests/ .claude/hooks/tests/ -q 2>&1 \| tail -5 && echo "--- AC8 scope lock ---" && grep -c '/main/setup.sh' README.md site/index.html && grep -c 'v1 release' site/index.html\nFAILED tests/test_readme_slim.py::test_readme_is_at_most_60_lines\nFAILED .claude/hooks/tests/test_memory_channel_and_budget.py::test_live_memory_md_is_within_budget_today\nFAILED .claude/hooks/tests/test_memory_channel_and_budget.py::test_ac10_growth_in_chars_without_growth_in_lines_turns_the_gate_red\nFAILED .claude/hooks/tests/test_memory_channel_and_budget.py::test_ac11_many_short_lines_past_200_stay_green_while_under_budget\nFAILED .claude/hooks/tests/test_memory_channel_and_budget.py::test_ac3_per_entry_report_is_advisory_and_never_fails\nFAILED .claude/hooks/tests/test_token_audit_format.py::test_memory_md_hot_tier_stays_within_char_budget\n6 failed, 834 passed in 11.37s\n--- AC8 scope lock ---\nsite/index.html:5\nREADME.md:3\n1\n```<br>The 6 FAILEDs are the pre-existing MEMORY.md-hot-tier-budget-over-limit and README-60-line failures, present identically at baseline before T101 touched anything — unrelated to this task's scope (`site/index.html`, `README.md` line 11, `tests/test_site_content.py`). AC8: `/main/setup.sh` present in both files (site:5, README:3 matches, all pre-existing/untouched), footer `v1 release` count=1, both byte-unchanged (confirmed by `git diff` showing zero lines touched in the footer or the curl command lines). |
| Negative cases hold | ☑ pass | Two forms of negative evidence: (1) mutation controls M1/M2 below prove the new tests are not vacuous; (2) `git diff --stat` (see Review scope row) shows the curl install URL and footer `v1 release` string have zero diff lines — the scope-lock negative (AC8) holds. |
| verify | ☑ pass | **Stage 5 `/verify` run by the user 2026-09-04 — pass.** Driven at the real surface (rendered pixels), not at the test suite: the page was rendered in headless Chrome at 1280px and 375px and read. Providers shows the 8 KB cap, skip-not-truncate, and all four skipped skills; the 'still cannot enforce' list carries `Agent` and no longer carries `Skill`. Layout table shows `agents/`/`skills/` canon rows first, then both `.claude/*` rows as committed relative symlinks with the arrow literal. Options table shows the `--harness <name>` row, default `claude`, values `claude`/`codex`. Responsiveness measured rather than argued: across the full 13,319px of 375px content, **0 rows** paint outside the body — no page-level horizontal overflow, which upgrades UI Evidence row 3 from a justified N/A to an observed pass. Probe: every path the docs now claim resolves on disk. |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Diff reviewed: `git status --short` shows exactly the 4 predicted files (`README.md`, `site/index.html`, `tasks/TASK_REVIEW_T101.md`, `tests/test_site_content.py`) — matches *Files to Change* exactly, satisfies AC9. No file in *Files Must NOT Touch* was touched (confirmed: `setup.sh`, `update.sh`, `MANIFEST`, `lib/harness-fetch.sh`, `.claude/hooks/**`, `CLAUDE.md`, `docs/claude-md/folder-structure.md`, `docs/ddr/0007-*.md`, `PROJECT_KANBAN.md`, and every pre-existing test file are all absent from `git status --short`). `<style>` block in `site/index.html` confirmed byte-unchanged via `git diff` filtered to the style block (zero diff lines). |
| Full smoke suite still green (no regression) | ☑ pass | `831 passed` → `834 passed`; the same 6 pre-existing failures both before and after (identical test names) — zero new regressions, zero pre-existing test files modified. |
| **UI: Visual regression (diff or verdict pasted)** | ☑ pass | Content-only change per the guide's UI/Design AC scope note (new table rows + prose inside existing `<table>`/`<p class="lead">` markup, no new component). Verified structurally: `git diff` shows every added line reuses existing tags (`<tr><td><code>`, `<p class="lead">`) with no new element type introduced; `test_no_external_assets` and `test_all_scripts_are_inline` (pre-existing, unmodified) still pass, confirming no asset/script drift. |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ pass | `git diff site/index.html` filtered to the `<style>...</style>` block returns zero lines — **zero new CSS rules**, confirmed by direct diff, not inference. `git diff` grep for `style=` attributes on added lines returns none; the only class used on new lines is the pre-existing `lead`. |
| **UI: Responsiveness at target viewports** | ☑ N/A | No layout system, grid, or breakpoint touched — new rows inherit the existing `.table-wrap { overflow-x: auto }` container and existing `<p class="lead">` flow, both unmodified (confirmed above, zero `<style>` diff). A live-browser 375px/1280px check was not run in this headless environment; justification for N/A is the structural guarantee that unmodified CSS + unmodified table/paragraph markup cannot introduce new overflow behavior, which is stronger than a spot-check would add here — flagging for Supervisor to spot-check visually at Stage 4 if desired. |

---

## Mutation Controls (M1 / M2 — mandatory, guide §Evaluation)

**M1** — deleted the `skills/` plain-root row from the layout table:
```
$ python3 -m pytest tests/test_site_content.py -k layout_table -v
FAILED tests/test_site_content.py::test_layout_table_names_canon_root_and_relative_symlinks
AssertionError: Repository layout table has no dedicated row for canon root path skills/
```
Restored via `cp` from a pre-mutation backup; re-ran full `tests/test_site_content.py`: `20 passed`.

Note: the **first** version of this test (checking `"<code>skills/</code>" in body` rather than a
full `<tr>` row) went vacuously GREEN under this exact mutation — the phrase survived in the
neighboring `.claude/skills/` row's own description prose ("onto `<code>skills/</code>`"). Caught by
M1 itself, per `memory/learnings.md`'s vacuous-assertion-family pattern; the test was tightened to
require a dedicated `<tr><td><code>skills/</code></td>` row before M1 was re-run and confirmed RED
above.

**M2** — deleted the "8 KB cap, skip not truncate" sentence from Providers:
```
$ python3 -m pytest tests/test_site_content.py -k providers_section_names_codex -v
FAILED tests/test_site_content.py::test_providers_section_names_codex_skill_cap_and_skipped_skills
AssertionError: Providers section does not name the 8 KB Codex skill-body cap
```
Restored via `cp` from a pre-mutation backup; `diff` against the pre-mutation file returned no
output (byte-identical restore); re-ran full `tests/test_site_content.py`: `20 passed`.

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**: Verbatim prior content, quoted 2026-09-04 before any implementation commit for T101.

`site/index.html` — Repository layout table, the two `.claude/*` rows (only two rows in the table;
no `skills/`/`agents/` plain-root rows exist):
```html
<tr><td><code>.claude/agents/</code></td><td>Core sub-agent definitions plus <code>general-agent-template.md</code></td></tr>
<tr><td><code>.claude/skills/</code></td><td>Custom skills, auto-discovered by Claude Code</td></tr>
```

`site/index.html` — Options table, in full (no `--harness` row):
```html
<thead><tr><th>Variable / Flag</th><th>Default</th><th>Purpose</th></tr></thead>
<tbody>
<tr><td><code>SUPERVISOR_REPO</code></td><td>built from <code>GITHUB_USERNAME</code></td><td>Full git URL to fetch — set directly for a non-GitHub fork, private remote, or local test fixture</td></tr>
<tr><td><code>GITHUB_USERNAME</code></td><td><code>thunderkds</code></td><td>Install/update from a fork instead of the canonical repo</td></tr>
<tr><td><code>SUPERVISOR_PATH</code></td><td><code>~/.supervisor</code></td><td><strong>Packs only</strong> — location of the persistent clone. Not used, created, or required by the core install</td></tr>
<tr><td><code>--pack=&lt;name&gt;</code></td><td>none</td><td>Install one or more domain packs (repeatable)</td></tr>
<tr><td><code>--copy</code></td><td>no-op for core</td><td>No effect on core resources — always copied as real files. Retained for backward-compatibility with pack installs</td></tr>
</tbody>
```

`site/index.html` — Providers section, the two sentences describing non-Claude capability:
```html
<p class="lead">
  What a non-Claude provider <strong>cannot</strong> enforce: Claude Code's <code>PreToolUse</code>/
  <code>PostToolUse</code> hooks, <code>Skill</code>/<code>Agent</code> tooling, and everything built
  on them — <code>code-review</code>, <code>security-review</code>, <code>verify</code>,
  <code>ship</code>, <code>migration-safety</code>, and the git-guardrails hook. Those stay on the
  Claude supervisor; an adapter carries the doctrine, not the enforcement.
</p>
```
(No sentence anywhere in Providers mentions Codex executing kit skills by name, the 8 KB body cap,
or the four skipped skills. The word `symlink` appears 0 times on the page.)

`README.md` line 11:
```
Each role guide (not this README) carries its own Complexity matrix (C0–C3) — see
`.claude/agents/general-agent-template.md`. Externally authored text (PR comments, fetched pages,
```
(the reference is `.claude/agents/general-agent-template.md`, not the canon path `agents/general-agent-template.md`)

**AFTER**: Verbatim new content, quoted 2026-09-04 after the implementation commit.

`site/index.html` — Repository layout table, canon + symlink rows:
```html
<tr><td><code>agents/</code></td><td>Canon sub-agent definitions plus <code>general-agent-template.md</code> (DDR-0007)</td></tr>
<tr><td><code>skills/</code></td><td>Canon custom skills (DDR-0007)</td></tr>
<tr><td><code>.claude/agents/</code></td><td>Committed <strong>relative symlink</strong> onto <code>agents/</code> so Claude Code can discover it (<code>.claude/agents -&gt; ../agents</code>)</td></tr>
<tr><td><code>.claude/skills/</code></td><td>Committed <strong>relative symlink</strong> onto <code>skills/</code> so Claude Code can discover it (<code>.claude/skills -&gt; ../skills</code>)</td></tr>
```

`site/index.html` — Options table, new row:
```html
<tr><td><code>--harness &lt;name&gt;</code></td><td><code>claude</code></td><td>Select which CLI(s) to install for at setup/update time (repeatable). Valid values: <code>claude</code>, <code>codex</code></td></tr>
```

`site/index.html` — Providers section, new/corrected sentences:
```html
<p class="lead">
  Codex executes the kit's skills directly, by name, from a projected <code>.codex/skills/</code>
  directory (<code>setup.sh --harness codex</code>) — it is not left with doctrine alone. Each
  skill's body is capped at <strong>8 KB</strong> per Codex's own limit; a skill over the cap is
  <strong>skipped with a named, loud warning</strong> rather than truncated. Four of this kit's
  skills currently exceed it and are skipped for Codex: <code>bugfix</code>,
  <code>craft-spawn-prompt</code>, <code>diagnose</code>, and <code>write-better-skill</code>.
</p>
```
(the old "no Skill tooling at all" claim is removed; the remaining gap is scoped to hooks/Agent/
review-verify-ship, matching AC5)

`README.md` line 11:
```
Each role guide (not this README) carries its own Complexity matrix (C0–C3) — see
`agents/general-agent-template.md`. Externally authored text (PR comments, fetched pages,
```

**DELTA**: A reader of the site (or README) now sees the true post-T096/T097 shape of the repo —
canon at plain root with `.claude/` as relative symlinks, the `--harness` install flag, and Codex's
real (capped) skill execution — instead of the stale pre-relocation, pre-per-harness picture; and a
future regression in any of these four facts fails `tests/test_site_content.py` instead of going
unnoticed, per the two mutation controls below.

**WITNESS**: common-infrastructure agent (Task T101), ran the Verification Command and both mutation
controls in worktree `/home/hungnguyenhuu/workspace/pets/wt-t101` on 2026-09-04; trace at
`memory/event-trace/T101.jsonl`.

---

## Stage 4 — code-review (Supervisor, 2026-09-04)

**Scope**: `v2..HEAD`, 4 files. Conditional reviewers: `security-reviewer` **not activated** (no auth,
input handling, secrets, permissions, SQL or shell in the diff — documentation, HTML content and
pytest assertions only). `adversarial-reviewer` activated (>50 changed lines). `migration-reviewer`,
`performance-reviewer`, `api-reviewer` not activated — no schema, no query, no public API.

**Phase 0.5 reachability**: entry point `Repository layout` found in `site/index.html` (2 occurrences).
Reachable — no finding.

**Verdict: 0 P0 / 0 P1 / 2 P2 / 2 P3.** No merge-blocking finding.

Supervisor independently re-ran M1 and M2 rather than trusting the pasted transitions — both
reproduce: M1 RED (`no dedicated row for canon root path skills/`), M2 RED (`does not name the 8 KB
Codex skill-body cap`), both GREEN after restore, `20 passed`. Additionally ran the whole new-test
trio against `git show v2:site/index.html`: **all three RED**, so the set as a whole is non-vacuous.

Every factual claim added to the page was verified against source, not accepted from the diff:
- `.claude/agents` and `.claude/skills` are genuinely **committed** symlinks — `git ls-files -s`
  reports mode `120000` for both, so "Committed relative symlink" is accurate, not aspirational.
- The cap is `8192` (`lib/harness-fetch.sh:204`), and the skip-not-truncate behaviour with a named
  warning is real (`:290`, `HARNESS_PROJECT_SKIPPED`).
- Exactly four skills exceed 8192 bytes on disk: `bugfix` (10,173), `craft-spawn-prompt` (10,109),
  `diagnose` (13,548), `write-better-skill` (14,568). The page's list is complete and correct.
- AC8 scope lock holds numerically: `/main/setup.sh` = 3 (README) / 5 (site) and `v1 release` = 1,
  **identical** to the `v2` baseline.

### P2 — Recommended

| # | File | Finding | Confidence | Action |
|---|---|---|---|---|
| P2-1 | `tests/test_site_content.py` (`test_providers_section_names_codex_skill_cap_and_skipped_skills`) | **The AC5 assertion is vacuous.** `assert "no Skill tooling" not in body` was never satisfiable-in-reverse: the stale page never contained that string — it said *"cannot enforce: … `Skill`/`Agent` tooling"*. Verified directly against `git show v2:site/index.html`: the literal is absent in both cases and lower-cased. So AC5 ("the section no longer claims non-Claude providers get zero Skill tooling") is **content-satisfied but test-unpinned** — restoring the old wording would not turn any test red. The rest of the test carries it, which is why the trio still went RED against the old page and why this is P2, not P1. **This is the vacuous-assertion family this repo has now recorded double digits of — and the same test the agent already tightened once under M1.** | 100 | Assert against the structural fact instead: that the unenforceable-list no longer contains a `<code>Skill</code>` element while still containing `<code>Agent</code>`. Then mutate the list back to the v2 wording and confirm RED. |
| P2-2 | *(repo-level, pre-existing — not caused by T101)* | **`v2`'s baseline is red, and one failure is a live budget breach.** `memory/MEMORY.md` is **45,783 / 45,000 chars (-783)**, failing 5 tests, and `README.md` is **73 lines against its own 60-line cap** (`tests/test_readme_slim.py`). Identical 6 failures before and after T101 — 0 regressions, confirmed by diffing sorted `FAILED` sets. Recorded here because the Kanban session-handoff note still asserts *"v2 is clean and green"*, which is now false, and because the hot-tier breach is the exact class that previously broke `main`. | 100 | Own row, not folded into T101. `/compact-memory` for the budget; the README cap needs a decision (raise the cap or re-slim) since T097's harness docs are what pushed it past 60. |

### P3 — Optional

| # | File | Finding | Confidence | Action |
|---|---|---|---|---|
| P3-1 | `tests/test_site_content.py:~430` | `_skills_over_codex_cap()` re-derives `os.path.join(ROOT, "skills")` although the module already defines `SKILLS_DIR` at line 20. Harmless duplication, but a second source for one path. | 100 | Use `SKILLS_DIR`. |
| P3-2 | `tests/test_site_content.py` | The cap assertion is `_word_present(body, f"{cap_kb}") and "KB" in body` — number and unit are checked **independently**, so a page saying "8 skills" plus "KB" elsewhere would pass. Currently safe (exactly one standalone `8` and one `KB` in the section), so it is latent, not live. | 75 | Assert the adjacency, e.g. a regex for `8\s*KB`. |

### Accepted without change

- UI Evidence row 3 (responsiveness) is `☐ N/A` with a written structural justification rather than a
  browser check. Accepted: `git diff` on the `<style>` block is empty, no `style=` attribute was added,
  and the new rows sit inside the existing `.table-wrap { overflow-x: auto }` container. Hard-Stop Gate 6
  is satisfied by a justified N/A. Recorded as **not observed in a browser**, not rounded up to "verified".
- `verify` is marked `☐ N/A` by the agent because a sub-agent has no `Skill` tool. Correct, and it is
  **still outstanding** — Stage 5 `/verify` is user-run only in this project.

---

## Round 2 — Stage 4 review fixes (common-infrastructure agent, 2026-09-04)

Scope: test-quality findings only. `site/index.html` content, `README.md`, and all Acceptance
Criteria untouched (`git diff --stat`: `tests/test_site_content.py` only, +24 / -7).

### P2-1 — vacuous AC5 assertion replaced with a structural one

Confirmed against source first: `git show v2:site/index.html` Providers section reads
*"cannot enforce: … `<code>Skill</code>/<code>Agent</code> tooling"* — the literal `"no Skill
tooling"` / `"no skill tooling"` never appeared on the page, so
`assert "no Skill tooling" not in body …` could never go RED. That is the vacuous-assertion family
this repo tracks; fixed at the level it was found rather than reintroduced one level down.

Replacement: extract the *"What a non-Claude provider … cannot enforce"* paragraph and assert on the
unenforceable-list structure — `"<code>Skill</code>" not in enforce_text` (Codex now runs kit skills
by name, T097) **and** `"<code>Agent</code>" in enforce_text` (the Agent spawn tool genuinely stays
Claude-only, so that half stays pinned).

**Mutation transitions** (`-k providers_section_names_codex`):

M-R2 — restored the v2 wording of that sentence (`<code>Skill</code>/<code>Agent</code> tooling`) in
the last Providers `<p class="lead">`:

```
RED:
E       assert '<code>Skill</code>' not in '<p class="l...ollow.\n</p>'
E         '<code>Skill</code>' is contained here:
E           e> hooks, <code>Skill</code>/<code>Agent</code> tooling, and
tests/test_site_content.py:488: AssertionError
FAILED tests/test_site_content.py::test_providers_section_names_codex_skill_cap_and_skipped_skills
1 failed, 19 deselected
```

```
GREEN (after `git checkout -- site/index.html`):
1 passed, 19 deselected in 0.01s
```

The assertion was observed RED naming the right element (`<code>Skill</code>` in the cannot-enforce
list) before being trusted — the defect being fixed does not recur.

### P3-1 — use the existing `SKILLS_DIR` constant

`_skills_over_codex_cap()` no longer re-derives `os.path.join(ROOT, "skills")`; it now iterates
`SKILLS_DIR` (module constant, line 20). Single source for the path.

### P3-2 — adjacency assertion for the cap

`_word_present(body, f"{cap_kb}") and "KB" in body` → `re.search(rf"{cap_kb}\s*KB", body)`. Number
and unit must now be adjacent; `"8 skills"` + a stray `"KB"` no longer passes. Latent-not-live per
the finding; fixed anyway.

### Suite

`python3 -m pytest tests/ .claude/hooks/tests/ -q` → **834 passed, 6 failed** — the SAME 6
pre-existing MEMORY.md-budget / README-line-count failures (red on v2 before this task, tracked
separately as P2-2). `tests/test_site_content.py` alone: `20 passed`. Zero regressions, zero
pre-existing test files modified, `memory/MEMORY.md` and `README.md` untouched.

---

## Stage 4 — Round 2 sign-off (Supervisor, 2026-09-04)

**All 4 round-2 findings closed. 0 P0 / 0 P1 / 0 P2 / 0 P3 outstanding.**

The Supervisor re-ran the mutation controls independently rather than accepting the agent's pasted
transitions, and extended them: the round-2 fix touches an assertion whose whole defect was that it
had never been observed RED, so two transitions were not enough to trust it.

| Mutation | Applied | Result |
|---|---|---|
| **M3a** — restore `v2`'s **exact** `cannot enforce` paragraph, lifted verbatim from `git show v2:site/index.html` | ✅ | **RED** — *"Providers 'cannot enforce' list still names `<code>Skill</code>` as unenforceable — stale post-T097"* (`:488`) |
| **M3b** — remove `<code>Agent</code>` from that list | ✅ | **RED** — *"must still name `<code>Agent</code>` — the Agent spawn tool remains Claude-only"* (`:492`) |
| **M4** — break the number/unit adjacency: `<strong>8 KB</strong>` → `<strong>8</strong> kilobytes` | ✅ | **RED** — *"does not name the 8 KB Codex skill-body cap as an adjacent number+unit"* (`:471`) |

All three restored byte-identically; `tests/test_site_content.py` → **20 passed**, `git status --short`
empty. M3a is the load-bearing one: the assertion now fails against the **real** prior wording, which
is precisely what its predecessor could not do.

M3b matters as much as M3a and was not requested — it proves the fix did not overshoot. Deleting
`Skill` from the unenforceable list is only correct if `Agent` stays pinned there, since the `Agent`
spawn tool genuinely does remain Claude-only. An assertion that merely required `Skill` to be absent
would go green on a page that had deleted the whole paragraph. Both directions are now pinned.

P3-1 confirmed: `_skills_over_codex_cap()` uses the module-level `SKILLS_DIR` (line 20); no second
path derivation remains in the file.

**Full suite after round 2: `6 failed, 834 passed`** — the same 6 pre-existing failures, unchanged
from the `v2` baseline of `6 failed, 831 passed`. +3 net new tests, 0 regressions, 0 pre-existing
test files modified. Those 6 are tracked as **T102** and are explicitly not this task's to fix.

**Outstanding before Done**: Stage 5 `/verify` only. It is user-invocable only in this project — the
Supervisor cannot run it and will not record a PASS it did not observe.

---

## Stage 5 — /verify (user-run, 2026-09-04): **PASS**

Surface: the rendered page. `site/index.html` is what a reader opens, so the evidence is pixels, not
pytest — the suite was deliberately **not** re-run here, since running it proves CI works, not that
the change does. The README half has no runtime surface and was verified by path resolution instead.

Observed at 1280px and 375px in headless Chrome; screenshots delivered to the user.

| # | Driven | Observed |
|---|---|---|
| 1 | Rendered the page at 1280px | Paints; all sections present |
| 2 | Read **Providers** | 8 KB cap, "skipped with a named, loud warning", all four skills as chips; `Skill` gone from the cannot-enforce list, `Agent` retained |
| 3 | Read **Repository layout** | `agents/`/`skills/` canon rows first; both `.claude/*` rows read "Committed **relative symlink** onto…" with the arrow literal shown |
| 4 | Read **Options** | `--harness <name>` row present, default `claude`, values `claude`, `codex`, styling identical to siblings |
| 5 | 🔍 Re-rendered at 375px, measured the right edge across all 13,319px of content | **0 rows** paint outside the body — no page-level horizontal overflow |
| 6 | 🔍 Resolved every path the docs now claim | `agents/general-agent-template.md`, `skills/`, `agents/` all exist; the old `.claude/` form still resolves via symlink |

**Step 5 upgrades UI Evidence row 3 from a justified `N/A` to an observed pass** — the agent could
only argue it structurally in a headless round; it is now measured.

### New finding from the verify run (NOT folded into T101)

⚠️ **The footer makes the same stale-canon claim this task existed to fix.** It reads *"drift-tested
against the live `.claude/` directory by `tests/test_site_content.py`"*, but that file resolves
`AGENTS_DIR = ROOT/agents` and `SKILLS_DIR = ROOT/skills` (lines 19–20) — **plain root, not
`.claude/`**. One word wrong, in a sentence about precisely the thing T101 corrected. Deliberately
**not** fixed here: AC8 locked the footer, and widening scope after a PASS is how a verified diff
stops matching what was verified. Routed to **T102**, which already owns the *"v2 is clean and
green"* correction — same category of claim-that-stopped-being-true.

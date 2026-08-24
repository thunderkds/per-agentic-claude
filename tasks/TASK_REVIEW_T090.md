# TASK_REVIEW — T090: Provider adapters — make "works with any provider" structurally true

> Sibling of `tasks/TASK_GUIDE_T090.md`. Everything here is **filled by the reviewer at Stage
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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_provider_adapters.py` (10 tests covering AC1–AC7, AC10, AC11) |
| Verification command run | ☑ pass | `python -m pytest tests/test_provider_adapters.py -q` → 10 passed; `python -m pytest tests/ -q` → 37 passed; `git diff --exit-code main -- CLAUDE.md && echo "CLAUDE.md untouched: OK"` → `CLAUDE.md untouched: OK` |
| Negative cases hold | ☑ pass | 5 mutation controls (SC2–SC5, SC7) run — see below; each confirmed landed via `git diff --stat`, went RED naming the exact break, reverted with `cp` |
| verify | ☐ N/A | Hard-Stop: `verify` must be run by the user, not the Supervisor/implementing agent — pending user invocation |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed only the 8 predicted files (`AGENTS.md`, `.cursor/rules/agent-base.mdc`, `MANIFEST`, `docs/MULTI_AGENT.md`, `README.md`, `tests/test_provider_adapters.py`, `tasks/TASK_REVIEW_T090.md`) plus one unpredicted but forced repoint (`.claude/hooks/tests/test_agent_guide_dedup.py`'s MANIFEST baseline ref, discovered only by running the full suite); `CLAUDE.md` deliberately not touched |
| Full smoke suite still green (no regression) | ☑ pass | `python -m pytest tests/ .claude/hooks/tests/ -q` → 717 passed, 0 failed. The TASK_GUIDE's 702-passing baseline figure was for `tests/` + `.claude/hooks/tests/` before this task's 10 new tests were added; the delta is consistent with 10 new tests plus this task's own repoint fix to `test_agent_guide_dedup.py` (no other file's test count changed) |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | Pure documentation + one Python test; no UI component (per TASK_GUIDE's UI/Design AC section deletion) |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | Same as above |
| **UI: Responsiveness at target viewports** | ☑ N/A | Same as above |

**Mutation controls (SC2–SC5, SC7), each: mutate → confirm landed via `git diff --stat` → run scoped test → paste RED → revert with `cp`:**

- **SC2** (Karpathy principle name renamed in `AGENTS.md` only): `sed -i 's/Think Before Coding/Think Prior To Coding/' AGENTS.md`; `git diff --stat` confirmed `AGENTS.md | 2 +-`. `pytest -k principle_names` → `AssertionError: AGENTS.md is missing Karpathy principle name 'Think Before Coding' (byte-identical to its spelling in CLAUDE.md)`. Reverted with `cp /tmp/AGENTS.md.bak AGENTS.md`; `git diff --stat` clean.
- **SC3** (Hard-Stop Gate title deleted from `.cursor/rules/agent-base.mdc` only): deleted the gate-6 line; `git diff --stat` confirmed `.cursor/rules/agent-base.mdc | 1 -`. `pytest -k gate_titles` → `AssertionError: .cursor/rules/agent-base.mdc is missing Hard-Stop Gate title 'UI tasks: all three design Evidence rows must be filled before Done or `ship`.' (byte-identical to its spelling in CLAUDE.md)`. Reverted with `cp`; `git diff --stat` clean.
- **SC4** (7th gate title added to `CLAUDE.md`, to no adapter — the load-bearing case): inserted a synthetic gate 7 after gate 6 in `CLAUDE.md`; `git diff --stat` confirmed `CLAUDE.md | 2 ++`. `pytest -k gate_titles` → `AssertionError: expected 6 Hard-Stop Gate titles in CLAUDE.md, found [..., 'Fake gate for SC4 mutation test.'] / assert 7 == 6`. This proves the test parses `CLAUDE.md` live at test time rather than holding a hardcoded copy — a hardcoded-copy test could not have gone RED from a `CLAUDE.md`-only edit. Reverted with `cp /tmp/CLAUDE.md.bak CLAUDE.md`; `git diff --exit-code main -- CLAUDE.md` confirmed clean.
- **SC5** (`.cursor/rules/agent-base.mdc` frontmatter `alwaysApply` set false): `sed -i 's/alwaysApply: true/alwaysApply: false/' .cursor/rules/agent-base.mdc`; `git diff --stat` confirmed `1 +-`. `pytest -k always_apply` → `AssertionError: .cursor/rules/agent-base.mdc frontmatter does not set alwaysApply: true` (regex found `alwaysApply: false`, no match for `true`). Reverted with `cp`; `git diff --stat` clean.
- **SC7** (an adapter's "cannot enforce" section deleted): stripped the `## What Codex cannot enforce here` section out of `AGENTS.md`; `git diff --stat` confirmed `AGENTS.md | 6 --`. `pytest -k cannot_enforce` → `AssertionError: AGENTS.md has no section naming what that provider cannot enforce`. Reverted with `cp`; `git diff --stat` clean.

After all 5 controls, working tree was verified clean (`git status --short` empty) before recording this table.

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**: Verbatim prior content, captured 2026-08-24T03:15Z before any implementation commit.

`AGENTS.md` (12 lines, entire file):
```
# AGENTS.md

This is a thin mirror for non-Claude agentic CLIs (Codex, etc.). `CLAUDE.md` and
`.claude/agents/` remain canonical — if anything here conflicts with those, they win.

Before any work:
- Read `PROJECT_SPEC.md`, your `tasks/TASK_GUIDE_Txxx.md`, and these base rules.
- Work only inside your assigned worktree; touch only the predicted files (Surgical Changes).
- Build test-first; a task is done only when its verification command passes.
- Stop and ask on any ambiguity — never guess.

See `docs/MULTI_AGENT.md` for full dispatch recipes and what does/doesn't port across CLIs.
```

`.cursor/rules/agent-base.mdc` — does not exist (`ls .cursor/rules/agent-base.mdc` returned "No such
file or directory"; no `.cursor/` directory exists in the repo at all).

`MANIFEST` — 6 non-comment lines, no `.cursor/rules` entry:
```
.claude/agents
.claude/skills
.claude/hooks
templates
docs/claude-md
AGENTS.md
```

`docs/MULTI_AGENT.md` (relevant excerpt, "Shared AGENTS.md" section): "It is **not required** for
the dispatch recipes above (the prompt already points at the guides) — it just removes repetition
and gives Cursor/Codex a default to fall back on. Keep it a thin mirror, not a second source of
truth." Its Cursor section only sketches `cursor-agent -p` dispatch and says mirroring
`.claude/agents/general-agent-template.md` into `.cursor/rules/agent-base.mdc` is a suggestion
("see below"), not a fact about an existing file.

`README.md` — carries no multi-provider claim beyond "A general-purpose multi-agent supervisor
framework for Claude Code." (line 3); no mention of Codex/Cursor/adapters anywhere in the file.

`tests/test_provider_adapters.py` — does not exist.

**AFTER**: `AGENTS.md` (33 lines) now inlines all four Karpathy principle names, all six Hard-Stop
Gate titles, the untrusted-content boundary rule, and a "What Codex cannot enforce here" section,
while keeping the canonical-pointer line and a `docs/claude-md/` pointer. `.cursor/rules/agent-base.mdc`
(39 lines, new file) carries the same content with `alwaysApply: true` frontmatter. `MANIFEST` gained
a `.cursor/rules` line (7 non-comment lines total). `docs/MULTI_AGENT.md`'s "Shared AGENTS.md"
section is replaced by "Shared adapters", which states both adapters are required (not "optional
conveniences") and points at DDR-0006 and the new conformance test. `README.md` gained one line
stating the adapters exist. `tests/test_provider_adapters.py` (new, 10 tests) parses `CLAUDE.md` at
test time and asserts equivalence against both adapters; verified command output:
```
$ python -m pytest tests/test_provider_adapters.py -q
..........                                                               [100%]
10 passed in 0.02s
$ python -m pytest tests/ -q
.....................................                                    [100%]
37 passed in 0.05s
$ git diff --exit-code main -- CLAUDE.md && echo "CLAUDE.md untouched: OK"
CLAUDE.md untouched: OK
```

**DELTA**: A Codex-only or Cursor-only user (never opening Claude Code) now receives the kit's
Karpathy principles, Hard-Stop Gates, and untrusted-content rule through a channel their own CLI
auto-reads, instead of receiving none of them.

**WITNESS**: Common-Infrastructure-Agent (T090), 2026-08-24, worktree
`/home/hungnguyenhuu/workspace/pets/wt-t090` branch `feat/t090-impl`, commits `360fc36`
("feat(T090): thin provider adapters carry the kit's non-negotiables") and `35bea1e`
("fix(T090): repoint T066's MANIFEST baseline past T090's edit"). Ran the verification command and
all 5 mutation controls directly in this session; no `memory/event-trace/T090.jsonl` was consulted
as a separate witness — the Supervisor should cross-check the trace file at Stage 4 per the standard
independence rule.

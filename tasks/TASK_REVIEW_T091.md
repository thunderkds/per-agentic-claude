# TASK_REVIEW — T091: Staleness Guard names the wrong source and misses the Cursor adapter

> Sibling of `tasks/TASK_GUIDE_T091.md`. Everything here is **filled by the reviewer at Stage
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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_provider_adapters.py::test_staleness_guard_describes_the_real_adapter_contract` — asserts AC1 (CLAUDE.md named, "this file's Base Rules" phrase absent), AC2 (both adapter paths named, derived from `ADAPTERS`), AC3 (`test_provider_adapters.py` named), AC4 (≤8 non-blank body lines) |
| Verification command run | ☑ pass | RED (pre-fix, current guard text): `AssertionError: Staleness Guard does not name CLAUDE.md as the source the adapters mirror` — 1 failed, 10 passed. GREEN (post-fix): `python3 -m pytest tests/test_provider_adapters.py -q` → `...........` `11 passed in 0.01s` |
| Negative cases hold | ☑ pass | Temporarily rewrote the guard to name only `AGENTS.md` (dropped `.cursor/rules/agent-base.mdc`) — test went red: `AssertionError: Staleness Guard does not name the adapter path '.cursor/rules/agent-base.mdc'`. Restored the fixed text; suite went green again (11 passed) |
| verify | ☑ pass | `/verify` run by the user 2026-08-24 — **pass**. Surface is agent config, so it was driven at the agent: two sub-agents given an identical maintainer task (rename Hard-Stop Gate 5 in `CLAUDE.md`; name what else must change), one with the wired template, one with an unwired control copy with the `## Staleness Guard` section stripped.<br>• WIRED → named **both** adapters: `AGENTS.md:26` and `.cursor/rules/agent-base.mdc:31`.<br>• CONTROL → named **only** `AGENTS.md`, concluding "these are the only two hits"; missed the Cursor adapter (its search skipped the dot-directory). `grep -rn "not done and not shippable" .` confirms three files exist, so the control's miss was real.<br>• Mechanism driven for real: renamed Gate 5 in `CLAUDE.md` leaving both adapters untouched → `FAILED tests/test_provider_adapters.py::test_gate_titles_present_in_every_adapter` (1 failed, 10 passed). Restored → 40 passed.<br>• Probe: whole guard section deleted → `AssertionError: could not locate the '## Staleness Guard' section`.<br>• Probe: identical prose rewrapped at 55 cols, no content added → `Staleness Guard body is 10 non-blank lines, expected <= 8` (budget counts wrapped lines, not content — known P3, accepted).<br>⚠️ Open observation, not an AC failure: asked how it would check its work, the WIRED agent proposed a hand-rolled `grep`, never naming `tests/test_provider_adapters.py`. The adapter-coverage half of the guard changed agent behaviour; the "run the test" half did not land at n=1. |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Touched only `.claude/agents/general-agent-template.md` (the `## Staleness Guard` section) and `tests/test_provider_adapters.py` (one new test + one new path constant), exactly the two files predicted in the guide's Files to Change table; no other file read for context beyond those named in the guide's Mandatory Startup |
| Full smoke suite still green (no regression) | ☑ pass | `python3 -m pytest tests/ -q` → `........................................` `40 passed in 0.08s` (before this task: 39 tests; +1 new test = 40, none broken) |
| Stage 4 review P2-1 fixed (directional word "below" pointed the wrong way) | ☑ pass | Guard's "not the Base Rules below" (Base Rules is at line 14, above the Staleness Guard at line 58, not below) rewritten to "not this file's Base Rules" — no directional word. |
| Stage 4 review P2-2 fixed (negative assertion was a verbatim-string pin) | ☑ pass | Replaced `"this file's Base Rules" not in section` with a regex over the normalized section, `mirrors?(?:\s+of)?\s+(?:this file's\|this template's\|the)\s+Base Rules`, matching the *claim* (mirror-of-Base-Rules as source) regardless of determiner, while the corrected text's negated form ("not this file's Base Rules") does not match. Four probes run against the corrected guard, all confirmed:<br>• Probe 1 ("is a mirror of this file's Base Rules") → RED: `matched 'mirror of this file's Base Rules'`<br>• Probe 2 ("mirrors this template's Base Rules") → RED: `matched 'mirrors this template's Base Rules'`<br>• Probe 3 ("is a mirror of the Base Rules") → RED: `matched 'mirror of the Base Rules'`<br>• Probe 4 (corrected text restored) → GREEN: `11 passed in 0.01s`<br>Full suite re-run after restore: `python3 -m pytest tests/ -q` → `40 passed in 0.04s` |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | Docs + test change only, no UI component |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | Docs + test change only, no UI component |
| **UI: Responsiveness at target viewports** | ☑ N/A | Docs + test change only, no UI component |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**: Verbatim prior content of the `## Staleness Guard` section in
`.claude/agents/general-agent-template.md` (lines 58-62), captured 2026-08-24 before this task's
first implementation commit:

```
## Staleness Guard

Root `AGENTS.md` is a thin mirror of this file's Base Rules for non-Claude CLIs (Codex, etc.). If
you edit Base Rules here, or the Karpathy Engineering Principles table that now lives in each of
the four role guides, check `AGENTS.md` is still an accurate mirror and update it if not.
```

**AFTER**: Verbatim new content of the `## Staleness Guard` section, post-fix:

```
## Staleness Guard

`AGENTS.md` and `.cursor/rules/agent-base.mdc` are adapters for non-Claude CLIs that mirror
`CLAUDE.md`'s non-negotiables (Karpathy principle names, Hard-Stop Gate titles, the
untrusted-content rule, "no TASK_GUIDE = no work"), not this file's Base Rules. If you edit any of
those non-negotiables in `CLAUDE.md`, both adapters need a matching update.
`tests/test_provider_adapters.py` enforces this mechanically at test time — run it rather than
auditing the adapters by eye.
```

(post-Stage-4-review correction, P2-1: "not the Base Rules below" pointed the wrong way — Base
Rules is at line 14, above the Staleness Guard at line 58 — so the directional word was dropped
and replaced with "this file's Base Rules")

**DELTA**: A maintainer editing `CLAUDE.md`'s non-negotiables now gets pointed at the two files
that actually need updating (`AGENTS.md` and `.cursor/rules/agent-base.mdc`) and the test that
mechanically catches drift, instead of being sent to audit `AGENTS.md` against the wrong source
(this file's Base Rules) while the Cursor adapter goes unchecked entirely.

**WITNESS**: Common-Infrastructure-Agent, T091, 2026-08-24 — ran red (against pre-fix guard text),
green (against the fixed text), full suite, and the negative probe (temporary removal of the
Cursor adapter path) in this session; commands and output pasted in the Evidence table above.

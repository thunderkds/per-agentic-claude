# TASK_REVIEW — T100: One response standard for the Supervisor and every sub-agent

> Sibling of `tasks/TASK_GUIDE_T[NNN].md`. Everything here is **filled by the reviewer at Stage
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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_response_standard.py` — 2 structural assertions for AC2: `## Response Standard` appears exactly once in `agents/general-agent-template.md`, and no role guide carries its rule text. Verified discriminating: at the pre-implementation commit `4096b2a` the heading count is 0, so test 1 was RED before the change. |
| Verification command run | ☑ pass | `python3 -m pytest .claude/hooks/tests/ -q` → `5 failed, 790 passed`; `python3 -m pytest tests/ -q` → `1 failed, 41 passed`; `bash scripts/validate.sh` → `validate.sh: PASS`. The 6 failures are exactly the known pre-existing set (`test_memory_channel_and_budget` ×4 + `test_token_audit_format` ×1 = `memory/MEMORY.md` 45,859 vs the 45,000 ratchet; `test_readme_slim::test_readme_is_at_most_60_lines` = README 73 vs 60). No new failure. |
| Negative cases hold | ☑ pass | Four pre-existing guards in `.claude/hooks/tests/` went RED. Two were RED against a first draft of this change and were resolved by tightening the text, not by relaxing the guard: `test_vital_slice::test_ac11_line_cap[CLAUDE.md]` (202 > 200 → rewritten line-for-line back to 200), and `test_agent_guide_dedup::test_t069_ac9_report_per_role_pair_size` (+894 chars > the 620-char table bound → standard tightened to **617** chars, under the bound, cap untouched). The other two are **baseline pins**, repointed to this task's edit commit `c87097e` following the documented T071/T082/T096 precedent in the file itself: `test_agent_guide_dedup::test_ac5_ac10_...byte_identical_to_the_baseline[CLAUDE.md]` (`T070_BASELINE_REF` 8f8cc47 → c87097e — AC1 requires changing `CLAUDE.md`, so the old pin is red by construction) and `test_ac7_per_role_loaded_size...[c-infra]` (`AC7_ROLE_BASELINE["c-infra"]` T082 → T100; c-infra 10,944 vs its 10,327 floor, +617; the other three stay pinned to T066's floor with ~780 chars of headroom, per that file's own "pin the one, leave the three" warning). **Flagged for the Supervisor**: the guide's Files-Must-NOT-Touch list bans `.claude/hooks/` — these are two ref constants and comments, no machinery, and AC1 is unsatisfiable without the first. |
| verify | ☐ pass / ☐ fail / ☐ N/A | |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed: `CLAUDE.md` `## Supervisor Communication Style`, `agents/general-agent-template.md`, the four role guides (checked for duplication only — not edited), and the three pre-existing suites that pin those files. Skipped: `skills/**`, hooks logic, install scripts — no code path touched. |
| Full smoke suite still green (no regression) | ☑ pass | `scripts/validate.sh` PASS; 790/795 hook tests and 41/42 repo tests pass, deltas are the 6 known failures only. |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | Instruction text only — no UI surface. |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | Instruction text only — no UI surface. |
| **UI: Responsiveness at target viewports** | ☑ N/A | Instruction text only — no UI surface. |

### AC6 — measured line counts

| File | Before | After | Delta |
|---|---|---|---|
| `CLAUDE.md` | 200 | 200 | 0 (13 `##` sections before and after — none added) |
| `agents/general-agent-template.md` | 62 | 77 | +15 |
| `agents/backend.md` / `frontend.md` / `qa.md` / `common-infrastructure.md` | 142 / 138 / 127 / 135 | unchanged | 0 |
| **Total (`CLAUDE.md` + `agents/*.md`)** | **804** | **819** | **+15** (budget ≤ 40) |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE** (verbatim prior content, captured 2026-09-02 before the first implementation commit):

`CLAUDE.md` lines 19-25 — `## Supervisor Communication Style`, opening paragraph:

```
## Supervisor Communication Style

The harness already keeps chat replies short and plain by default — no extra rule needed for that.
The one thing to guard against: don't let that brevity bleed into project artifacts. Keep
`PROJECT_KANBAN.md` rows, `TASK_GUIDE_Txxx.md` Evidence, `memory/decisions.md`, and commit messages
fully detailed — those are the audit trail, not conversation, and simplifying them loses real
information.
```

`agents/general-agent-template.md` — there is **no** `## Response Standard` section. Verbatim, the
file's complete section list before this task:

```
$ grep -n '^## ' agents/general-agent-template.md
9:## Base Rules (Inherited by All Sub-Agents)
33:## Search Before You Build
54:## Output Requirements (Every Task)
61:## Staleness Guard
```

`tests/` — no test asserts anything about a response standard:

```
$ grep -rl "Response Standard" tests/ CLAUDE.md agents/
(no matches)
```

**AFTER**:

`agents/general-agent-template.md` — new section, the single definition point (617 chars):

```
## Response Standard

Conversational replies only — Evidence, KANBAN rows, `memory/` and commit messages stay fully
detailed — the audit trail. Governs the prose around a role guide's
fenced `## Output Format` block, never the block.

- Lead with the answer or verdict; method and caveats come after.
- Asking for a decision: recommendation first, alternatives one line each.
- Under ~15 lines unless a report or pasted evidence needs it.
- One table maximum, only to compare on more than two dimensions.
- Say what is blocked and what you need, not all you could do.
- Don't re-list open items your last reply listed; point back in a line.
```

`CLAUDE.md` `## Supervisor Communication Style` — same five lines, false claim replaced, artifact
guard preserved:

```
Chat replies are **not** short by default — the session that registered this rule ran 40+ lines,
stacked tables and three-option menus. `agents/general-agent-template.md`'s `## Response Standard`
binds the Supervisor too: read it and apply it to your own replies. It governs conversation only —
keep `PROJECT_KANBAN.md` rows, `TASK_GUIDE_Txxx.md` Evidence, `memory/decisions.md` and commit
messages fully detailed, since that is the audit trail and simplifying it loses real information.
```

No role guide was edited: all four already mandate reading the template at startup step 4, so the
standard reaches every sub-agent with zero duplicated text.

```
$ python3 -m pytest tests/test_response_standard.py -q
2 passed
```

**DELTA**: The Supervisor and every sub-agent now read one six-rule, checkable standard for what a
reply may look like — recommendation before options, verdict before method, one table, no re-listed
open items — where before `CLAUDE.md` asserted, falsely, that the harness already handled it.

**WITNESS**: Commands above run by the Common-Infrastructure-Agent on 2026-09-02 in
`/home/hungnguyenhuu/workspace/pets/wt-t100` (`memory/event-trace/` is not present in this
worktree). **Not sufficient alone** — the `verify` row is deliberately left blank for the
Supervisor's user-run `/verify`, which is the independent witness.

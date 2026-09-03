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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_response_standard.py` — 2 structural assertions for AC2: `## Response Standard` appears exactly once in `agents/general-agent-template.md`, and no role guide carries its rule text. Verified discriminating: at the pre-implementation commit `4096b2a` the heading count is 0, so test 1 was RED before the change. **Stage 4 P1 (fixed, `551feca`)**: test 2 was vacuous as written — it probed for `state your recommendation first`, a string absent from the standard, so appending the whole standard verbatim to `agents/backend.md` left it green. Probe replaced with the verbatim rule line `recommendation first, alternatives one line each`, plus a self-check that the line still exists in the template so a future reword fails loudly instead of silently re-vacating the guard. Both mutations (duplicate into a role guide; reword the probed rule) now go RED. |
| Verification command run | ☑ pass | `python3 -m pytest .claude/hooks/tests/ -q` → `5 failed, 790 passed`; `python3 -m pytest tests/ -q` → `1 failed, 41 passed`; `bash scripts/validate.sh` → `validate.sh: PASS`. The 6 failures are exactly the known pre-existing set (`test_memory_channel_and_budget` ×4 + `test_token_audit_format` ×1 = `memory/MEMORY.md` 45,859 vs the 45,000 ratchet; `test_readme_slim::test_readme_is_at_most_60_lines` = README 73 vs 60). No new failure. |
| Negative cases hold | ☑ pass | Four pre-existing guards in `.claude/hooks/tests/` went RED. Two were RED against a first draft of this change and were resolved by tightening the text, not by relaxing the guard: `test_vital_slice::test_ac11_line_cap[CLAUDE.md]` (202 > 200 → rewritten line-for-line back to 200), and `test_agent_guide_dedup::test_t069_ac9_report_per_role_pair_size` (+894 chars > the 620-char table bound → standard tightened to **617** chars, under the bound, cap untouched). The other two are **baseline pins**, repointed to this task's edit commit `c87097e` following the documented T071/T082/T096 precedent in the file itself: `test_agent_guide_dedup::test_ac5_ac10_...byte_identical_to_the_baseline[CLAUDE.md]` (`T070_BASELINE_REF` 8f8cc47 → c87097e — AC1 requires changing `CLAUDE.md`, so the old pin is red by construction) and `test_ac7_per_role_loaded_size...[c-infra]` (`AC7_ROLE_BASELINE["c-infra"]` T082 → T100; c-infra 10,944 vs its 10,327 floor, +617; the other three stay pinned to T066's floor with ~780 chars of headroom, per that file's own "pin the one, leave the three" warning). **Flagged for the Supervisor**: the guide's Files-Must-NOT-Touch list bans `.claude/hooks/` — these are two ref constants and comments, no machinery, and AC1 is unsatisfiable without the first. |
| verify | ☑ pass | Stage 5 `/verify` run by the Supervisor 2026-09-03 at the **agent-config surface** — the change was driven, not read: the same decision-shaped question put to a fresh `common-infrastructure` sub-agent three times (control on `v2` without the standard; treatment with it; treatment with the reworded text). PASS on the claim: `recommendation first` moved the recommendation to the top of the reply in both treatment runs and left it buried mid-reply in control, so the standard demonstrably reaches every sub-agent through the template with zero duplicated text (AC2/AC4). Two rules were found not to bind and were reworded under this verdict — see **Adherence re-measurement** below. Recorded limits: reply *length* did not materially change in any run (~20 lines each), and the `one table` rule went untested since no run produced a table. Two findings outside this task's scope: `scripts/test-claude-md-refs.sh` fails identically on `v2` (pre-existing, and `validate.sh` never calls it — a dead guard); and all four role guides' startup step 4 still enumerates only two of the template's five sections, so the clause under-sells the file even though the standard does arrive. |
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

### Supervisor adjudication — the flagged `.claude/hooks/` edit (2026-09-03)

**Accepted.** The guide's Files-Must-NOT-Touch bans `.claude/hooks/` to keep this guidance-only task
from adding machinery. The change under that path is `.claude/hooks/tests/test_agent_guide_dedup.py`
only, and the diff is two baseline-ref string constants plus explanatory comments — no hook logic,
no new machinery, nothing the ban was written to prevent. `T070_BASELINE_REF` is red *by
construction* once AC1 edits `CLAUDE.md`, so AC1 is unsatisfiable without repointing it; both
repoints follow the T071/T082/T096 precedent documented in that file, keep the assertion bodies
untouched, and pin only the one role guide that breached (`c-infra`), leaving the other three on
T066's floor with their headroom intact — exactly the "pin the one, leave the three" warning the
file itself carries. Recorded here rather than waived silently.

### Supervisor check — AC7 not triggered (2026-09-03)

`agents/general-agent-template.md`'s Staleness Guard scopes the `AGENTS.md` /
`.cursor/rules/agent-base.mdc` mirror to `CLAUDE.md`'s non-negotiables (Karpathy names, Hard-Stop
Gate titles, untrusted content, "no TASK_GUIDE = no work") and explicitly **not** to this file's
Base Rules. `## Response Standard` is a Base-Rules-tier section of the template, so no mirror is
due. Confirmed live: `python3 -m pytest tests/test_provider_adapters.py -q` -> `11 passed`.

### Adherence re-measurement — three-run A/B at the agent surface (2026-09-03)

Stage 5 `/verify` drove the *agent config* surface directly rather than reading the text: the same
decision-shaped question ("21 stale worktrees, what do we do? I need to decide") put to a fresh
`common-infrastructure` sub-agent under three conditions, same model, same startup steps.

| Run | Standard in scope | Where the recommendation landed | Preamble before it |
|---|---|---|---|
| Control | absent (`v2` main checkout) | after two blocks of enumerated findings, mid-reply | full method + findings narration |
| Treatment v1 | present, original wording | bold single line, ~line 3 | two narration sentences ("So this is not really a judgment call about ambiguous state — the data is clean") |
| Treatment v2 | present, reworded | bold single line, ~line 3 | one factual clause; the narration sentences are gone |

**What this establishes.** The rule that binds is the structural one — `recommendation first` moved
the recommendation in both treatment runs and did not in control. That is AC4, the rule the guide
names as the highest-value one, demonstrated rather than asserted.

**What it disproves, and the fix applied.** The two rules carrying a self-granting escape clause did
not bind: `Under ~15 lines unless a report or pasted evidence needs it` (every agent judges its own
reply the exception) and `One table maximum, only to compare on more than two dimensions`. Treatment
v1 ran ~20 lines, no shorter than control. Both were reworded to describe a structural act instead of
a self-assessed threshold — `Cut sentences restating the question or narrating what you read` and
`A table only to compare on 3+ dimensions, never to lay out one thing`. Treatment v2 shows the
narration lead-in gone, which is the targeted effect.

**Honest limit, recorded rather than smoothed over.** Reply *length* did not materially change across
all three runs (~20 lines each). Guidance shifts a reply's structure; it does not compress it. The
numeric cap was removed rather than kept as decoration, since three runs showed nothing honored it.
Closing the length gap would need enforcement, which this task's cut list explicitly forbids and the
user explicitly chose against — so it belongs to a follow-up task, not to a silent scope widening
here.

Suites after the reword: `tests/test_response_standard.py` + `test_agent_guide_dedup.py` -> 58 passed;
`.claude/hooks/tests/` -> 5 failed / 790 passed; `tests/` -> 1 failed / 41 passed (the 6 known
pre-existing failures, unchanged); `scripts/validate.sh` -> PASS. Section is 635 chars, under the
620-char *pair-delta* bound as measured by the guard (qa pair +611); `agents/general-agent-template.md`
stays at 77 lines, so AC6 remains +15 against its 40-line budget.

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

# TASK_GUIDE — T095: The merge gate cannot see evidence created in a worktree, prescribes a remedy the project disproved, and blocks writes whose *data* mentions a push
**Date**: 2026-08-27
**Complexity Level**: C2
**Risk Level**: Medium
**Priority**: P0
**Assigned agent**: Common-Infrastructure-Agent
**Agent guide**: `.claude/agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

Before writing any code:
1. Read `PROJECT_SPEC.md`
2. Read `memory/MEMORY.md`
3. Read this file completely
4. Read `.claude/agents/common-infrastructure.md`
5. C2 task, multi-file: read `memory/codebase-map.md`
6. Read `.claude/hooks/lib/task_context.py`'s **module docstring in full** (lines 1–60). It is the
   authoritative account of why the env var does not work and why the state file is anchored to the
   main checkout. Defect B is a contradiction between that docstring and a message printed one file
   over; you cannot judge the fix without having read it.
7. Read `pre_bash_block_unsafe_merge.py` lines 55–120 before touching Defect C — the quoted-span and
   command-separator handling there is deliberate and was itself the product of an earlier fix.

---

## Requirement (Pillar 1 — Adapt the requirement)

User request, 2026-08-27, verbatim:

> "continue do the job that we should update before 94"

Context: T094's work is complete, verified, and committed on `fix/t094-hook-suite-green`, but the
push is **blocked** by `.claude/hooks/pre_bash_block_unsafe_merge.py`:

```
[hook:pre_bash] Pipeline gate failed — cannot push/merge:
  • Tasks in Ready for Review missing Stage 5 verify evidence: T094 (no evidence row)
Complete Stage 4 review and Stage 5 verify first.
  Note: a Bash command is attributed to a task only via CLAUDE_ACTIVE_TASK — run the task's
  verification command as `CLAUDE_ACTIVE_TASK=Txxx <command>` or no trace record is filed under it.
```

T094's evidence is real and filled. The gate cannot see it. This task unblocks T094 — hence
"before 94".

**Restated intent**:
> Make the merge gate able to see Stage 5 evidence produced where Stage 3 actually happens — inside
> a worktree — stop its remediation note from prescribing a mechanism this project measured as
> non-functional, and stop it from classifying a command as a push because the *data* the command
> carries mentions one. Fix all three at cause without weakening the gate: it must still fail
> closed, and still refuse a task whose evidence genuinely does not exist.

Three defects, unrelated in mechanism, sharing one deliverable: a gate whose block is truthful,
actionable, and aimed at actual pushes. All three were surfaced by the same blocked push, and
Defect C was surfaced by attempting to write this very file.

### Defect A — the gate reads the main checkout's `tasks/`, but Stage 3 writes evidence in the worktree

`has_filled_verify_row()` (`pre_bash_block_unsafe_merge.py:232`) resolves its Evidence section under
`TASKS_DIR`, which is `os.path.join(ROOT, "tasks")` (line 20). `ROOT` derives from the hook file's
own location, and `.claude/settings.json` invokes every hook as
`python3 "$CLAUDE_PROJECT_DIR"/.claude/hooks/...` — so `ROOT` is always the **main checkout**.

Since T064 the Evidence table lives in `tasks/TASK_REVIEW_Txxx.md`, and the guide keeps only a
pointer (`> Filled by the reviewer at Stage 4/5 in tasks/TASK_REVIEW_Txxx.md`). That review file is
created **by the agent, in its worktree, on its task branch**. Until the branch merges it does not
exist in the main checkout at all.

Reproduced live 2026-08-27, not theorised:
- `ls tasks/TASK_REVIEW_T094.md` in the main checkout → `No such file or directory`
- the same path in `wt-t094` → present, with a filled `☑ pass` verify row
- `has_filled_verify_row("T094")` therefore returns `False`, and the gate appends the literal suffix
  `(no evidence row)` — the exact message observed.

The function's own docstring calls this the one place where "a wrong answer is silent and
repo-wide". It is currently giving a wrong answer for every task whose evidence lives on a branch,
which — given Stage 3 is worktree-isolated by mandate (`CLAUDE.md:85`) — is every task.

**Why this stayed latent until now.** The gate only scans tasks sitting in **Ready for Review** on
the board. Previous tasks pushed from their worktrees while their row still read Todo or In
Progress, so the scan found nothing to check. T094 is the first task whose row was moved to Ready
for Review *before* its branch was pushed. The gate is not newly broken; it is newly reachable.
Do not "fix" this by advising that rows be moved later — that makes the gate's coverage depend on
bookkeeping order, which is the opposite of a gate.

### Defect B — the gate's remediation note prescribes the mechanism T047 disproved

Lines 329–330 print:

> `a Bash command is attributed to a task only via CLAUDE_ACTIVE_TASK — run the task's verification
> command as CLAUDE_ACTIVE_TASK=Txxx <command>`

`.claude/hooks/lib/task_context.py`'s docstring (and T047, and `craft-spawn-prompt`'s element 6)
record the measured opposite: a hook process is spawned by the harness as a **sibling** of the tool
call, not a child of the command inside it, so it inherits the harness's environment and never the
subshell a `Bash` tool call creates. Every record produced under that instruction landed in
`_untagged.jsonl`, and this very gate then correctly failed closed on it — blocking honest tasks.
That is precisely what happened to T094's Stage 5 run.

The working channel is documented in the same file (`task_context.py:115`): a state file at
`<main-checkout>/.claude/hooks/.state/active_task`, written with a shell redirect and an **absolute**
path.

So the gate blocks, then hands the operator instructions that cannot lift the block, while the
instructions that can sit one file away. The word "only" in that message is also false — the state
file is a second, working mechanism.

Line 84's separate comment ("export CLAUDE_ACTIVE_TASK and run it unwrapped") carries the same false
premise and is in scope for the same reason.

### Defect C — the gate classifies a command by its data, so writing *about* a push is treated as pushing

Found 2026-08-27 while attempting to create this guide. The Supervisor ran a single `cat > file`
heredoc whose **body** — the prose you are reading — contains the words `git push`. The gate
rejected it with the full pipeline-gate block. No push was attempted; the command was a file write.

This is the mirror image of the quoted-span handling already in the file: `QUOTED_SPAN_PATTERN`
(line 92) exists precisely because "quoted spans are data, not commands", and `bash -c "…"` is
deliberately treated as a mention. Heredoc bodies are the same category of data and are not
recognised as such.

Consequence, and why it is P0 rather than cosmetic: the gate makes it impossible to author any
document that discusses pushing or merging via a heredoc — which includes every future TASK_GUIDE
about this hook, this guide included. It also pushes authors toward non-Bash write paths purely to
evade a false positive, which is exactly the kind of workaround that erodes a gate's credibility.

The fail-closed principle does **not** justify this. Fail-closed is about ambiguity in a real
push; this is a misclassification of a write as a push.

**Out of scope**:
- Any weakening of fail-closed behaviour for genuine pushes/merges. A missing guide, missing review
  file, unreadable file, absent Evidence section, unfilled row, or template `☐ pass` placeholder
  must all still resolve to False. The docstring's warning stands: if "review file missing" ever
  means anything other than "no evidence", the gate stops gating on every task at once.
- The `trace_shows_verification()` trace requirement itself — correct and load-bearing (a text claim
  must be corroborated by a real tool call). Only the *advice for how to satisfy it* is wrong.
- The state file's deliberate anchoring to the main checkout (`task_context.py:50`). An intentional
  T047 decision, not a bug; do not "fix" it to be worktree-local.
- `find_kanban_section()` and anything T093/T094 touched.
- Making the gate resolve evidence from the *branch* via `git show`. Considered and rejected at
  grill: the gate runs before a push, when the relevant commit may not exist in the main checkout's
  object store at all. An implementer who believes otherwise must demonstrate it, not assume it.

**Requirement Refs**: none — defect registered from a live blocked push, not a PRD feature.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (Supervisor, 2026-08-27)
- [x] Domain terms align with `PROJECT_SPEC.md` — "merge gate", "fail closed", "worktree", "trace attribution" all pre-existing
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] Requirement Refs: none exist, and none are needed (defect task)

---

## Dependencies & Reachability

**Depends on**: `None`

**Blocks**: T094 — its push cannot proceed until Defect A is fixed.

**Entry point**: `printf '%s' '<PreToolUse Bash event JSON>' | python3 .claude/hooks/pre_bash_block_unsafe_merge.py`

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | With a task in Ready for Review whose `TASK_REVIEW_Txxx.md` exists **only in a worktree**, the gate finds the filled verify row and does not emit `(no evidence row)` | Defect A |
| 2 | With a task in Ready for Review whose review file exists **nowhere**, the gate still blocks with `(no evidence row)` — fail-closed preserved | Out of scope: no weakening |
| 3 | Each of the six fail-closed inputs named in `has_filled_verify_row`'s docstring (missing guide, missing review file, unreadable file, absent Evidence section, unfilled row, `☐ pass` placeholder) still returns False | Out of scope: no weakening |
| 4 | The gate's blocked-push message no longer instructs `CLAUDE_ACTIVE_TASK=Txxx <command>` as the way to attribute a Bash call, and instead names the state-file write with an absolute path | Defect B |
| 5 | The word "only" is gone from that message, or is accurate — both the env var (set before the session starts) and the state file are working channels | Defect B |
| 6 | Line 84's `export CLAUDE_ACTIVE_TASK and run it unwrapped` comment is corrected on the same grounds | Defect B |
| 7 | A heredoc write whose **body** contains `git push` / `git merge`, with no such command outside the body, is not treated as a push — the gate stays silent | Defect C |
| 8 | A real push **on the same command line as** a heredoc write is still caught (e.g. `cat > f <<'E' … E` followed by `; git push`) — the fix must not become a way to smuggle a push past the gate | Defect C, anti-evasion |
| 9 | Negative / anti-vacuity: with the AC1 fix reverted, the worktree-evidence scenario goes back to emitting `(no evidence row)`; with the AC7 fix reverted, the heredoc write is blocked again | A + C, anti-vacuity |
| 10 | `python3 -m pytest .claude/hooks/tests/ -q` stays green at ≥ 697 passed, and `python3 -m pytest tests/ -q` at 40 passed | no regression |
| 11 | At least one new test per defect (A, B, C), all against constructed fixtures — not against the live repo's worktree list, which varies by machine | Hard-Stop Gate 5 |

---

## Evaluation & Acceptance

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | Fixture: board row in Ready for Review, review file with `☑ pass` present only under a worktree path | gate allows (no `(no evidence row)`) | automated test |
| 2 | Same board row, no review file anywhere | gate blocks with `(no evidence row)` | automated test |
| 3 | Heredoc write whose body mentions `git push`, nothing else on the line | gate silent, exit 0 | automated test |
| 4 | Heredoc write body mentioning `git push`, plus a real `; git push` after the terminator | gate blocks | automated test (anti-evasion probe) |
| 5 | AC1 fix reverted, fixture 1 replayed | gate blocks again | automated test (anti-vacuity probe) |
| 6 | A real push attempted from `wt-t094` on `fix/t094-hook-suite-green` | proceeds, or fails only on the trace half, reported honestly | manual probe, output pasted |
| 7 | Gate's block message, captured verbatim | contains the state-file remedy, not `CLAUDE_ACTIVE_TASK=Txxx <command>` | manual probe, output pasted |

### Verification Command (exact, runnable)

```bash
python3 -m pytest .claude/hooks/tests/ -q && python3 -m pytest tests/ -q
```

Expected: `≥697 passed`, then `40 passed`.

### Evidence (filled by reviewer at Stage 4/5)

> Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T095.md`.

---

## Demonstration

> See `tasks/TASK_REVIEW_T095.md`.

---

## Approach

**Vital slice**: Defects A and C. A blocks T094 and every task after it; C blocks authoring any
document about this subsystem, including its own fix's guide. B is a two-string edit that costs
minutes and saves the next operator an hour spent on advice that cannot work.

**Cut list**:
- No redesign of where Evidence lives. T064 put it in `TASK_REVIEW_Txxx.md` and that stands.
- No general "make all hooks worktree-aware" sweep. One hook, one resolution path, fixed here.
- No change to how the board is parsed or how Ready for Review is detected.
- No general shell parser. Defect C is fixed by recognising heredoc bodies as data, not by
  attempting to tokenize shell properly — that is a rabbit hole and the existing quoted-span
  approach is the established local idiom.

**Recommended approach, Defect A.** Resolve the Evidence file across the main checkout **and** the
repo's live worktrees, taking the first filled row found. `git worktree list --porcelain` gives the
paths and git is already a dependency. Keep the existing main-checkout lookup first so the common
post-merge case does not change behaviour or cost. Every failure in the worktree enumeration — git
absent, command error, unparsable output — must degrade to "main checkout only", never to "allow":
the enumeration is an *additional* place to find evidence, never a reason to skip the check. Write
the test against a constructed fixture directory list injected via the existing `tasks_dir`
parameter shape, rather than shelling out to git inside the test.

**Recommended approach, Defect B.** Replace the two message/comment strings with the state-file
instruction already written and proven in `task_context.py:115`. Reuse that wording rather than
composing a new variant — a third phrasing of this mechanism is how the first two drifted apart.
Name the absolute-path requirement explicitly; a relative path silently resolves into the worktree
and is the T047 Stage 4 P1 finding.

**Recommended approach, Defect C.** Extend the existing data-stripping step: before scanning for
command invocations, replace heredoc bodies the same way `QUOTED_SPAN_PATTERN` replaces quoted
spans — with a space, not a deletion, so removal cannot glue two words into a spurious invocation.
Match the terminator that the heredoc header actually declares (quoted and unquoted forms,
`<<` and `<<-`), and strip only up to that terminator so anything after it is still scanned as a
command — that is what makes AC8 pass. Add AC8's test in the same commit as the fix, not after:
a fix here that over-strips silently disarms the gate, which is the highest-consequence failure in
this file.

Do **not** attempt Defect A by making agents copy their review file into the main checkout. That
puts an unversioned duplicate outside the task branch and reintroduces the drift T064 removed.

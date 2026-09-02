# TASK_GUIDE — T099: Quoted spans are sometimes data and sometimes code, and the gate cannot currently tell

**Complexity Level**: C2
**Risk Level**: Medium
**Priority**: P1
**Assigned agent**: Common-Infrastructure-Agent
**Agent guide**: `.claude/agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

1. Read `PROJECT_SPEC.md`.
2. Read this guide in full — **especially the "Why the T095 rule does not transfer" block**, which
   is the whole reason this task is C2 and not the C1 its registration guessed.
3. Read `.claude/agents/common-infrastructure.md`.
4. Read `memory/MEMORY.md`, then the **T095** entry in `memory/decisions.md` and both T095 entries
   in `memory/learnings.md`. Read `.claude/hooks/lib/shell_data.py` in full — its module docstring
   is the design rationale you are extending.
5. **Trace attribution**: `mkdir -p /home/hungnguyenhuu/workspace/pets/personal-agentic-claude/.claude/hooks/.state && printf '%s\n%s\n' "T099" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > /home/hungnguyenhuu/workspace/pets/personal-agentic-claude/.claude/hooks/.state/active_task`
   Literal absolute path. Not `$CLAUDE_PROJECT_DIR` (empty inside a `Bash` tool call), not relative.
6. **Demonstration BEFORE capture**: fill the BEFORE field in
   `<your-worktree>/tasks/TASK_REVIEW_T099.md` before your first implementation commit. This task
   changes executable code, so BEFORE is real timestamped output of the matrix in AC1/AC2 below.

> **Working note.** Any `Bash` command whose text contains the literal words `git push` or
> `git merge` — even inside quotes, even in a `grep` pattern — will be blocked by the very gate you
> are fixing, whenever any task sits in In Progress. That is the defect. Build such strings at
> runtime (e.g. `G="g"+"it p"+"ush"` in a Python heredoc) while you work.

---

## Requirement (Pillar 1 — Adapt the requirement)

Registered 2026-09-01 from T095's Stage 4/5, then **materially revised at Stage 2** after the
behaviour was measured rather than assumed.

T095 fixed the heredoc form of "a hook reads a command's data as command text". The **quoted-span**
form is still live, in both hooks, and it is worse than the registration recorded:

```
quoted arg to python3 -c     pre_bash=BLOCKS  post_bash=FIRES
echo of a sentence           pre_bash=BLOCKS  post_bash=FIRES
grep for the literal         pre_bash=BLOCKS  post_bash=FIRES
heredoc body (T095 fixed)    pre_bash=silent  post_bash=silent
a REAL push (control)        pre_bash=BLOCKS  post_bash=FIRES
```

The registration described this as prompt noise in `post_bash_memory_update.py`. It is not:
`pre_bash_block_unsafe_merge.py` **blocks** these commands outright. An ordinary
`grep -r "git push" .claude/` is refused whenever any task is In Progress — which is precisely when
an agent is most likely to run it. This is a live obstruction to honest work, not cosmetic.
It blocked the Supervisor's own probe while this guide was being written.

### Why the T095 rule does not transfer (read before designing anything)

`pre_bash_block_unsafe_merge.py` already has `QUOTED_SPAN_PATTERN` (line 105) and already strips
quoted spans — but **only** in `invokes_test_runner` (line 189), the *evidence* matcher. The
push/merge matcher in `main()` never sees it. The obvious fix is to reuse the pattern there too.
**That fix is wrong, and it fails in the dangerous direction.** Measured:

```
echo "... git push ..."          today=BLOCK   after naive quoted-strip=ALLOW
bash -c "git push origin main"   today=BLOCK   after naive quoted-strip=ALLOW  <-- a REAL push
ssh box "cd /r && git push"      today=BLOCK   after naive quoted-strip=ALLOW  <-- a REAL push
```

A heredoc body is *definitionally* data: it is being written to a file. A quoted span is **not** —
it is data in `echo "…"` and `grep "…"`, and it is executable command text in `bash -c "…"`,
`sh -c "…"`, `ssh host "…"`, `docker exec … "…"`. Stripping it unconditionally disarms the gate for
exactly the commands that matter most.

Note why `invokes_test_runner` gets away with the same stripping: it is proving a runner *was*
invoked, so a false negative means "not verified", which fails **closed**. In the push matcher a
false negative means "not a push", which fails **open**. Same pattern, opposite consequence. This
asymmetry is the task.

**Restated intent**:
> Teach the two hooks the difference between a quoted span that is data and a quoted span that is
> command text, so an operator can `grep` and `echo` the words "git push" without being blocked,
> while `bash -c "git push"` and `ssh host "… git push"` keep blocking exactly as they do today.
> Preserve T095's direction rule throughout: every uncertainty resolves toward treating the span as
> **code**, because over-blocking is recoverable and a silently disarmed gate is not.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] I can state, in my own words, why `bash -c "…"` makes quoted spans different from heredoc
      bodies, and I have reproduced the three-row ALLOW table above myself.
      **Signed off (Common-Infrastructure-Agent, 2026-09-02T03:31Z).** A heredoc body has a
      *syntactic* destination: `<<'EOF' … EOF` is text being fed to a redirection, so the shell will
      never execute it, whatever it says. A quoted span has no destination of its own — it is an
      argument, and whether the shell executes it is decided entirely by the *command it is an
      argument to*. `echo "git push"` prints it; `bash -c "git push"` runs it. Same bytes, opposite
      meaning, and nothing inside the span distinguishes them. So a quoted span can only be
      classified by looking left, at its wrapper — which is exactly the lookup heredoc stripping
      never needs. Three-row table reproduced above (see `tasks/TASK_REVIEW_T099.md` BEFORE):
      all three block today, all three would be allowed by an unconditional quoted-span strip, and
      two of the three are real pushes.
- [x] I understand that a false negative in the push matcher fails **open**, and that this is the
      opposite of `invokes_test_runner`'s failure direction.
      **Signed off.** `invokes_test_runner` returns "was a runner invoked?"; a false negative there
      answers "not verified", so the gate refuses the merge — the operator loses time. `main()`'s
      matcher returns "is this a push?"; a false negative there answers "not a push", so the gate
      steps aside and the push ships un-reviewed — and nobody is told. Same stripping, opposite
      cost, which is why the same pattern cannot simply be reused in the second place.
- [x] I have confirmed which of the two hooks' matchers currently lack quoted-span handling.
      **Signed off.** Both. `pre_bash_block_unsafe_merge.py` defines `QUOTED_SPAN_PATTERN` at line
      105 but uses it in exactly one place — `invokes_test_runner` (line 189), the evidence matcher.
      `main()`'s `BLOCKED_PATTERNS` loop sees only `strip_heredoc_bodies(command)`.
      `post_bash_memory_update.py` has no quoted-span handling at all — its `GIT_MEMORY_PATTERNS`
      loop likewise sees only `strip_heredoc_bodies(command)`. Confirmed by the BEFORE matrix:
      every AC1 data row is `pre_bash=BLOCKS  post_bash=FIRES`.

---

## Dependencies & Reachability

**Depends on**: T095 (merged) — `lib/shell_data.py` and its direction rule.
**Blocks**: nothing, but it obstructs every task while one is In Progress.
**Entry point**: `.claude/hooks/pre_bash_block_unsafe_merge.py` and
`.claude/hooks/post_bash_memory_update.py`, invoked by `settings.json` as PreToolUse/PostToolUse
Bash hooks. Drive them by piping event JSON, as `test_merge_gate_t095.py` does.

---

## Acceptance Criteria

- **AC1 — data spans stop blocking.** `echo "…git push…"`, `grep -r "git push" .claude/`, and
  `python3 -c "print('git push')"` are all allowed by `pre_bash_block_unsafe_merge.py` and silent in
  `post_bash_memory_update.py`, with a task In Progress. Red before the fix.
- **AC2 — code spans keep blocking.** `bash -c "git push origin main"`, `sh -c '… git merge …'`, and
  `ssh box "cd /r && git push"` still block. **This is the AC that makes the task non-trivial** — a
  naive quoted-span strip turns all three green-as-in-allowed and must be caught here.
- **AC3 — the real push still blocks.** Unquoted `git push origin main` blocks. Control.
- **AC4 — heredoc behaviour unchanged.** Every T095 assertion in
  `.claude/hooks/tests/test_merge_gate_t095.py` and `test_memory_hook_heredoc_data.py` still passes,
  unmodified. T099 composes with T095; it does not replace it.
- **AC5 — composition order is asserted.** A command that is both (a heredoc whose body contains
  `bash -c "git push"`) is treated as data — the heredoc wins, because its body is being written to
  a file regardless of what it says.
- **AC6 — the two importers keep their opposite guard directions.** `pre_bash` still blocks on an
  unavailable resolver; `post_bash` still falls back to the pre-T095 behaviour. Any shared change
  must preserve this (T095 decision, recorded in `memory/decisions.md`).
- **AC7 — nesting and mixed quotes.** `bash -c 'git push'` (single quotes), a quoted span inside a
  quoted span, and an unterminated quote each resolve toward **code** (block), never toward data.
- **AC8 — anti-vacuity.** A test that reverts the fix in place and asserts AC1 goes red again, and a
  second that replaces the fix with the *naive* quoted-span strip and asserts AC2 goes red — proving
  the wrapper-awareness is load-bearing and not decoration.

---

## Evaluation & Acceptance

### Success Criteria (observable, pass/fail)

An operator can grep and echo the blocked phrases freely while a task is In Progress; every real
push, including one wrapped in `bash -c` or `ssh`, still blocks.

### Verification Command (exact, runnable)

```sh
python3 -m pytest .claude/hooks/tests/ -q && python3 -m pytest tests/ -q
```

Baseline is 757 hook tests + 40 smoke as of T095's merge; the delta must be this task's new tests
only, with no pre-existing test modified (AC4).

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** See `tasks/TASK_REVIEW_T099.md`.

---

## Demonstration

> See `tasks/TASK_REVIEW_T099.md`.

---

## Approach

**Vital slice**: wrapper-aware quoted-span classification in `lib/shell_data.py`, applied to both
hooks' push/merge matchers.

Likely shape — **not prescriptive, but the constraint it satisfies is**: a `strip_quoted_spans` that
takes a set of shell-invoking prefixes (`bash -c`, `sh -c`, `zsh -c`, `ssh`, `docker exec`,
`docker run`, `env … sh -c`) and does **not** strip a span that follows one; everything else is
treated as data. Compose with `strip_heredoc_bodies` — heredocs first (AC5).

**Cut list** (deliberately not built):
- No shell tokenizer. `lib/shell_data.py`'s docstring names this as the rabbit hole it exists to
  avoid; that constraint is inherited, not up for revisiting.
- No attempt to be exhaustive about shell-invoking wrappers. An unknown wrapper must default to
  **not stripping** (block), so the list being incomplete over-blocks rather than under-blocks.
- No change to `invokes_test_runner` — its stripping is correct for its failure direction.
- No change to `QUOTED_SPAN_PATTERN` itself unless a test forces it.
- No new hook, no change to `settings.json`.

---

## Edge Case Checklist

- Escaped quotes inside a span; mismatched/unterminated quotes.
- `bash -c` with the command unquoted (`bash -c git`); `bash -lc "…"`.
- A wrapper appearing *after* a separator: `echo hi; bash -c "git push"`.
- A quoted span that is an argument to a wrapper but not the command (`ssh -o "StrictHostKeyChecking=no" box "git push"`).
- Empty command, non-string command, command with no quotes at all.

---

## Files to Change (Predicted)

- `.claude/hooks/lib/shell_data.py` — new `strip_quoted_spans`, wrapper-aware.
- `.claude/hooks/pre_bash_block_unsafe_merge.py` — apply it in `main()`'s matcher only.
- `.claude/hooks/post_bash_memory_update.py` — apply it in its matcher.
- `.claude/hooks/tests/` — new test file for AC1–AC8.

While you are in `lib/shell_data.py`, fix its stale line 39 docstring claim that
`post_bash_memory_update.py` is "untouched here (out of scope)" — untrue since T095's `00c54c6`.
That is a known open P2 from T095's review, and this is the task that touches the file.

## Files Must NOT Touch

- `.claude/hooks/tests/test_merge_gate_t095.py`, `test_memory_hook_heredoc_data.py` — T095's
  assertions must pass **unmodified** (AC4). Add new files instead.
- `invokes_test_runner` and `QUOTED_SPAN_PATTERN`'s existing use in the evidence matcher.
- `update.sh`, `setup.sh`, `lib/harness-fetch.sh` — T098 is live in those files.

## Test Plan

Fixture-driven, at the hook entry point, in the style of `test_merge_gate_t095.py`. Every AC gets an
assertion; AC8's two anti-vacuity probes are mandatory — one reverting the fix, one substituting the
naive strip.

## Completion Checklist

- [ ] Requirement Fidelity Gate signed off
- [ ] BEFORE captured before the first implementation commit
- [ ] AC1–AC8 covered by passing automated assertions
- [ ] Verification Command run, output pasted into Evidence
- [ ] AFTER + DELTA + WITNESS filled
- [ ] UI Evidence rows ☐ N/A (pure-infrastructure task, no UI surface)

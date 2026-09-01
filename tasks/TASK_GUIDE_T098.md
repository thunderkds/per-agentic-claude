# TASK_GUIDE — T098: `update.sh` re-Claude-ifies a Codex-only project

**Complexity Level**: C1
**Risk Level**: Low
**Priority**: P2
**Assigned agent**: Common-Infrastructure-Agent
**Agent guide**: `.claude/agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

1. Read `PROJECT_SPEC.md`.
2. Read this guide in full, including the **Decision (locked)** block below.
3. Read `.claude/agents/common-infrastructure.md`.
4. Read `memory/MEMORY.md` (path, not pasted) and follow its pointers into
   `memory/decisions.md` for the **T096** and **T097** entries — this task sits directly on top of
   both and contradicts the second one.
5. **Trace attribution**: before running any test or verification command, write the active-task
   state file so the trace hook can attribute your `Bash` calls:
   `mkdir -p /home/hungnguyenhuu/workspace/pets/personal-agentic-claude/.claude/hooks/.state && printf '%s\n%s\n' "T098" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > /home/hungnguyenhuu/workspace/pets/personal-agentic-claude/.claude/hooks/.state/active_task`
   Do this once at the start of your session. Do **not** try `CLAUDE_ACTIVE_TASK=T098 <cmd>` inside
   a `Bash` tool call, and do **not** write a cwd-relative path — neither reaches the hook (T047).
6. **Demonstration BEFORE capture**: before your first implementation commit, fill the
   `## Demonstration` BEFORE field in
   `<your-worktree>/tasks/TASK_REVIEW_T098.md`. This task changes executable code, so BEFORE is the
   real, timestamped output of the Verification Command below, captured on a clean install. A BEFORE
   captured after the change is not a BEFORE; there is no `N/A` path.

---

## Requirement (Pillar 1 — Adapt the requirement)

Registered 2026-08-31 from T097's Stage 5 `/verify`, observed on a clean install rather than
inferred.

`setup.sh --harness codex` correctly skips the Claude canon symlinks and logs
*"Harness 'claude' not selected — skipping .claude/{skills,agents} symlinks"*. But `update.sh` calls
`harness_install_canon_symlinks .` unconditionally at `update.sh:461`, so the very next no-flag
update recreates `.claude/skills` and `.claude/agents`. Verified: absent after setup, present after
one update.

The mechanism is a deliberate-looking special case one function up: `resolve_projection_harnesses`
(`update.sh:390-409`) computes, for every harness, "install if requested **or** already present" —
and explicitly excludes claude from that loop with `[ "$_h" = "claude" ] && continue` (`update.sh:394`).
Every non-claude harness is presence-detected; claude alone is unconditional.

This contradicts T097's own stated goal — *"a project only ever receives directories for CLIs it
actually uses"* — and, as registered, **the contradiction was undocumented**: nothing in
`memory/decisions.md` (T096 or T097), in the code comments, or in the DDRs recorded whether the
unconditional call was a deliberate safety net inherited from T096's upgrade-path fix or an
oversight. That gap was the real defect, and it is now closed by the decision below.

### Decision (locked, 2026-09-01 — Supervisor + user)

> **Presence-detect claude like every other harness.** Install the canon symlinks when claude was
> requested on this run **OR** `.claude/skills` / `.claude/agents` already exist in the target.
>
> **Why this and not the alternatives.** The safety net T096 added exists to *repair* an existing
> Claude install whose link went missing, went stale, or was replaced by a real directory —
> presence detection preserves that case exactly, because a Claude install that needs repairing has
> the directories present by definition. What it drops is the only case the net was never aimed at:
> manufacturing Claude directories in a project that never had them. Two alternatives were
> considered and rejected: keeping it unconditional and merely documenting it (leaves a Codex-only
> project carrying two directories it never asked for, and T097's goal would have to be weakened to
> match), and honouring the recorded lockfile selection strictly with no presence detection
> (semantically cleanest, but genuinely drops T096's repair path — an existing Claude install with a
> broken link would silently stop being fixed).

**Restated intent**:
> Make `update.sh` agree with `setup.sh` about which harnesses a project uses, by removing claude's
> special case rather than by adding a second rule for it — so the canon symlinks are installed for
> the same reason every other harness's files are, and a Codex-only project stays Codex-only across
> any number of updates. Separately, make a mid-install abort say that it aborted.

### Requirement Fidelity Gate (sign off BEFORE implementation)

Confirm in `tasks/TASK_REVIEW_T098.md` before writing code:

- [ ] I have read the T096 and T097 entries in `memory/decisions.md` and can state what the canon
      symlinks are for and why they must be **relative**.
- [ ] I understand the locked decision is presence-detection, and that I am **removing** claude's
      special case, not adding a parallel rule beside it.
- [ ] I have confirmed the current behaviour myself on a clean install (the BEFORE capture) rather
      than taking this guide's description of it on trust.

---

## Dependencies & Reachability

**Depends on**: T096 (canon at plain root, reached by relative symlinks), T097 (per-harness
projection, `--harness` flag). Both merged.

**Blocks**: nothing.

**Entry point**: `bash update.sh` — the installer's own CLI. Reached by an operator running an
update in an existing installed project.

---

## Acceptance Criteria

**Item 1 — presence-detected canon symlinks**

- **AC1** — After `setup.sh --harness codex` followed by `bash update.sh` with no flags,
  `.claude/skills` and `.claude/agents` do **not** exist. This is the reported defect and must go
  red before the fix.
- **AC2** — After a Claude install (`setup.sh` with claude selected) followed by `bash update.sh`,
  both symlinks exist, are **symlinks**, and have **relative** targets (`../skills`, `../agents`).
  T096's correctness requirement is unchanged by this task.
- **AC3** — Repair path preserved: given an install where `.claude/skills` exists but is a **stale
  real directory** (or a broken/absolute link), `bash update.sh` restores it to a correct relative
  symlink. This is the case the unconditional call existed for, and it must still work.
- **AC4** — `update.sh --harness claude` installs the symlinks even in a project that did not
  previously have them — an explicit request is honoured regardless of presence.
- **AC5** — The special case is **removed**, not shadowed: `[ "$_h" = "claude" ] && continue` no
  longer appears in `resolve_projection_harnesses`, and claude is resolved by the same loop as every
  other harness.
- **AC6** — Anti-vacuity: a test that reverts the fix in place and asserts AC1 goes red again.

**Item 2 — a mid-install abort must say so**

- **AC7** — `HARNESS_SKILL_BODY_CAP=abc bash update.sh` (or `setup.sh`) exits non-zero **and** emits
  a message stating that the install/update was aborted and the target tree may be partial. Today
  `harness_skill_body_cap` correctly rejects the value and `harness_project_manifest` returns 2
  (`lib/harness-fetch.sh:189-207`, `246-248`), but the caller aborts under `set -e` mid-projection
  with nothing said about the partial tree — the operator sees a cap complaint and a dead shell.
- **AC8** — The existing rejection behaviour is unchanged: a non-integer or empty override is still
  rejected by name, and `HARNESS_SKILL_BODY_CAP=0` still disables the check (it is the anti-vacuity
  lever for T097's AC5 and must keep working).

---

## Evaluation & Acceptance

### Success Criteria (observable, pass/fail)

A Codex-only project survives an arbitrary number of no-flag updates without acquiring
`.claude/skills` or `.claude/agents`; a Claude project keeps getting its links installed **and
repaired**; and an operator who trips the cap validation is told the tree is partial instead of
inferring it.

### Verification Command (exact, runnable)

```sh
bash scripts/smoke-install.sh && \
python3 -m pytest .claude/hooks/tests/ -q && \
python3 -m pytest tests/ -q
```

Plus the manual end-to-end that AC1 names, driven at the real entry point in a throwaway directory:
`setup.sh --harness codex` → assert absent → `bash update.sh` → assert still absent.

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** See `tasks/TASK_REVIEW_T098.md`.

---

## Demonstration

> See `tasks/TASK_REVIEW_T098.md`.

---

## Approach

**Vital slice**: Item 1. It is the reported defect, it is the one that contradicts a shipped goal,
and it is three lines of shell. Item 2 is a message, included because it came from the same verify
pass and costs minutes.

**Cut list** (deliberately not built):
- No rework of `resolve_projection_harnesses`' shape or of the lockfile format.
- No new `--no-claude` style flag. Presence detection plus the existing `--harness` is sufficient.
- No change to what the canon symlinks point at, or to `harness_install_canon_symlinks` itself.
- No attempt to *remove* `.claude/{skills,agents}` from a project that has them but no longer wants
  claude. Uninstall is a different task; this one only stops manufacturing them.

**Note the shape of the fix.** Claude differs from other harnesses in one real way: its destinations
are symlinks installed by `harness_install_canon_symlinks`, not MANIFEST-projected file copies, so
it cannot simply join the `PROJECTION_HARNESSES` loop. The presence test is therefore on the two
symlink destinations rather than on MANIFEST dests — but the *rule* ("requested or already present")
must be the same one, and shared with the other harnesses rather than re-expressed.

---

## Edge Case Checklist

- `.claude/` exists but `skills`/`agents` do not (a project using Claude hooks only).
- Exactly one of the two links present — repair must handle the asymmetric case.
- `.claude/skills` present as a real directory, a broken symlink, and an absolute symlink.
- A project with no `.claude/` at all.
- `update.sh --harness claude,codex` — both selected explicitly.
- Update run in a `git worktree` (relative targets are load-bearing here — T096).

---

## Files to Change (Predicted)

- `update.sh` — remove the claude special case in `resolve_projection_harnesses`; gate the
  `harness_install_canon_symlinks .` call at line 461.
- `lib/harness-fetch.sh` and/or the setup/update call sites — the partial-tree abort message (AC7).
- `tests/` and/or `scripts/smoke-install.sh` — new coverage for AC1–AC8.

## Files Must NOT Touch

- `skills/`, `agents/`, `.claude/skills`, `.claude/agents` — the canon and its links are the
  *subject* of this task, not its material.
- `.claude/hooks/` — unrelated subsystem.
- Any `tasks/TASK_GUIDE_T0*.md` other than this task's own review file.

## Test Plan

Shell-level tests driving `update.sh` against throwaway target directories, in the style already
used by `scripts/smoke-install.sh`. Every AC above gets at least one assertion; AC6 gets the
revert-in-place anti-vacuity probe. No mocking of the installer — drive the real script.

## Completion Checklist

- [ ] Requirement Fidelity Gate signed off in `tasks/TASK_REVIEW_T098.md`
- [ ] BEFORE captured before the first implementation commit
- [ ] AC1–AC8 each covered by a passing automated assertion
- [ ] Verification Command run, output pasted into the Evidence table
- [ ] AFTER + DELTA + WITNESS filled
- [ ] UI Evidence rows marked ☐ N/A (pure-infrastructure task, no UI surface)

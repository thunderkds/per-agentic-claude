# TASK_GUIDE — T108: Comma-separated pack choices are silently discarded at install
**Date**: 2026-09-07
**Complexity Level**: C1
**Risk Level**: Low
**Priority**: P1
**Assigned agent**: Common-Infrastructure-Agent
**Agent guide**: `agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

Before writing any code:
1. Read `PROJECT_SPEC.md`
2. Read `memory/MEMORY.md`
3. Read this file completely
4. Read `agents/common-infrastructure.md`
5. Note the **Complexity Level** above and apply the matching process from the Complexity matrix in your role guide
6. C1 single-file task — `memory/codebase-map.md` is optional here

---

## Requirement (Pillar 1 — Adapt the requirement)

Observed by the user on 2026-09-07 during a real install of the kit into
`/home/hungnguyenhuu/workspace/pets/hungnguyen111/kitchd`. At the interactive pack prompt the user
typed `1, 5, 3` — a natural reading of "Enter numbers separated by spaces" for anyone who has ever
typed a list. `setup.sh` printed:

```
[warn]  Unknown pack choice '1,' — skipping.
[warn]  Unknown pack choice '5,' — skipping.
[info]  Pack 'devops' installed.
```

Two of the three requested packs (`mobile`, `api`) were never installed. The install then reported
`[info]  Setup complete.` and exited 0. The user only discovered the loss by reading the warnings
back afterwards; a second run with `1 5 3` installed all three.

**Root cause** (verified, `setup.sh:198`): `for choice in $pack_choices` word-splits on `$IFS`
(whitespace) only, so `1, 5, 3` yields the tokens `1,` `5,` `3`. The first two miss every branch of
the `case` and fall to the `*)` reject arm. The single un-comma'd token survives, which is what
makes this so quiet — a partial success looks like a success.

**Restated intent**:
> A comma between pack numbers must not cost the user a pack. `1, 5, 3`, `1,5,3` and `1 5 3` must
> all select the same three packs, and a genuinely invalid entry must still warn.

**Out of scope** (what this task explicitly does NOT do):
- The `--pack=<name>` flag parser at `setup.sh:101` — it takes one name per flag and is not affected.
- Any change to which packs exist, or to `install_pack`.
- Making a bad pack choice fatal. An unknown choice stays a warning + continue, as today.
- The four Codex over-cap skills seen in the same install output — unrelated, tracked separately.

**Requirement Refs**: none — this is a defect against existing installer behavior, not new scope.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [x] Restated intent confirmed to match the user's request (Supervisor, from the pasted install log)
- [x] Domain terms align with `PROJECT_SPEC.md` ("pack", "harness", "canon" used as defined)
- [x] Every Acceptance Criterion below traces to a line in the Requirement
- [x] No `PRD.md` refs claimed, so none to verify

---

## Dependencies & Reachability

**Depends on**: `None`

**Entry point**: `prompt_packs` — the shell function in `setup.sh` that reads and parses the choice line.

---

## Acceptance Criteria

| # | Criterion (testable) | Traces to requirement |
|---|----------------------|-----------------------|
| 1 | `1, 5, 3` selects exactly `mobile api devops` — no warning emitted | the user's exact input, which lost two packs |
| 2 | `1,5,3` (no spaces) selects exactly `mobile api devops` — no warning emitted | "`1,5,3` must select the same three packs" |
| 3 | `1 5 3` still selects exactly `mobile api devops` — no regression | the documented form must keep working |
| 4 | An empty line selects no packs and emits no warning | pressing Enter to skip is documented behavior |
| 5 | `1 9 3` selects `mobile devops` AND warns once naming `9` | invalid input must still be reported |
| 6 | `,` alone (or `1,,3`) produces no empty-string warning | separators must never become a phantom choice |
| 7 | Selection order follows the numeric order the packs are defined in, not input order | keeps output stable and diffable |

---

## Evaluation & Acceptance

### Success Criteria (observable, pass/fail)

| # | Given (input/state) | Expect (output/behavior) | How it's checked |
|---|---------------------|--------------------------|------------------|
| 1 | choice line `1, 5, 3` | resolves to `mobile api devops`, zero warnings | automated test |
| 2 | choice line `1,5,3` | resolves to `mobile api devops`, zero warnings | automated test |
| 3 | choice line `1 5 3` | resolves to `mobile api devops`, zero warnings | automated test |
| 4 | choice line `` (empty) | resolves to nothing, zero warnings | automated test |
| 5 | choice line `1 9 3` | resolves to `mobile devops`, exactly one warning naming `9` | automated test |
| 6 | choice line `1,,3` | resolves to `mobile devops`, zero warnings | automated test |
| 7 | sourcing setup.sh with the define-only guard set | function is defined AND `main` did NOT run (no files created) | automated test |

> Row 7 is not optional padding. `memory/learnings.md` records that an unvalidated test seam is an
> invisible off switch: if the define-only guard silently stopped working, every row above would
> pass against a stale definition. The seam must assert on itself.

### Verification Command (exact, runnable)

```bash
bash tests/test_pack_choice_parsing.sh && \
bash tests/test_setup.sh && \
shellcheck -x setup.sh
```

### Evidence (filled by reviewer at Stage 4/5)

> Filled by the reviewer at Stage 4/5 in `tasks/TASK_REVIEW_T108.md`, copied from
> `templates/TASK_REVIEW_template.md`.

---

## Demonstration

> See `tasks/TASK_REVIEW_T108.md`.

---

## Approach

**Pattern reference**: `setup.sh:98-126` — the `--harness`/`--pack=` arg loop. Imitate its
`case`-per-token shape, its `log_warn`-and-continue reject arm, and its space-prefixed accumulator
string (`PACKS="$PACKS mobile"`). Do not introduce arrays or bashisms: this file is POSIX `sh` and
is shellchecked in CI (`.github/workflows/ci.yml:19`).

**Vital slice**: normalizing the separator before the existing `case` loop. The `case` block itself
is correct and stays untouched.
**Cut list**:
- Accepting pack *names* (`mobile api`) at the numeric prompt — not requested, and `--pack=` already covers it.
- Accepting ranges (`1-3`) — speculation, no user has asked.
- Re-prompting on invalid input — changes the non-interactive contract; warn-and-continue is the existing rule.

**Recommended implementation**: translate commas to spaces once, immediately after `read -r`, and let
the existing word-splitting loop do the rest:

```sh
read -r pack_choices
# Commas are the most common way users write a list; treat them as separators,
# not as part of the choice (T108: "1, 5, 3" silently lost two of three packs).
pack_choices=$(printf '%s' "$pack_choices" | tr ',' ' ')
for choice in $pack_choices; do
```

`tr` is POSIX and already assumed present. Because the shell collapses runs of whitespace during
word splitting, `1,,3` and `1, 5, 3` both fall out correctly with no extra guard — AC6 is satisfied
by the same one line, which is why nothing more is warranted here.

**Testability seam**: `prompt_packs` early-returns unless stdin is a tty, so a test cannot drive it
without a pty. Extract the parsing into a small pure function that takes the raw line and echoes the
resolved pack list, have `prompt_packs` call it, and guard the final `main` invocation at
`setup.sh:579` so the file can be sourced for its definitions alone. Keep the guard's default
behavior identical to today: unset means run `main`, exactly as now.

---

## Edge Case Checklist

- [ ] Trailing comma (`1,3,`) does not produce an empty-string warning
- [ ] Leading/trailing whitespace on the line is harmless
- [ ] A duplicated choice (`1 1`) does not install `mobile` twice, or if it does, `install_pack` is idempotent — verify which, don't assume
- [ ] Tabs as separators still work (word splitting already covers this — confirm, don't add code)
- [ ] The define-only guard does not change behavior when unset (the real install path)
- [ ] `shellcheck -x setup.sh` stays clean — no new suppressions

---

## Files to Change (Predicted)

| File | Change |
|------|--------|
| `setup.sh` | Normalize commas to spaces in `prompt_packs`; extract parsing into a pure function; guard the bottom `main` call for sourcing |
| `tests/test_pack_choice_parsing.sh` | New — drives the pure function across all 7 Success Criteria rows |

## Files Must NOT Touch

| File | Reason |
|------|--------|
| `packs/**` | Pack contents are unrelated to how a choice is parsed |
| `tests/test_pack_docs_flags.py` | Guards the `--pack=` flag/doc contract, a different parser (out of scope above) |
| `update.sh` | Does not prompt for packs |
| `MANIFEST`, `.claude/harness-lock.json` | No installed-file surface changes |

---

## Test Plan

New `tests/test_pack_choice_parsing.sh`, following the existing shell-test conventions in
`tests/test_setup.sh`: `set -u`, `PASS`/`FAIL` counters, `pass()`/`fail()` helpers, non-zero exit if
any assertion fails, self-contained with a `mktemp -d` workspace trapped for cleanup.

It sources `setup.sh` with the define-only guard set, then asserts one case per Success Criteria row
(1–6) on the pure function's output, plus row 7 asserting the seam itself: the function is defined
*and* `main` did not run (assert no `.claude/` was scaffolded in the scratch cwd).

Regression: `tests/test_setup.sh` must still pass unchanged — it exercises the real install path
with stdin redirected from `/dev/null`, which proves the sourcing guard did not disturb normal
execution.

---

## Completion Checklist

- [ ] Implementation done
- [ ] Self-review: `Skill({ skill: "code-review" })` run
- [ ] Security review — N/A (Low risk, no new input trust boundary: the parsed value never reaches a shell command, only a `case` whitelist)
- [ ] `shellcheck -x setup.sh` passes
- [ ] Tests written AND pass — output pasted into `tasks/TASK_REVIEW_T108.md` (Hard-Stop Gate 5)
- [ ] `Skill({ skill: "verify" })` run — user-invoked; the Supervisor cannot run this gate
- [ ] `memory/MEMORY.md` updated (if new patterns learned)
- [ ] Supervisor notified: task ready for Stage 4 review

# TASK_REVIEW — T099: Quoted spans are sometimes data and sometimes code

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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_quoted_spans_t099.py` — 34 new assertions, all written as part of T099. **Round 2** added the three that pin the *direction* rather than the enumerated shapes — `test_an_unrecognised_wrapper_resolves_toward_code` (12 unlisted wrappers incl. `eval`, `su … -c`, `perl -e`), `test_a_command_nobody_has_ever_heard_of_still_keeps_its_span` (invented names, so no list can cover them), and `test_only_the_enumerated_data_commands_can_ever_strip_a_span` (the inverse, asserted against `DATA_COMMAND_PATTERN` itself). Their absence is what let round 1's fail-open ship. Two round-1 tests were adjusted for the inverted default, not weakened: `test_a_stripped_span_is_replaced_with_a_space_not_deleted` now uses `echo a"x"b` (a bare `a"x"b` is no longer data under a keep-by-default rule), and `test_the_composition_order_is_the_one_that_produces_that` gained `HEREDOC_BEHIND_A_DATA_COMMAND`, a fixture where reversing the order really does leak the push (the quoted strip eats the heredoc's own `'EOF'` tag). AC1 `test_data_spans_are_not_blocked_by_the_merge_gate` / `..._do_not_demand_a_memory_pass` / `test_the_guides_three_named_data_shapes_specifically`; AC2 `test_code_spans_are_still_blocked_by_the_merge_gate` / `..._still_demand_a_memory_pass` / `test_a_wrapper_after_a_separator_still_applies` / `test_a_wrappers_other_quoted_arguments_do_not_shield_its_command` / `test_a_wrapper_in_an_earlier_segment_does_not_leak_into_a_later_one`; AC3 `test_the_real_unquoted_push_still_blocks` / `..._merge_and_rebase_still_block` / `test_a_real_push_alongside_a_data_span_still_blocks`; AC4 `test_plain_heredoc_data_is_still_data` / `test_an_unterminated_heredoc_is_still_left_alone` / `test_the_quoted_heredoc_tag_is_not_mistaken_for_a_data_span`, plus T095's own 50 assertions run unmodified; AC5 `test_a_heredoc_body_containing_a_wrapped_push_is_still_data` / `test_the_composition_order_is_the_one_that_produces_that` / `test_a_real_wrapped_push_after_the_heredoc_terminator_still_blocks`; AC6 `test_pre_bash_still_blocks_when_the_resolver_is_unavailable` / `test_post_bash_still_falls_back_to_prompting_...` / `test_the_two_hooks_still_guard_in_opposite_directions`; AC7 `test_single_quoted_wrapper_argument_is_code` / `test_a_wrapper_nested_inside_a_span_keeps_the_span` / `test_an_unterminated_quote_leaves_the_rest_alone` / `test_mixed_quote_types_do_not_terminate_each_other` / `test_bash_dash_c_with_an_unquoted_command_is_unaffected`; AC8 `test_ac1_goes_red_when_the_fix_is_reverted` / `test_ac2_goes_red_under_the_naive_quoted_span_strip` / `test_the_naive_strip_would_also_disarm_the_memory_hook`. `python3 -m pytest .claude/hooks/tests/test_quoted_spans_t099.py -q` → `34 passed in 0.72s`. **Round 3** added the four that pin the *position* invariant, the axis nothing in the suite could see: `test_a_data_word_that_is_not_the_command_never_strips_a_span` (Stage 4's six measured shapes plus three assignment shapes, against the invented host `zorblax-gw.invalid` so no future list can cover it by accident), `test_a_genuine_path_to_a_data_command_is_still_data` (the over-rejection side — `/usr/bin/echo`, `./echo`, `LC_ALL=C grep` are still AC1 data), and two anti-vacuity probes, `test_the_position_invariant_goes_red_when_the_anchor_is_reverted` (restores the pre-`9dd3035` pattern *and* its `.search` semantics via a shim and asserts the pushes leak again) and `test_the_leading_path_clause_cannot_swallow_an_assignment`. Measured: reverting `.match(`→`.search(` at the call site turns **3 of these red**; reverting the path clause to `\S*/` alone turns the **same 3** red. Before round 3 both reverts left the suite fully green. `python3 -m pytest .claude/hooks/tests/test_quoted_spans_t099.py -q` → `38 passed in 1.06s`. |
| Verification command run | ☑ pass | `python3 -m pytest .claude/hooks/tests/ -q` → **`5 failed, 790 passed in 10.97s`** (round 3; round 2 was `5 failed, 786 passed`); `python3 -m pytest tests/ -q` → **`1 failed, 39 passed`**. <br><br>**All 6 failures are pre-existing and untouched by this task** — measured, not assumed. Five are one condition: `memory/MEMORY.md` is 45,303 characters against a 45,000 ratchet, and `git show ced5ddd:memory/MEMORY.md \| wc -c` gives the same 45,303 at the branch point, before T099 changed anything. The sixth is `test_readme_slim.py` — `git show ced5ddd:README.md \| wc -l` gives 73 against a 60-line limit. `git diff --name-only ced5ddd HEAD` lists neither `README.md` nor `memory/MEMORY.md`. <br><br>The delta is therefore exactly this task's new tests: **752 → 790 hook tests, +38, with no pre-existing test modified (AC4)**. Note the guide's stated baseline of "757 hook tests" is stale — the suite is 788 collected, of which 752 passed at `ced5ddd`. Both pre-existing failures are outside T099's scope and are flagged to the Supervisor rather than fixed here (Surgical Changes). |
| Negative cases hold | ☑ pass | The AC2/AC3 half of the matrix is the negative case and is where the task's difficulty lives. Every real push still blocks: unquoted (`AC3`), double-quoted to `bash -c`, single-quoted to `sh -c`, through `ssh`, `zsh -c`, `bash -lc`, `docker exec`, `docker run … sh -c`, `env … sh -c`, after a `;` / `&&` / `\|` / `$(` separator, and alongside a wrapper's unrelated quoted option (`ssh -o "StrictHostKeyChecking=no" box "…"`). Every uncertain shape resolves toward blocking: unterminated quote, single-quoted wrapper argument, wrapper nested inside a span. Round 2 closed the hole that Stage 5 found here: `eval "<push>"`, `su user -c "<push>"` and `perl -e "system('<push>')"` were **allowed** by round 1, because its `WRAPPER_PATTERN` was an allowlist of spans to *keep* and an unlisted wrapper fell through to the strip. All three block now, and so does any wrapper nobody has enumerated, because the default is keep. AC8's second probe proves the stripping is load-bearing — substituting the naive `QUOTED_SPAN_PATTERN` strip makes three of those real pushes pass the gate, and the test asserts that they do. Round 3 closed a **third** instance of the same shape, one level down again: `DATA_COMMAND_PATTERN` was applied with `.search()` against the segment prefix, so a data *word* anywhere in the prefix counted rather than the segment's actual command — `ssh echo.example.com "<push>"` was enough, a hostname alone disarming the gate. Anchored in `9dd3035`; round 3's independent review then found the anchor's own `(?:\S*/)?` clause could backtrack over the assignment clause and eat a `VAR=` as a directory, so `X=/bin/echo sh -c "<push>"` still allowed a real push. Narrowed to `(?:[\w.\-/]*/)?`. All nine shapes block now, and all four are pinned by tests that go red on revert. |
| verify | ☑ pass | **Supervisor-run `/verify`, three rounds; round 3 (`ced5ddd..a58b850`, 8 commits) is the pass.** Driven at the hooks' real surface — event JSON on stdin, `CLAUDE_PROJECT_DIR` set, board armed with a task In Progress — against two isolated roots, pre-fix at `ced5ddd` and final. Not an import-and-call. <br><br>**Round 1 (`cdd9e6b`) FAILED**: `WRAPPER_PATTERN` was an allowlist of spans to *keep*, so an unlisted wrapper stripped the span — `eval`, `su user -c`, `perl -e "system(…)"` each went BLOCK -> allow. **Round 2 (`2b35cfa`) inverted the default** to keep-unless-a-data-command-precedes; that verified clean, but **Stage 4 then found the same shape one level down** — `DATA_COMMAND_PATTERN` used `.search()` on the segment prefix, so a data *word* anywhere in it counted and `ssh echo.example.com "<push>"` allowed a real push on a hostname alone. The Supervisor fixed that in `9dd3035`, **and that fix was itself unsound**: its `(?:\\S*/)?` clause backtracked over the assignment guard, so `X=/bin/echo sh -c "<push>"` allowed a real push. Caught by the implementing agent on independent review and fixed in `a58b850`. <br><br>**Round 3 PASS.** The motivating case `grep -r "<push>" .claude/` is allowed (exit 0, empty stdout) and `bash -c "<push> origin main"` blocks with the gate's own `{"decision": "block"}`. All eight historical fail-opens hold closed, including the two introduced during this task. An **invented** wrapper (`zorblax --run`) blocks — the load-bearing evidence that the default closes by construction, not by list coverage. Ten evasion shapes hold (backticks, `$(…)`, escaped quotes, empty spans, tab separation, data command then real push). All four git verbs checked: push/merge/rebase allow-as-data and block-as-code. Path spellings that could over-reject (`~/bin/echo`, `$HOME/bin/echo`, `$(which echo)`, `\\echo`) all block — over-blocking, the documented safe side. Both hooks move together. <br><br>**Two things recorded rather than rounded up.** (1) Accepted residual: `python3 -c "import os as o; f=o.system; f('<push>')"` -> allow; aliasing evades `SPAN_EXECUTOR_PATTERN`'s literal spellings, and closing it means an AC1 change or a Python parser. (2) Pre-existing, outside scope: `git pull` is absent from `BLOCKED_PATTERNS` while `post_bash` treats it as memory-relevant — the two hooks disagree about whether a pull is a merge. Identical at `ced5ddd`. — **pass** |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | **Reviewed**: the three changed files — `.claude/hooks/lib/shell_data.py` (new `strip_quoted_spans` + `WRAPPER_PATTERN` + `SEGMENT_BOUNDARY_PATTERN`, and the stale docstring line), and the single matcher call site in each of `pre_bash_block_unsafe_merge.py:main()` and `post_bash_memory_update.py:main()`, plus both guarded imports. `shell_data` has exactly two importers (`grep -rl shell_data .claude/`), both of them those hooks, so the affected set is closed. <br>**Skipped, deliberately**: `invokes_test_runner` and `QUOTED_SPAN_PATTERN`'s existing use in the evidence matcher (on the Files-Must-NOT-Touch list — its unconditional strip is correct for its opposite failure direction), and the rest of the repo, which cannot reach this module. `git diff --name-only ced5ddd HEAD` confirms no file outside that set was touched; `update.sh`, `setup.sh` and `lib/harness-fetch.sh` (T098) are untouched. |
| Full smoke suite still green (no regression) | ☑ pass | `python3 -m pytest tests/ -q` → `1 failed, 39 passed`, the one failure being the pre-existing 73-line `README.md` documented above. No test that passed at `ced5ddd` fails now; the hook suite gained 31 and lost none. T095's two files — `test_merge_gate_t095.py` and `test_memory_hook_heredoc_data.py` — were run unmodified alongside the new file: `81 passed in 0.79s`. |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | Pure-infrastructure task: two Python hooks and a shared library. No UI surface exists in this repo. |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | As above — no rendered surface, no tokens. |
| **UI: Responsiveness at target viewports** | ☑ N/A | As above — no viewport. |

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE**: captured at the commit below, before any T099 implementation commit existed. Both
hooks driven at their real entry points (`pre_bash.main()` over a constructed board with one task
In Progress; `post_bash` as a subprocess, as the harness runs it). Probe:
`/tmp/.../scratchpad/probe.py`, reproduced verbatim in
`.claude/hooks/tests/test_quoted_spans_t099.py`'s fixtures.

```
T099 hook matrix — 2026-09-02T03:31:18+00:00
git HEAD: ced5ddd
condition: one task In Progress on a constructed board

AC           command                                         pre_bash  post_bash
----------------------------------------------------------------------------------
AC1 data     echo "remember to git push the branch"          BLOCKS    FIRES
AC1 data     grep -r "git push" .claude/                     BLOCKS    FIRES
AC1 data     python3 -c "print('git push')"                  BLOCKS    FIRES
AC2 code     bash -c "git push origin main"                  BLOCKS    FIRES
AC2 code     sh -c 'git merge --no-ff feature'               BLOCKS    FIRES
AC2 code     ssh box "cd /r && git push"                     BLOCKS    FIRES
AC3 ctrl     git push origin main                            BLOCKS    FIRES
AC4 hdoc     cat > notes.md <<'EOF'\nThe Supervisor must...  allows    silent
AC5 both     cat > n.md <<'EOF'\nRun bash -c "git push" ...  allows    silent
AC7 nest     bash -c 'git push'                              BLOCKS    FIRES
AC7 unterm   bash -c "git push                               BLOCKS    FIRES
```

Every data span in AC1 is refused, which is the live obstruction. The AC2 code spans block too —
correctly, and that is what a naive quoted-span strip would destroy. Measured separately, with the
same three rows the guide predicts:

```
echo "... git push ..."            today=BLOCK  naive-strip=ALLOW
bash -c "git push origin main"     today=BLOCK  naive-strip=ALLOW
ssh box "cd /r && git push"        today=BLOCK  naive-strip=ALLOW
```

**AFTER (round 1, `af737d9`)**: the AC1–AC7 matrix flipped exactly as intended —
the three AC1 data rows went `BLOCKS`→`allows` / `FIRES`→`silent`, and every AC2
code row, the AC3 control, and the AC7 nesting and unterminated-quote rows held
their BEFORE values.

**Stage 5 `verify` FAILED that round anyway**, on a shape the matrix did not
contain. `WRAPPER_PATTERN` was an allowlist of spans to **keep**, so a wrapper
*missing* from it had its span stripped and the push inside became invisible to
the gate — under-blocking, not the over-blocking the module's own comment
claimed. Measured at the real hook surface against a pre-fix root:

```
eval "<push> origin main"        BEFORE=BLOCK  round-1=allow
su user -c "<push>"              BEFORE=BLOCK  round-1=allow
perl -e "system('<push>')"       BEFORE=BLOCK  round-1=allow
```

**AFTER (round 2)**: same probe, same fixture board, at the commit below.

```
T099 round-2 probe — 2026-09-02T04:28:47+00:00
condition: one task In Progress on a constructed board

shape                  pre_bash
eval                   BLOCK
su -c                  BLOCK
perl -e                BLOCK
--- adjacent (must hold) ---
sudo sh -c             BLOCK
fish -c                BLOCK
timeout bash -c        BLOCK
xargs sh -c            BLOCK
bash -c $(echo)        BLOCK
backtick               BLOCK
nested quotes          BLOCK
earlier-seg no leak    allow
```

All three regressions are closed; all eight adjacent shapes that round 1 got
right hold their values, including the last one, where a wrapper in an earlier
segment correctly does **not** leak into the later data span. The AC1–AC7 matrix
above is unchanged — the 34 assertions in `test_quoted_spans_t099.py` cover it,
`34 passed`.

**AFTER (round 3)**: Stage 4 `code-review` found a third instance of the
same shape and the Supervisor fixed it directly in `9dd3035`; the
Common-Infrastructure-Agent then reviewed that commit independently, because it
is Supervisor-authored implementation code in a security gate (Hard-Stop Gate 1)
and it shipped with no test. Both findings are measured at the classifier:

```
T099 round-3 probe — 2026-09-02

shape                                        pre-9dd3035  9dd3035  round-3
ssh echo.example.com "<push>"                allow        BLOCK    BLOCK
ssh ag.example.com "<push>"                  allow        BLOCK    BLOCK
ssh -o "LogLevel=echo" box "<push>"          allow        BLOCK    BLOCK
ssh --tag=echo box "<push>"                  allow        BLOCK    BLOCK
ssh box "echo hi" "<push>"                   allow        BLOCK    BLOCK
docker exec --env=echo c "<push>"            allow        BLOCK    BLOCK
X=/bin/echo sh -c "<push>"                   allow        allow    BLOCK   <- found in round 3
PAGER=/bin/echo bash -c "<push>"             allow        allow    BLOCK   <- found in round 3
A=x/echo ssh box "<push>"                    allow        allow    BLOCK   <- found in round 3
--- AC1 must not regress (over-rejection side) ---
echo / grep -r / python3 -c / rg / printf    allow        allow    allow
/usr/bin/echo "<push>" , ./echo , ../echo    allow        allow    allow
LC_ALL=C grep -r "<push>" .claude/           allow        allow    allow
```

**Verdict on `9dd3035`: right diagnosis, right direction, incomplete
anchoring.** Its six measured shapes are genuinely closed and its AC1 cases
genuinely still pass, so it is a real improvement and was not reverted. But the
optional leading-path clause was written `(?:\S*/)?`, and `\S*` matches
anything without a space — including an `=`. The regex engine therefore
backtracks *over* the assignment clause it sits behind and consumes an
assignment's own `VAR=` as if it were a directory, so any first token merely
*containing* `/echo` reads as "the command is echo". `X=/bin/echo sh -c
"<push>"` — a shape that runs a real `sh -c` — was still allowed after
`9dd3035`. Narrowing the clause to `(?:[\w.\-/]*/)?` excludes `=` and the quote
characters, which keeps a path a path; `/usr/bin/echo`, `./echo` and `../echo`
still strip, and `xecho` and `/b/echofoo` still do not.

The second finding is that **nothing in the 786-test suite could tell whether
`9dd3035` was present at all** — reverting `.match()` to `.search()` left the
suite fully green. Round 2's three direction tests pin *which names* may strip a
span; they say nothing about *where* the name has to be, and position is the
axis all three fail-opens have now travelled on. Four tests close it, and the
revert is measured rather than argued: `.match(`→`.search(` turns 3 red, and
reverting the path clause alone turns the same 3 red.

**DELTA**: the enumeration was **inverted**. `WRAPPER_PATTERN` (a list of spans
to keep, default strip) is replaced by `DATA_COMMAND_PATTERN` (a list of commands
after which a span is data, default keep), plus `SPAN_EXECUTOR_PATTERN`, which
drags a span back to code when its own text reaches out to a shell — the clause
that keeps `python -c` on the data list honest. An operator can still `grep`,
`echo`, `rg` and `python3 -c` the words this gate guards while a task is In
Progress; every real push still blocks, and now that includes every wrapper
nobody has thought of, because being unlisted is what decides it. The module
docstring and the pattern comment previously asserted the opposite of what the
code did — "a wrapper missing from this list over-blocks — the recoverable
direction" — and that contradiction is how the gap survived review; both now
state the real direction and record the correction rather than hiding it.

Round 3 completes that correction on the second axis: inverting the enumeration
fixed *which* names strip a span, and anchoring fixes *where* the name must
appear for the enumeration to mean anything. An unanchored list is not an
allowlist — it is a substring search over the whole prefix, which is how the
same fail-open shape reappeared twice at successively lower levels.

**WITNESS**: implemented and run by the Common-Infrastructure-Agent on
2026-09-02 (BEFORE 03:31Z at `ced5ddd`, round-1 AFTER 03:37Z at `af737d9`,
round-2 AFTER 04:28Z after a failed Stage 5 `verify`; round-3 review
and fix on 2026-09-02 against `9dd3035`), under
`memory/event-trace/T099.jsonl` — the active-task state file was written before
the first test command, so the run is attributable rather than landing in
`_untagged.jsonl`. **Not yet independently witnessed**: Stage 5 `verify` is
user-invoked only, so the second pair of eyes on the row above is still
outstanding and this task is not Done until it is filled. Round 1 was marked
ready with that row blank and failed the gate; this round makes no claim about
it either.

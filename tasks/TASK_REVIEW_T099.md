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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `.claude/hooks/tests/test_quoted_spans_t099.py` — 31 new assertions, all written as part of T099. AC1 `test_data_spans_are_not_blocked_by_the_merge_gate` / `..._do_not_demand_a_memory_pass` / `test_the_guides_three_named_data_shapes_specifically`; AC2 `test_code_spans_are_still_blocked_by_the_merge_gate` / `..._still_demand_a_memory_pass` / `test_a_wrapper_after_a_separator_still_applies` / `test_a_wrappers_other_quoted_arguments_do_not_shield_its_command` / `test_a_wrapper_in_an_earlier_segment_does_not_leak_into_a_later_one`; AC3 `test_the_real_unquoted_push_still_blocks` / `..._merge_and_rebase_still_block` / `test_a_real_push_alongside_a_data_span_still_blocks`; AC4 `test_plain_heredoc_data_is_still_data` / `test_an_unterminated_heredoc_is_still_left_alone` / `test_the_quoted_heredoc_tag_is_not_mistaken_for_a_data_span`, plus T095's own 50 assertions run unmodified; AC5 `test_a_heredoc_body_containing_a_wrapped_push_is_still_data` / `test_the_composition_order_is_the_one_that_produces_that` / `test_a_real_wrapped_push_after_the_heredoc_terminator_still_blocks`; AC6 `test_pre_bash_still_blocks_when_the_resolver_is_unavailable` / `test_post_bash_still_falls_back_to_prompting_...` / `test_the_two_hooks_still_guard_in_opposite_directions`; AC7 `test_single_quoted_wrapper_argument_is_code` / `test_a_wrapper_nested_inside_a_span_keeps_the_span` / `test_an_unterminated_quote_leaves_the_rest_alone` / `test_mixed_quote_types_do_not_terminate_each_other` / `test_bash_dash_c_with_an_unquoted_command_is_unaffected`; AC8 `test_ac1_goes_red_when_the_fix_is_reverted` / `test_ac2_goes_red_under_the_naive_quoted_span_strip` / `test_the_naive_strip_would_also_disarm_the_memory_hook`. `python3 -m pytest .claude/hooks/tests/test_quoted_spans_t099.py -q` → `31 passed in 0.52s`. |
| Verification command run | ☑ pass | `python3 -m pytest .claude/hooks/tests/ -q` → **`5 failed, 783 passed in 9.64s`**; `python3 -m pytest tests/ -q` → **`1 failed, 39 passed`**. <br><br>**All 6 failures are pre-existing and untouched by this task** — measured, not assumed. Five are one condition: `memory/MEMORY.md` is 45,303 characters against a 45,000 ratchet, and `git show ced5ddd:memory/MEMORY.md \| wc -c` gives the same 45,303 at the branch point, before T099 changed anything. The sixth is `test_readme_slim.py` — `git show ced5ddd:README.md \| wc -l` gives 73 against a 60-line limit. `git diff --name-only ced5ddd HEAD` lists neither `README.md` nor `memory/MEMORY.md`. <br><br>The delta is therefore exactly this task's new tests: **752 → 783 hook tests, +31, with no pre-existing test modified (AC4)**. Note the guide's stated baseline of "757 hook tests" is stale — the suite is 788 collected, of which 752 passed at `ced5ddd`. Both pre-existing failures are outside T099's scope and are flagged to the Supervisor rather than fixed here (Surgical Changes). |
| Negative cases hold | ☑ pass | The AC2/AC3 half of the matrix is the negative case and is where the task's difficulty lives. Every real push still blocks: unquoted (`AC3`), double-quoted to `bash -c`, single-quoted to `sh -c`, through `ssh`, `zsh -c`, `bash -lc`, `docker exec`, `docker run … sh -c`, `env … sh -c`, after a `;` / `&&` / `\|` / `$(` separator, and alongside a wrapper's unrelated quoted option (`ssh -o "StrictHostKeyChecking=no" box "…"`). Every uncertain shape resolves toward blocking: unterminated quote, single-quoted wrapper argument, wrapper nested inside a span. AC8's second probe proves this is load-bearing — substituting the naive `QUOTED_SPAN_PATTERN` strip makes three of those real pushes pass the gate, and the test asserts that they do. |
| verify | ☐ pass / ☐ fail / ☐ N/A | [what was observed — must literally state "pass" or "fail" here too, e.g. "skill run, feature confirmed working — pass": the merge gate scans this Notes column for the word "pass", not just the Result column] |
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

**AFTER**: the same probe, same fixture, same board, at `af737d9`:

```
T099 hook matrix — 2026-09-02T03:37:03+00:00
git HEAD: af737d9
condition: one task In Progress on a constructed board

AC           command                                         pre_bash  post_bash
----------------------------------------------------------------------------------
AC1 data     echo "remember to git push the branch"          allows    silent
AC1 data     grep -r "git push" .claude/                     allows    silent
AC1 data     python3 -c "print('git push')"                  allows    silent
AC2 code     bash -c "git push origin main"                  BLOCKS    FIRES
AC2 code     sh -c 'git merge --no-ff feature'               BLOCKS    FIRES
AC2 code     ssh box "cd /r && git push"                     BLOCKS    FIRES
AC3 ctrl     git push origin main                            BLOCKS    FIRES
AC4 hdoc     cat > notes.md <<'EOF'\nThe Supervisor must...  allows    silent
AC5 both     cat > n.md <<'EOF'\nRun bash -c "git push" ...  allows    silent
AC7 nest     bash -c 'git push'                              BLOCKS    FIRES
AC7 unterm   bash -c "git push                               BLOCKS    FIRES
```

Read the two blocks together, row by row: the three AC1 rows flipped
`BLOCKS`→`allows` and `FIRES`→`silent`, and **nothing else moved**. The AC2 code
rows, the AC3 control, and the AC7 nesting and unterminated-quote rows all hold
their BEFORE values — which is the point, because the naive fix flips those too.

**DELTA**: an operator can now `grep`, `echo` and `python3 -c` the words this gate
guards while a task is In Progress — the ordinary act of reading and documenting
the gate, which the gate itself was refusing — while every real push still
blocks, including the `bash -c` and `ssh` wrapped forms that an unconditional
quoted-span strip would have waved through.

**WITNESS**: implemented and run by the Common-Infrastructure-Agent on
2026-09-02 (BEFORE 03:31Z at `ced5ddd`, AFTER 03:37Z at `af737d9`), under
`memory/event-trace/T099.jsonl` — the active-task state file was written before
the first test command, so the run is attributable rather than landing in
`_untagged.jsonl`. **Not yet independently witnessed**: Stage 5 `verify` is
user-invoked only, so the second pair of eyes on the row above is still
outstanding and this task is not Done until it is filled.

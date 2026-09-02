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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☐ pass / ☐ fail | [test file path(s) — required before Done] |
| Verification command run | ☐ pass / ☐ fail | [paste actual output] |
| Negative cases hold | ☐ pass / ☐ fail | |
| verify | ☐ pass / ☐ fail / ☐ N/A | [what was observed — must literally state "pass" or "fail" here too, e.g. "skill run, feature confirmed working — pass": the merge gate scans this Notes column for the word "pass", not just the Result column] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☐ pass / ☐ fail | [what was reviewed vs. skipped, and why] |
| Full smoke suite still green (no regression) | ☐ pass / ☐ fail | |
| **UI: Visual regression (diff or verdict pasted)** | ☐ pass / ☐ fail / ☐ N/A | [screenshot path or LLM verdict — required for UI tasks, Hard-Stop Gate 6] |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☐ pass / ☐ fail / ☐ N/A | [method used + output] |
| **UI: Responsiveness at target viewports** | ☐ pass / ☐ fail / ☐ N/A | [viewports tested, any overflow findings] |

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

**AFTER**: [same command, post-change] OR [verbatim excerpt of the new content]

**DELTA**: [one sentence — what a user can now do that they could not before]

**WITNESS**: [who ran it and when — derived from `memory/event-trace/Txxx.jsonl`, never the
implementing agent alone]

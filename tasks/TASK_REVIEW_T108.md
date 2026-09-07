# TASK_REVIEW — T108: Comma-separated pack choices are silently discarded

> Sibling of `tasks/TASK_GUIDE_T108.md`. Everything here is **filled by the reviewer at Stage
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
| **New test(s) cover Acceptance Criteria (file paths pasted)** | ☑ pass | `tests/test_pack_choice_parsing.sh` — 14 assertions covering Success Criteria rows 1–7 plus the guide's Edge Case Checklist. Output below. |
| Verification command run | ☑ pass | `bash tests/test_pack_choice_parsing.sh && bash tests/test_setup.sh && shellcheck -x setup.sh` — output pasted below. |
| Negative cases hold | ☑ pass | `1 9 3` → `mobile devops` + exactly one warning naming `9` (row5); `1,,3` / `,` / trailing comma → no phantom empty-string warning (row6, edges). |
| verify | ☐ pass / ☐ fail / ☐ N/A | [user-invoked — the Supervisor/agent cannot run this gate. Left for the user to run `/verify`.] |
| Review scope bounded to the change's blast radius (affected set, not whole repo) | ☑ pass | Reviewed: `prompt_packs` + new `resolve_pack_choices` + the bottom `main` guard + `SCRIPT_DIR` override in `setup.sh`, and the new test. Not touched: the `case` arms (correct, unchanged logic — just relocated), `install_pack`, `--pack=` flag parser, `update.sh`, packs. |
| Full smoke suite still green (no regression) | ☑ pass | `tests/test_setup.sh` — 18/18 pass, unchanged. Confirms the sourcing guard does not disturb the real install path (it redirects stdin from `/dev/null`). |
| **UI: Visual regression (diff or verdict pasted)** | ☑ N/A | pure-backend task: `setup.sh` shell parsing, no UI component. UI/Design AC section deleted from the guide per Hard-Stop Gate 6. |
| **UI: Design-system compliance (tokens/colors/typography verified)** | ☑ N/A | pure-backend task: `setup.sh` shell parsing, no UI component. UI/Design AC section deleted from the guide per Hard-Stop Gate 6. |
| **UI: Responsiveness at target viewports** | ☑ N/A | pure-backend task: `setup.sh` shell parsing, no UI component. UI/Design AC section deleted from the guide per Hard-Stop Gate 6. |

---

## Verification Command — pasted output

`shellcheck` is not on the local box; it was run via `koalaman/shellcheck:stable` in Docker
(same binary CI uses). Exit 0, no findings.

```
$ bash tests/test_pack_choice_parsing.sh
PASS: row1: '1, 5, 3' -> mobile api devops, no warning
PASS: row2: '1,5,3' -> mobile api devops, no warning
PASS: row3: '1 5 3' -> mobile api devops, no warning (no regression)
PASS: row4: '' (empty) -> nothing, no warning
PASS: row5: '1 9 3' -> mobile devops, exactly one warning naming 9
PASS: row6: '1,,3' -> mobile devops, no warning (separator is never a choice)
PASS: edge: trailing comma '1,3,' -> mobile devops, no empty-string warning
PASS: edge: surrounding whitespace '  1 , 3  ' is harmless
PASS: edge: tab separators still work
PASS: edge: ',' alone -> nothing, no warning
PASS: edge: duplicate choice '1 1' -> one token per input (install_pack is idempotent)
PASS: regression: empty pack selection does not abort under 'set -e'
PASS: row7a: resolve_pack_choices is defined after a define-only source
PASS: row7b: define-only source did NOT run main (no install artifacts in cwd)
PASS: row7c: without the guard, sourcing runs main (guard is the off switch)

----- summary: 15 passed, 0 failed -----

$ bash tests/test_setup.sh
... (18 PASS, 0 FAIL)
----- summary: 18 passed, 0 failed -----

$ docker run --rm -v "$PWD:/mnt" -w /mnt koalaman/shellcheck:stable -x setup.sh tests/test_pack_choice_parsing.sh
(no output — exit 0)
```

---

## Demonstration

> Anchors what this task delivered to an observable before/after pair. BEFORE has no `N/A` path:
> if the task changes executable code, BEFORE is a pasted, timestamped terminal capture taken
> **before any implementation commit exists**; if it does not (docs, templates, skill-instruction
> text), BEFORE is the **verbatim prior content** of what changed — a quoted excerpt, not a command.

**BEFORE** (captured 2026-09-07T07:34:27Z, at commit `6f409d4`, before any implementation commit —
replaying `setup.sh:198-206`'s parse loop verbatim on the user's real input `1, 5, 3`):

```
$ date -u +%Y-%m-%dT%H:%M:%SZ
2026-09-07T07:34:27Z
$ # replay of setup.sh:198-206 `for choice in $pack_choices` on pack_choices="1, 5, 3"
[warn]  Unknown pack choice '1,' — skipping.
[warn]  Unknown pack choice '5,' — skipping.
RESULT PACKS: devops
```

Only `devops` selected; `mobile` and `api` silently dropped; two spurious warnings.

**AFTER** (captured 2026-09-07T07:40:36Z, post-change — `resolve_pack_choices` from setup.sh on the
same input `1, 5, 3`):

```
$ date -u +%Y-%m-%dT%H:%M:%SZ
2026-09-07T07:40:36Z
$ RAW="1, 5, 3" SETUP_SH_DEFINE_ONLY=1 sh -c 'set --; . ./setup.sh; \
    printf "RESULT PACKS: %s\n" "$(resolve_pack_choices "$RAW")"'
RESULT PACKS: mobile api devops
```

All three packs selected; no warnings on stderr.

**DELTA**: A user entering `1, 5, 3` (or `1,5,3`) at the pack prompt now gets exactly `mobile api
devops` with no warning, matching `1 5 3`.

**WITNESS**: [who ran it and when — derived from `memory/event-trace/T108.jsonl`, never the
implementing agent alone]

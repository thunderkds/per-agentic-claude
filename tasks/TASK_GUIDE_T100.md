# TASK_GUIDE — T100: One response standard for the Supervisor and every sub-agent

**Complexity Level**: C1
**Risk Level**: Low
**Priority**: P1
**Assigned agent**: Common-Infrastructure-Agent
**Agent guide**: `.claude/agents/common-infrastructure.md`

---

## Mandatory Startup (Do Not Skip)

1. Read `PROJECT_SPEC.md`.
2. Read this guide in full — **especially "The rule must not become the thing it forbids"**, which is
   the constraint that makes this task easy to fail.
3. Read `.claude/agents/common-infrastructure.md`.
4. Read `memory/MEMORY.md`, then `CLAUDE.md`'s `## Supervisor Communication Style` section and
   `agents/general-agent-template.md`'s `## Output Requirements (Every Task)`. Read the
   `## Communication Protocol` and `## Output Format` blocks in all four role guides.
5. **Trace attribution**: `mkdir -p /home/hungnguyenhuu/workspace/pets/personal-agentic-claude/.claude/hooks/.state && printf '%s\n%s\n' "T100" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > /home/hungnguyenhuu/workspace/pets/personal-agentic-claude/.claude/hooks/.state/active_task`
   Literal absolute path. Not `$CLAUDE_PROJECT_DIR` (empty inside a `Bash` tool call).
6. **Demonstration BEFORE capture**: fill the BEFORE field in
   `<your-worktree>/tasks/TASK_REVIEW_T100.md` before your first commit. This task changes
   instruction text, not executable code, so BEFORE is the **verbatim prior content** of each block
   you are about to change, quoted from the file as it exists right now.

---

## Requirement (Pillar 1 — Adapt the requirement)

Registered 2026-09-02 by the user: make agent responses focused, simple, and easy for a human to
follow — as one shared standard covering the Supervisor and every sub-agent, enforced by guidance
in `CLAUDE.md` and the agent guides rather than by new machinery. Both scope and enforcement were
chosen by the user at Stage 2; do not widen either.

### What is actually wrong today (measured, not assumed)

`CLAUDE.md`'s `## Supervisor Communication Style` opens with:

> "The harness already keeps chat replies short and plain by default — no extra rule needed for that."

**That claim is false in practice, and the session that registered this task is the evidence.** Over
T099 the Supervisor produced replies running 40+ lines with stacked tables, multi-column
BEFORE/AFTER matrices, and three-option decision menus at nearly every turn. The existing text
asserts a property nothing enforces and no one had re-checked — the same failure mode T099 hit three
times in its own docstrings (`memory/learnings.md`, 2026-09-02). Correcting that sentence is part of
this task, not a side note.

The sub-agent side is different and must not be treated as the same defect. Role guides already
define a `## Communication Protocol` and a fenced `## Output Format` block, and agents do follow
them. What is missing there is any rule about the **prose between the fenced blocks** — the long
findings narratives that arrive with no ordering and no signal about what needs a decision.

### The rule must not become the thing it forbids

External research (2026 AGENTS.md/CLAUDE.md practice) is unambiguous and cuts against the obvious
implementation: instruction files that **duplicate what the agent could already infer measurably
hurt** — one study found LLM-generated instruction files reduced task success ~2% and raised cost
~23%, precisely because they restated available context. Recommended length is well under 150 lines
total, hand-written, carrying only non-obvious information.

So a long, thorough style section is a **failure**, not a thorough job. The vital slice is a small
number of behavioural rules that change what a response looks like. If a rule would not change any
response in this repo's history, it does not go in.

**Restated intent**:
> Add the smallest set of response rules that would have visibly changed the T099 session's replies,
> place them where both the Supervisor and every sub-agent inherit them without duplication, and
> correct the false claim currently sitting in `CLAUDE.md`. Net line growth across all instruction
> files must be small — see AC6.

### Requirement Fidelity Gate (sign off BEFORE implementation)

- [ ] I can name the one sentence in `CLAUDE.md` that is factually wrong, and I have read the
      session behaviour that disproves it.
- [ ] I understand that adding length to instruction files has a measured cost, and that "more
      guidance" is therefore not automatically better.
- [ ] I have confirmed where a rule must live so that the Supervisor **and** all four role guides
      inherit it without the text being repeated in six places.

---

## Dependencies & Reachability

**Depends on**: nothing.
**Blocks**: nothing.
**Entry point**: `CLAUDE.md` (loaded into every session by the harness) and
`agents/general-agent-template.md` (inherited by every sub-agent per the Base Rules). No code path.

---

## Acceptance Criteria

- **AC1 — the false claim is corrected.** `CLAUDE.md`'s "The harness already keeps chat replies short
  and plain by default — no extra rule needed for that" is replaced with text that matches observed
  behaviour. The existing guard it introduces — brevity must not bleed into KANBAN rows, Evidence,
  `memory/`, or commit messages — is **preserved**, not dropped.
- **AC2 — one shared standard, defined once.** The response rules live in exactly one place that both
  the Supervisor and all sub-agents reach. The rule text is **not** copy-pasted into the four role
  guides; those may point at it, and only if a pointer is actually needed.
- **AC3 — the rules are behavioural and testable by reading.** Each rule says what to do or not do in
  a response, in a form a reader can check against an actual reply (e.g. "lead with the answer, not
  the method"). No rule may be a vague exhortation such as "be clear" or "write well".
- **AC4 — the decision-request rule exists.** A response that needs the user to choose must state the
  recommendation first and keep the alternatives to a short line each. This is the single highest-
  value rule from the registering session and must be present in some form.
- **AC5 — artifact detail is explicitly exempt.** The standard must state that it governs
  conversational responses only, and that TASK_GUIDE Evidence, KANBAN rows, `memory/` cold files and
  commit messages stay fully detailed. Without this the change would degrade the audit trail.
- **AC6 — net growth is bounded.** Total added lines across `CLAUDE.md` + `agents/*.md` is **≤ 40**,
  and `CLAUDE.md` does not grow past its current section count. Deleting stale text to make room is
  encouraged and counts in your favour. State the measured before/after line counts in Evidence.
- **AC7 — the staleness guard still holds.** If any non-negotiable named by
  `agents/general-agent-template.md`'s `## Staleness Guard` changes, `AGENTS.md` and
  `.cursor/rules/agent-base.mdc` are updated in the same commit and
  `tests/test_provider_adapters.py` still passes.

---

## Evaluation & Acceptance

### Success Criteria (observable, pass/fail)

A reader can point to each rule and to a response in this repo's history the rule would have changed.
The four role guides contain no duplicated copy of the standard. All existing suites stay green.

### Verification Command (exact, runnable)

```sh
python3 -m pytest .claude/hooks/tests/ -q && python3 -m pytest tests/ -q && bash scripts/validate.sh
```

Baseline as of T099's merge: 790 hook tests with **6 known pre-existing failures**
(`memory/MEMORY.md` 45,859 chars vs the 45,000 ratchet ×5, `README.md` 73 lines vs 60 ×1). Those are
**not yours** — do not fix them, and do not let them mask a new failure.

### Evidence (filled by reviewer at Stage 4/5)

> **Moved.** See `tasks/TASK_REVIEW_T100.md`.

---

## Demonstration

> See `tasks/TASK_REVIEW_T100.md`.

---

## Approach

**Vital slice**: one short `## Response Standard` block in `agents/general-agent-template.md` (which
every sub-agent already inherits), and a correction plus a pointer in `CLAUDE.md` so the Supervisor
is bound by the same text. Roughly 5–8 rules, one line each.

Rules worth considering — **your judgement, not a checklist to transcribe**; each must earn its line
against the T099 session:
- lead with the answer or verdict, then the evidence
- one table maximum per response, and only when comparing across more than two dimensions
- recommendation first when asking for a decision, alternatives to one line each
- say what is blocked and what you need, rather than listing everything you could do
- no restating what the user just said before answering it

**Cut list** (deliberately not built):
- No hook, no linter, no test that inspects response text — the user chose guidance-only, and the
  T099 session is a live demonstration of how a hook that judges free text fails open.
- No rewrite of the four role guides' existing `## Output Format` fenced blocks. They work.
- No change to skill files. Skills carry their own Communication Protocol lines; sweeping them is a
  separate, larger task.
- No new documentation file. This is a small rule set, not a doc.

---

## Edge Case Checklist

- A response that is genuinely a long report (a verification with real evidence) — the standard must
  not make honest evidence unreportable. AC5 is the release valve; confirm it actually covers this.
- A sub-agent's fenced `## Output Format` block vs. the prose around it — the standard governs the
  prose, and must not contradict the fenced format.
- `CLAUDE.md` is mirrored by `AGENTS.md` and `.cursor/rules/agent-base.mdc` for other harnesses
  (AC7). Check whether the Response Standard is a "non-negotiable" under the Staleness Guard's
  definition; if it is, all three move together.

## Files to Change (Predicted)

- `agents/general-agent-template.md` — the standard itself.
- `CLAUDE.md` — correct the false claim; point at the standard.
- `AGENTS.md`, `.cursor/rules/agent-base.mdc` — only if AC7 is triggered.

## Files Must NOT Touch

- The four role guides' `## Output Format` fenced blocks.
- `skills/**` — out of scope per the cut list.
- Anything under `.claude/hooks/` — this task adds no machinery.

## Test Plan

Guidance-only, per the user's explicit choice, so there is no behavioural test to write. **Hard-Stop
Gate 5 still applies**, and is satisfied the way this repo already satisfies it for doc-structure
work (`scripts/test-claude-md-refs.sh`, `tests/test_provider_adapters.py`): add a **minimal
structural assertion** that the Response Standard section exists where AC2 requires and is not
duplicated across the role guides. One assertion, not a suite. If you believe even that is
over-building, say so in your report and leave it out with your reasoning — the Supervisor will
decide rather than have you silently skip a Hard-Stop Gate.

## Completion Checklist

- [ ] Requirement Fidelity Gate signed off
- [ ] BEFORE captured (verbatim prior text) before the first commit
- [ ] AC1–AC7 satisfied, with before/after line counts stated for AC6
- [ ] Verification Command run, output pasted into Evidence, 6 known failures and no others
- [ ] AFTER + DELTA + WITNESS filled
- [ ] UI Evidence rows ☐ N/A (instruction text only, no UI surface)

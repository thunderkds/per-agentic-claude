"""
T092 — `craft-spawn-prompt/SKILL.md` must carry DDR-0004's cache-read finding
(spawn-prompt *size* is ~free because nearly all injected context bills as a
cache read; spawn *count* is the cost lever) inside its `#### 3. Assemble the
prompt` step, so a Supervisor assembling a spawn prompt doesn't waste effort
trimming guide refs / the memory path / orienting content to "save tokens".

Every numeric literal asserted here is parsed out of
`docs/ddr/0004-uphold-hard-stop-gate-1-over-spawn-elimination.md` **at test
time**, never hardcoded — AC5. Mutating the DDR's number (not the SKILL.md)
must turn this suite RED (AC5/AC6, SC4) or the test is comparing SKILL.md
against a copy of itself instead of the live source.
"""
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
SKILL_MD = os.path.join(ROOT, "skills", "craft-spawn-prompt", "SKILL.md")
DDR_GLOB = os.path.join(ROOT, "docs", "ddr", "0004-*.md")

BANNED_WORDS = ["budget", "target", "limit", "at most", "should be under"]


def _read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def _ddr_path():
    matches = glob.glob(DDR_GLOB)
    assert matches, f"no file matched {DDR_GLOB} — DDR-0004 missing or renamed"
    return matches[0]


def _skill_step_3():
    text = _read(SKILL_MD)
    m = re.search(
        r"#### 3\. Assemble the prompt(.*?)\n#### 4\.",
        text,
        re.DOTALL,
    )
    assert m, "SKILL.md has no '#### 3. Assemble the prompt' ... '#### 4.' span"
    return m.group(1)


def _added_passage(step_3_text):
    """The new cache-note paragraph: between the pre-existing caller-inputs
    sentence and the pre-existing '**Element 6' subsection that follows it."""
    start_marker = "Any caller-supplied inputs"
    end_marker = "**Element 6"
    start = step_3_text.find(start_marker)
    assert start != -1, "step 3 no longer contains the 'Any caller-supplied inputs' anchor sentence"
    end = step_3_text.find(end_marker, start)
    assert end != -1, "step 3 no longer contains the pre-existing '**Element 6' subsection"
    after_anchor = step_3_text[start:end]
    end_of_anchor_sentence = after_anchor.find("\n")
    return after_anchor[end_of_anchor_sentence:].strip("\n")


def _normalize_number(raw):
    """Strip commas/tildes/percent signs so '~97%' and '97%' compare equal,
    and '83,802' and '83802' compare equal."""
    return raw.replace(",", "").replace("~", "").replace("%", "").strip()



# Percentage- or token-count-shaped literals only: excludes IDs like
# "DDR-0004" or "T069" via the negative lookbehind on word chars/hyphen.
NUMBER_RE = re.compile(r"(?<![\w-])~?\d[\d,]*\.?\d*%?(?![\w-])")


def _numeric_literals(text):
    return [m.group(0) for m in NUMBER_RE.finditer(text)]


def test_ac1_states_measured_conclusion():
    passage = _added_passage(_skill_step_3())
    # Collapse newlines before matching: `.` does not cross a line break, so a
    # bounded window like `count.{0,40}cost` silently dies the moment the passage
    # wraps — the exact defect recorded as T085's Stage 4 P1. Without this the
    # regex below is dead code and the assertion passes only via the string
    # fallback, which is a weaker check than it looks.
    lowered = re.sub(r"\s+", " ", passage.lower())
    assert "cache" in lowered
    assert "count" in lowered
    assert "spawn" in lowered
    # conclusion: size is ~free (cache read), count is the lever
    assert re.search(r"count.{0,40}(lever|cost)|lever.{0,40}count", lowered) or (
        "not the cost lever" in lowered and "count" in lowered
    )


def test_ac2_explicit_do_not_names_t069():
    passage = _added_passage(_skill_step_3())
    assert "do not trim" in passage.lower()
    assert "memory/memory.md" in passage.lower()
    assert "t069" in passage.lower()


def test_ac3_points_at_ddr_by_filename():
    passage = _added_passage(_skill_step_3())
    assert "0004-uphold-hard-stop-gate-1-over-spawn-elimination.md" in passage


def test_ac4_added_lines_within_cap_and_no_new_heading():
    text = _read(SKILL_MD)
    line_count = len(text.splitlines())
    assert line_count <= 80, f"SKILL.md is {line_count} lines, cap is 80 (72 baseline + 8)"
    passage = _added_passage(_skill_step_3())
    assert not re.search(r"^#{2,3}\s", passage, re.MULTILINE), "added passage introduces a new heading"


def test_ac5_and_ac6_every_numeric_literal_traces_to_ddr():
    passage = _added_passage(_skill_step_3())
    ddr_text = _read(_ddr_path())
    ddr_numbers = {_normalize_number(n) for n in _numeric_literals(ddr_text)}

    passage_numbers = _numeric_literals(passage)
    assert passage_numbers, "AC5 expects at least one number-shaped literal in the added passage"

    for raw in passage_numbers:
        norm = _normalize_number(raw)
        assert norm in ddr_numbers, (
            f"literal {raw!r} in the added passage does not appear in "
            f"{os.path.basename(_ddr_path())} — AC5 requires every number to be sourced from the DDR"
        )

    # AC3/AC6: the DDR filename pointer itself must be present
    assert "0004-uphold-hard-stop-gate-1-over-spawn-elimination.md" in passage


def test_ac8_no_budget_target_language():
    passage = _added_passage(_skill_step_3()).lower()
    for word in BANNED_WORDS:
        assert word not in passage, f"banned word {word!r} found in added passage"

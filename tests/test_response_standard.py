"""T100 — structural assertion for the shared Response Standard (AC2).

Guidance-only task: there is no behavioural test. This asserts only the two
structural properties AC2 names — the standard exists in the one file every
sub-agent and the Supervisor reach, and its rule text is not copy-pasted into
the four role guides.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "agents" / "general-agent-template.md"
ROLE_GUIDES = [
    ROOT / "agents" / name
    for name in ("backend.md", "frontend.md", "qa.md", "common-infrastructure.md")
]


def test_response_standard_is_defined_once_in_the_shared_template():
    heading = "## Response Standard"
    assert TEMPLATE.read_text(encoding="utf-8").count(heading) == 1, (
        f"expected exactly one '{heading}' section in {TEMPLATE.name}"
    )


def test_response_standard_is_not_duplicated_into_the_role_guides():
    # A rule line, not the heading: a role guide may point at the section by
    # name, but must not carry the rules themselves.
    rule = "state your recommendation first"
    for guide in ROLE_GUIDES:
        assert rule not in guide.read_text(encoding="utf-8"), (
            f"{guide.name} duplicates the Response Standard rule text; it must point, not copy"
        )

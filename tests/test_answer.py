from aerodoc.answer import SYSTEM_PROMPT, build_messages, parse_citations
from aerodoc.search import Hit


def _hit(n: int) -> Hit:
    return Hit(n, "FR-1", "t", "directive", "2026-18-03", "u", "h", f"text {n}", 1, "1", "s")


def test_parse_citations_in_order_without_duplicates():
    assert parse_citations("A [2]. B [1][2]. C [3].") == [2, 1, 3]
    assert parse_citations("no citation") == []


def test_prompt_numbers_passages_and_states_the_rules():
    messages = build_messages("Q?", [_hit(1), _hit(2)])
    assert messages[0]["content"] == SYSTEM_PROMPT
    assert "[1] Source: AD 2026-18-03" in messages[1]["content"]
    assert "[2] Source:" in messages[1]["content"]
    assert "ONLY" in SYSTEM_PROMPT and "NOT_IN_DOCUMENTS" in SYSTEM_PROMPT

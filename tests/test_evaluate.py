from aerodoc.evaluate import contains_facts, is_relevant
from aerodoc.search import Hit


def _hit(ad=None, doc_type="directive", page_label=None) -> Hit:
    return Hit(1, "d", "t", doc_type, ad, "u", "h", "x", 1, page_label, "s")


def test_contains_facts_with_alternatives():
    ok, missing = contains_facts(
        "The ELAC caused a pitch-down event.",
        ["elevator aileron computer|ELAC", "pitch down|pitch-down"],
    )
    assert ok and missing == []
    ok, missing = contains_facts("Nickel plating was missing.", ["nickel", "corrosion"])
    assert not ok and missing == ["corrosion"]


def test_is_relevant_for_directives_and_handbook_pages():
    assert is_relevant(_hit(ad="2024-08-02"), {"ad_number": "2024-08-02"})
    assert not is_relevant(_hit(ad="2024-08-08"), {"ad_number": "2024-08-02"})
    assert is_relevant(_hit(doc_type="handbook", page_label="5-8"), {"pages": ["5-8", "5-7"]})
    assert not is_relevant(_hit(ad="2024-08-02"), {})


def test_wilson_interval_is_wide_for_small_samples():
    from aerodoc.evaluate import wilson

    low, high = wilson(16, 16)
    assert high == 1.0 and 0.79 < low < 0.81  # 16/16 is compatible with ~80 %
    low, high = wilson(0, 10)
    assert low == 0.0 and high < 0.31

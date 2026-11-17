from aerodoc.corpus import ad_number, govinfo_text_url, html_to_text, mentions_model


def test_ad_number_is_extracted_from_docket_ids():
    dockets = ["Docket No. FAA-2026-8793", "Amendment 39-23458", "AD 2026-18-03"]
    assert ad_number(dockets) == "2026-18-03"
    assert ad_number(["Docket No. FAA-2023-1"]) is None


def test_govinfo_text_url():
    pdf = "https://www.govinfo.gov/content/pkg/FR-2026-09-03/pdf/2026-18052.pdf"
    assert govinfo_text_url(pdf) == (
        "https://www.govinfo.gov/content/pkg/FR-2026-09-03/html/2026-18052.htm"
    )


def test_html_to_text_keeps_page_markers_and_unescapes():
    raw = "<html><body><pre>[[Page 56576]]\nA &amp; B <a href='x'>link</a></pre></body></html>"
    assert html_to_text(raw) == "[[Page 56576]]\nA & B link\n"


def test_mentions_model_is_case_insensitive():
    assert mentions_model("certain Model ATR72-212A airplanes", ["ATR72", "ATR 72"])
    assert not mentions_model("Model A350-941 airplanes", ["A320"])

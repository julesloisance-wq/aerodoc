from aerodoc.chunking import Paragraph, pack, parse_directive
from aerodoc.pipeline_config import ChunkingConfig

SAMPLE = """[Federal Register Volume 91]

DEPARTMENT OF TRANSPORTATION

SUMMARY: The FAA is adopting a new AD for certain Model A320 airplanes.

Background

    The landing gear support rib may crack.

[[Page 56578]]

(c) Applicability

    This AD applies to Model A320-214 airplanes.
"""


def test_parse_directive_tracks_sections_and_pages():
    paragraphs = parse_directive(SAMPLE, first_page=56577)
    assert [(p.section, p.page) for p in paragraphs] == [
        ("Summary", 56577),
        ("Background", 56577),
        ("(c) Applicability", 56578),
    ]
    assert paragraphs[0].text.startswith("The FAA is adopting")


def test_pack_respects_size_and_overlap():
    cfg = ChunkingConfig(max_words=10, overlap_words=3, min_words=2)
    words = " ".join(f"w{i}" for i in range(25))
    chunks = pack([Paragraph(words, 1, "1", "S")], cfg)
    assert all(len(c.text.split()) <= 10 for c in chunks)
    # The last 3 words of a chunk start the next one.
    assert chunks[0].text.split()[-3:] == chunks[1].text.split()[:3]


def test_pack_closes_chunk_at_new_section_only_when_big_enough():
    cfg = ChunkingConfig(max_words=100, overlap_words=0, min_words=5)
    paras = [
        Paragraph("one two", 1, "1", "(d) Subject"),  # too small to stand alone
        Paragraph("a b c d e f", 1, "1", "(e) Unsafe Condition"),
        Paragraph("x y z", 1, "1", "(f) Compliance"),
    ]
    chunks = pack(paras, cfg)
    assert len(chunks) == 2
    assert chunks[0].section == "(d) Subject / (e) Unsafe Condition"
    assert chunks[1].text == "x y z"

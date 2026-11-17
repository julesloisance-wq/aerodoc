"""Split documents into chunks (passages) that keep their page and section.

Each chunk gets a short *header* (document, AD number, section) that is embedded with the
text: a passage that only says "Comply with EASA AD 2026-0142" is then still linked to its
directive, aircraft and section.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from aerodoc.corpus import DocumentRecord
from aerodoc.pipeline_config import ChunkingConfig

PAGE_MARKER = re.compile(r"\[\[Page (\d+)\]\]")
LABEL_LINE = re.compile(r"^([A-Z][A-Z ]{2,40}):\s*(.*)$", re.S)


@dataclass
class Paragraph:
    text: str
    page: int | None
    page_label: str | None
    section: str | None


@dataclass
class Chunk:
    document_id: str
    chunk_index: int
    text: str
    header: str
    page: int | None
    page_label: str | None
    section: str | None

    @property
    def embedding_text(self) -> str:
        return f"{self.header}\n{self.text}"


# --------------------------------------------------------------------------- directives
def _is_heading(lines: list[str]) -> bool:
    text = " ".join(line.strip() for line in lines)
    return (
        len(lines) <= 2
        and not lines[0].startswith(" ")
        and len(text) < 100
        and not text.endswith((".", ",", ";", ":"))
        and not text.startswith("[")
    )


def parse_directive(text: str, first_page: int | None) -> list[Paragraph]:
    """Turn a Federal Register text into paragraphs tagged with page and section."""
    # Drop the Federal Register banner (everything before the agency line).
    start = text.find("DEPARTMENT OF TRANSPORTATION")
    text = text[start:] if start >= 0 else text
    page, section = first_page, None
    paragraphs: list[Paragraph] = []
    for block in re.split(r"\n\s*\n", text):
        pieces = PAGE_MARKER.split(block)  # [text, page, text, page, ...]
        for i, piece in enumerate(pieces):
            if i % 2 == 1:
                page = int(piece)
                continue
            lines = [line for line in piece.split("\n") if line.strip()]
            if not lines or set("".join(lines).strip()) <= set("=-"):
                continue
            if i == 0 and _is_heading(lines):
                section = " ".join(line.strip() for line in lines)
                continue
            body = " ".join(line.strip() for line in lines)
            label = LABEL_LINE.match(body) if i == 0 else None
            if label:  # "SUMMARY: The FAA is adopting ..." -> section "Summary"
                section = label.group(1).strip().title()
                body = label.group(2).strip()
            if body:
                label_text = str(page) if page else None
                paragraphs.append(Paragraph(body, page, label_text, section))
    return paragraphs


# --------------------------------------------------------------------------- handbook
def parse_handbook(pdf_path: Path) -> list[Paragraph]:
    """One paragraph per PDF page, tagged with the printed page label and TOC section."""
    import pymupdf

    doc = pymupdf.open(pdf_path)
    # The table of contents is flat: "Chapter 5", then the chapter title, then sections.
    toc = [(title.strip(), page) for _, title, page in doc.get_toc()]
    chapter_of: dict[int, str] = {}
    section_of: dict[int, str] = {}
    chapter, section, j = None, None, 0
    for pno in range(1, doc.page_count + 1):
        while j < len(toc) and toc[j][1] <= pno:
            title = toc[j][0]
            if re.fullmatch(r"Chapter \d+", title) and j + 1 < len(toc):
                chapter = f"{title}: {toc[j + 1][0]}"
                section = None
                j += 2
                continue
            section = title
            j += 1
        chapter_of[pno], section_of[pno] = chapter, section

    paragraphs = []
    for pno, page in enumerate(doc, start=1):
        text = re.sub(r"\s+", " ", page.get_text()).strip()
        if len(text.split()) < 30:  # blank pages, full-page figures
            continue
        label = page.get_label() or str(pno)
        text = text.removeprefix(label).strip()
        parts = [p for p in (chapter_of[pno], section_of[pno]) if p]
        paragraphs.append(Paragraph(text, pno, label, " > ".join(parts) or None))
    return paragraphs


# --------------------------------------------------------------------------- packing
def pack(paragraphs: list[Paragraph], cfg: ChunkingConfig) -> list[Paragraph]:
    """Greedily pack paragraphs into ~max_words chunks with a word overlap.

    A chunk keeps the page/section of the paragraph it starts with. It is closed at a
    section (or page) change once it has at least `min_words` words.
    """
    chunks: list[Paragraph] = []
    words: list[str] = []
    start: Paragraph | None = None
    sections: list[str] = []

    def flush(keep_overlap: bool) -> None:
        nonlocal words, start, sections
        if words and start:
            section = " / ".join(dict.fromkeys(s for s in sections if s)) or None
            chunks.append(Paragraph(" ".join(words), start.page, start.page_label, section))
        words = words[-cfg.overlap_words :] if keep_overlap and cfg.overlap_words else []
        sections = sections[-1:] if words else []

    for para in paragraphs:
        boundary = start is not None and (
            para.section != start.section or para.page_label != start.page_label
        )
        if boundary and len(words) >= cfg.min_words:
            flush(keep_overlap=False)
            start = None
        if start is None or not words:
            start = para
        if para.section not in sections:
            sections.append(para.section)
        for word in para.text.split():
            words.append(word)
            if len(words) >= cfg.max_words:
                flush(keep_overlap=True)
                start = para
    flush(keep_overlap=False)
    return chunks


def chunk_document(rec: DocumentRecord, data_dir: Path, cfg: ChunkingConfig) -> list[Chunk]:
    path = data_dir / rec.local_path
    if rec.doc_type == "directive":
        paragraphs = [
            p
            for p in parse_directive(path.read_text(encoding="utf-8"), rec.first_page)
            if p.section not in cfg.skip_sections
        ]
        ident = f"AD {rec.ad_number}" if rec.ad_number else f"FR Doc {rec.id[3:]}"
        families = ", ".join(rec.families)
        base_header = f"{ident} ({rec.title}; aircraft: {families}; effective {rec.effective_date})"
    else:
        paragraphs = parse_handbook(path)
        base_header = rec.title

    chunks = []
    for i, part in enumerate(pack(paragraphs, cfg)):
        header = base_header + (f" | {part.section}" if part.section else "")
        chunks.append(Chunk(rec.id, i, part.text, header, part.page, part.page_label, part.section))
    return chunks

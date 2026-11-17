"""Download the corpus: FAA airworthiness directives and the AMT handbook.

Outputs (all under `data/`, ignored by Git):
- `data/raw/directives/<document_number>.txt`: plain text of each directive, with
  Federal Register page markers such as `[[Page 56576]]`;
- `data/raw/handbooks/<id>.pdf`: handbook PDFs;
- `data/manifest.jsonl`: one line per document (id, type, title, dates, URLs, checksum).
"""

from __future__ import annotations

import hashlib
import html
import json
import re
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

import httpx
import yaml

FR_API = "https://www.federalregister.gov/api/v1/documents.json"
USER_AGENT = "aerodoc/0.1 (educational RAG project)"
FR_FIELDS = [
    "title",
    "abstract",
    "document_number",
    "publication_date",
    "effective_on",
    "html_url",
    "pdf_url",
    "docket_ids",
    "start_page",
    "end_page",
]


@dataclass
class DocumentRecord:
    id: str
    doc_type: str  # "directive" or "handbook"
    title: str
    source_url: str
    download_url: str
    local_path: str
    sha256: str = ""
    ad_number: str | None = None
    families: list[str] = field(default_factory=list)
    publication_date: str | None = None
    effective_date: str | None = None
    first_page: int | None = None
    abstract: str | None = None


def _client() -> httpx.Client:
    return httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=120, follow_redirects=True)


def _get(client: httpx.Client, url: str, **kwargs) -> httpx.Response:
    """GET with a few retries, because public servers sometimes hiccup."""
    for attempt in range(4):
        try:
            response = client.get(url, **kwargs)
            if response.status_code < 500 and response.status_code != 429:
                response.raise_for_status()
                return response
        except httpx.TransportError:
            if attempt == 3:
                raise
        time.sleep(2**attempt)
    response.raise_for_status()
    return response


def ad_number(docket_ids: list[str]) -> str | None:
    """Extract the AD number, e.g. ['Amendment 39-23458', 'AD 2026-18-03'] -> '2026-18-03'."""
    for docket in docket_ids or []:
        match = re.fullmatch(r"AD\s+(\d{4}-\d{2}-\d{2})", docket.strip())
        if match:
            return match.group(1)
    return None


def mentions_model(text: str, models: list[str]) -> bool:
    return any(model.lower() in (text or "").lower() for model in models)


def search_directives(client: httpx.Client, query: str, since: str, limit: int) -> list[dict]:
    """Newest final-rule ADs from the FAA matching `query`, at most `limit` (pre-filter)."""
    params = [
        ("conditions[agencies][]", "federal-aviation-administration"),
        ("conditions[type][]", "RULE"),
        ("conditions[term]", query),
        ("conditions[publication_date][gte]", since),
        ("per_page", "100"),
        ("order", "newest"),
    ] + [("fields[]", f) for f in FR_FIELDS]
    results, url = [], FR_API
    while url and len(results) < limit * 2:
        data = _get(client, url, params=params if url == FR_API else None).json()
        results.extend(data.get("results", []))
        url = data.get("next_page_url")
    return results


def govinfo_text_url(pdf_url: str) -> str:
    """govinfo serves the same document as plain text: .../pdf/X.pdf -> .../html/X.htm."""
    return pdf_url.replace("/pdf/", "/html/").removesuffix(".pdf") + ".htm"


def html_to_text(raw_html: str) -> str:
    """govinfo text pages are a single <pre> block: strip tags and unescape entities."""
    body = re.search(r"<pre>(.*)</pre>", raw_html, flags=re.S)
    text = re.sub(r"<[^>]+>", "", body.group(1) if body else raw_html)
    return html.unescape(text).strip() + "\n"


def collect_directives(config: dict) -> list[DocumentRecord]:
    """Select ADs for each aircraft family, deduplicated by document number."""
    cfg = config["directives"]
    selected: dict[str, DocumentRecord] = {}
    with _client() as client:
        for family, spec in cfg["families"].items():
            kept = 0
            for doc in search_directives(
                client, spec["query"], cfg["published_since"], cfg["max_per_family"]
            ):
                title = doc["title"]
                if not title.startswith("Airworthiness Directives;") or "Correction" in title:
                    continue
                if not mentions_model(doc.get("abstract") or "", spec["models"]):
                    continue
                number = doc["document_number"]
                if number in selected:
                    selected[number].families.append(family)
                    continue
                if kept >= cfg["max_per_family"]:
                    continue
                selected[number] = DocumentRecord(
                    id=f"FR-{number}",
                    doc_type="directive",
                    title=title,
                    source_url=doc["html_url"],
                    download_url=govinfo_text_url(doc["pdf_url"]),
                    local_path=f"raw/directives/{number}.txt",
                    ad_number=ad_number(doc.get("docket_ids")),
                    families=[family],
                    publication_date=doc.get("publication_date"),
                    effective_date=doc.get("effective_on"),
                    first_page=doc.get("start_page"),
                    abstract=doc.get("abstract"),
                )
                kept += 1
            print(f"{family}: {kept} directives")
    return list(selected.values())


def handbook_records(config: dict) -> list[DocumentRecord]:
    return [
        DocumentRecord(
            id=hb["id"],
            doc_type="handbook",
            title=hb["title"],
            source_url=hb["page_url"],
            download_url=hb["url"],
            local_path=f"raw/handbooks/{hb['id']}.pdf",
        )
        for hb in config.get("handbooks", [])
    ]


def download(records: list[DocumentRecord], data_dir: Path) -> None:
    """Download each document unless it is already on disk, and record its checksum."""
    with _client() as client:
        for i, rec in enumerate(records, 1):
            path = data_dir / rec.local_path
            path.parent.mkdir(parents=True, exist_ok=True)
            if not path.exists():
                response = _get(client, rec.download_url)
                if rec.doc_type == "directive":
                    path.write_text(html_to_text(response.text), encoding="utf-8")
                else:
                    path.write_bytes(response.content)
                time.sleep(0.2)  # be polite to public servers
            rec.sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
            if i % 25 == 0 or i == len(records):
                print(f"  downloaded {i}/{len(records)}")


def build_corpus(config_path: Path, data_dir: Path) -> list[DocumentRecord]:
    config = yaml.safe_load(config_path.read_text())
    records = collect_directives(config) + handbook_records(config)
    download(records, data_dir)
    records.sort(key=lambda r: (r.doc_type, r.id))
    manifest = data_dir / "manifest.jsonl"
    with manifest.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(asdict(rec), ensure_ascii=False) + "\n")
    print(f"Manifest: {manifest} ({len(records)} documents)")
    return records


def load_manifest(data_dir: Path) -> list[DocumentRecord]:
    lines = (data_dir / "manifest.jsonl").read_text(encoding="utf-8").splitlines()
    return [DocumentRecord(**json.loads(line)) for line in lines if line.strip()]

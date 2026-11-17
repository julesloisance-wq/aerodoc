# Data sources and licences

No corpus document is stored in this repository. The corpus is rebuilt with `make data`
(definition in `configs/corpus.yaml`); `data/manifest.jsonl` lists every document with its
source URL and SHA-256 checksum.

| Source | What | How it is fetched | Licence |
|---|---|---|---|
| [Federal Register API](https://www.federalregister.gov/developers/documentation/api/v1) | Search for FAA airworthiness directives (final rules, 2022 onwards) on Airbus A318–A321, Airbus A350, Boeing 737 and ATR 72 | `GET /api/v1/documents.json`, no API key | Works of the U.S. Government, not subject to copyright in the United States (17 U.S.C. § 105) |
| [govinfo.gov](https://www.govinfo.gov/app/collection/fr) (U.S. Government Publishing Office) | Full text of each directive, with Federal Register page markers | `https://www.govinfo.gov/content/pkg/FR-<date>/html/<number>.htm` | Same as above |
| [FAA handbooks](https://www.faa.gov/regulations_policies/handbooks_manuals/aviation) | *Aviation Maintenance Technician Handbook – General* (FAA-H-8083-30B), 677 pages | Direct PDF download | Work of the U.S. Government, not subject to copyright in the United States |

The documents are used as published, for an educational, non-commercial project. They are
not a substitute for the official, current versions: always check the FAA for the
directives in force.

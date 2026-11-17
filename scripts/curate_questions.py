"""Manual curation of eval/questions/generated.jsonl (decisions recorded here, reproducible).

Dropped: questions that do not identify a single directive (cost or date questions
answerable by many ADs, "this directive" wording) or that are badly phrased.
Relaxed: key facts that were too literal (copied with PDF spacing, long phrases, special
characters), so that a correct answer worded differently is not counted as wrong.
"""

import json
from pathlib import Path

SRC = Path("eval/questions/generated.jsonl")
OUT = Path("eval/questions/generated_curated.jsonl")

DROP = {
    # cost questions that match many directives
    "g03",
    "g05",
    "g08",
    "g18",
    "g28",
    "g29",
    "g30",
    "g32",
    "g33",
    # dates / requirements shared by many directives, or "this directive" wording
    "g07",
    "g12",
    "g13",
    "g16",
    "g26",
    "g35",
    "g37",
    "g39",
    "g43",
    # unclear question
    "g34",
}

KEYS = {
    "g01": ["fatigue", "corrosion"],
    "g02": ["oxygen mask", "replac"],
    "g04": ["1 and 0|0 and 1|1 or 0|0 or 1|1 and 0|0 and 1"],
    "g06": ["T-Duct|T-duct|T duct", "RR03-11011-001"],
    "g09": ["airworthiness limitation"],
    "g10": ["structural integrity", "loss of control"],
    "g11": ["shroud"],
    "g14": ["strengthen"],
    "g15": ["stuck"],
    "g17": ["read", "loss of control|loss of airplane control"],
    "g19": ["protective cap"],
    "g20": ["fire"],
    "g21": ["interference", "stringer"],
    "g23": ["inspect", "record"],
    "g24": ["radio altimeter", "interference"],
    "g25": ["inspection", "leak test"],
    "g27": ["fastener", "cap"],
    "g31": ["304"],
    "g36": ["April 19, 2024|19 April 2024|2024-04-19"],
    "g38": ["detailed inspection"],
    "g40": ["solder"],
    "g41": ["737-8", "737-9", "8200"],
    "g42": ["roll"],
    "g44": ["sleep"],
    "g45": ["water/methanol|water methanol|water-methanol"],
    "g46": ["divid", "moment"],
    "g47": ["base"],
    "g48": ["0.10 to 0.25|0.1 to 0.25|0.10-0.25|0.1-0.25", "gallon"],
    "g49": ["parenthes", "bracket"],
    "g50": ["slip ring", "commutator"],
    "g51": ["height", "1/2|half|½|1⁄2|/ 2|/2"],
    "g52": ["Number 1|No. 1|#1|size 1", "Number 2|No. 2|#2|size 2"],
    "g53": ["14.7", "29.92"],
    "g54": ["acme nut", "lubrication"],
    "g55": ["one side"],
    "g56": ["transition", "thread"],
    "g57": ["Notice of Proposed Rulemaking|NPRM", "Final Rule", "Emergency"],
    "g58": ["77", "50 percent|50%|50 %"],
    "g59": ["remov", "coating"],
    "g60": ["105"],
    "g61": ["crack", "inclusion"],
    "g62": ["farther apart|far apart|spaced"],
    "g63": ["strength-to-weight|strength to weight"],
    "g64": ["Pythagorean|square root"],
    "g65": ["24"],
    "g66": ["vinegar", "boric"],
}

kept = []
for line in SRC.read_text().splitlines():
    item = json.loads(line)
    if item["id"] in DROP:
        continue
    item["must_include"] = KEYS.get(item["id"], item["must_include"])
    kept.append(item)
OUT.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in kept) + "\n")
print(f"{len(kept)} kept, {len(DROP)} dropped")

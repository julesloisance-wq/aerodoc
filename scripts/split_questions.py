"""Assemble the full question set and split it once into dev (60 %) and test (40 %).

The split is stratified by question type and seeded, so it is reproducible. The test set
is used only once, for the final measurement; all analysis and tuning uses dev.
"""

import json
import random
from collections import defaultdict
from pathlib import Path

SEED = 42
DIR = Path("eval/questions")
items = []
for name in ("generated_curated.jsonl", "handcrafted.jsonl"):
    items += [json.loads(line) for line in (DIR / name).read_text().splitlines() if line]

by_type = defaultdict(list)
for item in items:
    by_type[item["type"]].append(item)
rng = random.Random(SEED)
dev, test = [], []
for kind in sorted(by_type):
    group = sorted(by_type[kind], key=lambda x: x["id"])
    rng.shuffle(group)
    n_dev = round(len(group) * 0.6)
    dev += group[:n_dev]
    test += group[n_dev:]
for name, rows in (("dev", dev), ("test", test)):
    (DIR / f"{name}.jsonl").write_text(
        "\n".join(json.dumps(x, ensure_ascii=False) for x in rows) + "\n"
    )
    counts = defaultdict(int)
    for r in rows:
        counts[r["type"]] += 1
    print(name, len(rows), dict(sorted(counts.items())))

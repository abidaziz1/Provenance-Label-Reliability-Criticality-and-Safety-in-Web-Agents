"""Which attributes survive in the Mind2Web archive, per site (task 1.8).

Rewritten on 26 Sep 2026: the 25 Sep version was lost with the workspace before it was pushed.
The rewrite keeps the recorded output fields so tests/test_claims.py::test_K21 still applies.

Frame: the 57-site frame of scripts/c1_robustness.py (first 3 trajectories per site by
annotation_id in train shards 0, 1 and 10), every step's raw_html, parsed with lxml as stored
(no deep_parse). Counts element nodes and the attribute names on them.
"""
from pathlib import Path
import collections, gc, json, sys

ROOT = Path(__file__).resolve().parents[1]
FILES = [ROOT / "data" / "mind2web" / "data" / "train" / f for f in ("train_0.json", "train_1.json", "train_10.json")]
PER_SITE = 3
OUT = ROOT / "experiments" / "2026-09-25_1.8_attr-survival" / "results" / "attr_survival.json"

# Inputs that structural defenses read, as attribute-name tests on the archive's spelling ('-' becomes '_').
DEFENSE_INPUTS = {
    "data-*": lambda a: a.startswith("data_") or a.startswith("data-"),
    "on*": lambda a: a.startswith("on") and len(a) > 2,
    "tabindex": lambda a: a == "tabindex",
    "contenteditable": lambda a: a == "contenteditable",
    "href": lambda a: a == "href",
    "for": lambda a: a == "for",
    "hidden": lambda a: a == "hidden",
    "style": lambda a: a == "style",
    "role": lambda a: a == "role",
    "aria-*": lambda a: a.startswith("aria_") or a.startswith("aria-"),
    "id": lambda a: a == "id",
    "class": lambda a: a == "class",
}


def frame():
    bysite = collections.defaultdict(list)
    for f in FILES:
        for t in json.load(open(f)):
            bysite[t["website"]].append(t)
        gc.collect()
    return [x for s in sorted(bysite) for x in sorted(bysite[s], key=lambda t: t["annotation_id"])[:PER_SITE]]


def main():
    from lxml import html as LH
    sel = frame()
    names = collections.Counter()
    per_site_nodes = collections.Counter()
    per_site_hits = collections.defaultdict(collections.Counter)
    pages = 0
    for t in sel:
        s = t["website"]
        for a in t["actions"]:
            try:
                tree = LH.fromstring(a["raw_html"])
            except Exception:
                continue
            els = [el for el in tree.iter() if isinstance(el.tag, str)]
            if not els:
                continue
            pages += 1
            per_site_nodes[s] += len(els)
            for el in els:
                for k in el.attrib.keys():
                    names[k] += 1
                    for d, test in DEFENSE_INPUTS.items():
                        if test(k.lower()):
                            per_site_hits[s][d] += 1
    sites = sorted(per_site_nodes)
    per1k = {s: {d: round(1000 * per_site_hits[s][d] / per_site_nodes[s], 3) for d in DEFENSE_INPUTS} for s in sites}
    res = {
        "sites": len(sites),
        "pages": pages,
        "tasks": len(sel),
        "nodes": sum(per_site_nodes.values()),
        "attribute_names_present": sorted(names),
        "attribute_name_counts": dict(names.most_common()),
        "data_attribute_names": sorted(k for k in names if k.startswith("data_") or k.startswith("data-")),
        "sites_with_defense_input_under_1_per_1k": {d: sum(1 for s in sites if per1k[s][d] < 1) for d in DEFENSE_INPUTS},
        "sites_with_any": {d: sum(1 for s in sites if per_site_hits[s][d] > 0) for d in DEFENSE_INPUTS},
        "per_site_per_1k_nodes": per1k,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump(res, open(OUT, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k not in ("per_site_per_1k_nodes", "attribute_name_counts")}, indent=1))
    print(json.dumps(res["attribute_name_counts"]))


if __name__ == "__main__":
    sys.exit(main())

"""UCM's published selectors on archived Mind2Web pages (C7, C8).

Pre-registered in experiments/2026-09-25_C7_ucm-selectors-on-archive/. Needs a clone of
github.com/ethz-spylab/untrusted-content-masking (commit acff2e4) at $UCM_DIR
(default ext/ucm under this repository's root) and the Mind2Web shards under data/mind2web.
"""
from pathlib import Path
import collections, glob, json, os, re, sys
from lxml import html as LH
from lxml.cssselect import CSSSelector

ROOT = Path(__file__).resolve().parents[1]
UCM = Path(os.environ.get("UCM_DIR", ROOT / "ext" / "ucm"))
ABD = UCM / "src" / "automatic_boundary_detection"
OUT = ROOT / "experiments" / "2026-09-25_C7_ucm-selectors-on-archive" / "results" / "ucm_selectors_on_archive.json"
SHARDS = [ROOT / "data" / "mind2web" / "data" / "train" / f for f in ("train_0.json", "train_1.json", "train_10.json")]

ATTR_RX = re.compile(r"\[\s*([a-zA-Z_:][-a-zA-Z0-9_:.]*)")
CLASS_RX = re.compile(r"\.(-?[_a-zA-Z][-_a-zA-Z0-9]*)")
ID_RX = re.compile(r"#(-?[_a-zA-Z][-_a-zA-Z0-9]*)")


def hashed(tok):
    t = tok.lower()
    if re.fullmatch(r"[a-f0-9]{6,}", t):
        return True
    return len(t) >= 6 and bool(re.search(r"\d", t)) and not re.search(r"[aeiou]{1}[a-z]{2}", t.replace("-", ""))


def deps(sel):
    attrs = [a.lower() for a in ATTR_RX.findall(sel)]
    classes = CLASS_RX.findall(re.sub(r"\[[^\]]*\]", "", sel))
    return {
        "data_attr": any(a.startswith("data-") for a in attrs),
        "other_attr": sorted({a for a in attrs if not a.startswith("data-") and a != "class"}),
        "id": bool(ID_RX.findall(re.sub(r"\[[^\]]*\]", "", sel))),
        "classes": sorted(set(classes)),
        "hashed_classes": sorted({c for c in classes if hashed(c)}),
        "class_attr_substring": "[class" in sel,
    }


def load_sets():
    sets = []
    for site in ("booking", "reddit", "gitlab"):
        d = json.load(open(ABD / "sites" / site / "hand_labels.json"))
        sets.append(dict(site=site, source="hand", run=None, page=None, selectors=[s["selector"] for s in d["untrusted_selectors"]]))
    for f in sorted(glob.glob(str(ABD / "results" / "*" / "run_*" / "*" / "llm_labels.json"))):
        p = Path(f)
        d = json.load(open(p))
        sets.append(dict(site=p.parts[-4], source="llm", run=p.parts[-3], page=p.parts[-2],
                         selectors=[s["selector"] for s in d["untrusted_selectors"]]))
    return sets


def ucm_capture_counts(site):
    """Max match count per selector across UCM's own captured pages (hand and llm result files)."""
    counts = collections.defaultdict(int)
    for f in glob.glob(str(ABD / "results" / site / "run_*" / "*" / "*_results.json")):
        for r in json.load(open(f)).get("results", []):
            counts[r["selector"]] = max(counts[r["selector"]], r.get("count", 0))
    return counts


def underscore(sel):
    return ATTR_RX.sub(lambda m: "[" + m.group(1).replace("-", "_"), sel)


def main():
    sets = load_sets()
    booking_pages = []
    for f in SHARDS:
        for t in json.load(open(f)):
            if t["website"] == "booking":
                for a in t["actions"]:
                    booking_pages.append(a["raw_html"])
    trees = []
    for h in booking_pages:
        try:
            trees.append(LH.fromstring(h))
        except Exception:
            pass
    classes_in_archive = collections.Counter()
    for tr in trees:
        for el in tr.iter():
            if isinstance(el.tag, str):
                for c in (el.get("class") or "").split():
                    classes_in_archive[c] += 1

    cap = ucm_capture_counts("booking")
    by_selector, parse_errors = {}, 0
    for s in sets:
        for sel in s["selectors"]:
            key = (s["site"], sel)
            if key in by_selector:
                by_selector[key]["sources"].add(f"{s['source']}:{s['run']}:{s['page']}")
                continue
            rec = {"site": s["site"], "selector": sel, "sources": {f"{s['source']}:{s['run']}:{s['page']}"}, **deps(sel)}
            if s["site"] == "booking":
                for variant, text in (("as_written", sel), ("underscored", underscore(sel))):
                    try:
                        css = CSSSelector(text)
                        hits = [len(css(tr)) for tr in trees]
                        rec[f"archive_{variant}_pages_matched"] = sum(1 for h in hits if h)
                        rec[f"archive_{variant}_nodes"] = sum(hits)
                    except Exception:
                        rec[f"archive_{variant}_pages_matched"] = None
                        parse_errors += 1
                rec["ucm_capture_max_count"] = cap.get(sel)
                rec["class_tokens_in_archive"] = {c: classes_in_archive.get(c, 0) for c in rec["classes"]}
            by_selector[key] = rec

    rows = []
    for rec in by_selector.values():
        rec["sources"] = sorted(rec["sources"])
        rec["hand"] = any(x.startswith("hand") for x in rec["sources"])
        rows.append(rec)

    def share(xs, pred):
        xs = list(xs)
        return {"n": len(xs), "k": sum(1 for x in xs if pred(x)),
                "pct": round(100 * sum(1 for x in xs if pred(x)) / len(xs), 1) if xs else None}

    summary = {"ucm_commit": "acff2e4", "archive_booking_pages": len(trees), "parse_errors": parse_errors}
    for site in ("booking", "reddit", "gitlab"):
        for src in ("hand", "llm"):
            xs = [r for r in rows if r["site"] == site and (r["hand"] if src == "hand" else not r["hand"])]
            if not xs:
                continue
            summary[f"{site}_{src}"] = {
                "selectors": len(xs),
                "data_attr": share(xs, lambda r: r["data_attr"]),
                "hashed_class": share(xs, lambda r: bool(r["hashed_classes"])),
                "data_attr_or_hashed_class": share(xs, lambda r: r["data_attr"] or bool(r["hashed_classes"])),
                "semantic_only": share(xs, lambda r: not r["data_attr"] and not r["hashed_classes"]),
            }
    bk = [r for r in rows if r["site"] == "booking"]
    for src in ("hand", "llm"):
        xs = [r for r in bk if (r["hand"] if src == "hand" else not r["hand"])]
        live = [r for r in xs if (r.get("ucm_capture_max_count") or 0) > 0]
        summary[f"booking_{src}_archive"] = {
            "selectors": len(xs),
            "match_on_ucm_captures": len(live),
            "of_those_match_nothing_on_archive": sum(1 for r in live if not r.get("archive_underscored_pages_matched")),
            "any_selector_matches_archive": sum(1 for r in xs if r.get("archive_underscored_pages_matched")),
            "archive_nodes_matched_total": sum(r.get("archive_underscored_nodes") or 0 for r in xs),
        }
    hashed_tokens = sorted({c for r in bk for c in r["hashed_classes"]})
    summary["booking_hashed_class_tokens"] = {c: classes_in_archive.get(c, 0) for c in hashed_tokens}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump({"summary": summary, "selectors": rows}, open(OUT, "w"), indent=1, default=list)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    sys.exit(main())

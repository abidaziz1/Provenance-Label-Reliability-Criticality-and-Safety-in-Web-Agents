"""Archive stripping versus site drift for UCM's Booking selectors (task C7c).

Pre-registered in experiments/2026-09-26_C7c_live-strip-vs-drift/README.md (saved to the project
before this script ran). Captures UCM's three Booking pages live, then applies UCM's published
selectors to (a) the live DOM and (b) the same DOM reduced to the 21 attribute names the
Mind2Web archive keeps (K21), with '-' renamed to '_' as the archive does. Because (a) and (b)
are the same page at the same moment, any selector that matches (a) and not (b) fails because of
stripping alone, with drift held fixed.

Usage: python3 scripts/live_strip_test.py capture   # 3 page loads, saves DOMs under data/live/
       python3 scripts/live_strip_test.py analyse   # no network
Prints counts only; captured pages are untrusted data and are never printed.
"""
from pathlib import Path
import hashlib, json, sys, time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import ucm_selectors_on_archive as U

EXP = ROOT / "experiments" / "2026-09-26_C7c_live-strip-vs-drift"
OUT = EXP / "results" / "live_strip_test.json"
CAP = ROOT / "data" / "live" / "booking"
CHECKIN, CHECKOUT = "2026-11-10", "2026-11-12"
PAGES = {  # UCM's pages (sites/booking/site.py), check-in moved from 2025-07-01 to a future date
    "homepage": "https://www.booking.com/index.html?lang=en-us&selected_currency=EUR",
    "search": f"https://www.booking.com/searchresults.html?ss=Paris&dest_id=-1456928&dest_type=city&checkin={CHECKIN}&checkout={CHECKOUT}",
    "hotel": f"https://www.booking.com/hotel/fr/pullman-paris-tour-eiffel.en-us.html?checkin={CHECKIN}&checkout={CHECKOUT}",
}
CONTENT_SELECTOR = ('[data-testid="property-card"], [data-testid="web-core-property-card"], '
                    '[data-testid="property-description"], [data-testid="review-card"], h2.pp-header__title')
ARCHIVE_ATTRS = {  # the 21 attribute names in the Mind2Web archive (experiments/2026-09-25_1.8_attr-survival)
    "alt", "aria_description", "aria_label", "aria_role", "backend_node_id", "bounding_box_rect", "class",
    "data_pw_testid_buckeye", "id", "input_checked", "input_value", "is_clickable", "label", "name",
    "option_selected", "placeholder", "role", "text_value", "title", "type", "value"}


def capture():
    from playwright.sync_api import sync_playwright
    CAP.mkdir(parents=True, exist_ok=True)
    meta = {}
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        ctx = b.new_context(locale="en-US", viewport={"width": 1366, "height": 768})
        for name, url in PAGES.items():
            pg = ctx.new_page()
            t0 = time.time()
            status, note = None, ""
            try:
                r = pg.goto(url, wait_until="networkidle", timeout=45000)
                status = r.status if r else None
            except Exception as e:
                note = f"goto: {type(e).__name__}"
            try:
                pg.wait_for_selector(CONTENT_SELECTOR, timeout=15000)
                content_found = True
            except Exception:
                content_found = False
            pg.wait_for_timeout(5000)
            html = pg.content()
            f = CAP / f"{name}_{time.strftime('%Y%m%d')}.html"
            f.write_text(html)
            meta[name] = {"http_status": status, "final_url_path": pg.url.split("?")[0], "content_selector_found": content_found,
                          "bytes": len(html.encode()), "sha256": hashlib.sha256(html.encode()).hexdigest(),
                          "file": str(f.relative_to(ROOT)), "seconds": round(time.time() - t0, 1), "note": note,
                          "captured_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            pg.close()
        b.close()
    (CAP / "capture_meta.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps({k: {x: v[x] for x in ("http_status", "final_url_path", "content_selector_found", "bytes")} for k, v in meta.items()}, indent=1))


def strip(tree):
    """Reduce every element to the archive's attribute names, renaming '-' to '_' first."""
    for el in tree.iter():
        if not isinstance(el.tag, str):
            continue
        items = list(el.attrib.items())
        el.attrib.clear()
        for k, v in items:
            k2 = k.replace("-", "_").lower()
            if k2 in ARCHIVE_ATTRS:
                el.set(k2, v)
    return tree


def count(css_text, trees):
    from lxml.cssselect import CSSSelector
    try:
        css = CSSSelector(css_text)
    except Exception:
        return None
    return [len(css(t)) for t in trees]


def analyse():
    from lxml import html as LH
    meta = json.loads((CAP / "capture_meta.json").read_text())
    live, stripped, testids = {}, {}, {}
    for name, m in meta.items():
        raw = (ROOT / m["file"]).read_text()
        live[name] = LH.fromstring(raw)
        testids[name] = sum(1 for el in live[name].iter() if isinstance(el.tag, str) and el.get("data-testid") is not None)
        stripped[name] = strip(LH.fromstring(raw))
    names = sorted(live)
    classes_live = {}
    for t in live.values():
        for el in t.iter():
            if isinstance(el.tag, str):
                for c in (el.get("class") or "").split():
                    classes_live[c] = classes_live.get(c, 0) + 1

    rows, errors = {}, 0
    for s in U.load_sets():
        if s["site"] != "booking":
            continue
        for sel in s["selectors"]:
            src = "hand" if s["source"] == "hand" else "llm"
            if sel in rows:
                rows[sel]["hand"] = rows[sel]["hand"] or src == "hand"
                continue
            a = count(sel, [live[n] for n in names])
            b1 = count(sel, [stripped[n] for n in names])
            b2 = count(U.underscore(sel), [stripped[n] for n in names])
            if a is None:
                errors += 1
                continue
            b = [max(x or 0, y or 0) for x, y in zip(b1 or [0] * len(names), b2 or [0] * len(names))]
            rows[sel] = {"selector": sel, "hand": src == "hand", **U.deps(sel),
                         "live_nodes": dict(zip(names, a)), "stripped_nodes": dict(zip(names, b))}
    for r in rows.values():
        r["matches_live"] = sum(r["live_nodes"].values()) > 0
        r["matches_stripped"] = sum(r["stripped_nodes"].values()) > 0

    def block(xs):
        live_m = [r for r in xs if r["matches_live"]]
        dead = [r for r in live_m if not r["matches_stripped"]]
        return {"selectors": len(xs), "match_live": len(live_m),
                "of_those_match_nothing_after_strip": len(dead),
                "share_disabled_by_strip_pct": round(100 * len(dead) / len(live_m), 1) if live_m else None,
                "survive_strip": sorted(r["selector"] for r in live_m if r["matches_stripped"]),
                "live_matching_use_data_attr": sum(1 for r in live_m if r["data_attr"])}

    hand = [r for r in rows.values() if r["hand"]]
    llm = [r for r in rows.values() if not r["hand"]]
    hashed = sorted({c for r in rows.values() for c in r["hashed_classes"]})
    res = {"capture": {n: {k: meta[n][k] for k in ("http_status", "final_url_path", "content_selector_found", "bytes", "sha256", "captured_utc")}
                       for n in names},
           "elements_with_data_testid_live": testids,
           "selector_parse_errors": errors,
           "hand": block(hand), "llm": block(llm), "pooled": block(hand + llm),
           "hashed_class_tokens": {"n": len(hashed), "present_live": sum(1 for c in hashed if classes_live.get(c)),
                                   "present_live_list": sorted(c for c in hashed if classes_live.get(c))},
           "decay_hand_vs_ucm_captures": {"ucm_captures_match": 25, "live_today_match": block(hand)["match_live"]}}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump({"summary": res, "selectors": list(rows.values())}, open(OUT, "w"), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    {"capture": capture, "analyse": analyse}[sys.argv[1]]()

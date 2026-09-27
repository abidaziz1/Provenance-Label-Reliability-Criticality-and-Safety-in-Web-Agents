"""Selector scoring, v2. Fixes the two scoring defects the audit found.

D1  v1 scored a prediction by whether each ground-truth region was "covered" by
    some predicted selector. The selector `body` covers everything, so it scored
    P = R = F1 = 1.00 on a page with nav, a button and one review. Overmasking was
    never charged. v2 scores at node level over the masked SUBTREE and reports an
    explicit overmask ratio, so a degenerate prediction is visibly bad.

D2  v1 accepted only bare selector strings. The official Prismata/UCM output shape
    is an object, e.g. {"css_selector": ".review", "reason": ...}. v1 silently
    produced TP 0 / FP 0 / FN 1 on a perfectly valid prediction. v2 normalizes the
    known shapes and RAISES on an unrecognized one rather than discarding it.
"""
import re
from lxml import html as LH
try:
    from lxml.cssselect import CSSSelector
    HAVE_CSS = True
except Exception:
    HAVE_CSS = False

SEL_KEYS = ('css_selector', 'cssSelector', 'selector', 'css', 'xpath', 'x_path', 'path')

class MalformedPrediction(ValueError):
    pass

def normalize_predictions(pred):
    """-> list of (kind, selector_string). Raises MalformedPrediction on anything
    it cannot interpret, instead of silently dropping it."""
    out = []
    def one(p):
        if p is None: return
        if isinstance(p, str):
            s = p.strip()
            if not s: return
            out.append(('xpath' if s.startswith(('/', '(')) else 'css', s)); return
        if isinstance(p, dict):
            for k in SEL_KEYS:
                if k in p and isinstance(p[k], str) and p[k].strip():
                    s = p[k].strip()
                    kind = 'xpath' if ('xpath' in k.lower() or s.startswith(('/', '('))) else 'css'
                    out.append((kind, s)); return
            raise MalformedPrediction(f"dict prediction has no selector key: {sorted(p)[:8]}")
        if isinstance(p, (list, tuple)):
            for q in p: one(q)
            return
        raise MalformedPrediction(f"unsupported prediction type {type(p).__name__}")
    one(pred)
    return out

def _match(tree, kind, sel):
    try:
        if kind == 'xpath':
            res = tree.xpath(sel)
        elif HAVE_CSS:
            res = CSSSelector(sel)(tree)
        else:
            res = tree.cssselect(sel)
    except Exception:
        return []
    return [e for e in res if hasattr(e, 'tag') and isinstance(e.tag, str)]

def _subtree(els):
    s = set()
    for e in els:
        s.add(id(e))
        for d in e.iterdescendants():
            if isinstance(d.tag, str): s.add(id(d))
    return s

def score(tree, truth_regions, predictions, strict=True):
    """truth_regions: list of elements that are the roots of true untrusted regions.
    predictions: str | dict | list of either. Returns node-level P/R/F1 plus the
    overmask ratio and the region-level numbers v1 reported.

    NOTE: lxml hands out element PROXIES on demand and frees them when the last
    reference drops, after which CPython happily reuses the id(). Comparing id()
    across two separately-built element sets is therefore unsound unless every
    proxy is pinned. `_pin` holds one reference to every element for the whole
    call. The first version of this function did not, and scored `nav` at recall
    0.667 against a disjoint `.review` ground truth."""
    _pin = [e for e in tree.iter() if isinstance(e.tag, str)]
    all_ids = {id(e) for e in _pin}
    T = _subtree(truth_regions)
    malformed = 0
    try:
        norm = normalize_predictions(predictions)
    except MalformedPrediction:
        if strict: raise
        norm, malformed = [], 1

    matched = []
    unmatched_selectors = 0
    for kind, sel in norm:
        m = _match(tree, kind, sel)
        if not m: unmatched_selectors += 1
        matched.extend(m)
    M = _subtree(matched)

    tp, fp, fn = len(M & T), len(M - T), len(T - M)
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else (1.0 if not T else 0.0)
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0

    mids = {id(e) for e in matched}
    region_hit = sum(1 for r in truth_regions
                     if id(r) in mids or any(id(a) in mids for a in r.iterancestors()))
    r_prec = region_hit / len(matched) if matched else 0.0
    r_rec = region_hit / len(truth_regions) if truth_regions else 0.0
    r_f1 = 2 * r_prec * r_rec / (r_prec + r_rec) if (r_prec + r_rec) else 0.0

    return dict(
        precision=round(prec, 4), recall=round(rec, 4), f1=round(f1, 4),
        tp=tp, fp=fp, fn=fn,
        overmask_ratio=round(len(M) / len(all_ids), 4) if all_ids else 0.0,
        truth_ratio=round(len(T) / len(all_ids), 4) if all_ids else 0.0,
        n_selectors=len(norm), n_unmatched_selectors=unmatched_selectors,
        malformed=malformed,
        v1_region_f1=round(r_f1, 4), v1_region_precision=round(r_prec, 4),
        v1_region_recall=round(r_rec, 4),
        _pinned=len(_pin),
    )

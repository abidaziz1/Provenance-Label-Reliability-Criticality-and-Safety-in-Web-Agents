"""C1 robustness (task N0.2, pre-registered in experiments/2026-09-25_N0.2_c1-robustness/).

Recounts Prismata-style criticality on the 57-site Mind2Web frame under the confounds the novelty
audit raised: unit granularity, the "non-hidden" filter, and the "onclick handler" clause.

Prismata's stated test (§3): an untrusted path instance is critical if it "contain[s] an actionable
descendant", an actionable element being "a non-hidden form control, a link, a label target, an
element with an interactive ARIA role, an onclick handler, an editable region, or a tabindex".

Visibility comes from Mind2Web's captured rendering: every node carries bounding_box_rect, and
"-1,-1,-1,-1" marks a node that was not rendered. The archive strips onclick attributes but keeps
the browser-computed is_clickable flag, used here as a variant of the onclick clause.
"""
from pathlib import Path
import collections, gc, json, sys, time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import pipeline_v2 as P
from lxml import html as LH

OUT = ROOT / "experiments" / "2026-09-25_N0.2_c1-robustness" / "results" / "c1_robustness.json"
FILES = [ROOT / "data" / "mind2web" / "data" / "train" / f for f in ("train_0.json", "train_1.json", "train_10.json")]
PER_SITE = 3
BLOCK_TAGS = {'div', 'li', 'article', 'section', 'tr', 'td', 'p', 'ul', 'ol', 'table',
              'dl', 'dd', 'dt', 'blockquote', 'figure', 'aside', 'form', 'main', 'header', 'footer'}
ARIA_INTERACTIVE = {'button', 'link', 'textbox', 'checkbox', 'menuitem', 'tab', 'combobox', 'radio',
                    'switch', 'slider', 'spinbutton', 'searchbox', 'menuitemcheckbox',
                    'menuitemradio', 'option', 'treeitem', 'gridcell'}
FORM_CONTROLS = {'input', 'select', 'textarea', 'button'}


def tag(el):
    return el.tag.lower() if isinstance(el.tag, str) else ''


def clause_attr(el, label_targets):
    t = tag(el)
    if t in FORM_CONTROLS and not (t == 'input' and (el.get('type') or '').lower() == 'hidden'):
        return 'formcontrol'
    if t == 'a':
        return 'link'
    if id(el) in label_targets:
        return 'labeltarget'
    if (P.gattr(el, 'role') or '').lower() in ARIA_INTERACTIVE:
        return 'ariarole'
    for k in ('onclick', 'onmousedown', 'onmouseup'):
        if P.gattr(el, k):
            return 'onclick'
    if P.gattr(el, 'contenteditable') is not None and (P.gattr(el, 'contenteditable') or '').lower() in ('', 'true'):
        return 'editable'
    tb = P.gattr(el, 'tabindex')
    if tb is not None and tb.strip().isdigit():
        return 'tabindex'
    return None


def clickable(el):
    v = el.get('is_clickable')
    return v is not None and v.strip().lower() not in ('false', '0', '')


def visible(el):
    """Strict: rendered with positive size, and not hidden by attribute. Missing geometry counts as hidden."""
    r = el.get('bounding_box_rect')
    if not r:
        return False
    try:
        x, y, w, h = (float(v) for v in r.split(','))
    except ValueError:
        return False
    if (x, y, w, h) == (-1, -1, -1, -1) or w <= 0 or h <= 0:
        return False
    if el.get('hidden') is not None or (P.gattr(el, 'aria-hidden') or '').lower() == 'true':
        return False
    if tag(el) == 'input' and (el.get('type') or '').lower() == 'hidden':
        return False
    return True


def ancestors(elems, include_self):
    seen = set()
    for a in elems:
        n = a if include_self else a.getparent()
        while n is not None and id(n) not in seen:
            seen.add(id(n))
            n = n.getparent()
    return seen


def analyse(raw_html, site):
    try:
        tree = LH.fromstring(raw_html)
    except Exception:
        return None
    P.deep_parse(tree)
    nodes = tree.xpath('//*')
    if not nodes:
        return None
    host = P.host_for(site)
    seeds = {}
    for el in nodes:
        lab, _ = P.gt_provenance(el, host)
        if lab:
            seeds[el] = lab
    prov = {}
    for el in nodes:
        if el in seeds:
            prov[el] = seeds[el]
        else:
            p_ = el.getparent()
            prov[el] = prov[p_] if (p_ is not None and p_ in prov) else 'D'
    byid, label_targets = {}, set()
    for el in nodes:
        if el.get('id'):
            byid.setdefault(el.get('id'), el)
    for el in nodes:
        if tag(el) == 'label':
            f = P.gattr(el, 'for')
            if f and f in byid:
                label_targets.add(id(byid[f]))

    vis = {id(el): visible(el) for el in nodes}
    act = {'attr': [], 'attr+click': []}
    for el in nodes:
        c = clause_attr(el, label_targets)
        if c:
            act['attr'].append(el)
        if c or clickable(el):
            act['attr+click'].append(el)
    anc = {}
    for aname, elems in act.items():
        for vname, keep in (('any', lambda e: True), ('nonhidden', lambda e: vis[id(e)])):
            chosen = [e for e in elems if keep(e)]
            anc[(aname, vname, 'desc')] = ancestors(chosen, include_self=False)
            anc[(aname, vname, 'self')] = ancestors(chosen, include_self=True)

    U = [el for el in nodes if prov[el] != 'D']
    Uset = {id(e) for e in U}
    G = {
        'G0_region': [el for el in U if el.getparent() is None or prov.get(el.getparent(), 'D') == 'D'],
        'G2_block': [el for el in U if tag(el) in BLOCK_TAGS],
        'G3_node': U,
        'G4_leafpath': [el for el in U if not any(id(ch) in Uset for ch in el if isinstance(ch.tag, str))],
        'G5_textcarrier': [el for el in U if (el.text or '').strip()],
    }
    G['G1_region_plus_items'] = list(G['G0_region']) + [
        ch for r in G['G0_region'] for ch in r if isinstance(ch.tag, str) and id(ch) in Uset]
    out = {}
    for gname, S in G.items():
        Svis = [e for e in S if vis[id(e)]]
        cell = {'n': len(S), 'n_vis': len(Svis)}
        for (aname, vname, rule), A in anc.items():
            cell[f'{aname}|{vname}|{rule}|all'] = sum(1 for e in S if id(e) in A)
            cell[f'{aname}|{vname}|{rule}|visunits'] = sum(1 for e in Svis if id(e) in A)
        out[gname] = cell
    return {'G': out, 'n_act_attr': len(act['attr']), 'n_act_click': len(act['attr+click']),
            'n_act_attr_vis': sum(1 for e in act['attr'] if vis[id(e)])}


def main():
    bysite = collections.defaultdict(list)
    for f in FILES:
        for t in json.load(open(f)):
            bysite[t['website']].append(t)
        gc.collect()
    selected = [x for s in sorted(bysite) for x in sorted(bysite[s], key=lambda t: t['annotation_id'])[:PER_SITE]]
    del bysite
    gc.collect()
    print(f"frame: {len(selected)} trajectories over {len({t['website'] for t in selected})} sites", flush=True)
    rows, t0 = [], time.time()
    for i, t in enumerate(selected):
        for step, a in enumerate(t['actions']):
            r = analyse(a['raw_html'], t['website'])
            if r:
                r.update(site=t['website'], task=t['annotation_id'], step=step)
                rows.append(r)
        if (i + 1) % 25 == 0:
            print(f"  [{i+1}/{len(selected)}] obs={len(rows)} ({time.time()-t0:.0f}s)", flush=True)
    agg = collections.defaultdict(collections.Counter)
    for r in rows:
        for g, cell in r['G'].items():
            agg[g].update(cell)
    pages = len(rows)
    summary = {}
    for g, c in agg.items():
        s = {'units': c['n'], 'units_per_page': round(c['n'] / pages, 2),
             'visible_units': c['n_vis'], 'visible_units_per_page': round(c['n_vis'] / pages, 2)}
        for k, v in c.items():
            if '|' in k:
                denom = c['n_vis'] if k.endswith('|visunits') else c['n']
                s[k] = round(100 * v / denom, 2) if denom else None
        summary[g] = s
    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump({'pages': pages, 'summary': summary,
               'actionable_per_page': {'attr': round(sum(r['n_act_attr'] for r in rows) / pages, 1),
                                       'attr_nonhidden': round(sum(r['n_act_attr_vis'] for r in rows) / pages, 1),
                                       'attr+click': round(sum(r['n_act_click'] for r in rows) / pages, 1)}},
              open(OUT, 'w'), indent=1)
    print(f"\n{pages} observations in {time.time()-t0:.0f}s")
    hdr = ['attr|any|desc|all', 'attr|nonhidden|desc|all', 'attr|nonhidden|desc|visunits',
           'attr+click|nonhidden|desc|visunits', 'attr|nonhidden|self|visunits']
    print(f"{'unit':22s} {'units/pg':>8s} {'vis/pg':>7s} " + " ".join(f"{h:>28s}" for h in hdr))
    for g in ['G0_region', 'G1_region_plus_items', 'G2_block', 'G5_textcarrier', 'G4_leafpath', 'G3_node']:
        s = summary[g]
        print(f"{g:22s} {s['units_per_page']:8.2f} {s['visible_units_per_page']:7.2f} " +
              " ".join(f"{s[h]:27.2f}%" for h in hdr))
    print("Prismata's Mind2Web ceiling: 1.66% (1,086 / 65,416); published pooled rate 1.2%; 23.10 units per page")


if __name__ == '__main__':
    main()


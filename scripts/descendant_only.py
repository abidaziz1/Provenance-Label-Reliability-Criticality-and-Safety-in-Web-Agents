"""Prismata's sentence says untrusted paths that "contain an actionable DESCENDANT".
Our published claim-1 counted a region as critical if it contained an actionable
descendant OR was itself actionable. On the 16-site frame that single choice is
worth 31.4 percentage points (46.45% vs 77.83%). This computes the like-for-like,
descendants-only figure on the 57-site frame under both pipelines."""
from pathlib import Path as _Path
ROOT = _Path(__file__).resolve().parents[1]
import json, sys, time, gc, collections, os
sys.path.insert(0, str(ROOT / 'src'))
import pipeline_v2 as P
from pipeline_v2 import *
from lxml import html as LH

V1 = os.environ.get('V1_PARSER', '0') == '1'
if V1: P.set_fixes(literal_markup=False, splice_count=False, attr_norm=False,
                   same_origin=False, cap_aware_label=False)
TAG = 'v1' if V1 else 'v2'
ARIA = {'button','link','textbox','checkbox','menuitem','tab','combobox','radio','switch',
        'slider','spinbutton','searchbox','menuitemcheckbox','menuitemradio','option',
        'treeitem','gridcell'}
FC = {'input','select','textarea','button'}
def act_pris(el):
    t = (el.tag if isinstance(el.tag, str) else '').lower()
    if t in FC and not (t == 'input' and (el.get('type') or '').lower() == 'hidden'): return True
    if t == 'a': return True
    if (gattr(el, 'role') or '').lower() in ARIA: return True
    if gattr(el, 'onclick'): return True
    tb = gattr(el, 'tabindex')
    return bool(tb and tb.strip().isdigit())

FILES = [f'{ROOT}/data/mind2web/data/train/train_{i}.json' for i in (0, 1, 10)]
bysite = collections.defaultdict(list)
for f in FILES:
    for t in json.load(open(f)): bysite[t['website']].append(t)
    gc.collect()
selected = [x for s in sorted(bysite) for x in sorted(bysite[s], key=lambda t: t['annotation_id'])[:3]]
keep16 = {t['task_id'] for t in json.load(open(f'{ROOT}/results/legacy/corpus.json'))}
del bysite; gc.collect()
c = collections.Counter(); t0 = time.time()
for i, t in enumerate(selected):
    in16 = t['annotation_id'] in keep16
    for a in t['actions']:
        try: tree = LH.fromstring(a['raw_html'])
        except Exception: continue
        deep_parse(tree); host = host_for(t['website']); nodes = tree.xpath('//*')
        if not nodes: continue
        seeds = {}
        for el in nodes:
            l, _ = gt_provenance(el, host)
            if l: seeds[el] = l
        prov = {}
        for el in nodes:
            if el in seeds: prov[el] = seeds[el]
            else:
                p_ = el.getparent()
                prov[el] = prov[p_] if (p_ is not None and p_ in prov) else 'D'
        for r in [el for el in nodes if prov[el] != 'D'
                  and (el.getparent() is None or prov.get(el.getparent(), 'D') == 'D')]:
            d_ours = any(is_actionable(d) for d in r.iterdescendants())
            d_pris = any(act_pris(d) for d in r.iterdescendants() if isinstance(d.tag, str))
            for pre, ok in (('57', True), ('16', in16)):
                if not ok: continue
                c[pre + '_n'] += 1
                c[pre + '_desc_ours'] += d_ours; c[pre + '_desc_pris'] += d_pris
                c[pre + '_self_ours'] += (d_ours or is_actionable(r))
                c[pre + '_self_pris'] += (d_pris or act_pris(r))
    if (i + 1) % 30 == 0: print(f"  [{i+1}/{len(selected)}] ({time.time()-t0:.0f}s)", flush=True)
print(f"\n[{TAG}] criticality, descendants-only vs including the region root")
print(f"{'frame':10s} {'regions':>8s} {'desc(ours)':>11s} {'desc(theirs)':>13s} "
      f"{'+root(ours)':>12s} {'+root(theirs)':>14s}")
for pre, nm in (('57', '57-site'), ('16', '16-site')):
    n = c[pre + '_n']
    print(f"{nm:10s} {n:8,d} {100*c[pre+'_desc_ours']/n:10.2f}% "
          f"{100*c[pre+'_desc_pris']/n:12.2f}% {100*c[pre+'_self_ours']/n:11.2f}% "
          f"{100*c[pre+'_self_pris']/n:13.2f}%")
json.dump(dict(c), open(f'{ROOT}/results/descendant_only_{TAG}.json', 'w'))

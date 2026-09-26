"""Definitional reconciliation: why does Prismata report 1.2% where we measure 74.65%?

Prismata, Section 3, verbatim:
  "Only 1,086 of the 90,408 untrusted paths (1.2%) contain an actionable descendant,
   an element the agent could click or fill (Fig. 5); the rest are leaves or text-only
   regions that cannot sit above a targetable element. We count a descendant as
   actionable if it is a non-hidden form control, a link, a label target, an element
   with an interactive ARIA role, an onclick handler, an editable region, or a tabindex."

Prismata, Section 1.1, verbatim:
  "of the over 90,000 instances of untrusted content sampled, only 1.2% lay on a
   critical path to an interactable element"

Prismata, Section 2.1, verbatim:
  "Prismata traces the critical path: the full HTML ancestor chain from the DOM root
   to that element."

Their Mind2Web half: 65,416 instances over 2,832 pages = 23.10 instances per page.
Ours: 6,159 maximal regions over 1,163 observations = 5.30 per observation.

This script walks a ladder of granularities and actionability definitions and reports,
for each, (units per page, % with an actionable descendant-or-self, % on the task
target's root path). The rung that lands simultaneously on ~23 units/page and ~1.2%
is the definition Prismata is using.
"""
from pathlib import Path as _Path
ROOT = _Path(__file__).resolve().parents[1]
import json, sys, time, gc, collections, os, re
sys.path.insert(0, str(ROOT / 'src'))
import pipeline_v2 as P
from lxml import html as LH

V1_PARSER = os.environ.get('V1_PARSER', '0') == '1'
OFF = [k for k in os.environ.get('FIX_OFF', '').split(',') if k]
if V1_PARSER:
    P.set_fixes(literal_markup=False, splice_count=False, attr_norm=False,
                same_origin=False, cap_aware_label=False)
    TAG = 'v1'
elif OFF:
    P.set_fixes(**{k: False for k in OFF})
    TAG = 'no_' + '_'.join(OFF)
else:
    TAG = 'v2'
SPLICE = collections.Counter()

FILES = [f'{ROOT}/data/mind2web/data/train/train_0.json',
         f'{ROOT}/data/mind2web/data/train/train_1.json',
         f'{ROOT}/data/mind2web/data/train/train_10.json']
PER_SITE = 3

BLOCK_TAGS = {'div','li','article','section','tr','td','p','ul','ol','table',
              'dl','dd','dt','blockquote','figure','aside','form','main','header','footer'}
ARIA_INTERACTIVE = {'button','link','textbox','checkbox','menuitem','tab','combobox','radio',
                    'switch','slider','spinbutton','searchbox','menuitemcheckbox',
                    'menuitemradio','option','treeitem','gridcell'}
FORM_CONTROLS = {'input','select','textarea','button'}

def actionable_prismata(el, label_targets):
    """Their stated definition, clause by clause. Returns the clause that fired."""
    t = (el.tag if isinstance(el.tag, str) else '').lower()
    if t in FORM_CONTROLS:
        if t == 'input' and (el.get('type') or '').lower() == 'hidden':
            pass
        else:
            return 'formcontrol'
    if t == 'a': return 'link'
    if id(el) in label_targets: return 'labeltarget'
    if (P.gattr(el, 'role') or '').lower() in ARIA_INTERACTIVE: return 'ariarole'
    for k in ('onclick', 'onmousedown', 'onmouseup'):
        if P.gattr(el, k): return 'onclick'
    ce = (P.gattr(el, 'contenteditable') or '').lower()
    if ce in ('', 'true') and P.gattr(el, 'contenteditable') is not None: return 'editable'
    tb = P.gattr(el, 'tabindex')
    if tb is not None and tb.strip().lstrip('-').isdigit() and not tb.strip().startswith('-'):
        return 'tabindex'
    return None

def anc_or_self_ids(elems):
    seen = set()
    for a in elems:
        n = a
        while n is not None and id(n) not in seen:
            seen.add(id(n)); n = n.getparent()
    return seen

def analyse(raw_html, site, tgt_backend_id):
    try:
        tree = LH.fromstring(raw_html)
    except Exception:
        return None
    _st = P.deep_parse(tree)
    SPLICE['spliced'] += _st.get('spliced', 0)
    SPLICE['nodes_added'] += _st.get('nodes_added', 0)
    SPLICE['skipped_literal'] += _st.get('skipped_literal', 0)
    SPLICE['pages'] += 1
    nodes = tree.xpath('//*')
    if not nodes: return None
    host = P.host_for(site)

    seeds = {}
    for el in nodes:
        lab, rule = P.gt_provenance(el, host)
        if lab: seeds[el] = lab
    prov = {}
    for el in nodes:
        if el in seeds: prov[el] = seeds[el]
        else:
            p_ = el.getparent()
            prov[el] = prov[p_] if (p_ is not None and p_ in prov) else 'D'

    label_targets = set()
    byid = {}
    for el in nodes:
        i = el.get('id')
        if i: byid.setdefault(i, el)
    for el in nodes:
        if isinstance(el.tag, str) and el.tag.lower() == 'label':
            f = P.gattr(el, 'for')
            if f and f in byid: label_targets.add(id(byid[f]))

    act_ours = [el for el in nodes if P.is_actionable(el)]
    clause = collections.Counter()
    act_pris = []
    for el in nodes:
        c = actionable_prismata(el, label_targets)
        if c: clause[c] += 1; act_pris.append(el)

    anc_ours = anc_or_self_ids(act_ours)
    anc_pris = anc_or_self_ids(act_pris)

    tpath = set()
    if tgt_backend_id:
        for el in nodes:
            if el.get('backend_node_id') == tgt_backend_id:
                n = el
                while n is not None:
                    tpath.add(id(n)); n = n.getparent()
                break

    U = [el for el in nodes if prov[el] != 'D']
    Uset = set(id(e) for e in U)

    G = {}
    G['G0_region'] = [el for el in U
                      if el.getparent() is None or prov.get(el.getparent(), 'D') == 'D']
    G['G1_region_plus_items'] = list(G['G0_region']) + [
        ch for r in G['G0_region'] for ch in r
        if isinstance(ch.tag, str) and id(ch) in Uset]
    G['G2_block'] = [el for el in U
                     if isinstance(el.tag, str) and el.tag.lower() in BLOCK_TAGS]
    G['G3_node'] = U
    G['G4_leafpath'] = [el for el in U
                        if not any(id(ch) in Uset for ch in el if isinstance(ch.tag, str))]
    G['G5_textcarrier'] = [el for el in U if (el.text or '').strip()]

    out = {}
    for name, S in G.items():
        out[name] = dict(
            n=len(S),
            crit_ours=sum(1 for e in S if id(e) in anc_ours),
            crit_pris=sum(1 for e in S if id(e) in anc_pris),
            on_target=sum(1 for e in S if id(e) in tpath) if tpath else 0,
        )
    return dict(n_nodes=len(nodes), n_untrusted=len(U),
                n_act_ours=len(act_ours), n_act_pris=len(act_pris),
                has_target=bool(tpath), clause=dict(clause), G=out)

# ---------------------------------------------------------------- frame
bysite = collections.defaultdict(list)
for f in FILES:
    for t in json.load(open(f)): bysite[t['website']].append(t)
    gc.collect()
selected = []
for s in sorted(bysite):
    selected += sorted(bysite[s], key=lambda t: t['annotation_id'])[:PER_SITE]
del bysite; gc.collect()
print(f"[{TAG}] FRAME: {len(selected)} trajectories over "
      f"{len(set(t['website'] for t in selected))} sites", flush=True)

FRAME16 = set(json.load(open(f'{ROOT}/results/legacy/corpus.json'))[0].keys()) if False else None
keep16 = {t['task_id'] for t in json.load(open(f'{ROOT}/results/legacy/corpus.json'))}

rows = []
t0 = time.time()
for i, t in enumerate(selected):
    for step, a in enumerate(t['actions']):
        r = analyse(a['raw_html'], t['website'], P.target_id(a))
        if not r: continue
        r.update(task=t['annotation_id'], site=t['website'], step=step,
                 in16=t['annotation_id'] in keep16, first_step=(step == 0))
        rows.append(r)
    if (i + 1) % 10 == 0:
        print(f"  [{i+1}/{len(selected)}] obs={len(rows)} ({time.time()-t0:.0f}s)", flush=True)

print(f"[{TAG}] deep_parse totals: {dict(SPLICE)}", flush=True)
json.dump(rows, open(f'{ROOT}/results/reconcile_{TAG}.json', 'w'))
print(f"[{TAG}] WROTE {len(rows)} observations in {time.time()-t0:.0f}s", flush=True)

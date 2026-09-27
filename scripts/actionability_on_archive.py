"""Prismata-style criticality when links need an href (task C7b, pre-registered in
experiments/2026-09-26_C7b_actionability-on-archive/).

Prismata §3 counts a descendant as actionable if it is "a non-hidden form control, a link, a label
target, an element with an interactive ARIA role, an onclick handler, an editable region, or a
tabindex". Our rule (`c1_robustness.clause_attr`) counts every <a> as a link. The Mind2Web archive
strips href, onclick, tabindex and contenteditable on all 57 sites (task 1.8), so a count that
requires an href for a link, as a browser does for a hyperlink, sees no links at all on the archive.
This script recomputes the published units under three rules:

  R0_tag             our rule as published: every <a> is a link
  R1_href_required   an <a> is a link only with an href; every other clause unchanged
  R2_href_or_flag    R1, plus any element whose stored is_clickable flag is true

Visibility, labels, frame and units are those of scripts/c1_robustness.py and scripts/unit_ladder.py.
"""
from pathlib import Path
import collections, gc, json, sys, time
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import pipeline_v2 as P
import c1_robustness as C
from lxml import html as LH

OUT = ROOT / "experiments" / "2026-09-26_C7b_actionability-on-archive" / "results" / "actionability_on_archive.json"
SEED, B = 20260925, 10_000
RULES = ("R0_tag", "R1_href_required", "R2_href_or_flag")
UNITS = ("G0_region", "G3_node", "G4_leafpath")


def clause_href(el, label_targets):
    """c1_robustness.clause_attr, except that an <a> is a link only when it carries an href."""
    t = C.tag(el)
    if t in C.FORM_CONTROLS and not (t == 'input' and (el.get('type') or '').lower() == 'hidden'):
        return 'formcontrol'
    if t == 'a' and P.gattr(el, 'href'):
        return 'link'
    if id(el) in label_targets:
        return 'labeltarget'
    if (P.gattr(el, 'role') or '').lower() in C.ARIA_INTERACTIVE:
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
        if C.tag(el) == 'label':
            f = P.gattr(el, 'for')
            if f and f in byid:
                label_targets.add(id(byid[f]))
    vis = {id(el): C.visible(el) for el in nodes}
    U = [el for el in nodes if prov[el] != 'D']
    Uset = {id(e) for e in U}
    G = {
        'G0_region': [el for el in U if el.getparent() is None or prov.get(el.getparent(), 'D') == 'D'],
        'G3_node': U,
        'G4_leafpath': [el for el in U if not any(id(ch) in Uset for ch in el if isinstance(ch.tag, str))],
    }
    r0 = {id(el): C.clause_attr(el, label_targets) for el in nodes}
    r1 = {id(el): clause_href(el, label_targets) for el in nodes}
    rule_of = {
        'R0_tag': lambda el: r0[id(el)] is not None,
        'R1_href_required': lambda el: r1[id(el)] is not None,
        'R2_href_or_flag': lambda el: r1[id(el)] is not None or C.clickable(el),
    }
    out = {'anchors_visible_actionable_R0': sum(1 for el in nodes if vis[id(el)] and r0[id(el)] == 'link'),
           'anchors_with_href': sum(1 for el in nodes if C.tag(el) == 'a' and P.gattr(el, 'href')),
           'anchors': sum(1 for el in nodes if C.tag(el) == 'a'), 'R': {}}
    for rname, is_act in rule_of.items():
        acts = [el for el in nodes if vis[id(el)] and is_act(el)]
        A = C.ancestors(acts, include_self=False)
        cell = {'n_act_vis': len(acts), 'exposed': any(id(u) in A for u in U)}
        for g, S in G.items():
            Svis = [e for e in S if vis[id(e)]]
            cell[g] = (sum(1 for e in Svis if id(e) in A), len(Svis))
        out['R'][rname] = cell
    return out


def site_ci_ratio(num_by_site, den_by_site, seed=SEED, b=B):
    sites = sorted(den_by_site)
    num = np.array([num_by_site[s] for s in sites], float)
    den = np.array([den_by_site[s] for s in sites], float)
    ix = np.random.default_rng(seed).integers(0, len(sites), size=(b, len(sites)))
    m = num[ix].sum(1) / np.maximum(den[ix].sum(1), 1)
    return [round(100 * float(np.percentile(m, 2.5)), 2), round(100 * float(np.percentile(m, 97.5)), 2)]


def main():
    bysite = collections.defaultdict(list)
    for f in C.FILES:
        for t in json.load(open(f)):
            bysite[t['website']].append(t)
        gc.collect()
    selected = [x for s in sorted(bysite) for x in sorted(bysite[s], key=lambda t: t['annotation_id'])[:C.PER_SITE]]
    del bysite
    gc.collect()
    rows, t0 = [], time.time()
    for i, t in enumerate(selected):
        for step, a in enumerate(t['actions']):
            r = analyse(a['raw_html'], t['website'])
            if r:
                r.update(site=t['website'], task=t['annotation_id'], step=step)
                rows.append(r)
        if (i + 1) % 25 == 0:
            print(f"  [{i+1}/{len(selected)}] obs={len(rows)} ({time.time()-t0:.0f}s)", flush=True)
    pages = len(rows)
    res = {'pages': pages, 'tasks': len({r['task'] for r in rows}), 'sites': len({r['site'] for r in rows}),
           'anchors_per_page': round(sum(r['anchors'] for r in rows) / pages, 2),
           'anchors_with_href_total': sum(r['anchors_with_href'] for r in rows),
           'rules': {}}
    for rname in RULES:
        n_act = sum(r['R'][rname]['n_act_vis'] for r in rows)
        rec = {'visible_actionable_per_page': round(n_act / pages, 2)}
        if rname == 'R0_tag':
            rec['anchor_share_of_visible_actionable_pct'] = round(
                100 * sum(r['anchors_visible_actionable_R0'] for r in rows) / n_act, 2)
        for g in UNITS:
            num = collections.Counter()
            den = collections.Counter()
            for r in rows:
                k, n = r['R'][rname][g]
                num[r['site']] += k
                den[r['site']] += n
            rec[f'{g}_crit_visunits_pct'] = round(100 * sum(num.values()) / sum(den.values()), 2)
            rec[f'{g}_crit_visunits_ci95_site'] = site_ci_ratio(num, den)
        e_num, e_den = collections.Counter(), collections.Counter()
        task_flag = {}
        for r in rows:
            e = r['R'][rname]['exposed']
            e_num[r['site']] += e
            e_den[r['site']] += 1
            task_flag[(r['site'], r['task'])] = task_flag.get((r['site'], r['task']), False) or e
        t_num, t_den = collections.Counter(), collections.Counter()
        for (s, _), f in task_flag.items():
            t_num[s] += f
            t_den[s] += 1
        rec['page_exposed_pct'] = round(100 * sum(e_num.values()) / pages, 2)
        rec['page_exposed_ci95_site'] = site_ci_ratio(e_num, e_den)
        rec['task_exposed_pct'] = round(100 * sum(t_num.values()) / len(task_flag), 2)
        rec['task_exposed_ci95_site'] = site_ci_ratio(t_num, t_den)
        res['rules'][rname] = rec
    r0, r1 = res['rules']['R0_tag'], res['rules']['R1_href_required']
    res['R1_over_R0'] = {g: (round(r1[f'{g}_crit_visunits_pct'] / r0[f'{g}_crit_visunits_pct'], 3)
                             if r0[f'{g}_crit_visunits_pct'] else None) for g in UNITS}
    res['R1_over_R0']['page_exposed'] = round(r1['page_exposed_pct'] / r0['page_exposed_pct'], 3)
    # Exploratory, added after the pre-registered run (README, deviations): a site-cluster interval
    # for the primary ratio, resampling sites and recomputing both rates on the same draw.
    num0, num1 = collections.Counter(), collections.Counter()
    for r in rows:
        num0[r['site']] += r['R']['R0_tag']['G3_node'][0]
        num1[r['site']] += r['R']['R1_href_required']['G3_node'][0]
    sites = sorted(num0)
    a0 = np.array([num0[s] for s in sites], float); a1 = np.array([num1[s] for s in sites], float)
    ix = np.random.default_rng(SEED).integers(0, len(sites), size=(B, len(sites)))
    ratio = a1[ix].sum(1) / np.maximum(a0[ix].sum(1), 1)
    res['exploratory_G3_ratio_ci95_site'] = [round(float(np.percentile(ratio, 2.5)), 3),
                                             round(float(np.percentile(ratio, 97.5)), 3)]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump(res, open(OUT, 'w'), indent=1)
    print(json.dumps(res, indent=1))
    print(f"done in {time.time()-t0:.0f}s")


if __name__ == '__main__':
    main()

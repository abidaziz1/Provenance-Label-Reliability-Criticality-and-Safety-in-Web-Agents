"""Exposure to untrusted content per interactive element, page, task and target (task N0.2 follow-up).

Pre-registered in experiments/2026-09-25_N0.2_unit-ladder/. Same frame, labels and actionability
definition as scripts/c1_robustness.py; see that file for the non-hidden rule.
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

OUT = ROOT / "experiments" / "2026-09-25_N0.2_unit-ladder" / "results" / "unit_ladder.json"
SEED, B = 20260925, 10_000


def analyse(raw_html, site, target_id):
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

    def untrusted_ancestor(el):
        n = el.getparent()
        while n is not None:
            if prov.get(n, 'D') != 'D':
                return True
            n = n.getparent()
        return False

    out = {}
    for variant in ('attr', 'attr+click'):
        acts = [el for el in nodes if C.visible(el) and
                (C.clause_attr(el, label_targets) or (variant == 'attr+click' and C.clickable(el)))]
        inside = sum(1 for el in acts if untrusted_ancestor(el))
        self_or_inside = sum(1 for el in acts if prov[el] != 'D' or untrusted_ancestor(el))
        out[variant] = dict(n_act=len(acts), inside=inside, self_or_inside=self_or_inside)
    tgt = None
    if target_id:
        for el in nodes:
            if el.get('backend_node_id') == target_id:
                tgt = prov[el] != 'D' or untrusted_ancestor(el)
                break
    U = [el for el in nodes if prov[el] != 'D']
    Uset = {id(e) for e in U}
    leaves = [el for el in U if not any(id(ch) in Uset for ch in el if isinstance(ch.tag, str))]
    return dict(v=out, target_inside=tgt, n_untrusted=len(U), n_leaves=len(leaves))


def site_ci(values_by_site, seed=SEED, b=B):
    sites = sorted(values_by_site)
    sums = np.array([sum(values_by_site[s]) for s in sites], dtype=float)
    cnts = np.array([len(values_by_site[s]) for s in sites], dtype=float)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(sites), size=(b, len(sites)))
    means = sums[idx].sum(1) / cnts[idx].sum(1)
    return [round(100 * float(np.percentile(means, 2.5)), 2), round(100 * float(np.percentile(means, 97.5)), 2)]


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
            r = analyse(a['raw_html'], t['website'], P.target_id(a))
            if r:
                r.update(site=t['website'], task=t['annotation_id'], step=step)
                rows.append(r)
        if (i + 1) % 25 == 0:
            print(f"  [{i+1}/{len(selected)}] obs={len(rows)} ({time.time()-t0:.0f}s)", flush=True)
    res = {'pages': len(rows), 'tasks': len({r['task'] for r in rows}), 'sites': len({r['site'] for r in rows})}
    for variant in ('attr', 'attr+click'):
        n_act = sum(r['v'][variant]['n_act'] for r in rows)
        inside = sum(r['v'][variant]['inside'] for r in rows)
        self_in = sum(r['v'][variant]['self_or_inside'] for r in rows)
        page_by_site, task_flag = collections.defaultdict(list), {}
        for r in rows:
            exposed = r['v'][variant]['inside'] > 0
            page_by_site[r['site']].append(exposed)
            task_flag[(r['site'], r['task'])] = task_flag.get((r['site'], r['task']), False) or exposed
        task_by_site = collections.defaultdict(list)
        for (s, _), f in task_flag.items():
            task_by_site[s].append(f)
        pages_exposed = sum(sum(v) for v in page_by_site.values())
        tasks_exposed = sum(task_flag.values())
        res[variant] = {
            'actionable_elements': n_act,
            'element_inside_untrusted_pct': round(100 * inside / n_act, 2),
            'element_self_or_inside_untrusted_pct': round(100 * self_in / n_act, 2),
            'page_exposed_pct': round(100 * pages_exposed / len(rows), 2),
            'page_exposed_ci95_site': site_ci(page_by_site),
            'task_exposed_pct': round(100 * tasks_exposed / len(task_flag), 2),
            'task_exposed_ci95_site': site_ci(task_by_site),
            'sites_with_any_exposed_page': sum(1 for v in page_by_site.values() if any(v)),
        }
    tg = [r['target_inside'] for r in rows if r['target_inside'] is not None]
    res['target_inside_untrusted_pct'] = round(100 * sum(tg) / len(tg), 2)
    res['observations_with_resolvable_target'] = len(tg)
    res['untrusted_leaves_per_page'] = round(sum(r['n_leaves'] for r in rows) / len(rows), 2)
    res['prismata_published_upper_bounds'] = {
        'critical_paths_per_page_max_pct': round(100 * 1086 / 5664, 2),
        'case3_paths_per_page_max_pct': round(100 * 94 / 5664, 2),
        'note': 'if every critical (Case-3) path sat on a different page of Prismata\'s 5,664 DOMs',
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump(res, open(OUT, 'w'), indent=1)
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()

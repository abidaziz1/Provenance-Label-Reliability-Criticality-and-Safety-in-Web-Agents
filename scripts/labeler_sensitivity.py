"""Labeler sensitivity of the exposure rates (task N0.3b).

Commits the analysis the 25 Sep adversarial review ran from its scratchpad
(`research/audit/2026-09-25_adversarial_C1prime_C4.md`, appendix `c1p_attr.py`), with the
logic unchanged. It re-implements `pipeline_v2.gt_provenance` so that every rule firing on a
node is kept in priority order, then recomputes the unit-ladder exposure rates with families
of rules removed (variants V0 to V5), and attributes each exposed control to its seed rule.

Frame and actionability are the same as scripts/unit_ladder.py. Output:
experiments/2026-09-25_N0.3b_labeler-sensitivity/results/labeler_sensitivity.json
(or the path given as the only argument).
"""
from pathlib import Path
import collections, gc, json, re, sys, time
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
import pipeline_v2 as P
import c1_robustness as C
from lxml import html as LH

OUT = ROOT / "experiments" / "2026-09-25_N0.3b_labeler-sensitivity" / "results" / "labeler_sensitivity.json"
SEED, B = 20260925, 10_000


def comb(p):
    p = sorted(p, key=len, reverse=True)
    return re.compile(r'(?:^|[-.])(' + '|'.join(re.escape(x) for x in p) + r')(?:$|[-.0-9])')


GEN = {'question', 'answer', 'qa', 'feedback'}
EXT = comb([p for p, _ in P.EXTERNAL])
UCORE = comb([p for p, _ in P.UGC if p not in GEN])
UGEN = comb(sorted(GEN))
HOST = comb([p for p, _ in P.HOSTED])
DEV = comb([p for p, _ in P.DEV])


def candidates(el, host):
    """Every provenance rule that fires on el, in gt_provenance's priority order: (label, rule, source)."""
    tag = el.tag.lower() if isinstance(el.tag, str) else ''
    c = []
    if tag in ('iframe', 'embed', 'object'):
        src = P.gattr(el, 'src') or P.gattr(el, 'data_src') or el.get('data') or ''
        if P.AD_HOST.search(src):
            c.append(('E', 'iframe:adnetwork', 'src'))
        elif P._frame_origin(src, host) == 'cross':
            c.append(('E', 'iframe:crossorigin', 'src'))
    toks = [(t, 'class') for t in P.class_tokens(el)]
    i = (el.get('id') or '').lower()
    if i:
        toks.append((i, 'id'))
    for k, v in el.attrib.items():
        if (k.startswith('data_') or k.startswith('data-')) and isinstance(v, str) and len(v) < 60:
            toks.append((v.lower(), 'data:' + k))
    for t, s in toks:
        m = EXT.search(t)
        if m:
            c.append(('E', 'ad:' + m.group(1), s))
    for k, v in el.attrib.items():
        if isinstance(v, str) and P.AD_HOST.search(v):
            c.append(('E', 'attr:adnetwork', 'attr:' + k))
            break
    for t, s in toks:
        m = UCORE.search(t)
        if m:
            c.append(('U', 'ugc:' + m.group(1), s))
        m = UGEN.search(t)
        if m:
            c.append(('U', 'ugcgen:' + m.group(1), s))
    for t, s in toks:
        m = HOST.search(t)
        if m:
            c.append(('H', 'hosted:' + m.group(1), s))
    if tag in P.DEV_TAGS:
        c.append(('D', 'tag:' + tag, 'tag'))
    role = (P.gattr(el, 'role') or '').lower()
    if role in P.DEV_ROLES:
        c.append(('D', 'role:' + role, 'role'))
    for t, s in toks:
        m = DEV.search(t)
        if m:
            c.append(('D', 'dev:' + m.group(1), s))
            break
    return c


VARS = {
    'V0_base': lambda c: True,
    'V1_no_data_attr_tokens': lambda c: not c[2].startswith('data:'),
    'V2_no_hosted_H': lambda c: c[0] != 'H',
    'V3_no_generic_ugc(question/answer/qa/feedback)': lambda c: not c[1].startswith('ugcgen:'),
    'V4_strict(V1+V2+V3)': lambda c: (not c[2].startswith('data:')) and c[0] != 'H' and not c[1].startswith('ugcgen:'),
    'V5_E_only(ads+crossorigin iframes, class/id/src)': lambda c: c[0] in ('E', 'D') and not c[2].startswith('data:'),
}


def key(c):
    return f"{c[0]}|{c[1]}|{c[2].split(':')[0]}"


def analyse(raw, site, tid):
    try:
        tree = LH.fromstring(raw)
    except Exception:
        return None
    P.deep_parse(tree)
    nodes = tree.xpath('//*')
    if not nodes:
        return None
    host = P.host_for(site)
    n = len(nodes)
    cand = [candidates(el, host) for el in nodes]
    mism = 0
    for k in range(0, n, 25):  # check against the published labeler on every 25th node
        lab, _ = P.gt_provenance(nodes[k], host)
        if lab != (cand[k][0][0] if cand[k] else None):
            mism += 1
    idx = {id(el): k for k, el in enumerate(nodes)}
    par = []
    for el in nodes:
        p = el.getparent()
        par.append(idx.get(id(p), -1) if p is not None else -1)
    byid, lt = {}, set()
    for el in nodes:
        v = el.get('id')
        if v:
            byid.setdefault(v, el)
    for el in nodes:
        if C.tag(el) == 'label':
            f = P.gattr(el, 'for')
            if f and f in byid:
                lt.add(id(byid[f]))
    vis = [C.visible(el) for el in nodes]
    act = [vis[k] and bool(C.clause_attr(nodes[k], lt)) for k in range(n)]
    tk = -1
    if tid:
        for k, el in enumerate(nodes):
            if el.get('backend_node_id') == tid:
                tk = k
                break
    kids = [[] for _ in range(n)]
    size = [1] * n
    had = [False] * n
    for k in range(n):
        if par[k] >= 0:
            kids[par[k]].append(k)
    for k in range(n - 1, -1, -1):
        p = par[k]
        if p >= 0:
            size[p] += size[k]
            if act[k] or had[k]:
                had[p] = True
    out = {'mism': mism, 'n': n, 'v': {}}
    for vn, keep in VARS.items():
        sr = [None] * n
        for k in range(n):
            for cc in cand[k]:
                if keep(cc):
                    sr[k] = cc
                    break
        src = [-1] * n
        prov = ['D'] * n
        for k in range(n):
            if sr[k] is not None:
                src[k] = k
                prov[k] = sr[k][0]
            elif par[k] >= 0:
                src[k] = src[par[k]]
                prov[k] = prov[par[k]]
        nu = [-1] * n  # nearest untrusted strict ancestor's seed
        for k in range(n):
            p = par[k]
            if p >= 0:
                nu[k] = src[p] if prov[p] != 'D' else nu[p]
        inside = [k for k in range(n) if act[k] and nu[k] >= 0]
        tf = None
        if tk >= 0:
            tf = prov[tk] != 'D' or nu[tk] >= 0
        rec = {'n_act': sum(act), 'inside': len(inside), 'target': tf}
        if vn == 'V0_base':
            rs = set(nu[k] for k in inside)
            rec['page_keys'] = sorted(set(key(sr[s]) for s in rs))
            rec['elem_keys'] = dict(collections.Counter(key(sr[nu[k]]) for k in inside))
            rec['data_attrs'] = sorted(set(sr[s][2] for s in rs if sr[s][2].startswith('data:')))
            rec['maxcov'] = max([size[s] / n for s in rs], default=0.0)
            rec['maxcov_tag'] = C.tag(nodes[max(rs, key=lambda s: size[s])]) if rs else None
            unt = [prov[k] != 'D' for k in range(n)]
            leaf = [unt[k] and not any(unt[c] for c in kids[k]) for k in range(n)]
            vl = [k for k in range(n) if leaf[k] and vis[k]]
            crit = [k for k in vl if had[k]]
            rec['g4'] = dict(
                vis_leaves=len(vl), crit=len(crit),
                crit_allkids_D=sum(1 for k in crit if kids[k] and all(sr[c] is not None and sr[c][0] == 'D' for c in kids[k])),
                crit_tags=[C.tag(nodes[k]) for k in crit][:5],
                crit_child_rules=[sr[kids[k][0]][1] for k in crit if kids[k] and sr[kids[k][0]] is not None][:5])
            if tf:
                s = src[tk] if prov[tk] != 'D' else nu[tk]
                se = nodes[s]
                rec['tinfo'] = dict(key=key(sr[s]), seed_tag=C.tag(se),
                                    seed_ci=((se.get('class') or '')[:40] + '#' + (se.get('id') or '')[:20]),
                                    cov=round(size[s] / n, 3), t_tag=C.tag(nodes[tk]),
                                    t_text=' '.join(' '.join(nodes[tk].itertext()).split())[:50])
        out['v'][vn] = rec
    return out


def site_ci(d, seed=SEED, b=B):
    s = sorted(d)
    sums = np.array([sum(d[x]) for x in s], float)
    cn = np.array([len(d[x]) for x in s], float)
    ix = np.random.default_rng(seed).integers(0, len(s), size=(b, len(s)))
    m = sums[ix].sum(1) / cn[ix].sum(1)
    return [round(100 * float(np.percentile(m, 2.5)), 2), round(100 * float(np.percentile(m, 97.5)), 2)]


def main(out=OUT):
    bys = collections.defaultdict(list)
    for f in C.FILES:
        for t in json.load(open(f)):
            bys[t['website']].append(t)
        gc.collect()
    sel = [x for s in sorted(bys) for x in sorted(bys[s], key=lambda t: t['annotation_id'])[:C.PER_SITE]]
    del bys
    gc.collect()
    rows, t0 = [], time.time()
    for i, t in enumerate(sel):
        for st, a in enumerate(t['actions']):
            r = analyse(a['raw_html'], t['website'], P.target_id(a))
            if r:
                r.update(site=t['website'], task=t['annotation_id'], step=st)
                rows.append(r)
        if (i + 1) % 25 == 0:
            print(f'[{i+1}/{len(sel)}] {len(rows)} {time.time()-t0:.0f}s', flush=True)
    res = {'pages': len(rows), 'tasks': len({r['task'] for r in rows}), 'sites': len({r['site'] for r in rows}),
           'mismatch_vs_gt_provenance_sampled': sum(r['mism'] for r in rows), 'variants': {}}
    for vn in VARS:
        pbs, tf = collections.defaultdict(list), {}
        for r in rows:
            e = r['v'][vn]['inside'] > 0
            pbs[r['site']].append(e)
            tf[(r['site'], r['task'])] = tf.get((r['site'], r['task']), False) or e
        tbs = collections.defaultdict(list)
        for (s, _), f in tf.items():
            tbs[s].append(f)
        tg = [r['v'][vn]['target'] for r in rows if r['v'][vn]['target'] is not None]
        na = sum(r['v'][vn]['n_act'] for r in rows)
        ins = sum(r['v'][vn]['inside'] for r in rows)
        res['variants'][vn] = dict(
            elem_pct=round(100 * ins / na, 2),
            page_pct=round(100 * sum(sum(v) for v in pbs.values()) / len(rows), 2), page_ci=site_ci(pbs),
            task_pct=round(100 * sum(tf.values()) / len(tf), 2), task_ci=site_ci(tbs),
            target_pct=round(100 * sum(tg) / len(tg), 2), target_n=len(tg),
            sites_any=sum(1 for v in pbs.values() if any(v)))
    V0 = [r['v']['V0_base'] for r in rows]
    ex = [(r, v) for r, v in zip(rows, V0) if v['inside'] > 0]
    pk = collections.Counter(k for _, v in ex for k in v['page_keys'])
    ek = collections.Counter()
    for _, v in ex:
        ek.update(v['elem_keys'])
    g4v = sum(v['g4']['vis_leaves'] for v in V0)
    g4c = sum(v['g4']['crit'] for v in V0)
    g4d = sum(v['g4']['crit_allkids_D'] for v in V0)
    p = g4c / g4v
    res['V0_detail'] = dict(
        exposed_pages=len(ex), page_keys_top=pk.most_common(20), elem_keys_top=ek.most_common(15),
        data_attr_names=collections.Counter(a for _, v in ex for a in v['data_attrs']).most_common(8),
        pages_only_H=sum(1 for _, v in ex if all(k.startswith('H|') for k in v['page_keys'])),
        pages_only_data_tokens=sum(1 for _, v in ex if all(k.endswith('|data') for k in v['page_keys'])),
        exposed_pages_maxcov_gt50=sum(1 for _, v in ex if v['maxcov'] > 0.5),
        exposed_pages_maxcov_gt20=sum(1 for _, v in ex if v['maxcov'] > 0.2),
        maxcov_tags=collections.Counter(v['maxcov_tag'] for _, v in ex).most_common(8),
        g4_vis_leaves=g4v, g4_crit=g4c, g4_crit_pct=round(100 * p, 2), g4_crit_with_all_children_seeded_D=g4d,
        g4_crit_child_rules=collections.Counter(x for v in V0 for x in v['g4']['crit_child_rules']).most_common(8),
        g4_crit_tags=collections.Counter(x for v in V0 for x in v['g4']['crit_tags']).most_common(8),
        page_with_crit_leaf_pct=round(100 * sum(1 for v in V0 if v['g4']['crit'] > 0) / len(V0), 2),
        indep_pred_page_pct=round(100 * float(np.mean([1 - (1 - p) ** v['g4']['vis_leaves'] for v in V0])), 2),
        site_exposed_pages=sorted(collections.Counter(r['site'] for r, _ in ex).items(), key=lambda x: -x[1])[:10],
        target_examples=[dict(site=r['site'], step=r['step'], **v['tinfo']) for r, v in zip(rows, V0) if v.get('tinfo')][:40],
        target_keys=collections.Counter(v['tinfo']['key'] for v in V0 if v.get('tinfo')).most_common(12))
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    json.dump(res, open(out, 'w'), indent=1, default=str)
    print(json.dumps(res['variants'], indent=1))
    print('DONE', round(time.time() - t0))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else OUT)

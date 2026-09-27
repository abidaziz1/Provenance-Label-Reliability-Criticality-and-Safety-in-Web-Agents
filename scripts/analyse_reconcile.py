from pathlib import Path as _Path
ROOT = _Path(__file__).resolve().parents[1]
import json, sys, collections
TAG = sys.argv[1] if len(sys.argv) > 1 else 'v2'
rows = json.load(open(f'{ROOT}/results/reconcile_{TAG}.json'))

def agg(rs, key='G'):
    tot = collections.defaultdict(lambda: collections.Counter())
    for r in rs:
        for g, d in r[key].items():
            for k, v in d.items(): tot[g][k] += v
    return tot

def table(rs, title, n_pages=None):
    n_pages = n_pages or len(rs)
    tot = agg(rs)
    print(f"\n{title}   ({n_pages} pages, "
          f"{sum(r['n_untrusted'] for r in rs):,} untrusted nodes)")
    print(f"{'granularity':24s} {'units':>9s} {'per page':>9s} "
          f"{'crit(ours)':>11s} {'crit(theirs)':>13s} {'on target':>10s}")
    order = ['G0_region','G1_region_plus_items','G2_block','G5_textcarrier','G4_leafpath','G3_node']
    for g in order:
        c = tot[g]; n = c['n']
        if not n: continue
        print(f"{g:24s} {n:9,d} {n/n_pages:9.2f} "
              f"{100*c['crit_ours']/n:10.2f}% {100*c['crit_pris']/n:12.2f}% "
              f"{100*c['on_target']/n:9.3f}%")

print(f"=== PARSER {TAG} ===")
print(f"observations: {len(rows)}   sites: {len({r['site'] for r in rows})}   "
      f"trajectories: {len({r['task'] for r in rows})}")
print(f"nodes: {sum(r['n_nodes'] for r in rows):,}   "
      f"actionable (ours): {sum(r['n_act_ours'] for r in rows):,}   "
      f"actionable (their definition): {sum(r['n_act_pris'] for r in rows):,}")
cl = collections.Counter()
for r in rows: cl.update(r['clause'])
print("their actionable clauses:", dict(cl.most_common()))

table(rows, "FULL 57-SITE FRAME, every step")
table([r for r in rows if r['first_step']], "ONE PAGE PER TRAJECTORY (first step only)")
table([r for r in rows if r['in16']], "16-SITE PUBLISHED FRAME, every step")
withT = [r for r in rows if r['has_target']]
table(withT, "OBSERVATIONS WITH A RESOLVABLE TASK TARGET")

print("\n--- PRISMATA REFERENCE (Section 3, Mind2Web half) ---")
print(f"{'':24s} {'units':>9s} {'per page':>9s} {'crit':>11s}")
print(f"{'their untrusted path':24s} {65416:9,d} {65416/2832:9.2f} {1.2:10.2f}%   (whole corpus 1,086/90,408)")

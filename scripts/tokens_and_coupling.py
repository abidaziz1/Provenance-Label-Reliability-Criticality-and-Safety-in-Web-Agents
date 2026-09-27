from pathlib import Path as _Path
ROOT = _Path(__file__).resolve().parents[1]
import json, sys, random, collections, gc
import numpy as np, tiktoken
from scipy.stats import fisher_exact
enc = tiktoken.get_encoding("o200k_base")
sys.path.insert(0, str(ROOT / 'src'))
exec(open(f'{ROOT}/scripts/ablation_v2.py').read().split("bysite = collections.defaultdict")[0])
tasks = json.load(open(f'{ROOT}/data/mind2web/data/train/train_1.json'))
random.seed(1); random.shuffle(tasks)
obs, html = [], []
for t in tasks[:40]:
    for a in t['actions'][:2]:
        tr = build(t, a, 'page', 'A2', 'P_correct', True)
        if tr: obs.append(tr['sent'])
        html.append(a['raw_html'][:200_000])
    if len(obs) >= 25: break
r_obs = np.mean([len(o) / max(len(enc.encode(o)), 1) for o in obs])
# sanitized-HTML proxy: tokenise the first 200k chars of sanitized pages
def san(raw):
    tree = LH.fromstring(raw)
    for bad in tree.xpath("//script | //style | //noscript | //svg | //iframe"):
        p = bad.getparent()
        if p is not None: p.remove(bad)
    for el in tree.iter():
        if not isinstance(el.tag, str): continue
        for k in list(el.attrib):
            if k.lower().startswith("on") or k.lower() == "style": del el.attrib[k]
        if el.text and el.text.strip(): el.text = f"[text:length:{len(el.text.strip())}]"
        if el.tail and el.tail.strip(): el.tail = f"[text:length:{len(el.tail.strip())}]"
    return LH.tostring(tree, encoding="unicode")[:200_000]
hs = [san(h) for h in html[:12]]
r_html = np.mean([len(h) / max(len(enc.encode(h)), 1) for h in hs])
print(f"chars per token (o200k proxy): agent observation {r_obs:.2f}   sanitized HTML {r_html:.2f}")
print(f"   sample sizes: {len(obs)} observations, {len(hs)} sanitized pages")

# ---- power for the COUPLING statistic (A-wrong x B-wrong association) ----
rng = np.random.default_rng(7)
def sim_power(n, p, kappa, B=800, deff=2.68):
    n_eff = int(n / deff); pb = min(kappa * p * p, p); hits = 0
    for _ in range(B):
        # multinomial over (A wrong,B wrong), (A wrong,B right), (A right,B wrong), (A right,B right)
        probs = [pb, p - pb, p - pb, 1 - 2 * p + pb]
        a, b, c, d = rng.multinomial(n_eff, probs)
        _, pv = fisher_exact([[a, b], [c, d]], alternative='greater'); hits += pv < 0.05
    return hits / B
def need(p, kappa):
    lo, hi, best = 100, 40000, None
    while lo <= hi:
        mid = (lo + hi) // 2
        if sim_power(mid, p, kappa) >= 0.8: best = mid; hi = mid - 100
        else: lo = mid + 100
    return best
print("\nitems needed for 80% power on the coupling test (one-sided, alpha .05, DEFF 2.68):")
print(f"{'per-vendor error':>17s} {'kappa 1.5':>10s} {'kappa 2.0':>10s} {'kappa 3.0':>10s}")
out = {}
for p in (0.05, 0.10, 0.20):
    row = [need(p, k) for k in (1.5, 2.0, 3.0)]; out[p] = row
    print(f"{p:17.0%} " + " ".join(f"{(str(x) if x else '>40k'):>10s}" for x in row), flush=True)
json.dump(dict(chars_per_token_obs=r_obs, chars_per_token_html=r_html,
               coupling_need={str(k): v for k, v in out.items()}),
          open(f'{ROOT}/results/roadmap/tokens_and_coupling.json', 'w'), indent=1)

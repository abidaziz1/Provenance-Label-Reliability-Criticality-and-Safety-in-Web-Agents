"""Regression suite: the six defects the 19 Sep audit found, each asserted as
v1-behaviour (the bug, reproduced) and v2-behaviour (the fix). Plus the negative
controls the audit asked for."""
from pathlib import Path as _Path
ROOT = _Path(__file__).resolve().parents[1]
import sys, json
sys.path.insert(0, str(ROOT / 'src'))
import pipeline_v2 as P
import score_v2 as S
from lxml import html as LH

PASS = []; FAIL = []
def chk(name, got, want):
    ok = (got == want)
    (PASS if ok else FAIL).append((name, got, want))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}\n        got={got!r}\n        want={want!r}")

# A page with the shape of a real product page: chrome and controls dominate,
# user content is a small minority. A toy page where the review IS most of the
# DOM cannot show overmasking, which is the whole point of the D1 check.
PAGE = """<html><body>
<nav class="site-nav"><a href="/">Home</a><a href="/c">Shop</a><a href="/d">Deals</a>
<a href="/e">Cart</a><a href="/f">Account</a><a href="/g">Help</a></nav>
<header class="site-header"><form><input name="q"><button>Search</button></form></header>
<main><h1>Product</h1><div class="gallery"><img src="/1.jpg"><img src="/2.jpg"></div>
<div class="price"><span>$39</span></div>
<div class="opts"><select><option>S</option><option>M</option></select>
<button id="buy">Buy</button><button id="wish">Save</button></div>
<div class="spec"><ul><li>a</li><li>b</li><li>c</li><li>d</li></ul></div>
<div class="review"><p>Great product</p><a href="/r/1">helpful</a></div>
</main><footer class="site-footer"><a href="/tos">Terms</a></footer></body></html>"""

print("=== D1  overmasking: the selector `body` ===")
tree = LH.fromstring(PAGE)
truth = tree.cssselect('.review')
v1 = S.score(tree, truth, 'body')
chk('D1 v1 region-level F1 for `body` (the bug)', v1['v1_region_f1'], 1.0)
print(f"        v2 node-level: P={v1['precision']} R={v1['recall']} F1={v1['f1']} "
      f"overmask={v1['overmask_ratio']} truth={v1['truth_ratio']}")
chk('D1 v2 node-level recall for `body` is still 1.0', v1['recall'], 1.0)
chk('D1 v2 node-level precision for `body` is below 0.5', v1['precision'] < 0.5, True)
chk('D1 v2 flags near-total overmasking', v1['overmask_ratio'] > 0.9, True)
exact = S.score(tree, truth, '.review')
chk('D1 v2 exact selector still scores F1 1.0', exact['f1'], 1.0)
chk('D1 v2 exact selector overmask is small', exact['overmask_ratio'] < 0.15, True)

print("\n=== D2  dict-shaped prediction ===")
d = S.score(tree, truth, {"css_selector": ".review", "reason": "user-generated"})
chk('D2 v2 parses the official object shape', (d['tp'] > 0, d['f1']), (True, 1.0))
try:
    S.normalize_predictions({"nope": 1}); got = 'no-raise'
except S.MalformedPrediction: got = 'raised'
chk('D2 v2 raises on an uninterpretable prediction', got, 'raised')
chk('D2 v2 accepts a list of objects',
    S.score(tree, truth, [{"selector": ".review"}])['f1'], 1.0)

print("\n=== D3  aria-label vs aria_label ===")
std = LH.fromstring('<div aria-label="Customer reviews"><span>x</span></div>')
arc = LH.fromstring('<div aria_label="Customer reviews"><span>x</span></div>')
P.set_fixes(attr_norm=False)
chk('D3 v1 misses the standard spelling (the bug)', P.visible_cue(std), None)
chk('D3 v1 matches the archive spelling', bool(P.visible_cue(arc)), True)
P.set_fixes(attr_norm=True)
chk('D3 v2 matches the standard spelling', bool(P.visible_cue(std)), True)
chk('D3 v2 still matches the archive spelling', bool(P.visible_cue(arc)), True)

print("\n=== D4  same-origin iframe ===")
rel = LH.fromstring('<iframe src="/help/faq.html"></iframe>')
same = LH.fromstring('<iframe src="https://www.kohls.com/help/faq.html"></iframe>')
cross = LH.fromstring('<iframe src="https://evil.example/x"></iframe>')
adf = LH.fromstring('<iframe src="https://tpc.googlesyndication.com/ad"></iframe>')
P.set_fixes(same_origin=False)
chk('D4 v1 labels a relative src external (the bug)', P.gt_provenance(rel, 'kohls.com'),
    ('E', 'iframe:crossorigin'))
P.set_fixes(same_origin=True)
chk('D4 v2 does not label a relative src external', P.gt_provenance(rel, 'kohls.com'), (None, None))
chk('D4 v2 does not label a same-site src external', P.gt_provenance(same, 'kohls.com'), (None, None))
chk('D4 v2 still labels a genuine cross-origin frame', P.gt_provenance(cross, 'kohls.com'),
    ('E', 'iframe:crossorigin'))
chk('D4 v2 still labels an ad frame', P.gt_provenance(adf, 'kohls.com'), ('E', 'iframe:adnetwork'))

print("\n=== D5  escaped markup inside <pre> ===")
CODE = ('<html><body><pre>&lt;div class="demo"&gt;&lt;button onclick="go()"&gt;'
        'Click me to submit the form&lt;/button&gt;&lt;a href="/x"&gt;link&lt;/a&gt;&lt;/div&gt;</pre>'
        '</body></html>')
for fix in (False, True):
    P.set_fixes(literal_markup=fix, splice_count=fix)
    t = LH.fromstring(CODE); st = P.deep_parse(t)
    n_act = sum(1 for e in t.iter() if isinstance(e.tag, str) and P.is_actionable(e))
    tag = 'v2' if fix else 'v1'
    print(f"        {tag}: actionable={n_act} stats={st}")
    if not fix:
        chk('D5 v1 manufactures a live control from code (the bug)', n_act >= 1, True)
        chk('D5 v1 reports nodes_added=0 while splicing', st['nodes_added'], 0)
    else:
        chk('D5 v2 splices nothing inside <pre>', (n_act, st['spliced']), (0, 0))
        chk('D5 v2 records the skip', st['skipped_literal'] >= 1, True)
P.set_fixes(literal_markup=True, splice_count=True)
REAL = ('<html><body><div>&lt;div class="review"&gt;&lt;a href="/x"&gt;'
        'a genuinely escaped review block with a link&lt;/a&gt;&lt;/div&gt;</div></body></html>')
t = LH.fromstring(REAL); st = P.deep_parse(t)
chk('D5 v2 still splices escaped markup outside a literal tag', st['spliced'] >= 1, True)
chk('D5 v2 counts the spliced nodes', st['nodes_added'] >= 2, True)

print("\n=== D6  pruned text leaking through a parent label ===")
LEAK = ('<html><body><a href="/buy" backend_node_id="7">Buy '
        '<span class="review">SECRET REVIEW TEXT</span></a></body></html>')
t = LH.fromstring(LEAK)
nodes = t.xpath('//*')
prov = {}
for el in nodes:
    lab, _ = P.gt_provenance(el, 'x.com')
    if lab: prov[el] = lab
    else:
        p_ = el.getparent(); prov[el] = prov.get(p_, 'D')
cap = P.build_capability_map(t, prov, {id(e) for e in nodes if P.is_actionable(e)}, set())
for fix in (False, True):
    P.set_fixes(cap_aware_label=fix)
    out = P.render_observation(t, cap)
    tag = 'v2' if fix else 'v1'
    print(f"        {tag}: {out!r}")
    if not fix:
        chk('D6 v1 leaks the pruned text (the bug)', 'SECRET' in out, True)
    else:
        chk('D6 v2 does not leak the pruned text', 'SECRET' in out, False)
        chk('D6 v2 keeps the legitimate label', 'Buy' in out, True)
P.set_fixes(cap_aware_label=True)

print("\n=== negative controls the audit asked for ===")
t = LH.fromstring(PAGE)
truth = t.cssselect('.review')
nc = {}
nc['all-page mask (body)'] = S.score(t, truth, 'body')
nc['empty prediction'] = S.score(t, truth, [])
nc['wrong region (nav)'] = S.score(t, truth, 'nav')
nc['exact'] = S.score(t, truth, '.review')
for k, v in nc.items():
    print(f"        {k:22s} P={v['precision']:.3f} R={v['recall']:.3f} "
          f"F1={v['f1']:.3f} overmask={v['overmask_ratio']:.3f}")
chk('control: exact beats all-page on F1', nc['exact']['f1'] > nc['all-page mask (body)']['f1'], True)
chk('control: wrong region scores zero recall', nc['wrong region (nav)']['recall'], 0.0)
chk('control: wrong region scores zero precision', nc['wrong region (nav)']['precision'], 0.0)
chk('control: empty prediction scores zero F1', nc['empty prediction']['f1'], 0.0)

HID = LH.fromstring('<div class="review"><input type="hidden" name="x"><p>text</p></div>')
chk('control: hidden input is not actionable',
    P.is_actionable(HID.cssselect('input')[0]), False)
NEST = LH.fromstring('<div class="review"><div class="comment"><p>t</p></div></div>')
nn = NEST.xpath('//*'); pv = {}
for el in nn:
    l, _ = P.gt_provenance(el, 'x.com')
    pv[el] = l if l else pv.get(el.getparent(), 'D')
regions = [e for e in nn if pv[e] != 'D' and (e.getparent() is None or pv.get(e.getparent(), 'D') == 'D')]
chk('control: a nested untrusted descendant is not a second region', len(regions), 1)

print(f"\n{'='*64}\nPASS {len(PASS)}   FAIL {len(FAIL)}")
if FAIL:
    for n, g, w in FAIL: print(f"  FAILED {n}: got {g!r} want {w!r}")
    sys.exit(1)

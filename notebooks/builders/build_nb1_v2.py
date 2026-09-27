"""Notebook 01 v2. Rebuilt after the 19 Sep independent audit.

Changes from v1, each traceable to an audit finding:
  [A-5a] the detection loop reached two Kohl's pages because five of six configured
         sites were absent from the single shard loaded. Replaced with a manifest
         that reports found/missing and refuses to continue on a partial frame.
  [A-5b] captured live pages were written but never entered the detection loop.
         Part 3 now iterates one PAGES list carrying both corpora, tagged.
  [A-5c] "stops if the clone fails" was asserted but not implemented. There is now
         an explicit hard stop, and a self-test that proves the stop fires.
  [A-1]  the repo clone was unpinned. The commit is recorded and printed.
  [A-2]  the sanitizer was a reimplementation described as UCM's. It now tries the
         repo's own sanitizer first and records which one ran.
  [A-3]  the scorer accepted only bare strings and never charged overmasking.
         Replaced by idea3_score.py, which does both and has negative controls.
  [A-4]  ground truth is our own heuristic, so the comparison is agreement, not
         accuracy. The wording now says so everywhere, and "lower bound" is gone.
"""
from pathlib import Path as _Path
ROOT = _Path(__file__).resolve().parents[2]
import sys
sys.path.insert(0, str(ROOT / 'notebooks' / 'builders'))
from build_v2_common import *

nb = new_notebook()
a = nb['cells'].append

a(new_markdown_cell("""# 01. Corpus fidelity and structure-only detection (v2)

**This replaces the v1 notebook. Do not run the v1 one.** Seven defects found by the 19 September independent audit are fixed here, and the two that mattered most had already fired in your Colab run: the detection loop reached two Kohl's pages, and the prompt guard I said existed did not exist.

### What this notebook decides

Whether a fair head-to-head against UCM's structure-only boundary detector is possible at all, and on what corpus.

UCM (arXiv:2607.05277) detects untrusted regions from DOM structure alone. It replaces every text node with `[text:length:N]` before the model sees the page, and its prompts lean on `data-testid` attributes while discouraging bare class selectors. It reports boundary F1 of 0.997 on Reddit, 0.879 on Booking and 0.840 on GitLab.

**The problem confirmed in your run:** Mind2Web's archived HTML strips `data-*`. Your output measured sports.yahoo at 0.44 `data-*` per 1,000 nodes against 15,533 class attributes, travelzoo at 1.37, kohls at 1.36, and exactly one surviving `data-*` name (`data_pw_testid_buckeye`). Running UCM's detector on Mind2Web as published would handicap it on the signal it was designed around.

### What changed since v1

| # | v1 behaviour | v2 behaviour |
|---|---|---|
| 1 | six sites configured, one shard loaded, two pages reached | manifest resolves sites against what is loaded and stops if any are missing |
| 2 | live captures written, never scored | one `PAGES` list carries both corpora, each row tagged `archive` or `live` |
| 3 | prompt load failure printed a message and continued | `RuntimeError`, with a self-test that proves it fires |
| 4 | `git clone` unpinned | commit recorded and printed with the results |
| 5 | our own sanitizer, described as theirs | theirs if importable, ours if not, and the run records which |
| 6 | `body` selector scored F1 1.00 | node-level scoring plus an explicit overmask ratio |
| 7 | "lower bound on their performance" | agreement with our heuristic, which is not a bound on anything |

Run top to bottom. `DRY_RUN` is on and no paid call happens until you turn it off."""))

# ---------------------------------------------------------------- config
a(new_markdown_cell("""## Git and results (task 1.13)

Results go to the branch `colab/<task-id>` of the research repo, never to main; a reviewer checks the branch and opens the PR. You need the Colab secret `GH_TOKEN_COLAB` (a fine-grained token for this repo, Contents read and write) and the model key named in the secrets cell. Part 3's calls go through `src/llm.py` under the budget in `EXP_DIR/config.yaml`. For the live capture alone (task 2.7), set `TASK_ID = "2.7"`."""))
a(new_code_cell(git_config("2.8", "2026-10-12_2.8_ucm-detector-archive-vs-live")))
a(new_code_cell(GIT_SETUP))
a(new_code_cell(PUSH_HELPER))

a(new_code_cell('''# ---------------------------------------------------------------- configuration
DRY_RUN = True            # no paid API calls while this is True
N_PAGES_PER_SITE = 2
MODEL = "claude-sonnet-4-5"   # [1.4] UCM's own selector model (UCM §7.1), for the reproduction; every row records it
MAX_HTML_CHARS = 200_000  # UCM uses CLEAN_HTML_MAX_SIZE = 200000

# Sites chosen by the pre-work measurement, not by convenience.
# The value is semantic_class_ratio: the share of class tokens that look like
# words rather than hashes. A structure-only detector has least to work with at
# the bottom of this list.
CANDIDATE_SITES = {
    "rentalcars":   0.126,   # hardest measured
    "seatgeek":     0.406,   # zero untrusted regions found by structural rules
    "booking":      0.458,   # UCM's own hard case, useful as a bridge
    "airbnb":       0.570,   # zero untrusted regions found by structural rules
    "sports.yahoo": 0.420,   # in the small shard, so the audit part runs cheaply
    "amazon":       0.795,   # easy case, acts as the control
    "kohls":        0.826,   # easy case
}
SITES = list(CANDIDATE_SITES)

# [A-5a] v1 loaded train_10.json only, which holds kohls, sports.yahoo and
# travelzoo. Asking for rentalcars, seatgeek, booking, airbnb or amazon from that
# shard yields nothing, and v1 did not notice. Declare the shards the requested
# sites actually need, and let the manifest check the result.
SHARDS = ["train_10.json", "train_0.json", "train_1.json"]   # 1.27 GB total
SMALL_SHARD_ONLY = True    # Part 1 runs on train_10.json alone; set False for the
                           # full fidelity audit across all 57 sites

# [A-5c] refuse to proceed on a partial frame rather than reporting a number
# computed from whatever happened to load.
REQUIRE_ALL_SITES = True

print(f"{len(SITES)} sites requested, {N_PAGES_PER_SITE} pages each, DRY_RUN={DRY_RUN}")
print("shards:", SHARDS if not SMALL_SHARD_ONLY else ["train_10.json"])'''))

a(new_code_cell('''%pip install -q lxml cssselect huggingface_hub numpy scipy anthropic pyyaml'''))
a(new_code_cell(SECRETS))
a(new_code_cell(LLM_SETUP))
a(new_code_cell(WRITE_PIPELINE))
a(new_code_cell(WRITE_SCORER))
a(new_code_cell(MANIFEST))

# ---------------------------------------------------------------- part 1
a(new_markdown_cell("""## Part 1. Corpus fidelity audit

No key needed. This measures what fraction of the attribute surface a structure-only detector depends on actually survives in the corpus.

`train_10.json` is 28 MB and enough for the audit. The full corpus is 1.27 GB and only Part 3 needs it."""))

a(new_code_cell('''from lxml import html as LH

shards_now = ["train_10.json"] if SMALL_SHARD_ONLY else SHARDS
frame, found, missing, present = load_frame(SITES, shards_now, per_site=N_PAGES_PER_SITE)
print(f"\\nrequested : {SITES}")
print(f"found     : {found}")
print(f"missing   : {missing}")
print(f"{len(present)} sites present in the loaded shard(s)")

# [A-5a] This is the check v1 did not have.
if missing and REQUIRE_ALL_SITES:
    if SMALL_SHARD_ONLY:
        raise RuntimeError(
            f"{len(missing)} of {len(SITES)} requested sites are not in the loaded "
            f"shard(s): {missing}. Set SMALL_SHARD_ONLY = False to pull all three "
            f"shards (1.27 GB), or trim CANDIDATE_SITES to {found}. "
            f"Refusing to report a fidelity number computed from a partial frame.")
    raise RuntimeError(f"sites absent from the full corpus: {missing}")
print(f"\\nframe: {len(frame)} trajectories over {len(set(t['website'] for t in frame))} sites")'''))

a(new_code_cell('''import collections

HOOKS = ("id", "class", "role", "aria_label", "aria-label", "itemprop", "itemtype",
         "name", "title", "alt", "placeholder")

def attribute_profile(raw_html):
    """Count the structural hooks a structure-only detector can key on."""
    try:
        tree = LH.fromstring(raw_html)
    except Exception:
        return None
    prof = collections.Counter(); n = 0
    for el in tree.iter():
        if not isinstance(el.tag, str):
            continue
        n += 1
        for k in el.attrib:
            kl = k.lower()
            if kl.startswith("data"):
                prof["data-*"] += 1
                prof[f"name::{kl}"] += 1
            elif kl in HOOKS:
                prof[kl.replace("aria-label", "aria_label")] += 1
    prof["nodes"] = n
    return prof

bysite = collections.defaultdict(lambda: collections.Counter())
n_pages = collections.Counter()
for t in frame:
    for act in t["actions"][:N_PAGES_PER_SITE]:
        p = attribute_profile(act["raw_html"])
        if p:
            bysite[t["website"]].update(p)
            n_pages[t["website"]] += 1

print(f"{'site':16s} {'pages':>6s} {'nodes':>9s} {'class':>8s} {'id':>7s} "
      f"{'role':>6s} {'aria':>6s} {'data-*':>7s} {'data/1k':>8s}")
audit = {}
for site, p in sorted(bysite.items(), key=lambda kv: -kv[1]["nodes"]):
    per_k = 1000 * p["data-*"] / max(p["nodes"], 1)
    audit[site] = dict(pages=n_pages[site], nodes=p["nodes"], data=p["data-*"],
                       cls=p["class"], per_k=round(per_k, 3))
    print(f"{site:16s} {n_pages[site]:6d} {p['nodes']:9,d} {p['class']:8,d} "
          f"{p['id']:7,d} {p['role']:6,d} {p['aria_label']:6,d} {p['data-*']:7,d} {per_k:8.2f}")

names = sorted({k[6:] for p in bysite.values() for k in p if k.startswith("name::")})
print("\\ndistinct data-* attribute names in this frame:", names or "(none)")
json.dump(audit, open("fidelity_audit.json", "w"), indent=1)

worst = min(audit.values(), key=lambda v: v["per_k"])["per_k"] if audit else 0
print(f"\\nlowest data-* density in the frame: {worst:.2f} per 1k nodes")
print("READ THIS: below roughly 1 per 1k nodes, UCM's detector is denied its primary")
print("signal, and any F1 measured on this corpus is a property of the archive.")'''))

# ---------------------------------------------------------------- part 2
a(new_markdown_cell("""## Part 2. Capture live pages that preserve the DOM

No key needed, but it needs network access and a browser.

Two honest constraints. Some commercial sites block automated browsers; record the failures rather than retrying around them, because a site you cannot capture is a reportable fact about deployability. And live pages in 2026 are not the pages Mind2Web archived in 2023, so anything comparing the corpora is measuring corpus age as well as corpus fidelity. Say so in the paper.

**[A-5b] What changed:** v1 wrote these files and then iterated the archive anyway, so nothing captured here was ever scored. Part 3 now builds one `PAGES` list from both sources."""))

a(new_code_cell('''LIVE_TARGETS = {
    "booking":      "https://www.booking.com/searchresults.html?ss=Paris",
    "seatgeek":     "https://seatgeek.com/concert-tickets",
    "amazon":       "https://www.amazon.com/s?k=usb+c+hub",
    "airbnb":       "https://www.airbnb.com/s/Paris/homes",
    "kohls":        "https://www.kohls.com/catalog/mens-shirts.jsp",
    "rentalcars":   "https://www.rentalcars.com/",
    "sports.yahoo": "https://sports.yahoo.com/nba/",
}
CAPTURE_LIVE = False   # flip on deliberately; expect some sites to refuse

captured = {}
if CAPTURE_LIVE:
    !pip -q install playwright && playwright install chromium 2>/dev/null | tail -1
    from playwright.sync_api import sync_playwright
    os.makedirs("live_pages", exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for site, url in LIVE_TARGETS.items():
            try:
                page = browser.new_page(viewport={"width": 1440, "height": 900})
                page.goto(url, timeout=45_000, wait_until="domcontentloaded")
                page.wait_for_timeout(3_000)
                html = page.content()
                open(f"live_pages/{site}.html", "w").write(html)
                prof = attribute_profile(html)
                captured[site] = dict(ok=True, chars=len(html),
                                      data_per_k=1000*prof["data-*"]/max(prof["nodes"],1))
                print(f"  {site:14s} captured {len(html):>9,d} chars  "
                      f"data-*/1k = {captured[site]['data_per_k']:.1f}")
                page.close()
            except Exception as e:
                captured[site] = dict(ok=False, error=str(e)[:120])
                print(f"  {site:14s} FAILED: {str(e)[:100]}")
        browser.close()
    json.dump(captured, open("live_capture_report.json", "w"), indent=1)
    ok = [s for s, v in captured.items() if v.get("ok")]
    print(f"\\ncaptured {len(ok)}/{len(LIVE_TARGETS)}: {ok}")
else:
    print("CAPTURE_LIVE is False. Part 3 will run on the archive corpus only,")
    print("and will say so in its output rather than implying a live comparison.")'''))

# ---------------------------------------------------------------- part 3
a(new_markdown_cell("""## Part 3. Structure-only detection

Uses UCM's own prompt, pulled from their public MIT-licensed repository at run time rather than retyped here.

**[A-5c] What changed:** v1 printed a warning and carried on when the prompt failed to load, and `(prompt_template or "")` accepted `None`. A paraphrased or empty prompt is not a test of their method, so this version raises. The cell after the clone proves the guard fires.

**[A-1] What changed:** the clone is pinned and the commit hash is stored with the results, so a later reader can tell which version of their prompt produced these numbers."""))

a(new_code_cell('''import re, pathlib, subprocess

UCM_REPO = "https://github.com/ethz-spylab/untrusted-content-masking"
UCM_PIN = "acff2e4"   # [1.4] the commit the 25 Sep audit read; None records whatever HEAD is

!rm -rf ucm
!git clone --quiet {UCM_REPO} ucm 2>/dev/null || echo "CLONE FAILED"
if UCM_PIN:
    !git -C ucm checkout --quiet {UCM_PIN}

UCM_COMMIT = None
try:
    UCM_COMMIT = subprocess.check_output(
        ["git", "-C", "ucm", "rev-parse", "HEAD"], text=True).strip()
except Exception as e:
    print("could not read commit:", e)

UCM_PROMPT = None
site_py = pathlib.Path("ucm/src/automatic_boundary_detection/sites/booking/site.py")
if site_py.exists():
    m = re.search(r'INITIAL_PROMPT_TEMPLATE\\s*=\\s*("""|\\'\\'\\')(.*?)\\1',
                  site_py.read_text(), re.S)
    if m:
        UCM_PROMPT = m.group(2)

print("commit:", UCM_COMMIT)
print("prompt:", f"{len(UCM_PROMPT)} chars" if UCM_PROMPT else "NOT LOADED")
if UCM_PROMPT:
    print(UCM_PROMPT[:400].replace("\\n", " ")[:400], "...")'''))

a(new_code_cell('''# [A-5c] The guard v1 claimed to have. It is a function so it can be unit-tested,
# and it is tested immediately below, because an untested safety check is a claim.

class PromptUnavailable(RuntimeError):
    pass

def require_prompt(prompt, commit):
    if not prompt or not prompt.strip():
        raise PromptUnavailable(
            "UCM's INITIAL_PROMPT_TEMPLATE did not load. Re-run the clone or check "
            "whether the file moved. Do NOT substitute a paraphrase: the experiment "
            "is a test of their prompt, and a paraphrase would measure ours.")
    if len(prompt) < 500:
        raise PromptUnavailable(f"prompt is only {len(prompt)} chars, which is not "
                                "the template. Inspect the file before continuing.")
    if not commit:
        raise PromptUnavailable("no commit hash: the result would not be attributable.")
    return prompt

# self-test: prove the guard fires before relying on it
for bad, why in ((None, "None"), ("", "empty"), ("short", "too short")):
    try:
        require_prompt(bad, "abc123"); print(f"  GUARD FAILED to fire on {why}")
    except PromptUnavailable:
        print(f"  guard fires on {why}")
try:
    require_prompt("x" * 600, None); print("  GUARD FAILED to fire on missing commit")
except PromptUnavailable:
    print("  guard fires on missing commit")

UCM_PROMPT = require_prompt(UCM_PROMPT, UCM_COMMIT)
print(f"\\nprompt accepted: {len(UCM_PROMPT)} chars at {UCM_COMMIT[:12]}")'''))

a(new_code_cell('''# [A-2] Try UCM's own sanitizer before falling back to ours, and record which ran.
import sys
sys.path.insert(0, "ucm/src")
SANITIZER = None
try:
    from automatic_boundary_detection.html_utils import clean_html as _ucm_clean
    SANITIZER = "ucm.clean_html"
except Exception:
    try:
        from automatic_boundary_detection.utils import clean_html as _ucm_clean
        SANITIZER = "ucm.utils.clean_html"
    except Exception:
        _ucm_clean = None

def ours_sanitize(raw_html, max_chars=MAX_HTML_CHARS):
    """Our mirror of UCM's sanitizer: drop scripts/styles/comments, strip event
    handlers and style attributes, replace every text node with [text:length:N]."""
    tree = LH.fromstring(raw_html)
    for bad in tree.xpath("//script | //style | //noscript | //svg | //iframe"):
        p = bad.getparent()
        if p is not None: p.remove(bad)
    for el in tree.iter():
        if not isinstance(el.tag, str): continue
        for k in list(el.attrib):
            kl = k.lower()
            if kl.startswith("on") or kl == "style":
                del el.attrib[k]
        if el.text and el.text.strip():
            el.text = f"[text:length:{len(el.text.strip())}]"
        if el.tail and el.tail.strip():
            el.tail = f"[text:length:{len(el.tail.strip())}]"
    return LH.tostring(tree, encoding="unicode")[:max_chars]

def sanitize(raw_html, max_chars=MAX_HTML_CHARS):
    if _ucm_clean is not None:
        try:
            return _ucm_clean(raw_html)[:max_chars]
        except Exception as e:
            print("  their sanitizer raised, falling back to ours:", str(e)[:80])
    return ours_sanitize(raw_html, max_chars)

if SANITIZER is None:
    SANITIZER = "ours (theirs not importable)"
print("sanitizer in use:", SANITIZER)
print("RECORD THIS in any write-up. A reimplementation described as theirs is a")
print("construct-validity problem, not a detail.")

sample = frame[0]["actions"][0]["raw_html"]
san = sanitize(sample)
print(f"\\nraw {len(sample):,} chars -> sanitized {len(san):,} chars")
print("text placeholders present:", "[text:length:" in san)
print(san[:300])'''))

a(new_code_cell('''# [A-5b] ONE page list, both corpora, each row tagged. v1 built the live corpus
# and then iterated the archive.
PAGES = []
for t in frame:
    for act in t["actions"][:N_PAGES_PER_SITE]:
        PAGES.append(dict(corpus="archive", site=t["website"], html=act["raw_html"]))
for site, v in captured.items():
    if v.get("ok"):
        PAGES.append(dict(corpus="live", site=site,
                          html=open(f"live_pages/{site}.html").read()))

byc = collections.Counter(p["corpus"] for p in PAGES)
print(f"{len(PAGES)} pages to score: {dict(byc)}")
print("sites:", sorted({p["site"] for p in PAGES}))
if byc["live"] == 0:
    print("\\nNOTE: archive only. Any result here is about the archive, and the")
    print("attribute-fidelity finding above says the archive handicaps the method.")'''))

a(new_code_cell('''%run -i idea3_pipeline.py
%run -i idea3_score.py

def ground_truth_untrusted(raw_html, site):
    """Our structural labeler's maximal untrusted regions.

    [A-4] This is NOT ground truth. It is one heuristic's opinion, and it reads
    class names and ids that the detector under test never sees. What follows is
    therefore AGREEMENT between two labelers, not accuracy, and it is not a bound
    on anyone's performance in either direction. v1 called it a lower bound on
    theirs. That was wrong: a disagreement can be their error or ours."""
    tree = LH.fromstring(raw_html)
    deep_parse(tree)
    host = host_for(site)
    nodes = tree.xpath("//*")
    seeds = {}
    for el in nodes:
        lab, _ = gt_provenance(el, host)
        if lab: seeds[el] = lab
    prov = {}
    for el in nodes:
        if el in seeds: prov[el] = seeds[el]
        else:
            p_ = el.getparent()
            prov[el] = prov[p_] if (p_ is not None and p_ in prov) else "D"
    regions = [el for el in nodes if prov[el] != "D"
               and (el.getparent() is None or prov.get(el.getparent(), "D") == "D")]
    return tree, regions, nodes   # nodes returned to pin the lxml proxies

# [A-3] negative controls, run before any paid call. If `body` scores well here,
# the scorer is broken and no result from it means anything.
demo = LH.fromstring(
    "<html><body><nav class=site-nav><a href=/>H</a><a href=/c>S</a><a href=/d>D</a></nav>"
    "<main><h1>P</h1><div class=opts><button>Buy</button><select><option>S</option></select></div>"
    "<div class=spec><ul><li>a</li><li>b</li><li>c</li></ul></div>"
    "<div class=review><p>Great</p><a href=/r/1>helpful</a></div></main>"
    "<footer class=site-footer><a href=/tos>T</a></footer></body></html>")
_pin = list(demo.iter())
dtruth = demo.cssselect(".review")
print(f"{'control':28s} {'P':>6s} {'R':>6s} {'F1':>6s} {'overmask':>9s}")
for name, pred in (("exact .review", ".review"),
                   ("official object shape", {"css_selector": ".review"}),
                   ("all-page mask (body)", "body"),
                   ("wrong region (nav)", "nav"),
                   ("empty prediction", [])):
    s = score(demo, dtruth, pred)
    print(f"{name:28s} {s['precision']:6.3f} {s['recall']:6.3f} {s['f1']:6.3f} "
          f"{s['overmask_ratio']:9.3f}")
assert score(demo, dtruth, "body")["f1"] < score(demo, dtruth, ".review")["f1"], \\
    "scorer still rewards masking the whole page"
assert score(demo, dtruth, {"css_selector": ".review"})["tp"] > 0, \\
    "scorer still discards the official object shape"
print("\\ncontrols pass: overmasking is charged and object-shaped predictions parse.")'''))

a(new_code_cell('''def ask_for_selectors(sanitized_html, site_label, prompt_template, model=MODEL):
    """One detection pass. Returns the model's proposed selectors, in whatever
    shape it emits them; idea3_score.py normalizes the known shapes and raises on
    anything it cannot interpret rather than silently scoring it as a miss."""
    require_prompt(prompt_template, UCM_COMMIT)     # [A-5c] no empty-prompt path
    prompt = prompt_template + (
        f"\\n\\nSite: {site_label}\\n"
        "Return ONLY a JSON array of CSS selectors identifying untrusted, "
        "third-party or user-generated regions. No prose.\\n\\n"
        f"HTML:\\n{sanitized_html}")
    # [1.16] through src/llm.py: budget cap, cost log, model_returned; a dry run logs the estimate only
    txt = llm.complete(model, prompt, max_tokens=2000, tag=f"{TASK_ID} {site_label}")
    if txt is None:
        print(f"  [DRY_RUN] would send {len(sanitized_html):,} chars for {site_label}")
        return None
    m = re.search(r"\\[.*\\]", txt, re.S)
    if not m:
        return dict(_unparsed=txt[:400])
    try:
        return json.loads(m.group(0))
    except Exception:
        return dict(_unparsed=txt[:400])

est_in = len(PAGES) * (MAX_HTML_CHARS / 3.5)
print(f"planned: {len(PAGES)} pages, roughly {est_in/1e6:.2f}M input tokens")
print("set DRY_RUN = False in the config cell when you are ready to spend that.")'''))

a(new_code_cell(long_cell('''results = []
for i, pg in enumerate(PAGES):
    try:
        tree, regions, _pin_nodes = ground_truth_untrusted(pg["html"], pg["site"])
    except Exception as e:
        print(f"  [{i+1}/{len(PAGES)}] {pg['site']:14s} parse failed: {str(e)[:60]}")
        continue
    san = sanitize(pg["html"])
    sel = ask_for_selectors(san, pg["site"], UCM_PROMPT)
    row = dict(corpus=pg["corpus"], site=pg["site"], n_regions=len(regions), model=MODEL,
               sanitized_chars=len(san), commit=UCM_COMMIT, sanitizer=SANITIZER)
    if sel is None:
        row["dry_run"] = True
    elif isinstance(sel, dict) and "_unparsed" in sel:
        row["unparsed"] = sel["_unparsed"]
    else:
        try:
            row.update(score(tree, regions, sel))
            row["selectors"] = sel if isinstance(sel, list) else [sel]
        except MalformedPrediction as e:
            row["malformed"] = str(e)
    results.append(row)
    print(f"  [{i+1}/{len(PAGES)}] {pg['corpus']:7s} {pg['site']:14s} "
          f"regions={len(regions):4d} " +
          (f"F1={row.get('f1', float('nan')):.3f} overmask={row.get('overmask_ratio', 0):.2f}"
           if "f1" in row else "(dry run)"))

os.makedirs(EXP_DIR, exist_ok=True)
json.dump(results, open(f"{EXP_DIR}/detection_results.json", "w"), indent=1)
f1s = [r["f1"] for r in results if "f1" in r and r.get("overmask_ratio", 1) <= 0.8]
push(f"{TASK_ID} detection: {len(results)} pages, non-degenerate mean F1 "
     f"{(sum(f1s) / len(f1s)) if f1s else float('nan'):.3f} (n={len(f1s)}), spent ${llm.spent:.2f}")
print(f"\\n{len(results)} rows written to {EXP_DIR}/detection_results.json")''')))

a(new_code_cell('''import numpy as np
scored = [r for r in results if "f1" in r]
if not scored:
    print("No scored rows. DRY_RUN is on, or every page failed. Nothing to report.")
else:
    print(f"{'corpus':8s} {'site':14s} {'n':>4s} {'P':>6s} {'R':>6s} {'F1':>6s} "
          f"{'overmask':>9s} {'truth':>7s}")
    byk = collections.defaultdict(list)
    for r in scored:
        byk[(r["corpus"], r["site"])].append(r)
    for (c, s), rs in sorted(byk.items()):
        f = lambda k: np.mean([x[k] for x in rs])
        print(f"{c:8s} {s:14s} {len(rs):4d} {f('precision'):6.3f} {f('recall'):6.3f} "
              f"{f('f1'):6.3f} {f('overmask_ratio'):9.3f} {f('truth_ratio'):7.3f}")

    # [A-3] a page where overmask_ratio approaches 1 has masked everything. Those
    # rows are not detections and must not be averaged in as if they were.
    degenerate = [r for r in scored if r["overmask_ratio"] > 0.8]
    print(f"\\ndegenerate (masked >80% of the page): {len(degenerate)}/{len(scored)}")
    if degenerate:
        print("  v1 would have scored these as successes. Exclude them or report")
        print("  them separately; do not average them into an F1.")
    clean = [r for r in scored if r["overmask_ratio"] <= 0.8]
    if clean:
        print(f"non-degenerate mean F1: {np.mean([r['f1'] for r in clean]):.3f} "
              f"over {len(clean)} pages")

    print("\\nWORDING FOR THE WRITE-UP [A-4]:")
    print("  These are agreement rates between a structure-only detector and our")
    print("  class-name heuristic. Neither is ground truth. A disagreement is")
    print("  evidence that one of them is wrong, and this design cannot say which.")
    print("  Do not describe any number here as a bound on UCM's performance.")'''))

a(new_markdown_cell("""## What this notebook can and cannot conclude

**Can:** whether the archive preserves the attribute surface a structure-only detector needs (Part 1, no key, already answered no for Mind2Web); whether live pages can be captured for the sites of interest (Part 2); how often a structure-only detector and a class-name heuristic pick out the same regions, per site and per corpus (Part 3).

**Cannot:** anything about UCM's accuracy. Both labelers here are heuristics with different inputs, and the design has no arbiter. Getting an accuracy number needs independent human ground truth on a sample that includes agreements and heuristic-negatives, not only disagreements. That is the next notebook to write, and it needs people, not a key.

**Carry these three facts into the paper regardless of what Part 3 returns:** the archive keeps 21 attribute names and no site-authored `data-*` on any of 57 sites (only a capture-tool attribute, `data_pw_testid_buckeye`; K21, `experiments/2026-09-25_1.8_attr-survival/`); the sanitizer actually used was `SANITIZER`; and the UCM commit was `UCM_COMMIT`."""))

a(new_code_cell(final_push("2.8")))

write(nb, f'{ROOT}/notebooks/colab/01_corpus_fidelity_and_structure_only_detection_v2.ipynb')

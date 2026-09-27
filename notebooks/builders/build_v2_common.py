"""Shared pieces for the v2 notebook builder.

Everything here changed because of the 19 Sep independent audit. The audit's
findings are cited inline as [A-n] so a reader can trace each change.
"""
from pathlib import Path as _Path
ROOT = _Path(__file__).resolve().parents[2]
import json, os
import nbformat as nbf
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell

FIX = str(ROOT / 'src')
PIPELINE = open(f'{FIX}/pipeline_v2.py').read()
SCORER = open(f'{FIX}/score_v2.py').read()

META = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "pygments_lexer": "ipython3",
                      "codemirror_mode": {"name": "ipython", "version": 3}, "version": "3.11"},
    "colab": {"provenance": []},
}

SECRETS = '''# Credentials come from the Colab secrets panel (key icon, left sidebar).
# Never paste a key into a notebook cell.
import os
def get_key(name):
    try:
        from google.colab import userdata
        v = userdata.get(name)
        if v: return v
    except Exception:
        pass
    return os.environ.get(name)

ANTHROPIC_API_KEY = get_key("ANTHROPIC_API_KEY")
OPENAI_API_KEY    = get_key("OPENAI_API_KEY")
print("anthropic key:", "present" if ANTHROPIC_API_KEY else "MISSING")
print("openai key   :", "present" if OPENAI_API_KEY else "MISSING")'''

WRITE_PIPELINE = "%%writefile idea3_pipeline.py\n" + PIPELINE
WRITE_SCORER = "%%writefile idea3_score.py\n" + SCORER

# [A-5] Notebook 01 v1 configured six sites and loaded only train_10.json, which
# holds three. The detection loop reached two Kohl's pages. A manifest that is
# built from what is actually loaded, and that refuses to continue when the
# requested sites are missing, makes that failure impossible to repeat silently.
MANIFEST = '''import json, collections, gc, os
from huggingface_hub import hf_hub_download

REPO, REV = "osunlp/Mind2Web", "17ece8eb89862368edc0cc806acee6fca5163474"
SHARD_SITES = {   # which shard holds which sites, measured once, not guessed
    "train_10.json": {"kohls", "sports.yahoo", "travelzoo"},
}

def fetch_shard(name):
    return hf_hub_download(repo_id=REPO, repo_type="dataset",
                           filename=f"data/train/{name}", revision=REV, local_dir="data")

def load_frame(sites_wanted, shards, per_site=3):
    """Load only the shards asked for, then report exactly which requested sites
    were found. Returns (frame, found, missing). The caller decides what to do
    about `missing` -- this function never quietly proceeds on a partial frame."""
    bysite = collections.defaultdict(list)
    for s in shards:
        p = fetch_shard(s)
        print(f"  loaded {s} ({os.path.getsize(p)/1e6:.0f} MB)")
        for t in json.load(open(p)):
            bysite[t["website"]].append(t)
        gc.collect()
    found = [s for s in sites_wanted if s in bysite]
    missing = [s for s in sites_wanted if s not in bysite]
    frame = []
    for s in found:
        frame += sorted(bysite[s], key=lambda t: t["annotation_id"])[:per_site]
    present = sorted(bysite)
    del bysite; gc.collect()
    return frame, found, missing, present'''


def write(nb, path):
    nb['metadata'] = META
    for i, c in enumerate(nb['cells']):   # fixed ids: a rebuild with no source change gives a byte-identical file
        c['id'] = f"cell-{i:03d}"
    with open(path, 'w') as f:
        nbf.write(nb, f)
    n_code = sum(1 for c in nb['cells'] if c['cell_type'] == 'code')
    print(f"wrote {os.path.basename(path)}: {len(nb['cells'])} cells "
          f"({n_code} code, {len(nb['cells'])-n_code} markdown), "
          f"{os.path.getsize(path):,} bytes")

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

SECRETS = '''# [1.16] Keys come from the Colab secrets panel (key icon, left sidebar), under the same
# names src/llm.py reads. Never paste a key into a cell; the notebook prints only presence.
import os
def get_key(name, fallback=None):
    try:
        from google.colab import userdata
        for n in (name, fallback):
            if not n: continue
            try:
                v = userdata.get(n)
            except Exception:
                v = None
            if v: return v
    except Exception:
        pass
    return os.environ.get(name) or (os.environ.get(fallback) if fallback else None)

for _name, _fallback in (("RESEARCH_ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY"),
                         ("OPENAI_API_KEY", None), ("GEMINI_API_KEY", None)):
    _v = get_key(_name, _fallback)
    if _v: os.environ[_name] = _v          # src/llm.py reads the environment
    print(f"{_name:27s}", "present" if _v else "missing")
os.environ.pop("ANTHROPIC_API_KEY", None)   # the research key must never double as Claude Code's own key'''

# ------------------------------------------------------------------ [1.13] git convention
# docs/NOTEBOOK_GIT_CONVENTION.md: config, clone or pull, push() with metric-valued messages,
# periodic push for long cells, results on colab/<task-id>, token from Colab secrets.
REPO_SLUG = "abidaziz1/Provenance-Label-Reliability-Criticality-and-Safety-in-Web-Agents"

def git_config(task_id, exp_name):
    return f'''TASK_ID    = "{task_id}"
REPO       = "{REPO_SLUG}"
REPO_DIR   = "/content/idea3"
BRANCH     = f"colab/{{TASK_ID}}"
GIT_USER   = "Alam"
GIT_EMAIL  = "139110271+abidaziz1@users.noreply.github.com"   # the repo owner's GitHub noreply address
PUSH_EVERY = 20                                      # minutes, long cells only
EXP_DIR    = "experiments/{exp_name}"               # Claude creates it, with config.yaml and budget, before any paid run'''

GIT_SETUP = '''import os, subprocess
try:
    from google.colab import userdata
    os.environ["GH_TOKEN_COLAB"] = userdata.get("GH_TOKEN_COLAB")
except Exception:
    pass                                             # outside Colab: set GH_TOKEN_COLAB yourself
askpass = "/content/.git-askpass" if os.path.isdir("/content") else os.path.expanduser("~/.git-askpass")
with open(askpass, "w") as f:
    f.write('#!/bin/sh\\ncase "$1" in Username*) echo x-access-token ;; *) echo "$GH_TOKEN_COLAB" ;; esac\\n')
os.chmod(askpass, 0o700)
os.environ["GIT_ASKPASS"] = askpass
os.environ["GIT_TERMINAL_PROMPT"] = "0"

def _git(*args, cwd=None):
    r = subprocess.run(["git", *args], capture_output=True, text=True, cwd=cwd)   # no shell: messages stay literal
    if r.returncode: print(r.stderr.strip()[-500:])
    return r

if not os.path.exists(REPO_DIR):
    _git("clone", f"https://github.com/{REPO}.git", REPO_DIR)
os.chdir(REPO_DIR)
_git("fetch", "origin")
_git("config", "user.name", GIT_USER); _git("config", "user.email", GIT_EMAIL)
_git("config", "core.hooksPath", ".githooks")       # the secret scan runs on every commit here too
on_remote = _git("ls-remote", "--heads", "origin", BRANCH).stdout.strip()
_git("checkout", "-B", BRANCH, f"origin/{BRANCH}" if on_remote else "origin/main")
print("ready on", _git("branch", "--show-current").stdout.strip())'''

PUSH_HELPER = '''from datetime import datetime

RESULT_PATHS = [EXP_DIR, "results/data_index.txt"]  # stage only result paths, never -A on the whole tree

def push(msg=None):
    msg = msg or f"{TASK_ID} checkpoint {datetime.now():%Y-%m-%d %H:%M}"
    paths = [p for p in RESULT_PATHS if os.path.exists(p)]
    if paths:
        _git("add", "-A", "--", *paths)
    if _git("commit", "-m", msg).returncode == 0:
        _git("push", "-u", "origin", BRANCH)
        print("pushed:", msg)'''

# [1.16] every paid call goes through src/llm.py, under the budget in EXP_DIR/config.yaml
LLM_SETUP = '''import sys
sys.path.insert(0, os.path.join(REPO_DIR, "src"))
from llm import LLM
os.environ["IDEA3_DRY_RUN"] = "1" if DRY_RUN else "0"
if not os.path.exists(os.path.join(EXP_DIR, "config.yaml")):
    raise SystemExit(f"{EXP_DIR}/config.yaml is missing. Claude creates the experiment folder, with its "
                     "pre-registration and budget_usd, before any run (skill: new-experiment).")
llm = LLM.from_experiment(EXP_DIR)
print(f"llm ready: budget ${llm.budget:.2f}, spent ${llm.spent:.4f}, reserved ${llm.reserved():.4f}, dry run {DRY_RUN}")'''

def final_push(task_id):
    return f'''push(f"{{TASK_ID}} notebook complete")
print("done")'''

def long_cell(body):
    """Wrap a long-running cell: a background thread pushes every PUSH_EVERY minutes, and the
    finally clause pushes even if the cell fails."""
    indented = "\n".join(("    " + ln) if ln.strip() else ln for ln in body.splitlines())
    return ('''import threading
_stop = threading.Event()
def _auto(every):
    while not _stop.wait(every * 60):
        push(f"{TASK_ID} checkpoint {datetime.now():%H:%M}")
threading.Thread(target=_auto, args=(PUSH_EVERY,), daemon=True).start()

try:
''' + indented + '''
finally:
    _stop.set()
    push(f"{TASK_ID} long cell finished")''')

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
    out_dir = os.environ.get('IDEA3_NB_OUT')          # tests build into a temp folder
    if out_dir: path = os.path.join(out_dir, os.path.basename(path))
    with open(path, 'w') as f:
        nbf.write(nb, f)
    n_code = sum(1 for c in nb['cells'] if c['cell_type'] == 'code')
    print(f"wrote {os.path.basename(path)}: {len(nb['cells'])} cells "
          f"({n_code} code, {len(nb['cells'])-n_code} markdown), "
          f"{os.path.getsize(path):,} bytes")

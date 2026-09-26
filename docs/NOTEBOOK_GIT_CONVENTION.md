# Notebook git convention (Colab)

Every notebook Alam runs in Colab keeps its results in this repo from the first cell. This follows Alam's research-notebook convention, adapted for a private repo and for review by Claude before anything reaches main.

## Rules

- Cell order: config, git setup, installs, imports and `push()`, work cells, final push.
- Pull before any work; push after every cell that produces a result worth keeping.
- Commit messages carry the numbers: `2.4 pilot done: compliance=0.31 (n=640), cost=$14.20`, never `update results`.
- Long cells (10 minutes or more) run a background thread that pushes every `PUSH_EVERY` minutes, inside `try/finally`, so a crash still pushes.
- Push to `colab/<task-id>`, never to main. Claude verifies the branch (skill: colab-intake), then opens a PR for Alam.
- Files over about 50 MB go to an orphan branch `data/<task-id>` in parts under 95 MB, with a `MANIFEST.json` of SHA-256 values. No Google Drive.
- The token comes from Colab secrets through `GIT_ASKPASS`, so it never appears in a URL, `.git/config`, a cell output or an error message.
- Commits stage only result paths (`RESULT_PATHS`), and the repo's pre-commit and commit-msg hooks run in Colab too.
- Code style in cells: short names, terse comments, no step-by-step prose.

## Cell templates

**Config**

```python
TASK_ID    = "2.7"
REPO       = "<owner>/<repo>"            # filled in by Claude when it builds the notebook
REPO_DIR   = "/content/idea3"
BRANCH     = f"colab/{TASK_ID}"
GIT_USER   = "Alam"
GIT_EMAIL  = "<the email on your GitHub account>"
PUSH_EVERY = 20                          # minutes, long cells only
```

**Git setup**

```python
import os, subprocess
from google.colab import userdata

os.environ["GH_TOKEN_COLAB"] = userdata.get("GH_TOKEN_COLAB")
askpass = "/content/.git-askpass"
with open(askpass, "w") as f:
    f.write('#!/bin/sh\ncase "$1" in Username*) echo x-access-token ;; *) echo "$GH_TOKEN_COLAB" ;; esac\n')
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
_git("config", "core.hooksPath", ".githooks")        # the secret scan runs on every commit here too
on_remote = _git("ls-remote", "--heads", "origin", BRANCH).stdout.strip()
_git("checkout", "-B", BRANCH, f"origin/{BRANCH}" if on_remote else "origin/main")
print("ready on", _git("branch", "--show-current").stdout.strip())
```

**Push helper**

```python
from datetime import datetime

RESULT_PATHS = ["experiments/", "results/data_index.txt"]   # stage only result paths, never -A on the whole tree

def push(msg=None):
    msg = msg or datetime.now().strftime("%Y-%m-%d %H:%M")
    paths = [p for p in RESULT_PATHS if os.path.exists(p)]
    if paths:
        _git("add", "-A", "--", *paths)
    if _git("commit", "-m", msg).returncode == 0:
        _git("push", "-u", "origin", BRANCH)
        print("pushed:", msg)
```

**Long cell**

```python
import threading

_stop = threading.Event()
def _auto(every):
    while not _stop.wait(every * 60):
        push(f"{TASK_ID} checkpoint {datetime.now():%H:%M}")
threading.Thread(target=_auto, args=(PUSH_EVERY,), daemon=True).start()

try:
    pass  # the long-running work
finally:
    _stop.set()
    push(f"{TASK_ID} run complete")
```

**Large files to an orphan data branch**

```python
import hashlib, json, glob

def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""): h.update(chunk)
    return h.hexdigest()

src = "/content/capture.zip"
d = f"/content/data_{TASK_ID}"
subprocess.run(["rm", "-rf", d]); os.makedirs(d)
subprocess.run(["split", "-b", "90m", src, f"{d}/capture.zip.part_"], check=True)
man = {"source": os.path.basename(src), "sha256": _sha(src),
       "parts": {os.path.basename(p): _sha(p) for p in sorted(glob.glob(f"{d}/*.part_*"))}}
json.dump(man, open(f"{d}/MANIFEST.json", "w"), indent=1)
_git("init", "-q", cwd=d); _git("checkout", "-q", "-b", f"data/{TASK_ID}", cwd=d)
_git("add", "-A", cwd=d)
_git("-c", f"user.name={GIT_USER}", "-c", f"user.email={GIT_EMAIL}", "commit", "-qm",
     f"data {TASK_ID}: {len(man['parts'])} parts", cwd=d)
_git("push", "-q", f"https://github.com/{REPO}.git", f"data/{TASK_ID}", cwd=d)
with open("results/data_index.txt", "a") as f:
    f.write(f"{TASK_ID}: branch data/{TASK_ID}, {man['source']} sha256 {man['sha256']}\n")
push(f"{TASK_ID} capture on data/{TASK_ID}: {len(man['parts'])} parts")
```

**Final cell**

```python
push(f"{TASK_ID} notebook complete")
print("done")
```

## Notes

- `GIT_EMAIL` should be the email on Alam's GitHub account (or his GitHub noreply address), so commits are attributed to him.
- Keys the notebook needs come from Colab secrets with `userdata.get`: `RESEARCH_ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`. The v2 notebooks still read `ANTHROPIC_API_KEY`; task 1.16 switches them (with a fallback to the old name). The notebook never prints a key.
- Task 1.13 retrofits the three v2 notebook builders in `notebooks/builders/` with these cells.

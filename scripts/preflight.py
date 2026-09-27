#!/usr/bin/env python3
"""Check what this environment can do, without ever printing a secret.

Reports only: whether each variable is set, HTTP status codes, tool availability, data presence.
Run it in the first session of any new environment and paste the table into STATUS.md.

Cloud note: with an API credential attached in the environment settings, the agent proxy adds the key
to requests for that host, so a call can return 200 even when the variable is absent or holds the
placeholder `proxy-injected`. That is the intended setup for OpenAI, Gemini and Hugging Face.
"""
import os, shutil, subprocess, sys, urllib.error, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VARS = ["RESEARCH_ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "HF_TOKEN",
        "SLACK_WEBHOOK_URL", "GH_TOKEN", "DOCKERHUB_TOKEN"]


def status(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {}, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status
    except urllib.error.HTTPError as e:
        reason = e.headers.get("x-deny-reason") if e.headers else None
        return f"{e.code} ({reason})" if reason else e.code
    except Exception as e:
        return f"unreachable ({type(e).__name__})"


def sh(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=40)
        return r.returncode, r.stdout.strip()
    except Exception:
        return 1, ""


def state(v):
    val = os.environ.get(v)
    if not val:
        return "absent"
    return "placeholder (proxy-injected)" if val == "proxy-injected" else "set"


def main():
    rows = [("where", "remote session" if os.environ.get("CLAUDE_CODE_REMOTE") == "true" else "local"),
            ("python", sys.version.split()[0])]
    rows += [(f"env {v}", state(v)) for v in VARS]

    ak = os.environ.get("RESEARCH_ANTHROPIC_API_KEY", "")
    ok_ = os.environ.get("OPENAI_API_KEY", "")
    gk = os.environ.get("GEMINI_API_KEY", "")
    hk = os.environ.get("HF_TOKEN", "")
    rows.append(("anthropic /v1/models (research key)",
                 status("https://api.anthropic.com/v1/models",
                        {"x-api-key": ak, "anthropic-version": "2023-06-01"}) if ak else "skipped: key absent"))
    rows.append(("openai /v1/models",
                 status("https://api.openai.com/v1/models", {"Authorization": f"Bearer {ok_}"} if ok_ else None)))
    rows.append(("gemini /v1beta/models",
                 status("https://generativelanguage.googleapis.com/v1beta/models", {"x-goog-api-key": gk} if gk else None)))
    rows.append(("huggingface Mind2Web api",
                 status("https://huggingface.co/api/datasets/osunlp/Mind2Web",
                        {"Authorization": f"Bearer {hk}"} if hk and hk != "proxy-injected" else None)))
    for name, url in [("arxiv.org", "https://arxiv.org/abs/2607.08147"),
                      ("export.arxiv.org api", "https://export.arxiv.org/api/query?search_query=all:prompt+injection&max_results=1"),
                      ("semantic scholar api", "https://api.semanticscholar.org/graph/v1/paper/arXiv:2607.05277?fields=title"),
                      ("openreview.net", "https://openreview.net/"),
                      ("api.openalex.org", "https://api.openalex.org/works?search=prompt%20injection&per_page=1"),
                      ("doi.org", "https://doi.org/10.1145/362375.362389"),
                      ("dl.acm.org", "https://dl.acm.org/"),
                      ("pypi.org", "https://pypi.org/simple/lxml/")]:
        rows.append((name, status(url)))

    rc, remote = sh("git remote get-url origin")
    slug = ""
    if rc == 0 and "github.com" in remote:
        slug = remote.split("github.com")[-1].lstrip(":/").removesuffix(".git")
    if slug and shutil.which("gh"):
        rc1, _ = sh(f"gh api repos/{slug} --jq .full_name")
        rc2, _ = sh(f"gh api 'repos/{slug}/issues?per_page=1' --jq length")
        rc3, _ = sh(f"gh api 'repos/{slug}/labels/needs-human' --jq .name")
        rows += [("gh REST: repo", "ok" if rc1 == 0 else "failed"),
                 ("gh REST: issues read", "ok" if rc2 == 0 else "failed"),
                 ("label needs-human", "exists" if rc3 == 0 else "missing (create it, task 0.1)")]
    else:
        rows.append(("gh", "no GitHub remote or gh missing"))

    rows.append(("git ls-remote UCM repo", "ok" if sh("git ls-remote https://github.com/ethz-spylab/untrusted-content-masking HEAD")[0] == 0
                 else "failed (clone via codeload.github.com, or ask Alam to fork it)"))
    rows.append(("gh on PATH", "yes" if shutil.which("gh") else "no (setup script installs it)"))
    rows.append(("docker", "ok" if sh("docker info")[0] == 0 else "daemon not running (start: dockerd > /tmp/dockerd.log 2>&1 &)"))
    rows.append(("git hooksPath", sh("git config core.hooksPath")[1] or "unset (run: git config core.hooksPath .githooks)"))
    train = ROOT / "data" / "mind2web" / "data" / "train"
    shards = sorted(p.name for p in train.glob("train_*.json")) if train.exists() else []
    rows.append(("mind2web shards", ", ".join(shards) or "none (run: python3 scripts/fetch_mind2web.py)"))
    rows.append(("disk free GB", round(shutil.disk_usage(ROOT).free / 1e9, 1)))
    rows.append(("cpus", os.cpu_count()))
    try:
        mem = next(l for l in open("/proc/meminfo") if l.startswith("MemTotal"))
        rows.append(("RAM GB", round(int(mem.split()[1]) / 1e6, 1)))
    except Exception:
        rows.append(("RAM GB", "unknown"))

    print("| check | result |\n|---|---|")
    for k, v in rows:
        print(f"| {k} | {v} |")
    print("\nCodes: 200 = reachable and authorized. 401 or 403 from the API itself = reachable, key missing or wrong."
          " 403 (host_not_allowed) = the environment's network allowlist blocks the host: add it (docs/OPERATIONS.md).")


if __name__ == "__main__":
    main()

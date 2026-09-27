#!/usr/bin/env python3
"""Block commits that contain credentials. Prints file:line and the pattern name, never the value.

  python3 scripts/scan_secrets.py              scan every tracked file
  python3 scripts/scan_secrets.py --staged     scan the staged content about to be committed (pre-commit hook)
  python3 scripts/scan_secrets.py --all        scan the working tree, tracked or not, skipping gitignored files and data/
  python3 scripts/scan_secrets.py --msg FILE   scan a commit message (commit-msg hook)
Exit code 1 when anything is found. A net, not a guarantee: it knows common key formats only.
"""
import re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "anthropic_key":   r"sk-ant-[A-Za-z0-9_\-]{20,}",
    "openai_key":      r"sk-(?:proj-|svcacct-|admin-)?[A-Za-z0-9_\-]{32,}",
    "google_api_key":  r"AIza[0-9A-Za-z_\-]{35}",
    "github_token":    r"(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{22,})",
    "slack_token":     r"xox[baprs]-[A-Za-z0-9\-]{10,}",
    "slack_webhook":   r"https://hooks\.slack\.com/services/[A-Za-z0-9/_\-]{20,}",
    "aws_access_key":  r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b",
    "hf_token":        r"\bhf_[A-Za-z0-9]{30,}\b",
    "docker_pat":      r"\bdckr_pat_[A-Za-z0-9_\-]{20,}",
    "private_key":     r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----",
    "gcp_sa_key":      r"\"private_key_id\"\s*:\s*\"[0-9a-f]{20,}\"",
    "bearer_literal":  r"(?i)authorization:\s*bearer\s+[A-Za-z0-9_\-\.]{24,}",
    "assigned_secret": r"(?i)\b(?:api[_-]?key|secret|token|password)\b\s*[:=]\s*['\"][A-Za-z0-9_\-\/\+]{24,}['\"]",
}
RX = {k: re.compile(v) for k, v in PATTERNS.items()}
SKIP_DIRS = {".git", "data", "node_modules", "__pycache__", ".venv"}
SKIP_SUFFIX = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".gz", ".parquet", ".pt", ".bin"}
MAX_BYTES = 20_000_000


def git(*args):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    return r.returncode, r.stdout


def in_git_repo():
    return git("rev-parse", "--is-inside-work-tree")[0] == 0


def targets(mode):
    """Yield (display path, text or None to read from disk, path on disk)."""
    if mode == "--staged":
        _, out = git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z")
        for f in [x for x in out.decode().split("\0") if x]:
            rc, blob = git("show", f":{f}")
            yield f, (blob.decode(errors="ignore") if rc == 0 else None), ROOT / f
        return
    if mode == "--all":
        ignored = set()
        if in_git_repo():
            _, out = git("ls-files", "--others", "--ignored", "--exclude-standard", "-z")
            ignored = {x for x in out.decode().split("\0") if x}
        for p in ROOT.rglob("*"):
            if not p.is_file():
                continue
            rel = p.relative_to(ROOT)
            if set(rel.parts) & SKIP_DIRS or str(rel) in ignored:
                continue
            yield str(rel), None, p
        return
    _, out = git("ls-files", "-z")
    for f in [x for x in out.decode().split("\0") if x]:
        yield f, None, ROOT / f


def scan_text(name, text):
    hits = []
    for n, line in enumerate(text.splitlines(), 1):
        for pname, rx in RX.items():
            if rx.search(line):
                hits.append((name, n, pname))
    return hits


def scan(items):
    hits = []
    for item in items:
        if isinstance(item, Path):                      # backwards compatible: a bare path
            item = (str(item.relative_to(ROOT)) if item.is_absolute() else str(item), None, item)
        name, text, path = item
        parts = set(Path(name).parts)
        if parts & SKIP_DIRS or Path(name).suffix.lower() in SKIP_SUFFIX:
            continue
        if Path(name).name == ".env" or re.fullmatch(r"\.env\.[\w.-]+", Path(name).name or ""):
            hits.append((name, 0, "dotenv_file"))       # a tracked or staged .env is a finding by itself
            continue
        if text is None:
            if not path.exists() or path.stat().st_size > MAX_BYTES:
                continue
            try:
                text = path.read_text(errors="ignore")
            except Exception:
                continue
        hits += scan_text(name, text)
    return hits


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "--msg":
        text = Path(sys.argv[2]).read_text(errors="ignore") if len(sys.argv) > 2 else ""
        hits = scan_text("commit message", text)
    else:
        hits = scan(targets(mode))
    if hits:
        for name, n, pname in hits:
            print(f"SECRET? {name}:{n}  [{pname}]")
        print(f"secret scan FAILED: {len(hits)} finding(s). Remove the value, use an environment variable, "
              f"and if it was ever pushed, tell Alam to rotate it.")
        sys.exit(1)
    print("secret scan clean")


if __name__ == "__main__":
    main()

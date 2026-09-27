#!/usr/bin/env python3
"""Download the Mind2Web train shards at the pinned revision used by every Idea 3 number.

  python3 scripts/fetch_mind2web.py                 the 3 shards the published frame uses (1.27 GB)
  python3 scripts/fetch_mind2web.py --all           all 11 train shards (about 6 GB), task 1.10
  python3 scripts/fetch_mind2web.py --dest /opt/idea3-data/mind2web   cache outside the repo

Files land in <dest>/data/train/. The repo expects them at data/mind2web/data/train/; when --dest
is elsewhere, the script links data/mind2web to it. data/ is gitignored. The dataset is public,
so no token is needed; HF_TOKEN is used only if set, to avoid rate limits.
"""
import argparse, hashlib, json, os, sys
from pathlib import Path

REPO, REV = "osunlp/Mind2Web", "17ece8eb89862368edc0cc806acee6fca5163474"
FRAME = ["train_0.json", "train_1.json", "train_10.json"]
ALL = [f"train_{i}.json" for i in range(11)]
ROOT = Path(__file__).resolve().parents[1]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--dest", default=str(ROOT / "data" / "mind2web"))
    ap.add_argument("--sha", action="store_true", help="print sha256 of each shard (slow)")
    a = ap.parse_args()
    from huggingface_hub import hf_hub_download
    dest = Path(a.dest); dest.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for name in (ALL if a.all else FRAME):
        p = hf_hub_download(repo_id=REPO, repo_type="dataset", filename=f"data/train/{name}",
                            revision=REV, local_dir=str(dest), token=os.environ.get("HF_TOKEN") or None)
        size = os.path.getsize(p)
        manifest[name] = {"bytes": size}
        if a.sha:
            h = hashlib.sha256()
            with open(p, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""): h.update(chunk)
            manifest[name]["sha256"] = h.hexdigest()
        print(f"{name}: {size/1e6:.0f} MB")
    link = ROOT / "data" / "mind2web"
    if dest.resolve() != link.resolve():
        link.parent.mkdir(exist_ok=True)
        if link.is_symlink() or not link.exists():
            if link.is_symlink(): link.unlink()
            link.symlink_to(dest, target_is_directory=True)
            print(f"linked {link} -> {dest}")
    (dest / "MANIFEST.json").write_text(json.dumps({"repo": REPO, "revision": REV, "files": manifest}, indent=1))
    print("done")

if __name__ == "__main__":
    sys.exit(main())

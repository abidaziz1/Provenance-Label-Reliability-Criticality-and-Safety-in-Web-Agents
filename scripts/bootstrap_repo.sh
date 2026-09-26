#!/bin/bash
# One-time: turn the unzipped handoff kit into your GitHub repo, with the baseline tag.
# Usage: bash scripts/bootstrap_repo.sh https://github.com/<you>/<repo>.git
# The GitHub repo must exist, be private and be empty (no README, no license).
# Your machine must be able to push to GitHub over HTTPS: sign in once with `gh auth login`,
# Git Credential Manager, or GitHub Desktop.
set -euo pipefail
URL="${1:?usage: bash scripts/bootstrap_repo.sh https://github.com/<you>/<repo>.git}"
cd "$(dirname "$0")/.."
if [ -d .git ]; then echo "This folder is already a git repo. Stopping."; exit 1; fi
if ! git config --global user.email >/dev/null; then
  echo "Set your git identity first: git config --global user.name 'Your Name'; git config --global user.email 'you@example.com'"
  exit 1
fi
python3 scripts/scan_secrets.py --all
git init -q
git checkout -q -b main   # works on git older than 2.28, where init -b does not exist
git config core.hooksPath .githooks
git add -A
git commit -q -m "v2.0 baseline: Idea 3 handoff kit (25 Sep 2026)"
git tag v2.0-baseline
git remote add origin "$URL"
git push -u origin main
git push origin v2.0-baseline
echo "Pushed main and tag v2.0-baseline to $URL"

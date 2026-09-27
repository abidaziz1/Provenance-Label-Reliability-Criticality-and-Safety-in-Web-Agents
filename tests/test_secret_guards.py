import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "scripts" / "guard_commands.py"

def _decision(cmd):
    r = subprocess.run([sys.executable, str(HOOK)], input=json.dumps({"tool_input": {"command": cmd}}),
                       capture_output=True, text=True)
    return json.loads(r.stdout)["hookSpecificOutput"]["permissionDecision"] if r.stdout.strip() else "pass"

BLOCK = [
    # printing the environment or a key
    "printenv", "printenv RESEARCH_ANTHROPIC_API_KEY", "env", "env -0", "/usr/bin/env", "(env)", "ls\nenv",
    "env | grep KEY", "export", "export -p", "declare -p", "declare -x", "typeset -p FOO", "set",
    "set -x; curl -H x https://api.anthropic.com", "bash -x run.sh",
    "echo $OPENAI_API_KEY", "echo ${RESEARCH_ANTHROPIC_API_KEY}", "echo \"$SLACK_WEBHOOK_URL\"",
    "printf '%s' \"$GEMINI_API_KEY\"", "echo $DOCKERHUB_TOKEN",
    "cat /proc/self/environ", "python3 -c 'import os; print(os.environ)'",
    "python3 -c 'import os, json; print(json.dumps(dict(os.environ)))'",
    # reading key files
    "cat .env", "head -3 ./.env", "grep KEY .env", "cat .env.local", "cat ~/.git-credentials",
    "cat ~/.docker/config.json", "cat secrets/gcp-service-account.json", "cat ~/.config/gh/hosts.yml",
    # staging secrets, skipping the scan
    "git add .env", "git add -f results/x", "git add --force x", "git add -Af x",
    "git commit --no-verify -m x", "git commit -n -m x", "git commit -nm x",
    "git -c core.hooksPath=/dev/null commit -m x", "git config --unset core.hooksPath",
    "git config core.hooksPath /tmp/none",
    # history and main
    "git push --force origin claude/x", "git push -f", "git push origin +claude/x", "git -C repo push --force",
    "git push --force-with-lease origin claude/x", "git push origin main", "git push -u origin main",
    "git push origin HEAD:main", "git push origin claude/x:refs/heads/main", "git push --all origin",
    "gh pr merge 12 --merge", "gh api -X PUT repos/o/r/pulls/12/merge", "cd r && gh pr merge 3",
    # verbose network
    "curl -v https://api.openai.com/v1/models", "curl -sv https://x", "curl -vvv https://x",
    "curl --trace-ascii - https://x",
]
ALLOW = [
    "python3 scripts/reconcile.py", "git add scripts/ src/", "git add experiments/2026-10-01_3.6_target-free-gates/",
    "git add results/final-figures.json scripts/fig-fidelity.py", "git add -A",
    "git commit -m 'exp(2.4): pilot done'", "git commit -m \"fix the -n flag in notebook 2\"",
    "git push origin task/2.4-nb3-pilot", "git push -u origin claude/idea3-session-abc", "git push",
    "git fetch origin && git merge origin/main", "git config core.hooksPath .githooks", "git config core.hooksPath",
    "test -n \"$OPENAI_API_KEY\" && echo present", "cat results/README.md", "cat env.example",
    "curl -s -o /dev/null -w '%{http_code}' https://huggingface.co", "python3 -m pytest -q",
    "ls -la env.example", "grep -n env_var docs/OPERATIONS.md",
    "docker login -u \"$DOCKERHUB_USER\" --password-stdin <<< \"$DOCKERHUB_TOKEN\"",
    "set -euo pipefail", "env IDEA3_DRY_RUN=1 python3 run.py", "IDEA3_DRY_RUN=1 python3 run.py",
    "export IDEA3_DRY_RUN=1", "gh api 'repos/o/r/pulls?state=all'", "gh pr create --title x --body-file b.md",
    "gh api repos/o/r/issues -f title=x -F body=@b.md -f 'labels[]=needs-human'",
    "python3 -c \"import os; print(bool(os.environ.get('OPENAI_API_KEY')))\"",
    "git log --oneline main", "git diff main...HEAD", "git merge-base main HEAD",
]

def test_hook_blocks_secret_leaks_and_merges():
    for cmd in BLOCK:
        assert _decision(cmd) == "deny", cmd

def test_hook_allows_normal_work():
    for cmd in ALLOW:
        assert _decision(cmd) == "pass", cmd

def test_scanner_finds_and_masks(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import scan_secrets as S
    fake = "sk" + "-ant-" + "api03-" + "Z" * 40
    p = ROOT / "tests" / "_tmp_leak.txt"
    p.write_text(f"key = {fake}\n")
    try:
        hits = S.scan([p])
        assert hits and hits[0][2] == "anthropic_key"
    finally:
        p.unlink()

def test_repo_is_clean():
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "scan_secrets.py"), "--all"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout

def test_commit_message_scan(tmp_path):
    fake = "sk" + "-ant-" + "api03-" + "Q" * 40
    bad = tmp_path / "msg_bad"; bad.write_text(f"exp(2.2): done, key {fake}\n")
    good = tmp_path / "msg_good"; good.write_text("exp(2.2): pilot done, false-trust 21% (n=300)\n")
    scan = [sys.executable, str(ROOT / "scripts" / "scan_secrets.py"), "--msg"]
    assert subprocess.run(scan + [str(bad)], capture_output=True).returncode == 1
    assert subprocess.run(scan + [str(good)], capture_output=True).returncode == 0

def test_all_mode_skips_gitignored_env():
    inside = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=ROOT, capture_output=True).returncode == 0
    if not inside:
        return  # before the repo exists there is no .gitignore context to test
    env = ROOT / ".env"
    if env.exists():
        return  # never touch a real local .env
    env.write_text("RESEARCH_ANTHROPIC_API_KEY=" + "sk" + "-ant-" + "api03-" + "R" * 40 + "\n")
    try:
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "scan_secrets.py"), "--all"], capture_output=True, text=True)
        assert r.returncode == 0, r.stdout
    finally:
        env.unlink()

def test_scanner_finds_new_google_key_format(tmp_path):
    sys.path.insert(0, str(ROOT / "scripts"))
    import scan_secrets as S
    fake = "AQ" + "." + "Ab8" + "x" * 47          # built at runtime so this file holds no key-shaped literal
    hits = [name for name, rx in S.RX.items() if rx.search("GEMINI_API_KEY=" + fake)]
    assert "google_api_key_aq" in hits
    assert not S.RX["google_api_key_aq"].search("see section AQ.1 of the report")


def test_scanner_finds_stripe_and_resend_keys():
    sys.path.insert(0, str(ROOT / "scripts"))
    import scan_secrets as S
    # built at runtime so this file holds no key-shaped literal
    cases = {"stripe_key": "sk" + "_test_" + "51" + "Ab" * 12, "stripe_webhook": "whsec" + "_" + "Z" * 30,
             "resend_key": "re" + "_" + "AbCdEfGh12" + "_" + "XyZ" * 6}
    for name, fake in cases.items():
        assert S.RX[name].search("KEY=" + fake), name
    assert not S.RX["resend_key"].search("see re_run_all_scripts in the log")
    assert not S.RX["stripe_key"].search("pk_test_suite")

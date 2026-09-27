#!/usr/bin/env python3
"""Claude Code PreToolUse hook for Bash.

Reads the tool call as JSON on stdin and denies commands that would print secrets, read key files,
stage secret files, skip the secret scan, rewrite shared history, push to main or merge a PR.
It is a second layer behind the deny rules in .claude/settings.json. Neither layer is a sandbox:
a script can still read the environment, so the rules in CLAUDE.md apply regardless.
"""
import json, re, sys

SECRET_VAR = (r"(?:RESEARCH_ANTHROPIC_API_KEY|ANTHROPIC_API_KEY|OPENAI_API_KEY|GEMINI_API_KEY|GOOGLE_API_KEY|"
              r"HF_TOKEN|HUGGING_FACE_HUB_TOKEN|SLACK_WEBHOOK_URL|DOCKERHUB_TOKEN|GH_TOKEN|GITHUB_TOKEN|"
              r"GH_TOKEN_COLAB|[A-Z0-9_]*(?:KEY|TOKEN|SECRET|PASSWORD|CREDENTIAL|WEBHOOK)[A-Z0-9_]*)")
SECRET_FILE = (r"(?:(?<![\w.])\.env(?:\.[\w.-]+)?(?![\w.])|\.git-credentials|\.netrc|\.docker/config\.json|"
               r"gh/hosts\.yml|huggingface/token|service-account[^\s'\"]*\.json|credentials[^\s'\"]*\.json|"
               r"[^\s'\"]+\.pem\b|/proc/[^/\s]+/environ)")
READERS = r"(?:cat|less|more|head|tail|bat|nl|strings|xxd|od|hexdump|grep|egrep|rg|awk|sed|base64|cut|sort|uniq|tee|cp|scp|curl)"

# Rules applied to the whole command text.
WHOLE = [
    (r"\b(?:echo|printf)\b[^\n;&|]*\$\{?" + SECRET_VAR + r"\b", "echoes a secret variable"),
    (r"(?:print|pprint|sys\.stdout\.write|json\.dumps)\s*\((?!\s*(?:bool|len)\s*\()[^\n]*(?:os\.environ|os\.getenv|environ\.get)",
     "prints environment values from Python"),
    (r"\b(?:dict|list|sorted)\s*\(\s*os\.environ\b|os\.environ\.(?:items|keys|values|copy)\s*\(", "dumps the Python environment"),
    (r"/proc/[^/\s]+/environ", "reads a process environment"),
    (r"\bgh\s+pr\s+merge\b", "merging into main is Alam's step"),
    (r"\bgh\s+api\b[^\n;&|]*/merge(?:\s|$|['\"?])", "merging into main is Alam's step"),
    (r"\bgh\s+api\s+graphql\b[^\n]*mergePullRequest", "merging into main is Alam's step"),
]

# Rules applied to each command segment, after quoted strings are removed.
SEGMENT = [
    (r"^(?:\S*/)?printenv\b", "prints environment variables"),
    (r"^(?:\S*/)?env(?:\s+-[-\w]+)*$", "prints every environment variable"),
    (r"^(?:export|declare|typeset)(?:\s+-[a-zA-Z]+)*$", "prints exported variables"),
    (r"^(?:declare|typeset)\s+-[a-zA-Z]*p\b", "prints variables"),
    (r"^set$", "prints all shell variables"),
    (r"^set\s+-[a-zA-Z]*x", "shell tracing prints expanded commands, including keys"),
    (r"^(?:\S*/)?(?:ba|z|da|k)?sh\s+-[a-zA-Z]*x", "shell tracing prints expanded commands, including keys"),
    (r"^" + READERS + r"\b.*" + SECRET_FILE, "reads a secret or credentials file"),
    (r"^(?:\S*/)?curl\b.*(?:\s-[a-zA-Z]*v[a-zA-Z]*(?:\s|$)|\s--verbose\b|\s--trace)", "verbose curl prints request headers, including keys"),
    (r"^(?:\S*/)?wget\b.*(?:\s-d\b|\s--debug\b)", "wget debug output prints request headers"),
]

GIT = re.compile(r"^git((?:\s+(?:-C\s+\S+|-c\s+\S+|--[\w-]+(?:=\S+)?))*)\s+([\w-]+)(.*)$")


def strip_quotes(s):
    return re.sub(r"'[^']*'|\"(?:\\.|[^\"\\])*\"", " Q ", s)


def segments(cmd):
    parts = re.split(r"\n|;|&&|\|\||\||&|\$\(|`|\(|\)|\{|\}", cmd)
    return [p.strip() for p in parts if p.strip()]


def git_rule(seg):
    m = GIT.match(seg)
    if not m:
        return None
    opts, sub, args = m.group(1), m.group(2), m.group(3)
    if re.search(r"core\.hookspath", opts, re.I):
        return "overrides the pre-commit hook path"
    if sub == "config" and re.search(r"core\.hookspath", args, re.I):
        if not re.fullmatch(r"\s*(?:--get\s+)?core\.hooksPath(?:\s+\.githooks)?\s*", args, re.I):
            return "changes the pre-commit hook path"
    if sub == "add":
        if re.search(r"(?:^|\s)(?:-f|--force)(?=\s|$)|(?:^|\s)-[a-zA-Z]*f[a-zA-Z]*(?=\s|$)", args):
            return "force-adds ignored files, which is how secrets get committed"
        if re.search(r"(?:^|[\s/])\.env(?:\.[\w.-]+)?(?=\s|$)", args):
            return "stages a .env file"
    if sub == "commit":
        if re.search(r"(?:^|\s)--no-verify\b|(?:^|\s)-[a-zA-Z]*n[a-zA-Z]*(?=\s|$)", args):
            return "skips the secret-scan hook"
    if sub == "push":
        if re.search(r"(?:^|\s)(?:-f|--force|--force-with-lease|--force-if-includes)(?=[\s=]|$)|(?:^|\s)-[a-zA-Z]*f[a-zA-Z]*(?=\s|$)|(?:^|\s)\+\S", args):
            return "force-push rewrites shared history"
        if re.search(r"(?:^|\s)(?:--all|--mirror|--delete|-d)(?=\s|$)", args):
            return "pushes or deletes more than your own branch"
        if re.search(r"(?:^|[\s:])(?:refs/heads/)?main(?=\s|$)", args):
            return "pushes to main; Alam merges into main"
        if re.search(r"(?:^|\s)--no-verify\b", args):
            return "skips hooks"
    return None


def check(cmd):
    for rx, why in WHOLE:
        if re.search(rx, cmd):
            return why
    for seg in segments(cmd):
        s = strip_quotes(seg)
        s = re.sub(r"^(?:sudo\s+|command\s+|time\s+|nohup\s+|exec\s+)+", "", s)
        s = re.sub(r"^(?:[A-Za-z_][A-Za-z0-9_]*=\S*\s+)+", "", s)   # leading VAR=value assignments
        for rx, why in SEGMENT:
            if re.search(rx, s):
                return why
        why = git_rule(s)
        if why:
            return why
    return None


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    cmd = (data.get("tool_input") or {}).get("command") or ""
    why = check(cmd)
    if why:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": f"Blocked by .claude/hooks/guard_secrets.py: {why}. "
                                        "Check a key's presence with `test -n \"$VAR\"`; see CLAUDE.md."}}))
    sys.exit(0)


if __name__ == "__main__":
    main()

"""Budgeted, logged model calls for Idea 3 experiments.

Every paid model call in this repo goes through `LLM.complete`. It:
- reads keys only from environment variables, never from files in the repo;
- refuses a call that could push the run past its budget (BudgetExceeded);
- refuses a model with no verified price in PRICES (UnknownPrice), so costs are never guessed;
- appends one JSON line per call to <run_dir>/llm_calls.jsonl and keeps <run_dir>/cost.json current;
- logs token counts, cost, latency and a sha256 of the prompt, never keys, headers or prompt text.

Key variables:
  RESEARCH_ANTHROPIC_API_KEY  research key for Claude models. Deliberately NOT named
                              ANTHROPIC_API_KEY, so Claude Code never picks it up for its own auth.
  OPENAI_API_KEY              or the literal value "proxy-injected" when a Claude Code cloud
                              environment attaches the real key as an API credential.
  GEMINI_API_KEY              optional; or "proxy-injected" when attached as an API credential.
                              scripts/preflight.py reports whether Google's API is reachable.
Set IDEA3_DRY_RUN=1 to log estimated costs without any network call.
Open a client with LLM.from_experiment(<experiment folder>), which reads budget_usd from its config.yaml.
Not yet here: the Batch API (task 1.15). ROADMAP.md budgets assume its 50% discount, so until 1.15 lands
price runs at list price.
"""
from __future__ import annotations
import hashlib, json, os, re, time
from dataclasses import dataclass
from pathlib import Path

# USD per 1M tokens (input, output). Verified list prices, Sep 2026. Add a model only after
# checking its official pricing page, and cite the page in the commit message.
PRICES = {
    "claude-sonnet-5":   (2.00, 10.00),
    "claude-sonnet-4-5": (3.00, 15.00),
    "claude-haiku-4-5":  (1.00, 5.00),
    "claude-opus-5-5":   (4.00, 20.00),
    "gpt-5.4-mini":      (0.75, 4.50),
}
KEY_ENV = {"anthropic": "RESEARCH_ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY"}
CHARS_PER_TOKEN_EST = 2.8   # conservative: measured 2.87 on agent observations, 3.98 on sanitized HTML

class BudgetExceeded(RuntimeError): pass
class UnknownPrice(RuntimeError): pass
class MissingKey(RuntimeError): pass

_SECRETISH = re.compile(r"(sk-[A-Za-z0-9_\-]{8,}|AIza[0-9A-Za-z_\-]{10,}|gh[pousr]_[A-Za-z0-9]{10,}|github_pat_[A-Za-z0-9_]{10,}|xox[baprs]-[A-Za-z0-9\-]{8,}|hf_[A-Za-z0-9]{10,})")

def redact(text: str) -> str:
    return _SECRETISH.sub("[REDACTED]", str(text))

def provider_of(model: str) -> str:
    if model.startswith("claude"): return "anthropic"
    if model.startswith("gpt") or model.startswith("o"): return "openai"
    if model.startswith("gemini"): return "gemini"
    raise ValueError(f"cannot infer provider for {model}")

@dataclass
class Usage:
    input_tokens: int
    output_tokens: int

class LLM:
    def __init__(self, run_dir, budget_usd: float, client_factory=None):
        self.run_dir = Path(run_dir); self.run_dir.mkdir(parents=True, exist_ok=True)
        self.budget = float(budget_usd)
        self.log_path = self.run_dir / "llm_calls.jsonl"
        self.cost_path = self.run_dir / "cost.json"
        self.spent = json.loads(self.cost_path.read_text())["spent_usd"] if self.cost_path.exists() else 0.0
        self._factory = client_factory or _default_client
        self._clients = {}
        self.dry = os.environ.get("IDEA3_DRY_RUN") == "1"

    def _client(self, provider):
        if provider not in self._clients:
            key = os.environ.get(KEY_ENV[provider])
            if not key and not self.dry:
                raise MissingKey(f"{KEY_ENV[provider]} is not set. Ask Alam via a needs-human issue; never ask for the value in chat.")
            self._clients[provider] = self._factory(provider, key)
        return self._clients[provider]

    @classmethod
    def from_experiment(cls, exp_dir, client_factory=None):
        """Open a client for an experiment folder, with the cap from its config.yaml (budget_usd)."""
        import yaml
        cfg = yaml.safe_load((Path(exp_dir) / "config.yaml").read_text()) or {}
        budget = float(cfg.get("budget_usd") or 0)
        if budget <= 0:
            raise ValueError(f"set budget_usd in {Path(exp_dir) / 'config.yaml'} before any paid call")
        return cls(exp_dir, budget, client_factory=client_factory)

    def estimate(self, model, prompt, max_tokens, system=None):
        if model not in PRICES:
            raise UnknownPrice(f"{model} has no verified price in src/llm.py PRICES")
        pin, pout = PRICES[model]
        chars = len(prompt) + len(system or "")
        return (chars / CHARS_PER_TOKEN_EST * pin + max_tokens * pout) / 1e6

    def complete(self, model: str, prompt: str, max_tokens: int = 256, system: str | None = None, tag: str = ""):
        est = self.estimate(model, prompt, max_tokens, system)
        if self.spent + est > self.budget:
            raise BudgetExceeded(f"spent ${self.spent:.4f} + next call up to ${est:.4f} exceeds budget ${self.budget:.2f}")
        rec = dict(ts=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), model=model, tag=tag,
                   prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest()[:16],
                   prompt_chars=len(prompt), system_chars=len(system or ""), max_tokens=max_tokens)
        if self.dry:
            rec.update(dry_run=True, est_cost_usd=round(est, 6)); self._log(rec); return None
        self._client(provider_of(model))          # a missing key fails here, before any retry
        t0 = time.time(); text, usage, err, returned = None, None, None, None
        for attempt in range(4):
            try:
                text, usage, returned = self._call(model, prompt, max_tokens, system)
                break
            except (MissingKey, UnknownPrice, ValueError):
                raise
            except Exception as e:   # rate limits and transient errors: back off, then give up
                err = redact(e)
                if attempt == 3: break
                time.sleep(2 ** attempt * 2)
        if usage is None:
            rec.update(error=err[:300]); self._log(rec)
            raise RuntimeError(f"call failed after retries: {err[:200]}")
        pin, pout = PRICES[model]
        cost = (usage.input_tokens * pin + usage.output_tokens * pout) / 1e6
        self.spent += cost
        rec.update(model_returned=returned, input_tokens=usage.input_tokens, output_tokens=usage.output_tokens,
                   cost_usd=round(cost, 6), latency_s=round(time.time() - t0, 2))
        self._log(rec); self._save_cost()
        return text

    def _call(self, model, prompt, max_tokens, system):
        prov = provider_of(model); c = self._client(prov)
        if prov == "anthropic":
            kw = dict(model=model, max_tokens=max_tokens, messages=[{"role": "user", "content": prompt}])
            if system: kw["system"] = system
            r = c.messages.create(**kw)
            return ("".join(getattr(b, "text", "") for b in r.content),
                    Usage(r.usage.input_tokens, r.usage.output_tokens), getattr(r, "model", None))
        if prov == "openai":
            msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
            r = c.chat.completions.create(model=model, max_completion_tokens=max_tokens, messages=msgs)
            # completion_tokens includes reasoning tokens, so cost is not undercounted
            return (r.choices[0].message.content, Usage(r.usage.prompt_tokens, r.usage.completion_tokens),
                    getattr(r, "model", None))
        if prov == "gemini":
            cfg = {"max_output_tokens": max_tokens}
            if system: cfg["system_instruction"] = system
            r = c.models.generate_content(model=model, contents=prompt, config=cfg)
            um = r.usage_metadata
            out = (um.candidates_token_count or 0) + (getattr(um, "thoughts_token_count", 0) or 0)  # thinking is billed as output
            return r.text, Usage(um.prompt_token_count or 0, out), getattr(r, "model_version", None)
        raise ValueError(prov)

    def _log(self, rec):
        with open(self.log_path, "a") as f: f.write(json.dumps(rec) + "\n")

    def _save_cost(self):
        self.cost_path.write_text(json.dumps({"spent_usd": round(self.spent, 6), "budget_usd": self.budget}, indent=1))

def _default_client(provider, key):
    if provider == "anthropic":
        import anthropic; return anthropic.Anthropic(api_key=key)
    if provider == "openai":
        import openai; return openai.OpenAI(api_key=key)
    if provider == "gemini":
        from google import genai; return genai.Client(api_key=key)
    raise ValueError(provider)

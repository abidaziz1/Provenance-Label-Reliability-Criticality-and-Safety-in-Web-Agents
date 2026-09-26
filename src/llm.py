"""Budgeted, logged model calls for Idea 3 experiments.

Every paid model call in this repo goes through `LLM.complete` or the Batch API methods below. They:
- read keys only from environment variables, never from files in the repo;
- refuse a call or batch that could push the run past its budget (BudgetExceeded), counting batches
  that are submitted but not yet collected as reserved spend;
- refuse a model with no verified price in PRICES (UnknownPrice), so costs are never guessed;
- append one JSON line per call (or per batch request) to <run_dir>/llm_calls.jsonl and keep
  <run_dir>/cost.json current;
- log token counts, cost, latency and a sha256 of the prompt, never keys, headers or prompt text.

Key variables:
  RESEARCH_ANTHROPIC_API_KEY  research key for Claude models. Deliberately NOT named
                              ANTHROPIC_API_KEY, so Claude Code never picks it up for its own auth.
  OPENAI_API_KEY              or the literal value "proxy-injected" when a Claude Code cloud
                              environment attaches the real key as an API credential.
  GEMINI_API_KEY              optional; or "proxy-injected" when attached as an API credential.
                              scripts/preflight.py reports whether Google's API is reachable.
Set IDEA3_DRY_RUN=1 to log estimated costs without any network call.
Open a client with LLM.from_experiment(<experiment folder>), which reads budget_usd from its config.yaml.

Batch API (task 1.15). `submit_batch` prices the whole batch at the provider's batch rate from each
request's prompt length and max_tokens, checks it against the budget minus what is spent and
reserved, submits, and records the batch in <run_dir>/batches.json so a later session can collect
it. `collect_batch` returns None until the provider reports the batch finished; then it logs every
request's tokens and cost, writes the texts to <run_dir>/batch_<id>.jsonl and releases the
reservation. Anthropic and Gemini batches were tested live on 26 Sep 2026; the OpenAI path is
tested with a mock only (no key yet).
"""
from __future__ import annotations
import hashlib, json, os, re, time
from dataclasses import dataclass
from pathlib import Path

# USD per 1M tokens (input, output). Verified list prices. Add a model only after checking its
# official pricing page, and cite the page in the commit message.
#   Claude: platform.claude.com/docs/en/about-claude/pricing (checked 26 Sep 2026)
#   Gemini: ai.google.dev/gemini-api/docs/pricing (checked 26 Sep 2026; paid tier, text input)
#   OpenAI: gpt-5.4-mini as verified at handoff (Sep 2026)
PRICES = {
    "claude-sonnet-5":        (2.00, 10.00),
    "claude-sonnet-4-5":      (3.00, 15.00),   # UCM's selector model (UCM §7.1)
    "claude-sonnet-4-6":      (3.00, 15.00),
    "claude-haiku-4-5":       (1.00, 5.00),
    "claude-opus-5-5":        (4.00, 20.00),
    "gemini-3-flash-preview": (0.50, 3.00),
    "gpt-5.4-mini":           (0.75, 4.50),
}
# Batch API price as a share of list price. All three providers list batch at 50% of standard
# (Anthropic and Google pricing pages as above; OpenAI Batch API documentation).
BATCH_FACTOR = {"anthropic": 0.5, "gemini": 0.5, "openai": 0.5}
KEY_ENV = {"anthropic": "RESEARCH_ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY"}
CHARS_PER_TOKEN_EST = 2.8   # conservative: measured 2.87 on agent observations, 3.98 on sanitized HTML
CUSTOM_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")   # Anthropic's rule; the strictest of the three
_DATED = re.compile(r"^(.*)-\d{8}$")

class BudgetExceeded(RuntimeError): pass
class UnknownPrice(RuntimeError): pass
class MissingKey(RuntimeError): pass

_SECRETISH = re.compile(r"(sk-[A-Za-z0-9_\-]{8,}|AIza[0-9A-Za-z_\-]{10,}|AQ\.[A-Za-z0-9_\-]{20,}|gh[pousr]_[A-Za-z0-9]{10,}|github_pat_[A-Za-z0-9_]{10,}|xox[baprs]-[A-Za-z0-9\-]{8,}|hf_[A-Za-z0-9]{10,})")

def redact(text: str) -> str:
    return _SECRETISH.sub("[REDACTED]", str(text))

def provider_of(model: str) -> str:
    if model.startswith("claude"): return "anthropic"
    if model.startswith("gpt") or model.startswith("o"): return "openai"
    if model.startswith("gemini"): return "gemini"
    raise ValueError(f"cannot infer provider for {model}")

def price_of(model: str):
    """List price for a model ID; a dated ID (claude-haiku-4-5-20251001) uses its undated entry."""
    if model in PRICES: return PRICES[model]
    m = _DATED.match(model)
    if m and m.group(1) in PRICES: return PRICES[m.group(1)]
    raise UnknownPrice(f"{model} has no verified price in src/llm.py PRICES")

def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

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
        self.batches_path = self.run_dir / "batches.json"
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
        pin, pout = price_of(model)
        chars = len(prompt) + len(system or "")
        return (chars / CHARS_PER_TOKEN_EST * pin + max_tokens * pout) / 1e6

    def complete(self, model: str, prompt: str, max_tokens: int = 256, system: str | None = None, tag: str = ""):
        est = self.estimate(model, prompt, max_tokens, system)
        if self.spent + self.reserved() + est > self.budget:
            raise BudgetExceeded(f"spent ${self.spent:.4f} + reserved ${self.reserved():.4f} + next call up to ${est:.4f} exceeds budget ${self.budget:.2f}")
        rec = dict(ts=_now(), model=model, tag=tag,
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
        pin, pout = price_of(model)
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
            return r.text, _gemini_usage(r.usage_metadata), getattr(r, "model_version", None)
        raise ValueError(prov)

    # ---------------------------------------------------------------- Batch API (task 1.15)
    def _batches(self):
        return json.loads(self.batches_path.read_text()) if self.batches_path.exists() else {}

    def _save_batches(self, b):
        self.batches_path.write_text(json.dumps(b, indent=1))

    def reserved(self):
        """Estimated cost of batches submitted but not yet collected."""
        return sum(v.get("est_usd", 0.0) for v in self._batches().values() if v.get("status") == "submitted")

    def estimate_batch(self, model, requests):
        return BATCH_FACTOR[provider_of(model)] * sum(
            self.estimate(model, r["prompt"], int(r.get("max_tokens", 256)), r.get("system")) for r in requests)

    def submit_batch(self, model: str, requests: list, tag: str = ""):
        """requests: [{"custom_id", "prompt", "max_tokens", "system" (optional)}]. Returns the batch ID,
        or None in a dry run."""
        if not requests:
            raise ValueError("empty batch")
        ids = [r["custom_id"] for r in requests]
        if len(set(ids)) != len(ids) or not all(CUSTOM_ID.match(i) for i in ids):
            raise ValueError("custom_id values must be unique and match ^[A-Za-z0-9_-]{1,64}$")
        est = self.estimate_batch(model, requests)
        if self.spent + self.reserved() + est > self.budget:
            raise BudgetExceeded(f"spent ${self.spent:.4f} + reserved ${self.reserved():.4f} + batch up to ${est:.4f} exceeds budget ${self.budget:.2f}")
        rec = dict(ts=_now(), kind="batch_submit", model=model, tag=tag, n_requests=len(requests),
                   est_cost_usd=round(est, 6),
                   prompts_sha256=hashlib.sha256("".join(r["prompt"] for r in requests).encode()).hexdigest()[:16])
        if self.dry:
            rec.update(dry_run=True); self._log(rec); return None
        prov = provider_of(model); c = self._client(prov)
        batch_id = self._submit(prov, c, model, requests, tag)
        b = self._batches()
        b[batch_id] = dict(provider=prov, model=model, tag=tag, n_requests=len(requests), est_usd=round(est, 6),
                           submitted=rec["ts"], status="submitted", custom_ids=ids)
        self._save_batches(b)
        rec.update(batch_id=batch_id); self._log(rec)
        return batch_id

    def batch_status(self, batch_id):
        meta = self._batches()[batch_id]
        return meta["status"] if meta["status"] == "collected" else self._state(meta["provider"], self._client(meta["provider"]), batch_id)

    def collect_batch(self, batch_id):
        """Return {custom_id: text} once the batch has ended, else None. Idempotent."""
        b = self._batches(); meta = b[batch_id]
        out_path = self.run_dir / f"batch_{re.sub(r'[^A-Za-z0-9_-]', '_', batch_id)}.jsonl"
        if meta["status"] == "collected":
            return {json.loads(l)["custom_id"]: json.loads(l)["text"] for l in out_path.read_text().splitlines()}
        prov = meta["provider"]
        items = self._results(prov, self._client(prov), batch_id, meta)
        if items is None:
            return None
        pin, pout = price_of(meta["model"]); f = BATCH_FACTOR[prov]; total = 0.0
        with open(out_path, "w") as fh:
            for it in items:
                cost = ((it.get("input_tokens") or 0) * pin + (it.get("output_tokens") or 0) * pout) / 1e6 * f
                total += cost
                rec = dict(ts=_now(), kind="batch_result", model=meta["model"], model_returned=it.get("model"),
                           tag=meta.get("tag", ""), batch_id=batch_id, custom_id=it["custom_id"],
                           input_tokens=it.get("input_tokens") or 0, output_tokens=it.get("output_tokens") or 0,
                           cost_usd=round(cost, 6))
                if it.get("error"): rec["error"] = redact(it["error"])[:300]
                self._log(rec)
                fh.write(json.dumps({"custom_id": it["custom_id"], "text": it.get("text"), "error": rec.get("error")}) + "\n")
        self.spent += total
        meta.update(status="collected", collected=_now(), cost_usd=round(total, 6), n_results=len(items))
        b[batch_id] = meta; self._save_batches(b); self._save_cost()
        return {it["custom_id"]: it.get("text") for it in items}

    def _submit(self, prov, c, model, requests, tag):
        if prov == "anthropic":
            reqs = []
            for r in requests:
                p = dict(model=model, max_tokens=int(r.get("max_tokens", 256)), messages=[{"role": "user", "content": r["prompt"]}])
                if r.get("system"): p["system"] = r["system"]
                reqs.append({"custom_id": r["custom_id"], "params": p})
            return c.messages.batches.create(requests=reqs).id
        if prov == "gemini":
            src = []
            for r in requests:
                cfg = {"max_output_tokens": int(r.get("max_tokens", 256))}
                if r.get("system"): cfg["system_instruction"] = r["system"]
                src.append({"contents": [{"role": "user", "parts": [{"text": r["prompt"]}]}],
                            "metadata": {"custom_id": r["custom_id"]}, "config": cfg})
            return c.batches.create(model=model, src=src, config={"display_name": (tag or "idea3")[:100]}).name
        if prov == "openai":
            lines = []
            for r in requests:
                msgs = ([{"role": "system", "content": r["system"]}] if r.get("system") else []) + [{"role": "user", "content": r["prompt"]}]
                lines.append(json.dumps({"custom_id": r["custom_id"], "method": "POST", "url": "/v1/chat/completions",
                                         "body": {"model": model, "max_completion_tokens": int(r.get("max_tokens", 256)), "messages": msgs}}))
            f = c.files.create(file=("batch.jsonl", ("\n".join(lines) + "\n").encode()), purpose="batch")
            return c.batches.create(input_file_id=f.id, endpoint="/v1/chat/completions", completion_window="24h").id
        raise ValueError(prov)

    def _state(self, prov, c, batch_id):
        if prov == "anthropic":
            return c.messages.batches.retrieve(batch_id).processing_status          # in_progress, canceling, ended
        if prov == "gemini":
            s = c.batches.get(name=batch_id).state
            return getattr(s, "name", str(s))                                        # JOB_STATE_*
        if prov == "openai":
            return c.batches.retrieve(batch_id).status                              # validating ... completed
        raise ValueError(prov)

    def _results(self, prov, c, batch_id, meta):
        """None while the batch runs; else a list of dicts: custom_id, text, input_tokens, output_tokens, model, error."""
        if prov == "anthropic":
            if c.messages.batches.retrieve(batch_id).processing_status != "ended":
                return None
            items = []
            for x in c.messages.batches.results(batch_id):
                res = x.result
                if getattr(res, "type", None) == "succeeded":
                    m = res.message
                    items.append(dict(custom_id=x.custom_id, text="".join(getattr(b, "text", "") for b in m.content),
                                      input_tokens=m.usage.input_tokens, output_tokens=m.usage.output_tokens,
                                      model=getattr(m, "model", None)))
                else:
                    items.append(dict(custom_id=x.custom_id, text=None, input_tokens=0, output_tokens=0,
                                      error=str(getattr(res, "type", res))))
            return items
        if prov == "gemini":
            job = c.batches.get(name=batch_id)
            state = getattr(job.state, "name", str(job.state))
            if state not in ("JOB_STATE_SUCCEEDED", "JOB_STATE_PARTIALLY_SUCCEEDED", "JOB_STATE_FAILED",
                             "JOB_STATE_CANCELLED", "JOB_STATE_EXPIRED"):
                return None
            responses = (job.dest.inlined_responses if job.dest else None) or []
            items = []
            for i, r in enumerate(responses):
                cid = (r.metadata or {}).get("custom_id") or (meta["custom_ids"][i] if i < len(meta["custom_ids"]) else f"idx{i}")
                if r.response is not None:
                    u = _gemini_usage(r.response.usage_metadata)
                    items.append(dict(custom_id=cid, text=r.response.text, input_tokens=u.input_tokens,
                                      output_tokens=u.output_tokens, model=getattr(r.response, "model_version", None)))
                else:
                    items.append(dict(custom_id=cid, text=None, input_tokens=0, output_tokens=0, error=str(r.error)))
            if not responses:
                items.append(dict(custom_id="(batch)", text=None, input_tokens=0, output_tokens=0, error=state))
            return items
        if prov == "openai":
            bt = c.batches.retrieve(batch_id)
            if bt.status not in ("completed", "failed", "expired", "cancelled"):
                return None
            items = []
            for fid in (bt.output_file_id, bt.error_file_id):
                if not fid:
                    continue
                for line in c.files.content(fid).text.splitlines():
                    if not line.strip():
                        continue
                    o = json.loads(line); resp = (o.get("response") or {}).get("body") or {}
                    u = resp.get("usage") or {}
                    ch = resp.get("choices") or []
                    items.append(dict(custom_id=o.get("custom_id"),
                                      text=ch[0]["message"]["content"] if ch else None,
                                      input_tokens=u.get("prompt_tokens", 0), output_tokens=u.get("completion_tokens", 0),
                                      model=resp.get("model"), error=json.dumps(o["error"]) if o.get("error") else None))
            return items
        raise ValueError(prov)

    def _log(self, rec):
        with open(self.log_path, "a") as f: f.write(json.dumps(rec) + "\n")

    def _save_cost(self):
        self.cost_path.write_text(json.dumps({"spent_usd": round(self.spent, 6), "budget_usd": self.budget}, indent=1))

def _gemini_usage(um):
    out = (um.candidates_token_count or 0) + (getattr(um, "thoughts_token_count", 0) or 0)  # thinking is billed as output
    return Usage(um.prompt_token_count or 0, out)

def _default_client(provider, key):
    if provider == "anthropic":
        import anthropic; return anthropic.Anthropic(api_key=key)
    if provider == "openai":
        import openai; return openai.OpenAI(api_key=key)
    if provider == "gemini":
        from google import genai; return genai.Client(api_key=key)
    raise ValueError(provider)

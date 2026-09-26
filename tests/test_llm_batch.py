"""Batch API support in src/llm.py (task 1.15), with mock clients. No network."""
import json, sys
from pathlib import Path
from types import SimpleNamespace as NS
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pytest
import llm as L


# ------------------------------------------------------------------ mock providers
class _AnthBatches:
    def __init__(self): self.created, self.status, self.reqs = 0, "in_progress", None
    def create(self, requests):
        self.created += 1; self.reqs = list(requests); return NS(id="msgbatch_TEST1")
    def retrieve(self, bid): return NS(processing_status=self.status)
    def results(self, bid):
        for r in self.reqs:
            if r["custom_id"] == "bad":
                yield NS(custom_id="bad", result=NS(type="errored"))
            else:
                msg = NS(content=[NS(text="ok " + r["custom_id"])], usage=NS(input_tokens=100, output_tokens=10),
                         model="claude-haiku-4-5-20251001")
                yield NS(custom_id=r["custom_id"], result=NS(type="succeeded", message=msg))

class _Anth:
    def __init__(self): self.messages = NS(batches=_AnthBatches(), create=None)


class _GemBatches:
    def __init__(self): self.src, self.state = None, "JOB_STATE_RUNNING"
    def create(self, model, src, config=None): self.src = src; return NS(name="batches/TEST2")
    def get(self, name):
        resps = []
        for s in self.src:
            um = NS(prompt_token_count=50, candidates_token_count=5, thoughts_token_count=20)
            resps.append(NS(metadata=s["metadata"], response=NS(text="ok", usage_metadata=um, model_version="gemini-3-flash-preview"), error=None))
        return NS(state=NS(name=self.state), dest=NS(inlined_responses=resps if self.state == "JOB_STATE_SUCCEEDED" else None))

class _Gem:
    def __init__(self): self.batches = _GemBatches()


class _OAI:
    def __init__(self):
        self.uploaded, self.status = None, "in_progress"
        outer = self
        class Files:
            def create(self, file, purpose): outer.uploaded = file[1].decode(); return NS(id="file-in")
            def content(self, fid):
                lines = []
                for l in outer.uploaded.splitlines():
                    o = json.loads(l)
                    lines.append(json.dumps({"custom_id": o["custom_id"], "response": {"body": {
                        "model": "gpt-5.4-mini", "choices": [{"message": {"content": "ok"}}],
                        "usage": {"prompt_tokens": 40, "completion_tokens": 8}}}}))
                return NS(text="\n".join(lines))
        class Batches:
            def create(self, input_file_id, endpoint, completion_window): return NS(id="batch_TEST3")
            def retrieve(self, bid): return NS(status=outer.status, output_file_id="file-out", error_file_id=None)
        self.files, self.batches = Files(), Batches()


def _mk(tmp_path, client, budget=1.0):
    return L.LLM(tmp_path, budget, client_factory=lambda p, k: client)


def _reqs(n, max_tokens=10, prompt="hello there"):
    return [{"custom_id": f"r{i}", "prompt": prompt, "max_tokens": max_tokens} for i in range(n)]


# ------------------------------------------------------------------ tests
def test_batch_is_priced_at_half_and_reserved(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCH_ANTHROPIC_API_KEY", "placeholder")
    c = _Anth(); m = _mk(tmp_path, c, budget=1.0)
    reqs = _reqs(3, max_tokens=1000, prompt="x" * 2800)
    full = sum(m.estimate("claude-haiku-4-5", r["prompt"], 1000) for r in reqs)
    assert abs(m.estimate_batch("claude-haiku-4-5", reqs) - full / 2) < 1e-12
    bid = m.submit_batch("claude-haiku-4-5", reqs, tag="t")
    assert bid == "msgbatch_TEST1" and c.messages.batches.created == 1
    assert abs(m.reserved() - full / 2) < 1e-6
    saved = json.loads((tmp_path / "batches.json").read_text())[bid]
    assert saved["status"] == "submitted" and saved["custom_ids"] == ["r0", "r1", "r2"]


def test_reservation_blocks_overcommit_before_any_call(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCH_ANTHROPIC_API_KEY", "placeholder")
    c = _Anth(); m = _mk(tmp_path, c)
    reqs = _reqs(2, max_tokens=4000, prompt="x" * 1000)
    m.budget = m.estimate_batch("claude-sonnet-5", reqs) * 1.4
    m.submit_batch("claude-sonnet-5", reqs)
    with pytest.raises(L.BudgetExceeded):
        m.submit_batch("claude-sonnet-5", [{"custom_id": "z", "prompt": "x" * 1000, "max_tokens": 4000}])
    with pytest.raises(L.BudgetExceeded):          # a direct call is also held back by the reservation
        m.complete("claude-sonnet-5", "x" * 1000, max_tokens=4000)
    assert c.messages.batches.created == 1


def test_collect_waits_then_logs_cost_once(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCH_ANTHROPIC_API_KEY", "placeholder")
    c = _Anth(); m = _mk(tmp_path, c)
    reqs = _reqs(2) + [{"custom_id": "bad", "prompt": "secret prompt text", "max_tokens": 10}]
    bid = m.submit_batch("claude-haiku-4-5", reqs)
    assert m.collect_batch(bid) is None                      # still running
    c.messages.batches.status = "ended"
    out = m.collect_batch(bid)
    assert out == {"r0": "ok r0", "r1": "ok r1", "bad": None}
    expect = 2 * (100 * 1.0 + 10 * 5.0) / 1e6 * 0.5
    assert abs(m.spent - expect) < 1e-9 and m.reserved() == 0
    assert m.collect_batch(bid) == out and abs(m.spent - expect) < 1e-9      # idempotent, no double charge
    log = (tmp_path / "llm_calls.jsonl").read_text()
    recs = [json.loads(l) for l in log.splitlines()]
    assert [r["kind"] for r in recs] == ["batch_submit", "batch_result", "batch_result", "batch_result"]
    assert "secret prompt text" not in log and "hello there" not in log
    assert any(r.get("error") == "errored" for r in recs)
    assert json.loads((tmp_path / "cost.json").read_text())["spent_usd"] == round(expect, 6)


def test_gemini_batch_maps_ids_and_bills_thinking(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "placeholder")
    c = _Gem(); m = _mk(tmp_path, c)
    bid = m.submit_batch("gemini-3-flash-preview", _reqs(2, max_tokens=64), tag="smoke")
    assert bid == "batches/TEST2" and c.batches.src[0]["metadata"] == {"custom_id": "r0"}
    assert c.batches.src[0]["config"]["max_output_tokens"] == 64
    assert m.collect_batch(bid) is None
    c.batches.state = "JOB_STATE_SUCCEEDED"
    assert m.collect_batch(bid) == {"r0": "ok", "r1": "ok"}
    expect = 2 * (50 * 0.50 + 25 * 3.00) / 1e6 * 0.5          # 5 candidate + 20 thinking tokens billed as output
    assert abs(m.spent - expect) < 1e-12
    assert (tmp_path / "batch_batches_TEST2.jsonl").exists()


def test_openai_batch_flow(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "placeholder")
    c = _OAI(); m = _mk(tmp_path, c)
    bid = m.submit_batch("gpt-5.4-mini", _reqs(2, max_tokens=32))
    body = json.loads(c.uploaded.splitlines()[0])["body"]
    assert body["max_completion_tokens"] == 32 and "max_tokens" not in body
    assert m.collect_batch(bid) is None
    c.status = "completed"
    assert m.collect_batch(bid) == {"r0": "ok", "r1": "ok"}
    assert abs(m.spent - 2 * (40 * 0.75 + 8 * 4.50) / 1e6 * 0.5) < 1e-12


def test_batch_dry_run_and_validation(tmp_path, monkeypatch):
    c = _Anth(); m = _mk(tmp_path, c)
    with pytest.raises(ValueError):
        m.submit_batch("claude-haiku-4-5", [{"custom_id": "a b", "prompt": "x"}])
    with pytest.raises(ValueError):
        m.submit_batch("claude-haiku-4-5", [{"custom_id": "a", "prompt": "x"}, {"custom_id": "a", "prompt": "y"}])
    monkeypatch.setenv("IDEA3_DRY_RUN", "1")
    m2 = _mk(tmp_path / "dry", c)
    assert m2.submit_batch("claude-haiku-4-5", _reqs(2)) is None and c.messages.batches.created == 0
    assert json.loads((tmp_path / "dry" / "llm_calls.jsonl").read_text())["dry_run"] is True


def test_dated_model_ids_use_the_undated_price(tmp_path):
    assert L.price_of("claude-haiku-4-5-20251001") == L.PRICES["claude-haiku-4-5"]
    assert L.price_of("claude-sonnet-4-5-20250929") == L.PRICES["claude-sonnet-4-5"]
    with pytest.raises(L.UnknownPrice):
        L.price_of("claude-imaginary-9-20990101")


def test_redact_new_google_key_format():
    fake = "AQ" + "." + "Ab8" + "q" * 47
    assert L.redact("bad key " + fake) == "bad key [REDACTED]"


def test_failed_submission_is_logged_and_reserves_nothing(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "placeholder")
    class Refuse:
        class batches:
            @staticmethod
            def create(model, src, config=None):
                raise RuntimeError("400 FAILED_PRECONDITION key " + "AQ" + "." + "z" * 45)
    m = _mk(tmp_path, Refuse())
    with pytest.raises(RuntimeError):
        m.submit_batch("gemini-3-flash-preview", _reqs(2))
    rec = json.loads((tmp_path / "llm_calls.jsonl").read_text().splitlines()[-1])
    assert rec["kind"] == "batch_submit" and "FAILED_PRECONDITION" in rec["error"] and "[REDACTED]" in rec["error"]
    assert m.reserved() == 0 and not (tmp_path / "batches.json").exists()

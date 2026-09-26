import json, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import pytest
import llm as L

class _Resp:
    def __init__(self, i, o):
        self.content = [type("B", (), {"text": "ok"})()]
        self.usage = type("U", (), {"input_tokens": i, "output_tokens": o})()

class _Fake:
    def __init__(self): self.calls = 0
    @property
    def messages(self): return self
    def create(self, **kw):
        self.calls += 1
        return _Resp(1000, 50)

def _mk(tmp_path, budget=1.0, fake=None):
    fake = fake or _Fake()
    return L.LLM(tmp_path, budget, client_factory=lambda p, k: fake), fake

def test_logs_cost_without_secrets(tmp_path, monkeypatch):
    fake_key = "sk" + "-ant-" + "x" * 30
    monkeypatch.setenv("RESEARCH_ANTHROPIC_API_KEY", fake_key)
    m, fake = _mk(tmp_path)
    assert m.complete("claude-haiku-4-5", "hello", max_tokens=50) == "ok"
    rec = json.loads((tmp_path / "llm_calls.jsonl").read_text().splitlines()[0])
    assert rec["input_tokens"] == 1000 and rec["output_tokens"] == 50
    assert abs(rec["cost_usd"] - (1000 * 1.0 + 50 * 5.0) / 1e6) < 1e-9
    blob = (tmp_path / "llm_calls.jsonl").read_text() + (tmp_path / "cost.json").read_text()
    assert fake_key not in blob and "hello" not in blob

def test_budget_blocks_before_spending(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCH_ANTHROPIC_API_KEY", "placeholder")
    m, fake = _mk(tmp_path, budget=0.0001)
    with pytest.raises(L.BudgetExceeded):
        m.complete("claude-sonnet-5", "x" * 10000, max_tokens=1000)
    assert fake.calls == 0

def test_unknown_model_refused(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCH_ANTHROPIC_API_KEY", "placeholder")
    m, _ = _mk(tmp_path)
    with pytest.raises(L.UnknownPrice):
        m.complete("claude-imaginary-9", "hi")

def test_missing_key_is_a_human_task(tmp_path, monkeypatch):
    monkeypatch.delenv("RESEARCH_ANTHROPIC_API_KEY", raising=False)
    m = L.LLM(tmp_path, 1.0)
    with pytest.raises(L.MissingKey):
        m.complete("claude-haiku-4-5", "hi")

def test_dry_run_makes_no_call(tmp_path, monkeypatch):
    monkeypatch.setenv("IDEA3_DRY_RUN", "1")
    m, fake = _mk(tmp_path)
    assert m.complete("claude-haiku-4-5", "hi") is None and fake.calls == 0

def test_redact():
    s = "error with key " + "sk" + "-proj-" + "A" * 24
    assert "[REDACTED]" in L.redact(s)

def test_system_prompt_counts_toward_budget(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCH_ANTHROPIC_API_KEY", "placeholder")
    m, fake = _mk(tmp_path, budget=0.001)
    # prompt alone fits; prompt plus a long system prompt does not
    assert m.estimate("claude-haiku-4-5", "x" * 100, 10) < 0.001
    with pytest.raises(L.BudgetExceeded):
        m.complete("claude-haiku-4-5", "x" * 100, max_tokens=10, system="s" * 5000)
    assert fake.calls == 0

def test_logs_the_model_the_api_returned(tmp_path, monkeypatch):
    monkeypatch.setenv("RESEARCH_ANTHROPIC_API_KEY", "placeholder")
    class R(_Resp):
        model = "claude-haiku-4-5-20251001"
    class F(_Fake):
        def create(self, **kw):
            self.calls += 1; return R(10, 5)
    m, _ = _mk(tmp_path, fake=F())
    m.complete("claude-haiku-4-5", "hi", max_tokens=5)
    rec = json.loads((tmp_path / "llm_calls.jsonl").read_text().splitlines()[0])
    assert rec["model_returned"] == "claude-haiku-4-5-20251001"

def test_from_experiment_reads_the_cap(tmp_path):
    (tmp_path / "config.yaml").write_text("budget_usd: 2.5\n")
    m = L.LLM.from_experiment(tmp_path, client_factory=lambda p, k: _Fake())
    assert m.budget == 2.5
    (tmp_path / "config.yaml").write_text("budget_usd: 0\n")
    with pytest.raises(ValueError):
        L.LLM.from_experiment(tmp_path)

def test_gemini_counts_thinking_and_passes_system(tmp_path, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "proxy-injected")
    L.PRICES["gemini-test-model"] = (1.0, 10.0)
    seen = {}
    class Models:
        def generate_content(self, model, contents, config):
            seen.update(config)
            um = type("UM", (), {"prompt_token_count": 100, "candidates_token_count": 10, "thoughts_token_count": 40})()
            return type("R", (), {"text": "ok", "usage_metadata": um, "model_version": "gemini-test-model-001"})()
    client = type("C", (), {"models": Models()})()
    try:
        m = L.LLM(tmp_path, 1.0, client_factory=lambda p, k: client)
        assert m.complete("gemini-test-model", "hi", max_tokens=64, system="be brief") == "ok"
        rec = json.loads((tmp_path / "llm_calls.jsonl").read_text().splitlines()[0])
        assert rec["output_tokens"] == 50 and seen["system_instruction"] == "be brief" and seen["max_output_tokens"] == 64
    finally:
        del L.PRICES["gemini-test-model"]

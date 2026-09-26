"""Smallest paid check of the research keys and of src/llm.py (tasks 0.1, 1.4, 1.15).

  python3 scripts/api_smoke_test.py direct    one call each to claude-sonnet-5 and gemini-3-flash-preview
  python3 scripts/api_smoke_test.py submit    a 2-request batch each to claude-haiku-4-5 and gemini-3-flash-preview
  python3 scripts/api_smoke_test.py collect   collect every submitted batch that has finished
Prints the reply text (one word expected), tokens and cost from the experiment's log; never keys.
"""
from pathlib import Path
import json, sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from llm import LLM

EXP = ROOT / "experiments" / "2026-09-26_1.15_api-smoke-test"
PROMPT = "Reply with the single word OK."


def main(step):
    m = LLM.from_experiment(EXP)
    if step == "direct":
        for model, mt in (("claude-sonnet-5", 8), ("gemini-3-flash-preview", 256)):
            try:
                print(model, "->", repr(m.complete(model, PROMPT, max_tokens=mt, tag="smoke-direct")))
            except Exception as e:
                print(model, "failed:", type(e).__name__, str(e)[:200])
    elif step == "submit":
        for model, mt in (("claude-haiku-4-5", 8), ("gemini-3-flash-preview", 256)):
            reqs = [{"custom_id": f"smoke{i}", "prompt": PROMPT, "max_tokens": mt} for i in (1, 2)]
            try:
                print(model, "batch ->", m.submit_batch(model, reqs, tag="smoke-batch"))
            except Exception as e:
                print(model, "batch failed:", type(e).__name__, str(e)[:200])
    elif step == "collect":
        for bid, meta in m._batches().items():
            if meta["status"] == "submitted":
                out = m.collect_batch(bid)
                print(bid, "->", "still running" if out is None else out)
    print(json.dumps(json.loads((EXP / "cost.json").read_text()) if (EXP / "cost.json").exists() else {}, indent=None),
          "reserved", round(m.reserved(), 6))


if __name__ == "__main__":
    main(sys.argv[1])

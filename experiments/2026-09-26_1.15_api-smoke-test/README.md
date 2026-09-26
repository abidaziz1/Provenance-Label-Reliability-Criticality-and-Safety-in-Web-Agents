# 1.15: API smoke test of the research keys and the Batch API

## Purpose (written before any paid call)

Check, at the smallest possible cost, that:

- the research keys work through `src/llm.py`;
- the model IDs chosen in 1.4 exist;
- the Batch API code from 1.15 submits, records and collects a batch, and logs cost from returned usage.

This is a plumbing check with no hypothesis. The prompt is "Reply with the single word OK."

- **Calls.**
  - One direct call to `claude-sonnet-5` (max 8 output tokens) and one to `gemini-3-flash-preview` (max 256; Gemini 3 spends part of its output budget on thinking).
  - A 2-request batch to `claude-haiku-4-5` (max 8 each) and another to `gemini-3-flash-preview` (max 256 each).
- **Budget.** $0.05 cap in `config.yaml`. The expected spend is under $0.002.
- **Cost accounting.** The Gemini key is on the free tier, so Google may charge nothing. `src/llm.py` still logs list price, a deliberate overstatement.
- **What would count as failure.** A missing key, an unknown model ID, a batch that cannot be submitted or collected, or cost fields missing from the log.

## Results

(filled after the run)

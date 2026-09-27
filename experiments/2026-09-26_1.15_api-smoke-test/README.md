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

Run 26 Sep 2026, 13:37 to 13:42 UTC. The files are the record: `llm_calls.jsonl`, `cost.json`, `batches.json` and `batch_msgbatch_0132hQRDrg797fPUk7s8uC3i.jsonl`.

| Call | Model returned | Reply | Input tokens | Output tokens | Logged cost |
| --- | --- | --- | ---: | ---: | ---: |
| direct | `claude-sonnet-5` | OK | 16 | 4 | $0.000072 |
| direct | `gemini-3-flash-preview` | OK | 8 | 54 (thinking included) | $0.000166 at list price; free tier, likely $0 charged |
| batch `smoke1` | `claude-haiku-4-5-20251001` | OK | 14 | 4 | $0.000017 (batch price) |
| batch `smoke2` | `claude-haiku-4-5-20251001` | OK | 14 | 4 | $0.000017 (batch price) |

- **Anthropic Batch API.** The batch was submitted at 13:39:21 and collected at 13:41:47. Its reservation ($0.000051, estimated from `max_tokens`) was released at collection, and the logged cost ($0.000034) came from the returned usage.
- **Gemini Batch API.** Google refused it with `400 FAILED_PRECONDITION` on this free-tier key. Nothing was charged or reserved. `src/llm.py` did not log failed submissions at the time; it does now (commit a5e1c04).
- **Spend.** $0.000272 logged, of which $0.000166 is Gemini at list price. Actual charge: about $0.0001 on the Claude key.
- **Verdict.** Both keys work, the model IDs from 1.4 exist, and the Anthropic batch path works end to end. The Gemini batch path waits for a paid-tier key; the Gemini arm (task 2.3) can use direct calls on the free tier within its rate limits.

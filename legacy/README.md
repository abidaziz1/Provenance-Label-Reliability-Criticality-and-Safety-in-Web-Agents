# Legacy code

The August and early-September code behind the smoke test and the first 57-site scale-up. Kept for provenance, because several withdrawn findings came from it and a reviewer may ask how.

- Do not run it as is. Many files still contain absolute paths from the original workspace (`/home/claude/...`).
- Do not cite numbers it produced without checking `research/CORRECTIONS.md` and `docs/context/05_CORRECTIONS_19Sep2026.md`.
- The corrected versions live in `src/` (pipeline v2, scorer v2) and `scripts/`.
- `verify_pipeline.py` is imported by `scripts/scale57.py` through `legacy/`; that script reproduces the pre-correction scale-up only.

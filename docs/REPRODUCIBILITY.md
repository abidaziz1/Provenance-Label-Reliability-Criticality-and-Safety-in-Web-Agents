# Reproduction guide

Distinguish local regression tests, analyses of the pinned dataset, and live or paid experiments when reporting what you reproduced.

## Local checks

CI uses Python 3.11 and [`requirements.txt`](../requirements.txt). Most scientific dependencies are pinned; model SDKs and pytest use minimum versions, so this is not a fully locked environment. Record installed versions when reproducing a result.

Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q tests
python scripts/scan_secrets.py
python -m pip freeze
git rev-parse HEAD
```

PowerShell, without changing execution policy:

```powershell
python -m venv .venv
$env:PYTHONUTF8 = '1'
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q tests
.\.venv\Scripts\python.exe scripts/scan_secrets.py
.\.venv\Scripts\python.exe -m pip freeze
git rev-parse HEAD
```

Expected without Mind2Web: **47 passed, 1 skipped**. `test_nb03_score_tables_match_direct_scoring` requires `train_10.json`; with it available, the expected count is 48 passed. Tests use model-client test doubles and need no research credentials.

UTF-8 matters on Windows because notebook builders read and write text. Their tests compare generated files byte for byte with the committed notebooks.

## Pinned dataset analyses

[`fetch_mind2web.py`](../scripts/fetch_mind2web.py) uses `osunlp/Mind2Web` revision `17ece8eb89862368edc0cc806acee6fca5163474`. By default it downloads `train_0.json`, `train_1.json`, and `train_10.json`, approximately 1.27 GB. The public dataset needs no token; an optional `HF_TOKEN` is used if present.

```bash
python scripts/fetch_mind2web.py --sha
python scripts/attr_survival.py
python scripts/actionability_on_archive.py
python -m pytest -q tests
```

The downloader writes `data/mind2web/MANIFEST.json`, including file hashes with `--sha`. Analyses may overwrite result files; use a separate checkout and compare outputs before committing. `data/` is ignored by Git.

For selector analyses, clone `https://github.com/ethz-spylab/untrusted-content-masking` separately, check out recorded revision `acff2e4`, and set `UCM_DIR` to that checkout. Read the relevant [experiment README](../experiments/) for exact input requirements.

## Live captures and paid runs

The live stripping experiment's captured pages are not committed. New captures can differ because websites change or block access; they are new observations, not exact recovery of the original inputs.

Model experiments need provider credentials, an approved budget, recorded model IDs, and the experiment configuration. Use [`src/llm.py`](../src/llm.py), which tracks spend and reservations. The commands above do not run these experiments. An API smoke test is not necessary to check the local installation.

Passing tests supports the computations covered. It does not validate omitted inputs, independent annotation, cross-site generalization, or interpretation of another paper. Claim status remains separate in the [ledger](../research/CLAIMS_LEDGER.md).

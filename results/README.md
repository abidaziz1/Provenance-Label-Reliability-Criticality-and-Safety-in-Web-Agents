# Results index

Outputs from before the `experiments/` folder existed (up to 25 Sep 2026). Files here are frozen: a rerun writes a new file, and any changed value is logged in `research/CORRECTIONS.md`. New runs write into their own `experiments/<...>/results/`.

| File | Produced by | What it holds | Described in |
| --- | --- | --- | --- |
| `reconcile_v1.json`, `reconcile_v2.json` (+ `.log`) | `scripts/reconcile.py` | Per-observation granularity ladder, pipeline v1 and v2 | `docs/context/02` |
| `reconcile_no_same_origin.json`, `reconcile_no_attr_norm.json` | `scripts/reconcile.py` with `FIX_OFF=` | One fix switched off at a time | `docs/context/02`, `04` |
| `descendant_only_v1.json`, `descendant_only_v2.json`, `desc_v1.log`, `desc_v2.log` | `scripts/descendant_only.py` | Descendants-only vs region-root criticality, 57-site and 16-site | `docs/context/02` section 3 |
| `C_gate_v1.json`, `C_gate_v2.json` (+ `.log`) | `scripts/recompute_C_and_gate.py` | C and the gate-width curve, both pipelines | `docs/context/04` |
| `gate_comparison.json` (+ `.log`) | `scripts/gate_comparison.py` | Target-free vs oracle gate | `docs/context/04` |
| `ablation_v2.json` (+ `.log`) | `scripts/ablation_v2.py` | Four-arm ablation, 5,088 trials, 159 pages, 27 sites | `docs/context/03` |
| `ablation_v2_contrasts.json` | `scripts/ablation_contrasts.py` (N0.1, 25 Sep; rewritten 26 Sep) | Paired contrasts between policy arms with site-bootstrap intervals (K8, K9, K11) | `research/CLAIMS_LEDGER.md` |
| `roadmap/budget_nb2.json`, `roadmap/budget_nb13.json` | `scripts/budget_nb2.py`, `scripts/budget_nb13.py` | Item supply and API cost estimates for notebooks 01 to 03 | `docs/context/01` |
| `roadmap/tokens_and_coupling.json` | `scripts/tokens_and_coupling.py` | Token sizes and the coupling power table | `docs/context/01`, ROADMAP.md |
| `legacy/` | `legacy/src/`, `scripts/scale57.py`, `scripts/gate_ablation_v1_confounded.py` | Pre-correction outputs (corpus, 57-site scale-up, the confounded v1 gate ablation, kill test, label packets) | `docs/history/`, `docs/context/05` |

`legacy/gate_ablation.json` is the confounded v1 ablation that produced the withdrawn "0% to 100% on one label error". It stays for provenance; never cite it.

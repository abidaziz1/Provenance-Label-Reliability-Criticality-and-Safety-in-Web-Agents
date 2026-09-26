# N0.2: C1 robustness to unit granularity, the non-hidden filter and is_clickable

## Status of this file

**Reconstructed on 26 Sep 2026.** The original README (pre-registration in local commit 78e50c7, results in 92a75b7) was lost with the workspace before any push. The pre-registration cannot be checked, so treat this experiment as exploratory. The script, `scripts/c1_robustness.py`, survived unchanged. Rerunning it needs `src/pipeline_v2.py` from the kit.

## What it measures

Prismata-style criticality on the 57-site frame: an untrusted unit is critical if it has an actionable strict descendant, in Prismata's §3 sense (a non-hidden form control, a link, a label target, an interactive ARIA role, an onclick handler, an editable region or a tabindex). It varies three things:

- **the unit:** G0 region, G1 region plus items, G2 block, G3 every node, G4 leaf, G5 text carrier;
- **the non-hidden filter:** based on the archive's bounding boxes;
- **the onclick clause:** replaced by the archive's `is_clickable` flag.

## Results recorded on 25 Sep (tests in `tests/test_claims.py`)

- **G4 leaf (K16):** 1.58% of all leaves, 2.10% of visible leaves.
- **G0 region (K17):** 52.56% per visible region; 49.93% with any unit and any descendant (the same as K3). G1: 45.21%.
- **G3 every untrusted node:** 15.83% of all units, 19.57% of visible units (as quoted by the adversarial review).
- **`is_clickable`:** adding it changed the rates by at most 0.2 points.

## After the adversarial review

The leaf "reproduction" of Prismata's 1.2% is a labeler artifact (`research/audit/2026-09-25_adversarial_C1prime_C4.md`, F1). What survives is the unit band: 1.6% to 19.6% on our units. Whether the 1.2% reproduces depends on Prismata's unit and labels (email 1.1).

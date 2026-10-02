# Review guide

Start with the question, then follow each claim to its evidence. This is an ongoing study; its results have not yet completed construct review.

## Reading order

1. [README](../README.md): question, observations, scope, and limits.
2. [Contribution statement](../research/CONTRIBUTION_STATEMENT.md): P1 and the conditions on P2 and P3.
3. [Claims ledger](../research/CLAIMS_LEDGER.md): units, sampling frames, scripts, results, tests, and status.
4. The dated experiment README linked from each claim: method, inputs, and deviations.
5. [Corrections](../research/CORRECTIONS.md) and [novelty ledger](../research/NOVELTY_LEDGER.md): withdrawn interpretations and unresolved comparisons.
6. [Reproduction guide](REPRODUCIBILITY.md): local checks and external input requirements.

## Follow the primary evidence

| Claims | Experiment | Analysis |
| --- | --- | --- |
| K21 | [Attribute census](../experiments/2026-09-25_1.8_attr-survival/README.md) | [`attr_survival.py`](../scripts/attr_survival.py) |
| K22–K23 | [Selector transfer](../experiments/2026-09-25_C7_ucm-selectors-on-archive/README.md) | [`ucm_selectors_on_archive.py`](../scripts/ucm_selectors_on_archive.py) |
| K25 | [Stripping versus drift](../experiments/2026-09-26_C7c_live-strip-vs-drift/README.md) | [`live_strip_test.py`](../scripts/live_strip_test.py) |
| K26 | [Link actionability](../experiments/2026-09-26_C7b_actionability-on-archive/README.md) | [`actionability_on_archive.py`](../scripts/actionability_on_archive.py) |

[`tests/test_claims.py`](../tests/test_claims.py) checks committed evidence. Some tests recompute statistics from saved outputs; they do not regenerate every capture or establish that a measurement represents the construct claimed.

## Open questions

- Does UCM generate effective new selectors when given stripped pages?
- Does the Booking result generalize to other sites and page types?
- Which Mind2Web page representation did Prismata's §3 measurement use? The paper states its unit (one flagged untrusted node) and identifies `a[href]` and `role=link` in its link breakdown.
- What happens when selectors stop matching untrusted content without a warning? UCM states that correct labels are required; the open check concerns detection of missing matches at runtime.
- Do controller upper bounds predict behavior in the real-agent pilot?
- Does independent annotation support the provenance labeler's exposure estimates?

## Historical material

[`docs/context/`](context/), [`docs/history/`](history/), and [`legacy/`](../legacy/) preserve earlier work. Their interpretations and plans may be superseded. Current claim status takes precedence. Historical records retain their original provenance.

When reporting a discrepancy, include the commit, claim ID, command, Python version, dataset revision, expected result, and observed result. Sanitize logs.

For anonymous review, prepare a separate artifact according to the venue's requirements. This repository and its Git history identify the maintainer.

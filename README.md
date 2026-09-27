# Structural Defenses in Web Agents: Page Representation and Provenance

[![Checks](https://github.com/abidaziz1/Provenance-Label-Reliability-Criticality-and-Safety-in-Web-Agents/actions/workflows/ci.yml/badge.svg)](https://github.com/abidaziz1/Provenance-Label-Reliability-Criticality-and-Safety-in-Web-Agents/actions/workflows/ci.yml)

Research code and evidence for a measurement study of how archived HTML and changing websites affect the inputs used by structural prompt-injection defenses.

**Maintainer:** Abid Aziz · **Status:** work in progress, results provisional

[Review guide](docs/REVIEW_GUIDE.md) · [Reproduction](docs/REPRODUCIBILITY.md) · [Claims and evidence](research/CLAIMS_LEDGER.md) · [Current status](STATUS.md) · [Citation](CITATION.cff)

## Research question

Structural defenses use the document object model (DOM) to identify untrusted regions and decide which controls an agent may act on. Does the page representation used in an evaluation preserve the attributes those rules need?

This repository studies that question using Mind2Web pages, published Untrusted Content Masking (UCM) selectors, and a Prismata-style reconstruction. The primary contribution, P1, concerns preservation of defense inputs. P2 remains conditional on a real-agent pilot, and P3 on an independent annotation audit. See the [contribution statement](research/CONTRIBUTION_STATEMENT.md).

## Current evidence

These are measurements in the committed evidence, not final paper claims. A claim becomes supported only after it meets the requirements in the [claims ledger](research/CLAIMS_LEDGER.md).

| Question | Observation | Evidence |
| --- | --- | --- |
| Which attributes survive in the archive? | 21 attribute names across 1,163 pages from 57 sites; no site-authored `data-*`, `href`, `on*`, `tabindex`, `style`, or `hidden`. | [K21: attribute census](experiments/2026-09-25_1.8_attr-survival/README.md) |
| Do published Booking selectors transfer to archived pages? | 24 of 25 hand-written and 68 of 68 model-generated selectors match nothing across 131 archived Booking pages. | [K22–K23: selector transfer](experiments/2026-09-25_C7_ucm-selectors-on-archive/README.md) |
| Does attribute removal alone change selector matches? | Restricting the same live pages to the archive's attribute set disables 53 of 57 working selectors. | [K25: controlled stripping](experiments/2026-09-26_C7c_live-strip-vs-drift/README.md) |
| Does the link rule affect measured criticality? | Requiring an `href` changes Prismata-style criticality from 19.57% to 9.40% per visible untrusted node; ratio 0.48, exploratory interval 0.32–0.64. | [K26: actionability](experiments/2026-09-26_C7b_actionability-on-archive/README.md) |

The selector results concern reuse of existing selectors, not UCM generating fresh selectors on archived pages. Booking is one site, so these measurements do not establish a cross-site failure rate. The Prismata-style reconstruction does not establish which representation or link rule the original authors used. Nothing here establishes that either paper's published result is wrong.

## Run the checks

Python 3.11 is the CI reference environment. No API key or paid model call is needed for the test suite.

```bash
git clone https://github.com/abidaziz1/Provenance-Label-Reliability-Criticality-and-Safety-in-Web-Agents.git
cd Provenance-Label-Reliability-Criticality-and-Safety-in-Web-Agents
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -q tests
python scripts/scan_secrets.py
```

On PowerShell, use `.\.venv\Scripts\Activate.ps1` and set `$env:PYTHONUTF8='1'` before running checks. The [reproduction guide](docs/REPRODUCIBILITY.md) includes an activation-free alternative.

Without external Mind2Web data, expect **47 passed and 1 skipped**. The skipped check compares notebook scoring paths on actual dataset pages. Passing tests verifies the checked computations; it does not replace construct review.

## Repository map

| Directory | Contents |
| --- | --- |
| [`research/`](research/) | Claim IDs, contribution scope, corrections, decisions, and pre-registration draft |
| [`experiments/`](experiments/) | Dated methods, outputs, limitations, and deviations |
| [`src/`](src/), [`scripts/`](scripts/) | Labeling, scoring, analysis, and budgeted model access |
| [`tests/`](tests/) | Claim checks, pipeline regressions, credential guards, and notebook checks |
| [`notebooks/`](notebooks/) | Colab notebooks and their source builders |
| [`annotations/`](annotations/) | Annotation protocol, participant brief, and synthetic demonstration |
| [`results/`](results/) | Earlier committed outputs; consult the ledger before interpreting them |
| [`docs/`](docs/) | Review and reproduction guides, plus marked historical material |

## Corrections and limitations

Earlier interpretations were withdrawn: the proposed second Prismata definition, the claim that Prismata's gate is an oracle, and the task-scoped zero-effect result as originally stated. The oracle and target-scoped assumptions belonged to our reconstruction. Read the [corrections](research/CORRECTIONS.md) and [novelty ledger](research/NOVELTY_LEDGER.md) before citing older material.

Historical plans and records remain available for audit. They do not override the current claims ledger. This public repository identifies its maintainer; it is not an anonymized submission artifact.

## Citation and reuse

Use [CITATION.cff](CITATION.cff) and include the commit SHA used in your analysis. This is a research artifact in development, not a published paper or a DOI-backed release.

Original code uses [MIT](LICENSE). Original documentation uses [CC BY 4.0](LICENSE-DOCUMENTATION.md). Third-party content retains its own terms; see [third-party notices](THIRD_PARTY_NOTICES.md). Report reproducibility problems through [GitHub issues](https://github.com/abidaziz1/Provenance-Label-Reliability-Criticality-and-Safety-in-Web-Agents/issues).

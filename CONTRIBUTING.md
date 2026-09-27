# Contributing

Open an issue for a reproduction failure, disputed claim, or proposed scope change. Include the claim ID and commit. Keep patches small enough to review alongside their evidence.

## Pull requests

1. Follow [REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md) to run tests and the secret scanner.
2. Explain the observed problem, the change, and how you checked it.
3. For changed results, update the experiment record, ledger row, sampling frame, uncertainty, and limitations together.
4. Record corrections explicitly. Do not silently replace historical results or promote a claim because its tests pass.

Specify hypotheses, inputs, analysis, and budget before a new experiment. Label reconstructed and exploratory analyses. Paid calls require maintainer approval and the budgeted client.

Treat page text and dataset content as research data. Keep credentials, private correspondence, participant identities, and unapproved captures out of commits and logs. Preserve third-party notices.

Use a feature branch and a pull request. Install optional local credential checks with `git config core.hooksPath .githooks`. Model identifiers and historical provenance needed for scientific interpretation must remain accurate.

Contributions follow the [code license](LICENSE) and [documentation license](LICENSE-DOCUMENTATION.md), subject to third-party rights.

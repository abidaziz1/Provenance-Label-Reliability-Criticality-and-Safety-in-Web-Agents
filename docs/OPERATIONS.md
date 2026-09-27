# Repository operations

Start with [reproduction](REPRODUCIBILITY.md) and [contributor guidance](../CONTRIBUTING.md). Use feature branches and pull requests; preserve research evidence and record corrections explicitly.

Keep credentials in environment variables or notebook secret storage. Never commit credentials or print their values. Paid experiments require explicit approval and the budgeted client. [External services](EXTERNAL_SERVICES.md) records historical setup details; verify current access before a new run.

The optional command-policy guard is `scripts/guard_commands.py`. Git commit hooks in `.githooks/` run the secret scanner. These checks are pattern-based, not a sandbox or a guarantee against leaks.

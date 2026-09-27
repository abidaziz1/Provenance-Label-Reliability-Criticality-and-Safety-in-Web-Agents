# Third-party notices

This repo quotes or derives from the following work. Neither project endorses this study.

## Mind2Web

- **Source:** the `osunlp/Mind2Web` dataset on Hugging Face, https://huggingface.co/datasets/osunlp/Mind2Web, revision `17ece8eb`.
- **Paper:** Deng et al., "Mind2Web: Towards a Generalist Agent for the Web", NeurIPS 2023 Datasets and Benchmarks Track.
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/.
- **What this repo holds:** no Mind2Web files. `results/legacy/corpus.json` and `results/legacy/corpus57.json` hold task IDs, task text and per-page features that our scripts derived from the archived pages. Other result files hold counts and statistics computed from the data.
- **Changes:** we parsed the archived pages and reduced them to the fields above. `scripts/fetch_mind2web.py` downloads the data from the source.

## Untrusted Content Masking (UCM)

- **Source:** https://github.com/ethz-spylab/untrusted-content-masking, commit `acff2e4`.
- **What this repo holds:** UCM's CSS selectors, quoted in our result files. Our scripts read them from a local clone (`UCM_DIR`).
- **License:** MIT. The notice as it appears in UCM's `LICENSE` file:

```text
MIT License

Copyright (c) 2026 Kristina Nikolić, Egor Zverev, Javier Rando, Matthew Jagielski, Edoardo Debenedetti, and Florian Tramèr

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Prismata

Only the paper (arXiv:2607.08147) is used. No code or data has been released, and none is included here.

# Pre-registration (draft, task 1.6)

Status: not started. Claude drafts it in task 1.6; Alam files it on OSF. After filing, this file is guarded: changes need Alam's review, and any deviation is listed in the experiment README and in the paper.

Use the OSF "Preregistration" template headings. Minimum content:

1. **Hypotheses**, each tied to a claims-ledger row and a novelty-ledger candidate. Include the direction and the smallest effect that would matter.
2. **Frame**: Mind2Web revision `17ece8eb89862368edc0cc806acee6fca5163474`, shards, sites, trajectories per site, observation filters. State what is held out.
3. **Definitions**: both criticality readings (root-to-target; actionable descendant), unit of analysis, whether the region root counts, target-free and oracle gates with K.
4. **Conditions and controls**: the four policy arms (`P_correct`, `P_err1_fixedgate`, `P_err1_derived`, `P_none`), envelopes, attacks, paired no-injection controls, and a random gate of matched width (external review item E7).
5. **Primary outcomes** and how each is computed, with the script path.
6. **Sample sizes** and the power analysis. The planning design effect of 2.68 rests on a disagreement ICC of 0.24 (95% interval 0.065 to 0.409) from the 26 Aug smoke test; show the sizes at the upper end too (design effect 3.86), and pre-register re-estimating the ICC from the 2.1 human labels.
7. **Analysis**: site-clustered bootstrap intervals, the unit of resampling, multiple-comparison handling.
8. **Decision rules and gates**: the coupling go/no-go thresholds, Gates 1 and 2 as in ROADMAP.md.
9. **Stopping rules** and the budget cap per experiment.
10. **Models**: exact model IDs and dates; what happens if a model is retired mid-study.
11. **Human labels**: annotation guide version, annotators, adjudication rule, kappa threshold.
12. **What is exploratory**: everything not listed above.

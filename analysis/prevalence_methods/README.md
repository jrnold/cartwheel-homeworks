# Prevalence correction: judgy vs bootstrap and reference intervals

How well do 95% intervals for a judge-corrected rate cover the truth? This
compares the interval in `judgy` (used by the validate-evaluator skill and the
HW5 optional step) with other bootstrap schemes, with Lang–Reiczigel, and with
the known-accuracy interval that epiR uses by default.

Reference design: Flor M, Weiß M, Selhorst T, Müller-Graf C, Greiner M.
*Comparison of Bayesian and frequentist methods for prevalence estimation under
misclassification.* BMC Public Health 20:1135 (2020),
[doi:10.1186/s12889-020-09177-4](https://doi.org/10.1186/s12889-020-09177-4).
They simulated three independent binomial samples: an Se validation sample, an
Sp validation sample, and the test application. They found that intervals
treating Se/Sp as known under-cover badly, while Lang–Reiczigel stays near 95%.
They did not test bootstrap intervals.

## Mapping to HW5

Pass is the positive class, so Se = TPR (the judge's hits on `n_se` human Pass
labels), Sp = TNR (hits on `n_sp` human Fail labels), and the apparent rate is
the judge's Pass rate on `n` unlabeled traces. The target is the true Pass
rate, estimated with Rogan–Gladen `(AP + TNR − 1) / (TPR + TNR − 1)`, clipped
to [0, 1].

## Methods (`methods.py`)

| Key | Interval | Uncertainty included |
|---|---|---|
| `judgy` | judgy 0.1.0: percentile bootstrap of the test pairs, unstratified; drops replicates with TPR + TNR ≤ 1 | test set only (AP fixed) |
| `skill` | validate-evaluator skill `bootstrap_ci`: same, but keeps TPR + TNR < 1 (drops only \|·\| < 1e-6) | test set only |
| `repo` | course helper `analysis/helpers/reporting.py::_estimate_prevalence`: also resamples the unlabeled predictions | test + unlabeled |
| `stratified` | parametric bootstrap with class sizes fixed (Flor et al.'s sampling model) | test + unlabeled |
| `lang_reiczigel` | Lang & Reiczigel (2014), from `asht::prevSeSp` | all three samples |
| `wilson_known` | epiR `epi.prev` default: Wilson interval for AP mapped through Rogan–Gladen, TPR/TNR known | unlabeled only |

Bootstraps use B = 2,000 (judgy's default is 20,000; the check below shows the
two agree). `methods.py` and `bayes_pymc.py` also contain a Bayesian estimator
(Flor et al.'s model); it was removed from the simulation and is not part of
these results.

## Checks (`check_methods.py`)

`uv run --with judgy==0.1.0 python -m analysis.prevalence_methods.check_methods`

- `boot_judgy` vs the real `judgy.estimate_success_rate` at B = 20,000 on 8
  cases: limits within 0.005 (Monte Carlo error); point estimates identical.
- `lang_reiczigel` vs R `asht::prevSeSp` 1.0.3: within 5e-5 (the R output's
  4-digit rounding).

The first check case has gpt-4o-like counts (TPR 11/12, TNR 3/28, 70% judged
Pass). judgy returns the interval [0, 0], and Lang–Reiczigel returns [0, 1].

## Design (`simulate.py`)

Two full-factorial grids, 500 data sets per cell, seed 20260928. The shared
factors are:

- true Pass rate ∈ {0.1, 0.3, 0.5, 0.7, 0.9}
- human labels per class in the test split (n_se = n_sp) ∈ {10, 20, 50, 100, 200}
- unlabeled traces ∈ {100, 1000}

The grids differ in TPR and TNR:

- **Main** (`--grid main`, 450 cells): TPR, TNR ∈ {0.6, 0.75, 0.9}.
- **Low** (`--grid low`, 950 cells): 19 TPR/TNR pairs from {0.2, 0.3, 0.45,
  0.55, 0.65, 0.8, 0.95} with at least one value below 0.6 and
  TPR + TNR ≥ 1.1, so TPR + TNR − 1 runs from 0.10 to 0.50. It includes
  gpt-4o-like shapes such as TPR 0.95 / TNR 0.2.

As in Flor et al., data sets whose observed TPR + TNR ≤ 1 are excluded (judgy
refuses them). That is 1.4% of data sets on the main grid and 7.6% on the low
grid (19% at TPR + TNR − 1 = 0.10), so coverage is conditional on the judge
looking better than chance in the sample. Coverage Monte Carlo SE ≈ 1 point
per cell.

## Results (`results/`)

`uv run python -m analysis.prevalence_methods.report [--grid low]` writes
`summary[_low].md` and the figures from `cells[_low].csv`.

| Method | Main: median coverage | Main: cells < 90% | Low: median coverage | Low: cells < 90% |
|---|---:|---:|---:|---:|
| judgy | 0.892 | 54% | 0.901 | 49% |
| skill bootstrap | 0.902 | 48% | 0.930 | 35% |
| repo helper | 0.946 | 8% | 0.959 | 6% |
| stratified bootstrap | 0.946 | 8% | 0.956 | 6% |
| Lang–Reiczigel | 0.963 | 0% | 0.970 | 2% |
| Wilson, TPR/TNR known | 0.635 | 87% | 0.610 | 89% |

![Coverage by cell, main grid](results/coverage_by_cell.png)
![Coverage by test-split size, main grid](results/coverage_by_n.png)
![Coverage by judge quality, low grid](results/coverage_by_youden_low.png)

Findings:

1. **judgy under-covers because it treats the judge's unlabeled Pass rate as
   exact.** The gap grows as the test split grows and as the unlabeled sample
   shrinks. With 200 labels per class and 100 unlabeled traces, mean coverage
   is 0.61 (main) and 0.64 (low).
2. **Dropping TPR + TNR ≤ 1 replicates matters near chance.** On the main grid,
   judgy and the skill's keep-everything variant differ by about 1 point (1.8%
   of replicates dropped). On the low grid at TPR + TNR − 1 = 0.10, judgy drops
   13% and covers 0.87, while the skill variant covers 0.95.
3. **Resampling the unlabeled predictions fixes most of it.** The repo helper and
   the stratified bootstrap reach about 0.95 from 50 labels per class on both
   grids. Unstratified and stratified resampling perform the same.
4. **Every bootstrap under-covers with 10 labels per class** (main: 0.85–0.90
   mean). Lang–Reiczigel stays at 0.97 across both grids and every test size,
   slightly conservative, as Flor et al. report.
5. **Treating TPR/TNR as known is not fit for use** (median about 0.6 on both
   grids), confirming Flor et al. It gets worse with more unlabeled data,
   because its interval shrinks toward a biased center.
6. **Near-chance judges often cannot be corrected at all:** at TPR + TNR − 1 =
   0.10, 19% of data sets show TPR + TNR ≤ 1 in the test split.

For HW5-sized test splits (roughly 10–30 labels per class), use Lang–Reiczigel,
or at least a bootstrap that also resamples the unlabeled predictions (as the
course helper does), not judgy's interval.

## Limits

- n_se = n_sp throughout; unbalanced splits (HW5 dev is 12 Pass / 28 Fail) are
  not simulated.
- Coverage is conditional on the observed TPR + TNR > 1.
- No BCa or studentized bootstraps.

| Method | Median coverage | Cells < 90% | Cells < 80% | Mean width |
|---|---:|---:|---:|---:|
| judgy (test only, drops TPR+TNR≤1) | 0.901 | 49% | 23% | 0.567 |
| skill bootstrap (test only, keeps) | 0.930 | 35% | 17% | 0.639 |
| repo helper (test + unlabeled) | 0.959 | 6% | 2% | 0.704 |
| stratified bootstrap (test + unlabeled) | 0.956 | 6% | 2% | 0.696 |
| Lang–Reiczigel | 0.970 | 2% | 0% | 0.710 |
| Wilson, TPR/TNR known (epiR default) | 0.610 | 89% | 73% | 0.351 |

Mean coverage by labels per class (averaged over the other factors):

| Method | 10 | 20 | 50 | 100 | 200 |
|---|---:|---:|---:|---:|---:|
| judgy (test only, drops TPR+TNR≤1) | 0.879 | 0.891 | 0.884 | 0.842 | 0.774 |
| skill bootstrap (test only, keeps) | 0.907 | 0.925 | 0.921 | 0.875 | 0.801 |
| repo helper (test + unlabeled) | 0.929 | 0.948 | 0.964 | 0.960 | 0.956 |
| stratified bootstrap (test + unlabeled) | 0.920 | 0.943 | 0.962 | 0.960 | 0.956 |
| Lang–Reiczigel | 0.966 | 0.969 | 0.970 | 0.969 | 0.966 |
| Wilson, TPR/TNR known (epiR default) | 0.359 | 0.478 | 0.618 | 0.715 | 0.798 |

Mean coverage by unlabeled sample size:

| Method | 100 | 1000 |
|---|---:|---:|
| judgy (test only, drops TPR+TNR≤1) | 0.796 | 0.912 |
| skill bootstrap (test only, keeps) | 0.840 | 0.931 |
| repo helper (test + unlabeled) | 0.956 | 0.946 |
| stratified bootstrap (test + unlabeled) | 0.953 | 0.943 |
| Lang–Reiczigel | 0.972 | 0.964 |
| Wilson, TPR/TNR known (epiR default) | 0.762 | 0.425 |

Mean coverage by true TPR + TNR − 1:

| Method | 0.10 | 0.15 | 0.20 | 0.25 | 0.35 | 0.40 | 0.50 |
|---|---:|---:|---:|---:|---:|---:|---:|
| judgy (test only, drops TPR+TNR≤1) | 0.867 | 0.842 | 0.871 | 0.856 | 0.864 | 0.832 | 0.823 |
| skill bootstrap (test only, keeps) | 0.947 | 0.860 | 0.912 | 0.870 | 0.875 | 0.835 | 0.826 |
| repo helper (test + unlabeled) | 0.976 | 0.937 | 0.968 | 0.943 | 0.948 | 0.929 | 0.928 |
| stratified bootstrap (test + unlabeled) | 0.972 | 0.933 | 0.966 | 0.940 | 0.945 | 0.927 | 0.926 |
| Lang–Reiczigel | 0.978 | 0.962 | 0.972 | 0.965 | 0.965 | 0.962 | 0.963 |
| Wilson, TPR/TNR known (epiR default) | 0.583 | 0.591 | 0.582 | 0.593 | 0.591 | 0.607 | 0.621 |

Exclusions and judgy's dropped replicates by true TPR + TNR − 1:

| TPR + TNR − 1 | Data sets excluded (observed TPR + TNR ≤ 1) | Cells with < 100 usable | Mean share of judgy replicates dropped |
|---:|---:|---:|---:|
| 0.10 | 19.3% | 0 of 250 | 13.0% |
| 0.15 | 7.2% | 0 of 100 | 6.6% |
| 0.20 | 8.0% | 0 of 100 | 7.1% |
| 0.25 | 3.4% | 0 of 200 | 4.0% |
| 0.35 | 1.6% | 0 of 100 | 2.7% |
| 0.40 | 0.5% | 0 of 100 | 1.2% |
| 0.50 | 0.1% | 0 of 100 | 0.6% |

Point estimates (mean over cells):

| Estimator | Mean bias | Mean |bias| | Mean RMSE |
|---|---:|---:|---:|
| Rogan–Gladen, clipped (judgy) | +0.0000 | 0.0565 | 0.2349 |

Cells with fewer than 100 usable data sets (excluded above): 0 of 950. Data sets excluded for observed TPR + TNR ≤ 1: 7.6%. Mean share of judgy bootstrap replicates dropped for TPR + TNR ≤ 1: 6.2% (max cell 19.9%).

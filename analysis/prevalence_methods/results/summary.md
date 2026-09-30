| Method | Median coverage | Cells < 90% | Cells < 80% | Mean width |
|---|---:|---:|---:|---:|
| judgy (test only, drops TPR+TNR≤1) | 0.892 | 54% | 28% | 0.378 |
| skill bootstrap (test only, keeps) | 0.902 | 48% | 26% | 0.410 |
| repo helper (test + unlabeled) | 0.946 | 8% | 3% | 0.476 |
| stratified bootstrap (test + unlabeled) | 0.946 | 8% | 3% | 0.468 |
| Lang–Reiczigel | 0.963 | 0% | 0% | 0.472 |
| Wilson, TPR/TNR known (epiR default) | 0.635 | 87% | 71% | 0.229 |

Mean coverage by labels per class (averaged over the other factors):

| Method | 10 | 20 | 50 | 100 | 200 |
|---|---:|---:|---:|---:|---:|
| judgy (test only, drops TPR+TNR≤1) | 0.851 | 0.893 | 0.874 | 0.828 | 0.752 |
| skill bootstrap (test only, keeps) | 0.869 | 0.909 | 0.882 | 0.833 | 0.752 |
| repo helper (test + unlabeled) | 0.902 | 0.939 | 0.949 | 0.948 | 0.948 |
| stratified bootstrap (test + unlabeled) | 0.897 | 0.936 | 0.949 | 0.948 | 0.949 |
| Lang–Reiczigel | 0.977 | 0.971 | 0.963 | 0.957 | 0.956 |
| Wilson, TPR/TNR known (epiR default) | 0.400 | 0.498 | 0.641 | 0.733 | 0.812 |

Mean coverage by unlabeled sample size:

| Method | 100 | 1000 |
|---|---:|---:|
| judgy (test only, drops TPR+TNR≤1) | 0.776 | 0.904 |
| skill bootstrap (test only, keeps) | 0.788 | 0.910 |
| repo helper (test + unlabeled) | 0.941 | 0.933 |
| stratified bootstrap (test + unlabeled) | 0.941 | 0.931 |
| Lang–Reiczigel | 0.965 | 0.965 |
| Wilson, TPR/TNR known (epiR default) | 0.780 | 0.454 |

Mean coverage by true TPR + TNR − 1:

| Method | 0.20 | 0.35 | 0.50 | 0.65 | 0.80 |
|---|---:|---:|---:|---:|---:|
| judgy (test only, drops TPR+TNR≤1) | 0.876 | 0.870 | 0.847 | 0.822 | 0.756 |
| skill bootstrap (test only, keeps) | 0.915 | 0.883 | 0.852 | 0.824 | 0.755 |
| repo helper (test + unlabeled) | 0.969 | 0.952 | 0.936 | 0.926 | 0.902 |
| stratified bootstrap (test + unlabeled) | 0.966 | 0.951 | 0.935 | 0.925 | 0.901 |
| Lang–Reiczigel | 0.973 | 0.966 | 0.963 | 0.962 | 0.965 |
| Wilson, TPR/TNR known (epiR default) | 0.588 | 0.592 | 0.612 | 0.633 | 0.678 |

Exclusions and judgy's dropped replicates by true TPR + TNR − 1:

| TPR + TNR − 1 | Data sets excluded (observed TPR + TNR ≤ 1) | Cells with < 100 usable | Mean share of judgy replicates dropped |
|---:|---:|---:|---:|
| 0.20 | 8.1% | 0 of 50 | 7.2% |
| 0.35 | 1.8% | 0 of 100 | 2.8% |
| 0.50 | 0.2% | 0 of 150 | 0.9% |
| 0.65 | 0.0% | 0 of 100 | 0.2% |
| 0.80 | 0.0% | 0 of 50 | 0.0% |

Point estimates (mean over cells):

| Estimator | Mean bias | Mean |bias| | Mean RMSE |
|---|---:|---:|---:|
| Rogan–Gladen, clipped (judgy) | -0.0001 | 0.0184 | 0.1371 |

Cells with fewer than 100 usable data sets (excluded above): 0 of 450. Data sets excluded for observed TPR + TNR ≤ 1: 1.4%. Mean share of judgy bootstrap replicates dropped for TPR + TNR ≤ 1: 1.8% (max cell 16.2%).

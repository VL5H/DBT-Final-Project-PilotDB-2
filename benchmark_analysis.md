# Benchmark Analysis

The original paper's implementation fares poorly on realistic queries on smaller datasets (1GB-10GB).
This is to be expected, since large samples (which are harder to acquire from complex queries on smaller datasets) are required to achieve
the desired error bounds.

## Original Benchmark

When running our benchmark on the original implementation, only 1 of the 15 tested queries runs through our sample pipeline.
Additionally, two of the queries crashed due to a bug in the query rewriting process.

| Q | exact (s) | aqp (s) | AQP outcome |
|---|---|---|---|
| 1 | 30.65 | 29.32 | fallback (pilot ran, bounds > table) |
| 3 | 13.38 | 13.08 | gatekeeper skip (pilot cost > 5% of exact) |
| 4 | 13.5 | 15.17 | gatekeeper skip |
| 5 | 63.96 | 75.98 | gatekeeper skip |
| 6 | 5.75 | 2.5 | 1.95% sample rate, 2.30x speedup |
| 7 | 9.69 | 9.94 | gatekeeper skip |
| 8 | 11.89 | 12.11 | gatekeeper skip |
| 9 | 43.19 | 50.18 | gatekeeper skip |
| 10 | 21.69 | 18.98 | gatekeeper skip |
| 12 | 11.81 | 12.65 | gatekeeper skip |
| 14 | 7.4 | 9.12 | fallback |
| 17 | timeout | timeout | timeout (>30min) |
| 18 | 166.79 | crash | rewriter bug |
| 19 | 7.32 | 7.87 | fallback |
| 22 | 4.93 | crash | rewriter bug |

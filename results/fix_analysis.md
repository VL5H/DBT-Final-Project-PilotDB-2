# Fix Phase — Implementation and Results (Nov 9-10, 2026)

Three repairs to published PilotDB, each behind the published default so all
experiments are controlled A/Bs. Modified files: `pilotdb/execute.py`,
`pilotdb/pilot_engine/error_bounds.py`, `pilotdb/utils/utils.py`.
New experiment scripts: `run_benchmark_plugin.py`, `coverage_check.py`.

## Repair A — subquery substitution ordering bug (crash fix)
`execute_aqp` passed the pilot query to the cost gate BEFORE substituting
extracted WHERE-subquery placeholders, so queries like Q18/Q22 sent literal
`... IN subquery_0` to PostgreSQL and crashed. Fix: execute + substitute
subqueries before the gate.
Validated: Q22 error(1) -> clean 4s run; Q18 error(1) -> clean 86-117s run,
which is FASTER than the original exact query (159s) because the precomputed
IN-list beats the nested aggregate join.
Limitation: correlated subqueries (Q17) cannot be pre-executed; documented.

## Repair B / Fix 1 — measurement-based ("plugin") bounds
`PILOTDB_BOUNDS=plugin`: sample-size formulas use the pilot's measured
mean/std (CLT plug-in) instead of chi^2-inflated std upper bounds, t-deflated
means, and Bernoulli worst-case population sizes. Guarantee structure (Sidak
split across groups/statistics) unchanged - only estimation changed.

## Repair C — configurable max-sample-rate ceiling
`get_largest_sample_rate` hardcodes 5% for Postgres; any feasible plan above
it silently fell back. Now overridable via `PILOTDB_MAX_RATE`.

## Suite A/B (TPC-H SF10, 5% error @ 95%, PILOTDB_MAX_RATE=20)
Baseline: results/benchmark_sf10.csv. Fixed: results/benchmark_sf10_plugin.csv.

| | Published | Fixed |
|---|---|---|
| Queries sampling | 1 (Q6 @ 2.08%) | 2 (Q6 @ 1.69%, 2.7x wall; Q1 @ 6.35%, 1.7x wall) |
| Crashes | 2 (Q18, Q22) | 0 |
| Q1 demanded sample | 11.96x the table (fallback) | 6.35% (sampled; worst group error 0.63%) |
| Honest fallbacks | - | Q14 (41.7% demanded), Q19 (100%): selective predicates, pilot sees too few rows - sampling genuinely infeasible |
| Gatekeeper skips | 8 | 10 (5% cost-gate threshold untouched - future work) |
| Q17 | 30-min timeout | diagnosed: pilot query alone takes 905s (correlated predicate re-scans lineitem per sampled row); demanded 65% -> fallback |

## Coverage experiment (results/coverage_results.csv)
Does the 95% promise hold empirically without the worst-case machinery?
30 repetitions each of Q6 and Q1 under plugin bounds, max relative error per
run vs exact across all groups and columns:

- Q6: mean error 0.74%, max 1.87%, violations (>5%): 0/30
- Q1: mean error 1.00%, max 2.04%, violations (>5%): 0/30
- Overall: 0 violations in 60 runs. Rule of three: true violation rate
  bounded below ~5% at 95% confidence - the promise holds empirically at a
  fraction of the sample the published bounds demanded.

## Takeaway
Published PilotDB accelerated 1 of 15 TPC-H queries at SF10. With one bug fix
and measurement-based bounds, it accelerates 2 (including the first grouped
query), crashes on none, declines honestly where sampling cannot pay, and
keeps the 5%-at-95% promise empirically. Remaining levers: the 5% cost-gate
threshold (blocks 10 queries before sampling is considered), the error-budget
decomposition (halves the target before the bounds run), and per-group
allocation for selective/grouped workloads (Fix 2).

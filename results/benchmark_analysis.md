# SF10 Full-Suite Benchmark — Analysis (Nov 9, 2026)

TPC-H SF10 (60M-row lineitem), PostgreSQL 18, no indexes, 5% error @ 95% confidence,
30-min timeout per run. 15 queries x {exact, aqp}. Raw outputs: results/raw/.

## Headline
**PilotDB sampled on exactly 1 of 15 queries.** 8 were refused by the cost
gatekeeper before any sampling was attempted, 3 ran the pilot and fell back to
exact (bounds demanded more rows than the table holds), 2 crashed on a rewriter
bug, 1 timed out in both modes.

| Q | exact (s) | aqp (s) | AQP outcome |
|---|---|---|---|
| 1 | 49.5 | 50.6 | fallback (pilot ran, bounds > table) |
| 3 | 27.1 | 26.4 | gatekeeper skip (pilot cost > 5% of exact) |
| 4 | 36.1 | 33.8 | gatekeeper skip |
| 5 | 38.7 | 40.1 | gatekeeper skip |
| **6** | **17.2** | **9.6** | **sampled 2.08% — 1.8x wall / 2.7x engine speedup** |
| 7 | 23.7 | 24.3 | gatekeeper skip |
| 8 | 24.2 | 24.4 | gatekeeper skip |
| 9 | 60.6 | 59.2 | gatekeeper skip |
| 10 | 30.2 | 32.1 | gatekeeper skip |
| 12 | 29.7 | 28.6 | gatekeeper skip |
| 14 | 21.8 | 23.0 | fallback |
| 17 | timeout | timeout | exact baseline itself > 30 min (correlated subquery, no indexes) |
| 18 | 159.2 | crash | rewriter bug (below) |
| 19 | 21.6 | 22.5 | fallback |
| 22 | 12.1 | crash | rewriter bug (below) |

## Q6, the one success — oversampling confirmed again
aqp revenue 1,228,061,212.5 vs exact 1,230,113,636.0 -> achieved error **0.17%**
(target 5%, ~30x tighter). Sample rate 2.08%. Reading 2% of the data bought only
1.8x wall-clock speedup.

## Bug found: subquery placeholder never substituted (Q18, Q22)
The pilot rewriter extracts WHERE-clause subqueries into a placeholder token
(`subquery_0`, logged by pilot.py:770) but never substitutes a value back. The
pilot query reaches PostgreSQL containing literal invalid SQL:
- Q18: `... WHERE o_orderkey IN subquery_0`  -> psycopg2 SyntaxError
- Q22: `... AND c_acctbal > subquery_0`      -> psycopg2 UndefinedColumn

Crash site: `postgres_utils.is_high_estimated_cost` (line 34), called from
`execute.py:56` — i.e., any query with a subquery in WHERE dies before the cost
gate is even evaluated. Full tracebacks: results/raw/q18_aqp.txt, q22_aqp.txt.

## Q17
Timed out in BOTH modes: the exact baseline itself exceeds 30 min on an
index-less SF10 schema (correlated avg-per-part subquery). Excluded from
speedup comparisons; its aqp path would also hit the subquery bug above.

## Takeaway for the fixes
Across the standard benchmark, the published system's guarantee machinery plus
its cost gate reduce "approximate query processing" to one accelerated query.
Fix 1 (measurement-based bounds) targets the 3 fallbacks + the oversampling on
Q6; Fix 2 (per-group allocation) targets Q1-style grouped fallbacks; the
gatekeeper threshold and the subquery substitution bug are additional concrete
repair points.

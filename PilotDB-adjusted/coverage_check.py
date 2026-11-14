"""Coverage experiment: do plugin bounds still deliver <=5% error at least 95% of the time?
Runs Q6 and Q1 repeatedly under PILOTDB_BOUNDS=plugin, compares each run's result
to the exact answer, and reports the empirical error distribution and violation rate.
"""
import subprocess, sys, time, csv, glob, os

REPS = 30
CONFIG = "db_configs/postgres_tpch10.yml"
ENV = dict(os.environ, PILOTDB_BOUNDS="plugin", PILOTDB_MAX_RATE="20")

def newest(pat):
    f = sorted(glob.glob(pat), key=os.path.getmtime)
    return f[-1] if f else None

def load_rows(p):
    return list(csv.DictReader(open(p)))

# ground truths (newest exact result files)
exact6 = float(load_rows(newest("results/tpch-6-exact-*.csv"))[0]["revenue"])
e1 = {(r["l_returnflag"], r["l_linestatus"]): r for r in load_rows(newest("results/tpch-1-exact-*.csv"))}
cols1 = [c for c in list(e1.values())[0] if c not in ("", "l_returnflag", "l_linestatus")]

out = open("results/coverage_results.csv", "w", newline="", encoding="utf-8")
w = csv.writer(out)
w.writerow(["rep", "qid", "wall_s", "max_rel_error", "violation(>5%)"])

for rep in range(1, REPS + 1):
    for qid in ("6", "1"):
        before = set(glob.glob(f"results/tpch-{qid}-aqp-*.csv"))
        t0 = time.time()
        subprocess.run([sys.executable, "evaluate.py", "--benchmark", "tpch", "--qid", qid,
                        "--dbms", "postgres", "--db_config_file", CONFIG,
                        "--process_mode", "aqp", "--error", "0.05", "--failure_probability", "0.05"],
                       capture_output=True, text=True, timeout=600, env=ENV)
        wall = round(time.time() - t0, 2)
        new = set(glob.glob(f"results/tpch-{qid}-aqp-*.csv")) - before
        if not new:
            w.writerow([rep, qid, wall, "NO_RESULT", ""])
            continue
        rows = load_rows(new.pop())
        if qid == "6":
            err = abs(float(rows[0]["revenue"]) - exact6) / exact6
        else:
            err = 0.0
            for r in rows:
                g = (r["l_returnflag"], r["l_linestatus"])
                for c in cols1:
                    err = max(err, abs(float(r[c]) - float(e1[g][c])) / abs(float(e1[g][c])))
        w.writerow([rep, qid, wall, f"{err:.5f}", "YES" if err > 0.05 else "no"])
        out.flush()
        print(f"rep {rep:2d} Q{qid}: max err {err*100:.3f}%  ({wall}s)", flush=True)

print("DONE -> results/coverage_results.csv")

import subprocess, sys, time, csv, re, os

QIDS = ["1","3","4","5","6","7","8","9","10","12","14","17","18","19","22"]
CONFIG = "db_configs/postgres_tpch10.yml"
ERROR, PROB = "0.05", "0.05"
TIMEOUT = 1800  # 30 min cap per run

os.makedirs("results/raw", exist_ok=True)
rows = []

for qid in QIDS:
    for mode in ["exact", "aqp"]:
        cmd = [sys.executable, "evaluate.py", "--benchmark", "tpch", "--qid", qid,
               "--dbms", "postgres", "--db_config_file", CONFIG,
               "--process_mode", mode, "--error", ERROR, "--failure_probability", PROB]
        print(f"=== Q{qid} {mode} ...", flush=True)
        t0 = time.time()
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT)
            out = (p.stdout or "") + (p.stderr or "")
            status = "ok" if p.returncode == 0 else f"error({p.returncode})"
        except subprocess.TimeoutExpired as e:
            out = ((e.stdout or "") if isinstance(e.stdout, str) else "") + "\nTIMEOUT"
            status = "timeout"
        wall = round(time.time() - t0, 2)

        with open(f"results/raw/q{qid}_{mode}.txt", "w", encoding="utf-8") as f:
            f.write(out)

        def grab(pattern):
            m = re.search(pattern, out)
            return m.group(1) if m else ""

        rows.append({
            "qid": qid, "mode": mode, "status": status, "wall_seconds": wall,
            "exact_time": grab(r"exact execution time: ([\d.]+)"),
            "pilot_time": grab(r"pilot query executing time: ([\d.]+)"),
            "sampling_time": grab(r"sampling execution time: ([\d.]+)"),
            "final_sample_rate": grab(r"final sample rate: ([\d.]+)"),
            "fallback": "yes" if ("fall back" in out or "falls back" in out) else "no",
            "gatekeeper_skip": "yes" if "retrieving query plan time" in out and mode == "aqp" and "final sample rate" not in out else "no",
        })
        print(f"    done in {wall}s ({status})", flush=True)

        with open("results/benchmark_sf10.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows(rows)

print("ALL DONE -> results/benchmark_sf10.csv")
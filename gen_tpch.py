import duckdb
con = duckdb.connect()
con.execute("INSTALL tpch; LOAD tpch;")
print("generating 1GB of data, takes a minute...")
con.execute("CALL dbgen(sf=1)")
tables = ["lineitem","orders","customer","part","partsupp","supplier","nation","region"]
for t in tables:
    con.execute(f"COPY {t} TO '{t}.csv' (HEADER, DELIMITER ',')")
    print("wrote", t + ".csv")
print("done")
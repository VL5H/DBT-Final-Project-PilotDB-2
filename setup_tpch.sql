-- TPC-H SF1 schema + load for PostgreSQL (run in psql: first CREATE DATABASE tpch; then \c tpch)
-- Generate the CSVs first with gen_tpch.py, then fix the paths below to your username.

CREATE TABLE region (r_regionkey INT, r_name VARCHAR, r_comment VARCHAR);
CREATE TABLE nation (n_nationkey INT, n_name VARCHAR, n_regionkey INT, n_comment VARCHAR);
CREATE TABLE supplier (s_suppkey INT, s_name VARCHAR, s_address VARCHAR, s_nationkey INT, s_phone VARCHAR, s_acctbal DECIMAL(15,2), s_comment VARCHAR);
CREATE TABLE customer (c_custkey INT, c_name VARCHAR, c_address VARCHAR, c_nationkey INT, c_phone VARCHAR, c_acctbal DECIMAL(15,2), c_mktsegment VARCHAR, c_comment VARCHAR);
CREATE TABLE part (p_partkey INT, p_name VARCHAR, p_mfgr VARCHAR, p_brand VARCHAR, p_type VARCHAR, p_size INT, p_container VARCHAR, p_retailprice DECIMAL(15,2), p_comment VARCHAR);
CREATE TABLE partsupp (ps_partkey INT, ps_suppkey INT, ps_availqty INT, ps_supplycost DECIMAL(15,2), ps_comment VARCHAR);
CREATE TABLE orders (o_orderkey INT, o_custkey INT, o_orderstatus VARCHAR, o_totalprice DECIMAL(15,2), o_orderdate DATE, o_orderpriority VARCHAR, o_clerk VARCHAR, o_shippriority INT, o_comment VARCHAR);
CREATE TABLE lineitem (l_orderkey INT, l_partkey INT, l_suppkey INT, l_linenumber INT, l_quantity DECIMAL(15,2), l_extendedprice DECIMAL(15,2), l_discount DECIMAL(15,2), l_tax DECIMAL(15,2), l_returnflag VARCHAR, l_linestatus VARCHAR, l_shipdate DATE, l_commitdate DATE, l_receiptdate DATE, l_shipinstruct VARCHAR, l_shipmode VARCHAR, l_comment VARCHAR);

-- Load (psql only). CHANGE the path to wherever your CSVs are:
\copy region FROM 'C:/Users/YOURNAME/region.csv' WITH (FORMAT csv, HEADER true)
\copy nation FROM 'C:/Users/YOURNAME/nation.csv' WITH (FORMAT csv, HEADER true)
\copy supplier FROM 'C:/Users/YOURNAME/supplier.csv' WITH (FORMAT csv, HEADER true)
\copy customer FROM 'C:/Users/YOURNAME/customer.csv' WITH (FORMAT csv, HEADER true)
\copy part FROM 'C:/Users/YOURNAME/part.csv' WITH (FORMAT csv, HEADER true)
\copy partsupp FROM 'C:/Users/YOURNAME/partsupp.csv' WITH (FORMAT csv, HEADER true)
\copy orders FROM 'C:/Users/YOURNAME/orders.csv' WITH (FORMAT csv, HEADER true)
\copy lineitem FROM 'C:/Users/YOURNAME/lineitem.csv' WITH (FORMAT csv, HEADER true)

-- Verify: SELECT count(*) FROM lineitem;  -- should be 6001215 at SF1
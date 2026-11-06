"""STEP 3: Load clean data into SQLite and run the SQL queries."""
import sqlite3
import pandas as pd

pd.set_option("display.width", 140)
pd.set_option("display.max_columns", 20)

df = pd.read_csv("data/processed/telco_clean.csv")
conn = sqlite3.connect("data/processed/churn.db")
df.to_sql("customers", conn, if_exists="replace", index=False)

sql_text = open("sql/churn_queries.sql").read()
# split on semicolons, keep the comment line as the title of each query
for block in [b.strip() for b in sql_text.split(";") if "SELECT" in b]:
    title = [l for l in block.splitlines() if l.startswith("-- Q")][-1]
    query = "\n".join(l for l in block.splitlines() if not l.startswith("--"))
    print("=" * 70)
    print(title)
    print(pd.read_sql_query(query, conn).to_string(index=False))
conn.close()

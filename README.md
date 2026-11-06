# Customer Churn Analysis & Retention Insights

End-to-end churn analysis on the public IBM Telco Customer Churn dataset (7,043 customers, 21 columns).
Stack: Python, Pandas, SQL (SQLite), Power BI, statistical testing (SciPy).

## How to run
```
pip install pandas numpy scipy matplotlib
bash run_all.sh        # or run one step at a time, e.g. python3 src/step1_load.py
```
Dataset: `data/raw/telco_raw.csv` (original source: IBM telco-customer-churn sample data, also on Kaggle as "Telco Customer Churn").

## Pipeline
| Step | Script | What it does |
|---|---|---|
| 1 | src/step1_load.py | Load, inspect shape, dtypes, target balance |
| 2 | src/step2_clean.py | Fix TotalCharges (11 blank rows, all tenure 0), tidy categories, engineer TenureGroup / NumAddOns / AvgMonthlySpend |
| 3 | src/step3_sql.py + sql/churn_queries.sql | Load into SQLite, run 6 KPI queries |
| 4 | src/step4_eda.py | Segment churn charts, distributions, correlation ranking |
| 5 | src/step5_cohort.py | Tenure bands + Kaplan-Meier retention curves by contract |
| 6 | src/step6_hypothesis.py | Chi-square and Welch t-tests with effect sizes |
| 7 | src/step7_powerbi_export.py | Power BI-ready CSVs |

## Key findings
- Overall churn 26.5% (1,869 of 7,043), about $139K of monthly revenue.
- Contract is the strongest driver: month-to-month 42.7%, one-year 11.3%, two-year 2.8% (Cramer's V = 0.41).
- Tenure: churners average 18 months vs 37.6 for retained customers (Cohen's d = -0.89). Customers in months 1-12 churn at 47%.
- Fiber optic (41.9%) churns far more than DSL (19.0%). Electronic-check payers churn at 45.3% vs about 15-19% elsewhere.
- Among internet customers, churn falls steadily with add-on services: 52% with none down to 5% with all six. Tech support alone: 41.6% without vs 15.2% with.
- New month-to-month customers (tenure <= 12 months): 1,994 customers, 51.4% churn vs 16.7% for everyone else.
- Gender has no effect (p = 0.49), included as a control hypothesis.

## Retention recommendations
1. Offer incentives to move month-to-month customers to one- or two-year contracts, especially in the first 12 months.
2. Bundle tech support / security add-ons for fiber customers.
3. Nudge electronic-check payers toward auto-pay.
4. Investigate fiber service quality and pricing (higher charges, higher churn).

## Caveats (be ready to say these in interviews)
- Association, not causation: these are observational patterns.
- The dataset is a snapshot with no signup dates, so "cohorts" are tenure bands, and retention curves use Kaplan-Meier treating active customers as censored.
- Retention curve tails (months 65-72) rest on few customers and are noisy.

## Power BI dashboard (build this in Power BI Desktop yourself)
1. Get Data > Text/CSV > `outputs/tables/powerbi_customers.csv`. Optionally also load `outputs/tables/powerbi_segments.csv` and `retention_curves.csv`.
2. Create these measures (Modeling > New measure):
```
Total Customers = COUNTROWS(powerbi_customers)
Churned Customers = CALCULATE([Total Customers], powerbi_customers[Churned] = 1)
Churn Rate = DIVIDE([Churned Customers], [Total Customers])
Monthly Revenue Lost = CALCULATE(SUM(powerbi_customers[MonthlyCharges]), powerbi_customers[Churned] = 1)
Avg Tenure = AVERAGE(powerbi_customers[TenureMonths])
```
3. Page layout: KPI cards (Total Customers, Churn Rate, Monthly Revenue Lost, Avg Tenure) on top; bar charts of Churn Rate by Contract, TenureGroup, InternetService, PaymentMethod; a line chart from retention_curves.csv; slicers for Contract, InternetService, SeniorCitizen.
4. Check your numbers against `outputs/tables/powerbi_segments.csv`. They must match.
5. Screenshot the finished dashboard into the repo as `dashboard.png`.

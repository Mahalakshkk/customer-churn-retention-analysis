-- Churn analysis queries (SQLite syntax, works in Oracle/Postgres with minor changes)
-- Table: customers (loaded from data/telco_clean.csv)

-- Q1. Overall churn KPIs
SELECT COUNT(*)                                   AS total_customers,
       SUM(ChurnFlag)                             AS churned_customers,
       ROUND(100.0 * SUM(ChurnFlag) / COUNT(*), 2) AS churn_rate_pct,
       ROUND(SUM(CASE WHEN ChurnFlag = 1 THEN MonthlyCharges END), 0) AS monthly_revenue_lost
FROM customers;

-- Q2. Churn rate by contract type
SELECT Contract,
       COUNT(*)                                    AS customers,
       ROUND(100.0 * SUM(ChurnFlag) / COUNT(*), 2) AS churn_rate_pct
FROM customers
GROUP BY Contract
ORDER BY churn_rate_pct DESC;

-- Q3. Churn rate by tenure group
SELECT TenureGroup,
       COUNT(*)                                    AS customers,
       ROUND(100.0 * SUM(ChurnFlag) / COUNT(*), 2) AS churn_rate_pct
FROM customers
GROUP BY TenureGroup
ORDER BY MIN(tenure);

-- Q4. Churn by internet service and payment method (top risky segments)
SELECT InternetService, PaymentMethod,
       COUNT(*)                                    AS customers,
       ROUND(100.0 * SUM(ChurnFlag) / COUNT(*), 2) AS churn_rate_pct
FROM customers
GROUP BY InternetService, PaymentMethod
HAVING COUNT(*) >= 100
ORDER BY churn_rate_pct DESC
LIMIT 5;

-- Q5. Does having add-on services reduce churn?
SELECT NumAddOns,
       COUNT(*)                                    AS customers,
       ROUND(100.0 * SUM(ChurnFlag) / COUNT(*), 2) AS churn_rate_pct
FROM customers
GROUP BY NumAddOns
ORDER BY NumAddOns;

-- Q6. Revenue at risk: monthly revenue of month-to-month customers in their first year
SELECT COUNT(*)                         AS customers_at_risk,
       ROUND(SUM(MonthlyCharges), 0)    AS monthly_revenue_at_risk
FROM customers
WHERE Contract = 'Month-to-month' AND tenure <= 12 AND ChurnFlag = 0;

"""STEP 7: Export Power BI-ready tables."""
import pandas as pd

df = pd.read_csv("data/processed/telco_clean.csv")

# Fact table for the dashboard: one row per customer, readable column names
fact = df.rename(columns={"customerID": "CustomerID", "tenure": "TenureMonths", "ChurnFlag": "Churned"})
fact["ChurnStatus"] = fact["Churned"].map({1: "Churned", 0: "Retained"})
fact["RiskSegment"] = (
    (fact["Contract"] == "Month-to-month") & (fact["TenureMonths"] <= 12)
).map({True: "High risk: new month-to-month", False: "Other"})
fact.to_csv("outputs/tables/powerbi_customers.csv", index=False)

# Pre-aggregated segment table (handy for quick visuals and for checking your DAX results)
seg_frames = []
for dim in ["Contract", "TenureGroup", "InternetService", "PaymentMethod", "TechSupport", "SeniorCitizen"]:
    g = df.groupby(dim, observed=True).agg(Customers=("customerID", "count"),
                                           Churned=("ChurnFlag", "sum"),
                                           AvgMonthlyCharge=("MonthlyCharges", "mean")).reset_index()
    g.insert(0, "Dimension", dim)
    g = g.rename(columns={dim: "Segment"})
    g["ChurnRatePct"] = (g["Churned"] / g["Customers"] * 100).round(2)
    g["AvgMonthlyCharge"] = g["AvgMonthlyCharge"].round(2)
    seg_frames.append(g)
seg = pd.concat(seg_frames, ignore_index=True)
seg.to_csv("outputs/tables/powerbi_segments.csv", index=False)

print("powerbi_customers.csv:", fact.shape)
print("powerbi_segments.csv:", seg.shape)
print("\nRisk segment size:")
print(fact.groupby("RiskSegment").agg(customers=("CustomerID", "count"),
                                      churn_rate_pct=("Churned", lambda x: round(x.mean() * 100, 1))))

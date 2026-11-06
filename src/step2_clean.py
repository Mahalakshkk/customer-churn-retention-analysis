"""STEP 2: Clean the data and engineer features."""
import pandas as pd
import numpy as np

df = pd.read_csv("data/raw/telco_raw.csv")

# 1. TotalCharges is text because some rows contain a blank space " "
blank_mask = df["TotalCharges"].str.strip() == ""
print("Rows with blank TotalCharges:", blank_mask.sum())
print(df.loc[blank_mask, ["customerID", "tenure", "MonthlyCharges", "TotalCharges", "Churn"]])

df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
# These customers have tenure = 0 (brand new, never billed) -> TotalCharges is really 0
df.loc[df["tenure"] == 0, "TotalCharges"] = 0.0
print("\nMissing TotalCharges after fix:", df["TotalCharges"].isna().sum())

# 2. Duplicates
print("Duplicate customerIDs:", df["customerID"].duplicated().sum())

# 3. Binary target
df["ChurnFlag"] = (df["Churn"] == "Yes").astype(int)

# 4. SeniorCitizen 0/1 -> readable label
df["SeniorCitizen"] = df["SeniorCitizen"].map({0: "No", 1: "Yes"})

# 5. Tidy 'No internet service' / 'No phone service' (same meaning as 'No')
cols_no_service = ["MultipleLines", "OnlineSecurity", "OnlineBackup", "DeviceProtection",
                   "TechSupport", "StreamingTV", "StreamingMovies"]
for c in cols_no_service:
    df[c] = df[c].replace({"No internet service": "No", "No phone service": "No"})

# 6. Feature engineering
df["TenureGroup"] = pd.cut(df["tenure"], bins=[-1, 12, 24, 48, 60, 72],
                           labels=["0-12 mo", "13-24 mo", "25-48 mo", "49-60 mo", "61-72 mo"])
df["AvgMonthlySpend"] = np.where(df["tenure"] > 0, df["TotalCharges"] / df["tenure"], df["MonthlyCharges"])
addons = ["OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies"]
df["NumAddOns"] = (df[addons] == "Yes").sum(axis=1)

df.to_csv("data/processed/telco_clean.csv", index=False)
print("\nClean shape:", df.shape)
print(df[["tenure", "MonthlyCharges", "TotalCharges", "TenureGroup", "NumAddOns", "ChurnFlag"]].describe(include="all").T)
print("\nSaved -> data/processed/telco_clean.csv")

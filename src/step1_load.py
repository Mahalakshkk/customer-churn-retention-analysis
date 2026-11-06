"""STEP 1: Load the dataset and inspect it."""
import pandas as pd

df = pd.read_csv("data/raw/telco_raw.csv")

print("Shape (rows, columns):", df.shape)
print("\nColumn names and data types:")
print(df.dtypes)
print("\nFirst 5 rows:")
print(df.head())
print("\nMissing values per column:")
print(df.isna().sum()[df.isna().sum() > 0] if df.isna().sum().sum() else "None (but check blank strings!)")
print("\nTarget balance (Churn):")
print(df["Churn"].value_counts())
print(df["Churn"].value_counts(normalize=True).round(3))

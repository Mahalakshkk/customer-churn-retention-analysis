"""STEP 6: Statistical hypothesis testing of business assumptions.

For each assumption we state H0/H1, pick the right test, report the p-value AND an effect size
(a tiny p-value alone just means 'large sample'), then give the business reading.
alpha = 0.05
"""
import pandas as pd
import numpy as np
from scipy import stats

df = pd.read_csv("data/processed/telco_clean.csv")
ALPHA = 0.05
results = []


def cramers_v(table):
    chi2 = stats.chi2_contingency(table, correction=False)[0]
    n = table.values.sum()
    return np.sqrt(chi2 / (n * (min(table.shape) - 1)))


def chi_square_test(name, col, assumption):
    table = pd.crosstab(df[col], df["Churn"])
    chi2, p, dof, _ = stats.chi2_contingency(table)
    v = cramers_v(table)
    rates = (df.groupby(col)["ChurnFlag"].mean() * 100).round(1).to_dict()
    results.append({"test": name, "type": "Chi-square", "statistic": round(chi2, 1), "p_value": p,
                    "effect_size": f"Cramer's V = {v:.2f}", "significant": p < ALPHA})
    print("=" * 72)
    print(f"{name}\n  Assumption: {assumption}")
    print(f"  H0: churn is independent of {col}.   H1: churn depends on {col}.")
    print(f"  Churn rates (%): {rates}")
    print(f"  Chi-square = {chi2:.1f}, dof = {dof}, p = {p:.2e}, Cramer's V = {v:.2f}")
    print(f"  -> {'REJECT H0' if p < ALPHA else 'Fail to reject H0'}")


# --- H1: Contract type
chi_square_test("H1: Contract type", "Contract", "Longer contracts retain customers better")

# --- H2: Internet service type
chi_square_test("H2: Internet service", "InternetService", "Fiber customers churn more than DSL customers")

# --- H3: Payment method
chi_square_test("H3: Payment method", "PaymentMethod", "Electronic-check payers churn more")

# --- H4: Tech support (internet customers only, to avoid the 'no internet' confound)
inet = df[df["InternetService"] != "No"]
table = pd.crosstab(inet["TechSupport"], inet["Churn"])
chi2, p, dof, _ = stats.chi2_contingency(table)
rates = (inet.groupby("TechSupport")["ChurnFlag"].mean() * 100).round(1).to_dict()
v = cramers_v(table)
results.append({"test": "H4: Tech support (internet customers)", "type": "Chi-square", "statistic": round(chi2, 1),
                "p_value": p, "effect_size": f"Cramer's V = {v:.2f}", "significant": p < ALPHA})
print("=" * 72)
print("H4: Tech support (internet customers only)\n  Assumption: Customers with tech support churn less")
print(f"  Churn rates (%): {rates}")
print(f"  Chi-square = {chi2:.1f}, p = {p:.2e}, Cramer's V = {v:.2f}  -> {'REJECT H0' if p < ALPHA else 'Fail to reject H0'}")

# --- H5: Gender (a 'control' hypothesis - expected NOT to matter)
chi_square_test("H5: Gender (control)", "gender", "Gender does not affect churn")

# --- H6: Monthly charges differ between churned and retained (Welch t-test + Mann-Whitney)
a = df.loc[df.ChurnFlag == 1, "MonthlyCharges"]
b = df.loc[df.ChurnFlag == 0, "MonthlyCharges"]
t, p = stats.ttest_ind(a, b, equal_var=False)
u, p_mw = stats.mannwhitneyu(a, b, alternative="two-sided")
pooled = np.sqrt((a.var() + b.var()) / 2)
d = (a.mean() - b.mean()) / pooled
results.append({"test": "H6: Monthly charges (churned vs retained)", "type": "Welch t-test", "statistic": round(t, 1),
                "p_value": p, "effect_size": f"Cohen's d = {d:.2f}", "significant": p < ALPHA})
print("=" * 72)
print("H6: Monthly charges, churned vs retained\n  Assumption: Churned customers pay more per month")
print(f"  Mean churned = ${a.mean():.2f}, mean retained = ${b.mean():.2f}")
print(f"  Welch t = {t:.1f}, p = {p:.2e}; Mann-Whitney p = {p_mw:.2e}; Cohen's d = {d:.2f}")
print(f"  -> {'REJECT H0' if p < ALPHA else 'Fail to reject H0'}")

# --- H7: Tenure
a = df.loc[df.ChurnFlag == 1, "tenure"]
b = df.loc[df.ChurnFlag == 0, "tenure"]
t, p = stats.ttest_ind(a, b, equal_var=False)
u, p_mw = stats.mannwhitneyu(a, b, alternative="two-sided")
d = (a.mean() - b.mean()) / np.sqrt((a.var() + b.var()) / 2)
results.append({"test": "H7: Tenure (churned vs retained)", "type": "Welch t-test", "statistic": round(t, 1),
                "p_value": p, "effect_size": f"Cohen's d = {d:.2f}", "significant": p < ALPHA})
print("=" * 72)
print("H7: Tenure, churned vs retained\n  Assumption: Churned customers have shorter tenure")
print(f"  Mean churned = {a.mean():.1f} months, mean retained = {b.mean():.1f} months")
print(f"  Welch t = {t:.1f}, p = {p:.2e}; Mann-Whitney p = {p_mw:.2e}; Cohen's d = {d:.2f}")
print(f"  -> {'REJECT H0' if p < ALPHA else 'Fail to reject H0'}")

# --- Summary table
res = pd.DataFrame(results)
res["p_value"] = res["p_value"].map(lambda x: f"{x:.2e}")
print("\n" + "=" * 72)
print("SUMMARY (alpha = 0.05)")
print(res.to_string(index=False))
res.to_csv("outputs/tables/hypothesis_test_results.csv", index=False)

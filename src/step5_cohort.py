"""STEP 5: Cohort / retention analysis.

This dataset is a snapshot (no signup dates), so we use TENURE to build a survival-style
retention curve: for each month t, of customers observed at least t months, what share
had NOT yet churned? (Kaplan-Meier estimator, written by hand so you can explain it.)
Churned customers: event happened at `tenure`. Active customers: censored at `tenure`.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("data/processed/telco_clean.csv")
df = df[df["tenure"] > 0]          # tenure 0 = just joined, no observation time

SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
COLORS = {"Month-to-month": "#2a78d6", "One year": "#eb6834", "Two year": "#1baf7a"}


def km_curve(sub):
    """Kaplan-Meier survival: S(t) = prod over months <= t of (1 - churned_t / at_risk_t)."""
    out, s = [], 1.0
    for t in range(1, 73):
        at_risk = (sub["tenure"] >= t).sum()
        events = ((sub["tenure"] == t) & (sub["ChurnFlag"] == 1)).sum()
        if at_risk > 0:
            s *= 1 - events / at_risk
        out.append(s)
    return pd.Series(out, index=range(1, 73))


overall = km_curve(df)
print("Overall retention (share of customers still active):")
for m in (6, 12, 24, 36, 48, 72):
    print(f"  after {m:>2} months: {overall[m]*100:5.1f}%")

# ---- Cohort table: tenure cohorts (the year each customer joined, relative to the data snapshot)
# NOTE: for churned customers tenure = months stayed before leaving, so these are TENURE bands,
# not true signup cohorts (the dataset has no signup date).
df["TenureBand"] = pd.cut(df["tenure"], [0, 12, 24, 36, 48, 60, 72],
                          labels=["1-12 mo", "13-24 mo", "25-36 mo", "37-48 mo", "49-60 mo", "61-72 mo"])
cohort = df.groupby("TenureBand", observed=True).agg(
    customers=("customerID", "count"),
    churned=("ChurnFlag", "sum"),
    churn_rate_pct=("ChurnFlag", lambda x: round(x.mean() * 100, 1)),
    avg_monthly_charge=("MonthlyCharges", lambda x: round(x.mean(), 1)),
)
print("\nTenure-band table (customers grouped by months of tenure):")
print(cohort)

# ---- Retention by contract
print("\nRetention by contract type:")
rows = {}
for name in COLORS:
    c = km_curve(df[df["Contract"] == name])
    rows[name] = c
    print(f"  {name:<15} 12mo: {c[12]*100:5.1f}%   24mo: {c[24]*100:5.1f}%   48mo: {c[48]*100:5.1f}%   72mo: {c[72]*100:5.1f}%")

# ---- Chart: retention curves by contract
fig, ax = plt.subplots(figsize=(7.5, 4.4), facecolor=SURFACE)
for name, curve in rows.items():
    ax.plot(curve.index, curve.values * 100, color=COLORS[name], linewidth=2, label=name)
    ax.text(72.5, curve.values[-1] * 100, f"{curve.values[-1]*100:.0f}%", color=INK2, va="center", fontsize=9)
ax.set_facecolor(SURFACE)
ax.set_title("Customer retention curve by contract type", loc="left", fontsize=13, color=INK, fontweight="bold", pad=12)
ax.set_xlabel("Months since joining", color=INK2)
ax.set_ylabel("Customers still active (%)", color=INK2)
ax.set_ylim(0, 102)
ax.set_xlim(0, 77)
ax.tick_params(colors=INK2)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.grid(axis="y", color=GRID, linewidth=0.8)
ax.legend(frameon=False, labelcolor=INK2, loc="lower left")
fig.tight_layout()
fig.savefig("outputs/charts/06_retention_curves.png", dpi=150, facecolor=SURFACE)
plt.close(fig)

# ---- Save tables for Power BI
cohort.reset_index().to_csv("outputs/tables/cohort_table.csv", index=False)
pd.DataFrame(rows).rename_axis("month").reset_index().to_csv("outputs/tables/retention_curves.csv", index=False)
print("\nSaved: outputs/charts/06_retention_curves.png, cohort_table.csv, retention_curves.csv")

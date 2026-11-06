"""STEP 4: Exploratory data analysis with charts saved to outputs/."""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("data/processed/telco_clean.csv")
df["TenureGroup"] = pd.Categorical(df["TenureGroup"],
                                   ["0-12 mo", "13-24 mo", "25-48 mo", "49-60 mo", "61-72 mo"], ordered=True)

SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e6e5e1"
BLUE, ORANGE = "#2a78d6", "#eb6834"   # series 1 = retained, series 2 = churned
overall = df["ChurnFlag"].mean() * 100


def style(ax, title, xlabel="", ylabel=""):
    ax.set_facecolor(SURFACE)
    ax.set_title(title, loc="left", fontsize=13, color=INK, fontweight="bold", pad=12)
    ax.set_xlabel(xlabel, color=INK2)
    ax.set_ylabel(ylabel, color=INK2)
    ax.tick_params(colors=INK2)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def churn_bar(col, title, fname, order=None):
    g = df.groupby(col, observed=True)["ChurnFlag"].agg(["mean", "size"])
    if order is not None:
        g = g.loc[order]
    g["mean"] *= 100
    fig, ax = plt.subplots(figsize=(7, 4.2), facecolor=SURFACE)
    labels = [str(i).replace(" (automatic)", "\n(automatic)") for i in g.index]
    bars = ax.bar(labels, g["mean"], color=BLUE, width=0.55)
    ax.axhline(overall, color=INK2, linestyle="--", linewidth=1)
    ax.text(len(g) - 0.5, overall + 1, f"Overall {overall:.1f}%", ha="right", color=INK2, fontsize=9)
    for b, (v, n) in zip(bars, zip(g["mean"], g["size"])):
        ax.text(b.get_x() + b.get_width() / 2, v + 1, f"{v:.1f}%", ha="center", color=INK, fontsize=10)
    style(ax, title, ylabel="Churn rate (%)")
    ax.set_ylim(0, max(g["mean"]) * 1.2)
    fig.tight_layout()
    fig.savefig(f"outputs/charts/{fname}", dpi=150, facecolor=SURFACE)
    plt.close(fig)


# ---- Chart 1-4: churn rate by key segments
churn_bar("Contract", "Churn rate by contract type", "01_churn_by_contract.png",
          ["Month-to-month", "One year", "Two year"])
churn_bar("TenureGroup", "Churn rate by customer tenure", "02_churn_by_tenure.png")
churn_bar("InternetService", "Churn rate by internet service", "03_churn_by_internet.png",
          ["DSL", "Fiber optic", "No"])
churn_bar("PaymentMethod", "Churn rate by payment method", "04_churn_by_payment.png")

# ---- Chart 5: monthly charges distribution, churned vs retained (2 series, legend present)
fig, ax = plt.subplots(figsize=(7, 4.2), facecolor=SURFACE)
bins = np.linspace(df["MonthlyCharges"].min(), df["MonthlyCharges"].max(), 25)
ax.hist([df.loc[df.ChurnFlag == 0, "MonthlyCharges"], df.loc[df.ChurnFlag == 1, "MonthlyCharges"]],
        bins=bins, stacked=True, color=[BLUE, ORANGE], label=["Retained", "Churned"],
        edgecolor=SURFACE, linewidth=1)
style(ax, "Monthly charges: churned vs retained customers", "Monthly charges ($)", "Customers")
ax.legend(frameon=False, labelcolor=INK2)
fig.tight_layout()
fig.savefig("outputs/charts/05_monthly_charges_dist.png", dpi=150, facecolor=SURFACE)
plt.close(fig)

# ---- Numeric summary: churned vs retained
print("Average values, retained (0) vs churned (1):")
print(df.groupby("ChurnFlag")[["tenure", "MonthlyCharges", "TotalCharges", "NumAddOns"]].mean().round(1))

# ---- Follow-up on the add-on puzzle from SQL Q5: exclude customers with no internet
inet = df[df["InternetService"] != "No"]
print("\nAdd-ons vs churn, INTERNET customers only (n = %d):" % len(inet))
print((inet.groupby("NumAddOns")["ChurnFlag"].agg(["size", "mean"]).assign(mean=lambda x: (x["mean"] * 100).round(1))
       .rename(columns={"size": "customers", "mean": "churn_rate_pct"})))

# ---- Churn correlation ranking for numeric/encoded features
enc = pd.get_dummies(df.drop(columns=["customerID", "Churn", "TenureGroup"]), drop_first=True)
corr = enc.corr()["ChurnFlag"].drop("ChurnFlag").sort_values()
print("\nTop 5 features most associated with LOWER churn:")
print(corr.head(5).round(3))
print("\nTop 5 features most associated with HIGHER churn:")
print(corr.tail(5).round(3))

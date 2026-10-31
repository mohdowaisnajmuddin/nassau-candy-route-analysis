
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "data" / "processed" / "nassau_shipping_audited.csv"
OUTPUT = ROOT / "reports" / "ship_mode_analysis.csv"

df = pd.read_csv(INPUT)

# Aggregate product lines into unique orders.
orders = (
    df.groupby("Order ID", as_index=False)
    .agg(
        Ship_Mode=("Ship Mode", "first"),
        Sales=("Sales", "sum"),
        Cost=("Cost", "sum"),
        Gross_Profit=("Gross Profit", "sum"),
        Units=("Units", "sum"),
    )
)

if orders["Order ID"].duplicated().any():
    raise ValueError("Duplicate orders after aggregation.")

summary = (
    orders.groupby("Ship_Mode")
    .agg(
        Unique_Orders=("Order ID", "nunique"),
        Total_Sales=("Sales", "sum"),
        Total_Cost=("Cost", "sum"),
        Total_Gross_Profit=("Gross_Profit", "sum"),
        Total_Units=("Units", "sum"),
        Average_Order_Value=("Sales", "mean"),
        Average_Gross_Profit_Per_Order=("Gross_Profit", "mean"),
    )
    .reset_index()
)

summary["Gross_Margin_Percent"] = (
    summary["Total_Gross_Profit"] / summary["Total_Sales"] * 100
)

summary["Order_Share_Percent"] = (
    summary["Unique_Orders"] / len(orders) * 100
)

summary = summary.sort_values("Unique_Orders", ascending=False)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
summary.to_csv(OUTPUT, index=False)

print("ORDER-LEVEL SHIP MODE ANALYSIS")
print("--------------------------------")
print("Total unique orders:", len(orders))
print(summary.round(2).to_string(index=False))
print("\nSaved:", OUTPUT)

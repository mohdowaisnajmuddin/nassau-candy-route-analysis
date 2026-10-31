
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "data" / "processed" / "route_analysis_input.csv"
REPORTS = ROOT / "reports"

df = pd.read_csv(INPUT)

# One order must have consistent route and distance attributes.
order_fields = [
    "Factory",
    "Region",
    "State/Province",
    "Country/Region",
    "Straight_Line_Distance_KM",
    "Geographic_Validation_Result",
    "Geographic_Validation_Usable",
]

for column in order_fields:
    inconsistent = df.groupby("Order ID")[column].nunique(dropna=False)
    if (inconsistent > 1).any():
        raise ValueError(
            f"Some orders have inconsistent values for {column}."
        )

# Convert product-line data into one row per unique order.
orders = df.drop_duplicates(subset="Order ID").copy()

if len(orders) != df["Order ID"].nunique():
    raise ValueError("Order-level aggregation failed.")

orders["Geographic_Validation_Usable"] = (
    orders["Geographic_Validation_Usable"].astype(str).str.lower()
    .map({"true": True, "false": False})
)

if orders["Geographic_Validation_Usable"].isna().any():
    raise ValueError("Unexpected geographic usability values.")

def summarize_routes(data, route_columns):
    result = (
        data.groupby(route_columns, dropna=False)
        .agg(
            Unique_Orders=("Order ID", "nunique"),
            Mean_Distance_KM=("Straight_Line_Distance_KM", "mean"),
            Median_Distance_KM=("Straight_Line_Distance_KM", "median"),
            Distance_Std_KM=("Straight_Line_Distance_KM", "std"),
            Minimum_Distance_KM=("Straight_Line_Distance_KM", "min"),
            Maximum_Distance_KM=("Straight_Line_Distance_KM", "max"),
            Geographically_Usable_Orders=(
                "Geographic_Validation_Usable", "sum"
            ),
        )
        .reset_index()
    )

    result["Geographic_Usable_Percent"] = (
        result["Geographically_Usable_Orders"]
        / result["Unique_Orders"] * 100
    )

    return result.sort_values(
        ["Unique_Orders", "Mean_Distance_KM"],
        ascending=[False, True],
    )

# Include every order, retaining geographic exceptions.
region_all = summarize_routes(orders, ["Factory", "Region"])
state_all = summarize_routes(
    orders, ["Factory", "Country/Region", "State/Province"]
)

# Sensitivity analysis: use only orders inside matching reference areas.
verified_orders = orders[
    orders["Geographic_Validation_Usable"]
].copy()

region_verified = summarize_routes(
    verified_orders, ["Factory", "Region"]
)
state_verified = summarize_routes(
    verified_orders, ["Factory", "Country/Region", "State/Province"]
)

REPORTS.mkdir(parents=True, exist_ok=True)

outputs = {
    "factory_region_routes_all.csv": region_all,
    "factory_state_routes_all.csv": state_all,
    "factory_region_routes_verified.csv": region_verified,
    "factory_state_routes_verified.csv": state_verified,
}

for filename, result in outputs.items():
    result.to_csv(REPORTS / filename, index=False)

print("ROUTE DISTANCE AGGREGATION")
print("--------------------------")
print("Product lines:", len(df))
print("Unique orders:", len(orders))
print("Orders inside matching reference areas:", len(verified_orders))
print(
    "Orders outside or without matching boundaries:",
    len(orders) - len(verified_orders),
)

print("\nFactory → Region routes (all orders):")
print(region_all.to_string(index=False))

print("\nFactory → State route count:")
print(len(state_all))

print("\nFactory → Region routes (verified subset):")
print(region_verified.to_string(index=False))

print("\nSaved reports:")
for filename in outputs:
    print(REPORTS / filename)


from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

SOURCE = ROOT / "data" / "processed" / "nassau_shipping_audited.csv"
DISTANCES = ROOT / "data" / "processed" / "geographically_audited_distances.csv"
OUTPUT = ROOT / "data" / "processed" / "route_analysis_input.csv"

source = pd.read_csv(SOURCE)
distances = pd.read_csv(DISTANCES)

# Keep only the fields needed to restore Region.
region_data = source[["Row ID", "Region"]].copy()

# Verify the join key before merging.
if region_data["Row ID"].duplicated().any():
    raise ValueError("Duplicate Row IDs in source data.")

if distances["Row ID"].duplicated().any():
    raise ValueError("Duplicate Row IDs in distance data.")

# Add Region without changing the original distance records.
result = distances.merge(
    region_data,
    on="Row ID",
    how="left",
    validate="one_to_one",
    indicator=True,
)

if not (result["_merge"] == "both").all():
    raise ValueError("Some distance records could not be matched.")

result = result.drop(columns="_merge")

# Verify order-level consistency.
region_counts = result.groupby("Order ID")["Region"].nunique()

if (region_counts > 1).any():
    raise ValueError("Some orders have multiple regions.")

if result["Region"].isna().any():
    raise ValueError("Missing Region values after merge.")

# Preserve row count and distance values.
if len(result) != len(distances):
    raise ValueError("Row count changed after merge.")

if not result["Straight_Line_Distance_KM"].equals(
    distances["Straight_Line_Distance_KM"]
):
    raise ValueError("Distance values changed after merge.")

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
result.to_csv(OUTPUT, index=False)

print("ROUTE ANALYSIS INPUT PREPARED")
print("-----------------------------")
print("Rows:", len(result))
print("Unique orders:", result["Order ID"].nunique())
print("Unique Row IDs:", result["Row ID"].nunique())
print("Missing regions:", result["Region"].isna().sum())

print("\nRegion distribution:")
print(result["Region"].value_counts().to_string())

print("\nGeographic validation:")
print(result["Geographic_Validation_Result"].value_counts().to_string())

print("\nSaved:", OUTPUT)

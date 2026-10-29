
from pathlib import Path

import pandas as pd
import plotly.express as px

# --------------------------------------------------
# 1. Paths
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

RAW_FILE = ROOT / "data" / "raw" / "Nassau Candy Distributor.csv"

DISTANCE_FILE = (
    ROOT / "data" / "processed"
    / "factory_destination_distances.csv"
)

OUTPUT_FILE = (
    ROOT / "reports" / "ship_mode_analysis.csv"
)

# --------------------------------------------------
# 2. Load and validate source data
# --------------------------------------------------

raw = pd.read_csv(RAW_FILE)
distance = pd.read_csv(DISTANCE_FILE)

required_raw = {"Row ID", "Ship Mode", "Order ID"}
required_distance = {
    "Row ID",
    "Order ID",
    "Straight_Line_Distance_KM",
}

if not required_raw.issubset(raw.columns):
    raise ValueError(
        f"Missing raw columns: {required_raw - set(raw.columns)}"
    )

if not required_distance.issubset(distance.columns):
    raise ValueError(
        "Distance file is missing required columns: "
        f"{required_distance - set(distance.columns)}"
    )

for name, frame in [("raw", raw), ("distance", distance)]:
    if frame["Row ID"].isna().any():
        raise ValueError(f"{name} contains missing Row IDs.")

    if frame["Row ID"].duplicated().any():
        raise ValueError(f"{name} contains duplicate Row IDs.")

# Join only the required fields using the validated Row ID.
ship_modes = raw[["Row ID", "Ship Mode"]].copy()

df = distance.merge(
    ship_modes,
    on="Row ID",
    how="left",
    validate="one_to_one",
    indicator=True,
)

if len(df) != len(distance):
    raise ValueError("Join unexpectedly changed the row count.")

if not df["_merge"].eq("both").all():
    raise ValueError("Some processed rows did not match the raw data.")

df = df.drop(columns="_merge")

if df["Ship Mode"].isna().any():
    raise ValueError("Some rows have no Ship Mode after joining.")

# --------------------------------------------------
# 3. Summarize by shipping method
# --------------------------------------------------

summary = (
    df.groupby("Ship Mode", dropna=False)
    .agg(
        Order_Lines=("Row ID", "size"),
        Distinct_Orders=("Order ID", "nunique"),
        Mean_Estimated_Distance_KM=(
            "Straight_Line_Distance_KM", "mean"
        ),
        Median_Estimated_Distance_KM=(
            "Straight_Line_Distance_KM", "median"
        ),
        Minimum_Estimated_Distance_KM=(
            "Straight_Line_Distance_KM", "min"
        ),
        Maximum_Estimated_Distance_KM=(
            "Straight_Line_Distance_KM", "max"
        ),
    )
    .reset_index()
)

distance_columns = [
    "Mean_Estimated_Distance_KM",
    "Median_Estimated_Distance_KM",
    "Minimum_Estimated_Distance_KM",
    "Maximum_Estimated_Distance_KM",
]

summary[distance_columns] = summary[distance_columns].round(2)

# --------------------------------------------------
# 4. Save report
# --------------------------------------------------

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
summary.to_csv(OUTPUT_FILE, index=False)

# --------------------------------------------------
# 5. Print validation and results
# --------------------------------------------------

print("SHIP-MODE ANALYSIS")
print("------------------")
print("Raw rows:", len(raw))
print("Distance rows:", len(distance))
print("Joined rows:", len(df))
print("Unmatched rows:", int((df["Ship Mode"].isna()).sum()))
print("Shipping methods:", df["Ship Mode"].nunique())

print("\nSUMMARY")
print(summary.to_string(index=False))

print("\nSaved report:", OUTPUT_FILE)
print(
    "\nInterpretation note: distances are estimated straight-line "
    "distances, not road distances or delivery times. The date anomaly "
    "prevents reliable shipping-speed or on-time-delivery conclusions."
)

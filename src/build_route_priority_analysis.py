
from pathlib import Path

import pandas as pd


# --------------------------------------------------
# 1. Project paths
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    ROOT
    / "reports"
    / "factory_destination_route_analysis.csv"
)

OUTPUT_FILE = (
    ROOT
    / "reports"
    / "route_priority_analysis.csv"
)

if not INPUT_FILE.exists():
    raise FileNotFoundError(
        f"Route analysis file not found: {INPUT_FILE}"
    )


# --------------------------------------------------
# 2. Load and validate data
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE)

required_columns = [
    "Factory",
    "Country/Region",
    "State/Province",
    "City",
    "Postal Code",
    "Distinct_Orders",
    "Distinct_Orders",
    "Mean_Estimated_Distance_KM",
    "Status_Count_Found",
    "Status_Count_Found_Canada_FSA",
    "Status_Count_Retry_Found",
    "Status_Count_Review",
    "Missing_Distance_Rows",
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Required columns are missing: {missing_columns}"
    )

if df.empty:
    raise ValueError("The route analysis file contains no rows.")

if df.duplicated(
    subset=[
        "Factory",
        "Country/Region",
        "State/Province",
        "City",
        "Postal Code",
    ]
).any():
    raise ValueError(
        "Duplicate factory-destination groups detected. "
        "Investigate these before ranking."
    )

# Convert analysis columns to numeric.
numeric_columns = [
    "Order_Lines",
    "Distinct_Orders",
    "Mean_Estimated_Distance_KM",
    "Status_Count_Found",
    "Status_Count_Found_Canada_FSA",
    "Status_Count_Retry_Found",
    "Status_Count_Review",
    "Missing_Distance_Rows",
]

for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce",
    )

if (df["Order_Lines"].dropna() < 0).any():
    raise ValueError("Negative order-line counts detected.")

if (
    df["Mean_Estimated_Distance_KM"].dropna() < 0
).any():
    raise ValueError("Negative estimated distances detected.")


# --------------------------------------------------
# 3. Measure coordinate-status uncertainty
# --------------------------------------------------

# These are status counts, not independently verified errors.
# Canada FSA coordinates represent postal areas rather than
# necessarily exact customer addresses.

# --------------------------------------------------
# 3. Classify coordinate-quality concerns separately
# --------------------------------------------------

# These categories indicate different types of uncertainty.
# They do not prove that any coordinate is incorrect.

df["Canada_FSA_Count"] = (
    df["Status_Count_Found_Canada_FSA"].fillna(0)
)

df["Retry_Found_Count"] = (
    df["Status_Count_Retry_Found"].fillna(0)
)

df["Ambiguous_Review_Count"] = (
    df["Status_Count_Review"].fillna(0)
)

df["Coordinate_Status_Flag_Count"] = (
    df["Canada_FSA_Count"]
    + df["Retry_Found_Count"]
    + df["Ambiguous_Review_Count"]
)

df["Has_Ambiguous_Matches"] = (
    df["Ambiguous_Review_Count"] > 0
)

df["Has_Canada_FSA_Coordinates"] = (
    df["Canada_FSA_Count"] > 0
)

df["Has_Retry_Found_Matches"] = (
    df["Retry_Found_Count"] > 0
)

df["Has_Missing_Distances"] = (
    df["Missing_Distance_Rows"].fillna(0) > 0
)

# Percentage of unique orders in a group with a flagged status.
df["Coordinate_Status_Flag_Rate_Pct"] = (
    df["Coordinate_Status_Flag_Count"]
    .div(df["Distinct_Orders"].replace(0, pd.NA))
    .mul(100)
)


# --------------------------------------------------
# 4. Identify high-volume and long-distance groups
# --------------------------------------------------

# Use the 75th percentile as a transparent screening threshold.
# This is an analytical choice, not an official business target.

volume_threshold = df["Distinct_Orders"].quantile(0.75)

distance_values = df[
    "Mean_Estimated_Distance_KM"
].dropna()

distance_threshold = (
    distance_values.quantile(0.75)
    if not distance_values.empty
    else None
)

df["High_Volume"] = (
    df["Distinct_Orders"] >= volume_threshold
)

if distance_threshold is not None:
    df["Long_Estimated_Distance"] = (
        df["Mean_Estimated_Distance_KM"]
        >= distance_threshold
    )
else:
    df["Long_Estimated_Distance"] = False


# --------------------------------------------------
# 5. Assign transparent investigation categories
# --------------------------------------------------

def assign_priority(row):
    high_volume = bool(row["High_Volume"])
    long_distance = bool(row["Long_Estimated_Distance"])
    ambiguous = bool(row["Has_Ambiguous_Matches"])
    canada_fsa = bool(row["Has_Canada_FSA_Coordinates"])
    retry_found = bool(row["Has_Retry_Found_Matches"])
    missing_distance = bool(row["Has_Missing_Distances"])

    if missing_distance:
        return "Data validation required"

    if ambiguous:
        return "Ambiguous geocoding review"

    if canada_fsa:
        return "Approximate Canadian postal-area coordinates"

    if retry_found:
        return "Retry-found coordinates to verify"

    if high_volume and long_distance:
        return "High volume + long estimated distance"

    if high_volume:
        return "High volume"

    if long_distance:
        return "Long estimated distance"

    return "Routine screening"


df["Investigation_Category"] = df.apply(
    assign_priority,
    axis=1,
)


# --------------------------------------------------
# 6. Rank groups for investigation
# --------------------------------------------------

# This ordering is deliberately not a claimed efficiency score.
# It sorts by visible criteria so the highest-volume and
# longest-distance candidates can be reviewed first.


df = df.sort_values(
    by=[
        "Has_Missing_Distances",
        "Has_Ambiguous_Matches",
        "Has_Canada_FSA_Coordinates",
        "Has_Retry_Found_Matches",
        "High_Volume",
        "Long_Estimated_Distance",
        "Distinct_Orders",
    ],
    ascending=[
        False,
        False,
        False,
        False,
        False,
        False,
        False,
    ],
).reset_index(drop=True)


df.insert(
    0,
    "Investigation_Rank",
    range(1, len(df) + 1),
)


# --------------------------------------------------
# 7. Save the report
# --------------------------------------------------

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

df.to_csv(
    OUTPUT_FILE,
    index=False,
)


# --------------------------------------------------
# 8. Print validation and summary
# --------------------------------------------------

print("ROUTE PRIORITY ANALYSIS")
print("=" * 60)

print(f"Input groups: {len(df):,}")
print(f"Output groups: {len(df):,}")
print(f"Volume threshold (75th percentile): {volume_threshold:.2f}")

if distance_threshold is not None:
    print(
        "Distance threshold (75th percentile): "
        f"{distance_threshold:.2f} km"
    )
else:
    print("Distance threshold: unavailable")

print(
    "High-volume groups: "
    f"{df['High_Volume'].sum():,}"
)

print(
    "Long estimated-distance groups: "
    f"{df['Long_Estimated_Distance'].sum():,}"
)

print(
    "Groups with coordinate-status flags: "
    f"{df['Has_Ambiguous_Matches'].sum():,}"
    " (ambiguous geocoding groups)"
)

print(
    "Groups with missing distances: "
f"{df['Has_Missing_Distances'].sum():,}"
)

print("\nInvestigation categories:")
print(
    df["Investigation_Category"]
    .value_counts()
    .to_string()
)

print("\nTop 10 groups for investigation:")
display_columns = [
    "Investigation_Rank",
    "Factory",
    "City",
    "State/Province",
    "Distinct_Orders",
    "Order_Lines",
    "Mean_Estimated_Distance_KM",
    "Coordinate_Status_Flag_Count",
    "Investigation_Category",
]

print(
    df[display_columns]
    .head(10)
    .to_string(index=False)
)

print(f"\nSaved report: {OUTPUT_FILE}")

print(
    "\nLimitations: distance is straight-line geographic "
    "separation, not road distance. Priority categories are "
    "screening indicators, not measured shipping efficiency. "
    "Shipping-date anomalies remain unresolved."
)

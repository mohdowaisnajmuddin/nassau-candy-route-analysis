
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "data" / "processed" / "factory_destination_distances.csv"
OUTPUT = ROOT / "reports" / "longest_distance_audit.csv"

df = pd.read_csv(INPUT)

# Select the ten longest row-level distance estimates.
longest = (
    df.nlargest(10, "Straight_Line_Distance_KM")
    [
        [
            "Row ID",
            "Order ID",
            "Country/Region",
            "State/Province",
            "City",
            "Postal Code",
            "Product Name",
            "Factory",
            "Factory_Latitude",
            "Factory_Longitude",
            "Latitude",
            "Longitude",
            "Lookup_Status",
            "Match_Display_Name",
            "Straight_Line_Distance_KM",
        ]
    ]
    .copy()
)

# Recalculate the Haversine distance independently as a numerical check.
def haversine_km(lat1, lon1, lat2, lon2):
    radius_km = 6371.0088

    lat1, lon1, lat2, lon2 = map(
        np.radians, [lat1, lon1, lat2, lon2]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    )
    a = np.clip(a, 0, 1)

    return 2 * radius_km * np.arcsin(np.sqrt(a))


longest["Recalculated_Distance_KM"] = haversine_km(
    longest["Factory_Latitude"].to_numpy(),
    longest["Factory_Longitude"].to_numpy(),
    longest["Latitude"].to_numpy(),
    longest["Longitude"].to_numpy(),
)

longest["Absolute_Distance_Difference_KM"] = (
    longest["Straight_Line_Distance_KM"]
    - longest["Recalculated_Distance_KM"]
).abs()

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
longest.to_csv(OUTPUT, index=False)

print("Ten longest distance estimates:")
print(
    longest[
        [
            "City",
            "State/Province",
            "Postal Code",
            "Factory",
            "Lookup_Status",
            "Latitude",
            "Longitude",
            "Straight_Line_Distance_KM",
            "Absolute_Distance_Difference_KM",
        ]
    ].to_string(index=False)
)

print(
    "\nMaximum recalculation difference (km):",
    longest["Absolute_Distance_Difference_KM"].max(),
)
print("\nSaved:", OUTPUT)
print("No source coordinates or distances were changed.")

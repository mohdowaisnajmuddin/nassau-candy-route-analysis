
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import Geod

ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "data" / "processed" / "factory_destination_distances.csv"
OUTPUT = ROOT / "reports" / "independent_distance_verification.csv"

df = pd.read_csv(INPUT)

# WGS84 ellipsoidal geodesic calculator
geod = Geod(ellps="WGS84")

# Independent calculation using pyproj
azimuth_forward, azimuth_backward, distance_m = geod.inv(
    df["Factory_Longitude"].to_numpy(),
    df["Factory_Latitude"].to_numpy(),
    df["Longitude"].to_numpy(),
    df["Latitude"].to_numpy(),
)

df["Independent_Geodesic_KM"] = distance_m / 1000

df["Absolute_Difference_KM"] = (
    df["Straight_Line_Distance_KM"] - df["Independent_Geodesic_KM"]
).abs()

df["Percentage_Difference"] = (
    df["Absolute_Difference_KM"]
    / df["Independent_Geodesic_KM"].replace(0, np.nan)
) * 100

# A 0.5% tolerance allows for the difference between
# spherical and ellipsoidal Earth models.
df["Calculation_Check"] = np.where(
    df["Percentage_Difference"] <= 0.5,
    "Within 0.5% tolerance",
    "Review required",
)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT, index=False)

print("INDEPENDENT DISTANCE VERIFICATION")
print("---------------------------------")
print("Records checked:", len(df))
print(
    "Within 0.5% tolerance:",
    (df["Calculation_Check"] == "Within 0.5% tolerance").sum()
)
print(
    "Require review:",
    (df["Calculation_Check"] == "Review required").sum()
)

print("\nDifference statistics (km):")
print(df["Absolute_Difference_KM"].describe().round(6).to_string())

print("\nPercentage difference statistics:")
print(df["Percentage_Difference"].describe().round(6).to_string())

print("\nSaved:", OUTPUT)

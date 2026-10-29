
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = ROOT / "data" / "processed" / "geocoded_destinations.csv"
OUTPUT_PATH = ROOT / "reports" / "coordinate_match_audit.csv"

df = pd.read_csv(INPUT_PATH, dtype=str)

print("Available columns:")
print(df.columns.tolist())

# Preserve the original source values.
# This script does not modify or overwrite geocoded coordinates.
required = [
    "City",
    "State/Province",
    "Postal Code",
    "Latitude",
    "Longitude",
    "Lookup_Status",
]

missing = [col for col in required if col not in df.columns]
if missing:
    raise ValueError(
        f"Missing expected columns: {missing}. "
        "Check the printed column names and update the script."
    )

df["Latitude_Numeric"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude_Numeric"] = pd.to_numeric(df["Longitude"], errors="coerce")

# US ZIP codes may lose leading zeros when stored as numbers.
# Restore five-digit formatting only when the value is numeric.
def normalize_us_zip(value):
    if pd.isna(value):
        return ""
    value = str(value).strip()
    if value.endswith(".0"):
        value = value[:-2]
    if value.isdigit() and len(value) <= 5:
        return value.zfill(5)
    return value

df["Postal_Code_Normalized"] = df["Postal Code"].apply(normalize_us_zip)

df["Coordinate_Range_Valid"] = (
    df["Latitude_Numeric"].between(-90, 90)
    & df["Longitude_Numeric"].between(-180, 180)
)

# A coordinate-range check is not a geographic match check.
# We cannot establish postal-code consistency from coordinates alone
# without an independent postal-area boundary or geocoder reference.
df["Independent_Postal_Verification"] = "Not performed"
df["Audit_Note"] = (
    "Coordinates require comparison with an independent "
    "postal-area reference; range validity is not proof of accuracy."
)

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False)

print("\nCoordinate range validity:")
print(df["Coordinate_Range_Valid"].value_counts(dropna=False).to_string())

print("\nRecords by lookup status:")
print(df["Lookup_Status"].value_counts(dropna=False).to_string())

print(f"\nSaved audit file: {OUTPUT_PATH}")
print("No coordinates were changed.")

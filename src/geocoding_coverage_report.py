
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = ROOT / "data" / "processed" / "geocoded_destinations.csv"
OUTPUT_PATH = ROOT / "reports" / "geocoding_coverage_report.csv"

df = pd.read_csv(
    INPUT_PATH,
    dtype={"Postal Code": str},
)

# Check that coordinate values exist and are within valid geographic ranges.
df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

df["Has_Valid_Coordinates"] = (
    df["Latitude"].between(-90, 90)
    & df["Longitude"].between(-180, 180)
)

print("Total destination records:", len(df))
print("Valid coordinate records:", int(df["Has_Valid_Coordinates"].sum()))
print("Missing or invalid coordinates:", int((~df["Has_Valid_Coordinates"]).sum()))

print("\nGeocoding status counts:")
print(df["Lookup_Status"].value_counts(dropna=False).to_string())

print("\nCoordinate availability by status:")
print(
    df.groupby("Lookup_Status", dropna=False)["Has_Valid_Coordinates"]
    .agg(["count", "sum"])
    .to_string()
)

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

df.to_csv(OUTPUT_PATH, index=False)
print(f"\nSaved report: {OUTPUT_PATH}")

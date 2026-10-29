
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "processed" / "geocoded_destinations.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "ambiguous_geocoding.csv"

df = pd.read_csv(INPUT_PATH, dtype={"Postal Code": str})

review = df[df["Lookup_Status"] == "Review"].copy()

columns = [
    "Country/Region",
    "State/Province",
    "City",
    "Postal Code",
    "Latitude",
    "Longitude",
    "Match_Count",
    "Match_Display_Name",
]

review[columns].to_csv(OUTPUT_PATH, index=False)

print("Ambiguous destinations:", len(review))
print("\nReview details:")
print(review[columns].to_string(index=False))
print(f"\nSaved review file: {OUTPUT_PATH}")


from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "processed" / "geocoded_destinations.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "geocoding_review.csv"

df = pd.read_csv(INPUT_PATH, dtype={"Postal Code": str})

# Keep ambiguous and unsuccessful lookups for manual review.
needs_review = df[
    df["Lookup_Status"].isin(["Review", "Not found", "Error"])
].copy()

columns = [
    "Country/Region",
    "State/Province",
    "City",
    "Postal Code",
    "Lookup_Status",
    "Match_Count",
    "Latitude",
    "Longitude",
    "Match_Display_Name",
]

needs_review = needs_review[columns]
needs_review.to_csv(OUTPUT_PATH, index=False)

print("Destinations requiring review:", len(needs_review))
print("\nCounts by status:")
print(needs_review["Lookup_Status"].value_counts().to_string())

print("\nReview sample:")
print(needs_review.head(15).to_string(index=False))

print(f"\nFull review file saved to: {OUTPUT_PATH}")

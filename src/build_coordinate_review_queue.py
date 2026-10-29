
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = ROOT / "reports" / "coordinate_match_audit.csv"
OUTPUT_PATH = ROOT / "reports" / "coordinate_review_queue.csv"

df = pd.read_csv(INPUT_PATH, dtype=str)

# Prioritize records already flagged during geocoding.
flagged_statuses = {"Review", "Retry_Found", "Found_Canada_FSA"}

df["Review_Reason"] = ""

df.loc[
    df["Lookup_Status"].isin(flagged_statuses),
    "Review_Reason"
] = "Geocoding status requires review"

# Keep ordinary Found records in the queue too because they have
# not been independently verified.
df.loc[
    df["Lookup_Status"].eq("Found"),
    "Review_Reason"
] = "Independent verification not performed"

review_queue = df[
    [
        "City",
        "State/Province",
        "Postal Code",
        "Latitude",
        "Longitude",
        "Lookup_Status",
        "Coordinate_Range_Valid",
        "Independent_Postal_Verification",
        "Review_Reason",
    ]
].copy()

review_queue.to_csv(OUTPUT_PATH, index=False)

print("Review queue records:", len(review_queue))
print("\nReview queue by status:")
print(review_queue["Lookup_Status"].value_counts().to_string())

print("\nReview reasons:")
print(review_queue["Review_Reason"].value_counts().to_string())

print(f"\nSaved: {OUTPUT_PATH}")
print("Original geocoding coordinates were not changed.")

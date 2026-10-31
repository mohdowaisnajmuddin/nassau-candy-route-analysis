

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = ROOT / "reports" / "coordinate_match_audit.csv"

REVIEW_PATH = ROOT / "reports" / "coordinate_review_queue.csv"
REGISTER_PATH = ROOT / "reports" / "coordinate_verification_register.csv"

df = pd.read_csv(INPUT_PATH, dtype=str)

# Classify each destination without changing its original coordinates.
def classify_status(status):
    if status == "Review":
        return "Manual review required"
    if status == "Found_Canada_FSA":
        return "Approximate postal-area match"
    if status == "Retry_Found":
        return "Retry match; verification pending"
    if status == "Found":
        return "Matched; independent verification pending"
    return "Unknown status; investigation required"


df["Verification_Category"] = df["Lookup_Status"].apply(classify_status)

# Manual review queue: only records requiring investigation.
manual_review = df[
    df["Lookup_Status"].isin(["Review", "Found_Canada_FSA"])
].copy()

# Keep all destinations in a separate verification register.
verification_register = df.copy()

columns = [
    "City",
    "State/Province",
    "Postal Code",
    "Latitude",
    "Longitude",
    "Lookup_Status",
    "Coordinate_Range_Valid",
    "Independent_Postal_Verification",
    "Verification_Category",
]

manual_review[columns].to_csv(REVIEW_PATH, index=False)
verification_register[columns].to_csv(REGISTER_PATH, index=False)

print("TOTAL DESTINATIONS:", len(df))

print("\nMANUAL REVIEW QUEUE")
print("Records:", len(manual_review))
print(manual_review["Lookup_Status"].value_counts().to_string())

print("\nVERIFICATION REGISTER")
print("Records:", len(verification_register))
print(
    verification_register["Verification_Category"]
    .value_counts()
    .to_string()
)

print("\nSaved manual review queue:", REVIEW_PATH)
print("Saved verification register:", REGISTER_PATH)
print("\nOriginal geocoding coordinates were not changed.")

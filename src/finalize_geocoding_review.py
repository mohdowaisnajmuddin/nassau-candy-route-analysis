
from pathlib import Path
import pandas as pd
import re

ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = ROOT / "data" / "processed" / "ambiguous_geocoding_candidates.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "final_geocoding_review.csv"


def normalize_zip(value):
    if pd.isna(value):
        return ""
    digits = re.sub(r"\D", "", str(value))
    return digits.zfill(5) if digits else ""


df = pd.read_csv(
    INPUT_PATH,
    dtype={"Postal Code": str, "Candidate_Postcode": str},
)

df["Requested_ZIP_Normalized"] = df["Postal Code"].apply(normalize_zip)
df["Candidate_ZIP_Normalized"] = df["Candidate_Postcode"].apply(normalize_zip)

# A matching ZIP is evidence of consistency, not proof of exact coordinates.
df["ZIP_Consistent"] = (
    df["Requested_ZIP_Normalized"].ne("")
    & df["Requested_ZIP_Normalized"].eq(df["Candidate_ZIP_Normalized"])
)

# Keep every candidate visible; do not automatically select one.
df["Review_Decision"] = "Needs_Manual_Review"

df.loc[
    df["ZIP_Consistent"],
    "Review_Decision"
] = "ZIP_Consistent_Candidate"

no_zip = df["Candidate_ZIP_Normalized"].eq("")
has_city_state = (
    df["Candidate_City"].notna()
    & df["Candidate_State"].notna()
)

df.loc[
    no_zip & has_city_state,
    "Review_Decision"
] = "Approximate_City_Candidate"

columns = [
    "City",
    "State/Province",
    "Postal Code",
    "Candidate_Number",
    "Candidate_City",
    "Candidate_State",
    "Candidate_Postcode",
    "Candidate_Latitude",
    "Candidate_Longitude",
    "ZIP_Consistent",
    "Review_Decision",
    "Candidate_Display_Name",
]

df[columns].to_csv(OUTPUT_PATH, index=False)

print("Destination-level summary:")
summary = (
    df.groupby(["City", "State/Province", "Postal Code"], dropna=False)
    .agg(
        Candidate_Count=("Candidate_Number", "count"),
        ZIP_Consistent_Candidate=("ZIP_Consistent", "any"),
        Review_Decision=("Review_Decision", lambda s: ", ".join(sorted(set(s)))),
    )
    .reset_index()
)

print(summary.to_string(index=False))

print("\nCandidate-level decision counts:")
print(df["Review_Decision"].value_counts().to_string())

print(f"\nSaved review report: {OUTPUT_PATH}")
print("No source coordinates were changed.")


from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "processed" / "ambiguous_geocoding_candidates.csv"

df = pd.read_csv(INPUT_PATH, dtype={"Postal Code": str, "Candidate_Postcode": str})

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
    "Search_Status",
]

print("Total candidate rows:", len(df))
print(
    "Destinations searched:",
    df[["City", "State/Province", "Postal Code"]]
    .drop_duplicates()
    .shape[0],
)

print("\nCandidate details:")
print(df[columns].to_string(index=False))

print("\nSaved candidate file:", INPUT_PATH)

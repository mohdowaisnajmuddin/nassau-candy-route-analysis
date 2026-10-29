
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = ROOT / "data" / "processed" / "ambiguous_geocoding.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "geocoding_review_classified.csv"


def normalize(value):
    if pd.isna(value):
        return ""
    return str(value).strip().lower()


def normalize_zip(value):
    if pd.isna(value):
        return ""
    digits = re.sub(r"\D", "", str(value))
    return digits.zfill(5) if digits else ""


df = pd.read_csv(INPUT_PATH, dtype={"Postal Code": str})

review_status = []
review_reason = []

for _, row in df.iterrows():
    city = normalize(row["City"])
    state = normalize(row["State/Province"])
    postal_code = normalize_zip(row["Postal Code"])
    display = normalize(row["Match_Display_Name"])

    # Find ZIP-like codes in the geocoder's displayed result.
    result_zips = re.findall(r"(?<!\d)\d{5}(?!\d)", display)

    city_match = bool(city) and city in display
    state_match = bool(state) and state in display

    if result_zips and postal_code not in result_zips:
        status = "Needs_Review"
        reason = (
            f"Returned ZIP code(s) {', '.join(result_zips)} "
            f"do not match requested ZIP {postal_code}"
        )
    elif postal_code and postal_code in result_zips:
        status = "Potential_ZIP_Match"
        reason = "Requested ZIP appears in result; coordinate still needs verification"
    elif city_match and state_match:
        status = "Approximate_City_Candidate"
        reason = "City and state appear in result, but ZIP match is not confirmed"
    else:
        status = "Needs_Review"
        reason = "City, state, or postal-code match is not sufficiently established"

    review_status.append(status)
    review_reason.append(reason)

df["Review_Status"] = review_status
df["Review_Reason"] = review_reason

df.to_csv(OUTPUT_PATH, index=False)

print("Review classification counts:")
print(df["Review_Status"].value_counts().to_string())

print("\nClassified destinations:")
print(
    df[
        [
            "City",
            "State/Province",
            "Postal Code",
            "Match_Display_Name",
            "Review_Status",
            "Review_Reason",
        ]
    ].to_string(index=False)
)

print(f"\nSaved classified review: {OUTPUT_PATH}")


from pathlib import Path
import time
import requests
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = ROOT / "data" / "processed" / "ambiguous_geocoding.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "ambiguous_geocoding_candidates.csv"

df = pd.read_csv(INPUT_PATH, dtype={"Postal Code": str})

session = requests.Session()
session.headers.update({
    "User-Agent": "NassauCandyRouteAnalysis/1.0 (research project)"
})

results = []

for _, row in df.iterrows():
    city = str(row["City"]).strip()
    state = str(row["State/Province"]).strip()
    postal_code = str(row["Postal Code"]).strip()

    params = {
        "city": city,
        "state": state,
        "postalcode": postal_code,
        "country": "United States",
        "countrycodes": "us",
        "format": "jsonv2",
        "addressdetails": 1,
        "limit": 3,
    }

    record = {
        "City": city,
        "State/Province": state,
        "Postal Code": postal_code,
        "Candidate_Count": 0,
        "Candidate_Number": None,
        "Candidate_Latitude": None,
        "Candidate_Longitude": None,
        "Candidate_Display_Name": None,
        "Candidate_Postcode": None,
        "Candidate_City": None,
        "Candidate_State": None,
        "Search_Status": None,
    }

    try:
        response = session.get(
            "https://nominatim.openstreetmap.org/search",
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        candidates = response.json()

        record["Candidate_Count"] = len(candidates)
        record["Search_Status"] = (
            "Candidates_Returned" if candidates else "No_Candidates"
        )

        if not candidates:
            results.append(record)
        else:
            for number, candidate in enumerate(candidates, start=1):
                address = candidate.get("address", {})

                results.append({
                    **record,
                    "Candidate_Number": number,
                    "Candidate_Latitude": candidate.get("lat"),
                    "Candidate_Longitude": candidate.get("lon"),
                    "Candidate_Display_Name": candidate.get("display_name"),
                    "Candidate_Postcode": address.get("postcode"),
                    "Candidate_City": (
                        address.get("city")
                        or address.get("town")
                        or address.get("village")
                        or address.get("municipality")
                    ),
                    "Candidate_State": address.get("state"),
                })

        print(f"Checked: {city}, {state} {postal_code}")

    except requests.RequestException as exc:
        record["Search_Status"] = f"Request_Error: {exc}"
        results.append(record)
        print(f"Request failed: {city}, {state} {postal_code}: {exc}")

    # Keep requests spaced apart in line with the public service's usage policy.
    time.sleep(1.2)

output = pd.DataFrame(results)
output.to_csv(OUTPUT_PATH, index=False)

print("\nSearch status counts:")
print(output.drop_duplicates(
    ["City", "State/Province", "Postal Code"]
)["Search_Status"].value_counts(dropna=False).to_string())

print(f"\nCandidate results saved to: {OUTPUT_PATH}")
print("No existing coordinates were overwritten.")


from pathlib import Path
import time

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "processed" / "geocoded_destinations.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "geocoded_destinations.csv"
BACKUP_PATH = ROOT / "data" / "processed" / "geocoded_destinations_before_us_retry.csv"

def main():
    df = pd.read_csv(INPUT_PATH, dtype={"Postal Code": str})

    if not BACKUP_PATH.exists():
        df.to_csv(BACKUP_PATH, index=False)

    mask = (
        df["Country/Region"].eq("United States")
        & df["Lookup_Status"].isin(["Not found", "Error"])
    )

    session = requests.Session()
    session.headers.update({
        "User-Agent": "NassauCandyRouteAnalysis/1.0 (educational research project)"
    })

    for index in df.index[mask]:
        row = df.loc[index]
        query = {
            "city": row["City"],
            "state": row["State/Province"],
            "country": "United States",
            "postalcode": row["Postal Code"],
            "countrycodes": "us",
            "format": "jsonv2",
            "limit": 3,
            "addressdetails": 1,
        }

        try:
            response = session.get(
                "https://nominatim.openstreetmap.org/search",
                params=query,
                timeout=30,
            )
            response.raise_for_status()
            matches = response.json()

            # Only accept a unique result for now.
            if len(matches) == 1:
                match = matches[0]
                df.at[index, "Latitude"] = float(match["lat"])
                df.at[index, "Longitude"] = float(match["lon"])
                df.at[index, "Lookup_Status"] = "Retry_Found"
                df.at[index, "Match_Display_Name"] = match.get("display_name", "")
                df.at[index, "Match_Count"] = 1
                print(f"Found: {row['City']}, {row['State/Province']}")
            elif len(matches) > 1:
                df.at[index, "Lookup_Status"] = "Review"
                df.at[index, "Match_Count"] = len(matches)
                df.at[index, "Match_Display_Name"] = "Multiple results; needs validation"
                print(f"Review: {row['City']} - {len(matches)} candidates")
            else:
                print(f"Still not found: {row['City']}")

        except requests.RequestException as exc:
            print(f"Request failed for {row['City']}: {exc}")

        # Keep requests at least 1.1 seconds apart.
        time.sleep(1.1)

    df.to_csv(OUTPUT_PATH, index=False)

    print("\nUpdated status counts:")
    print(df["Lookup_Status"].value_counts(dropna=False).to_string())
    print(f"\nBackup: {BACKUP_PATH}")

if __name__ == "__main__":
    main()

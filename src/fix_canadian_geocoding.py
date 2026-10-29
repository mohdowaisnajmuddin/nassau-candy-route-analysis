
from pathlib import Path
import time
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "processed" / "geocoded_destinations.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "geocoded_destinations.csv"
BACKUP_PATH = ROOT / "data" / "processed" / "geocoded_destinations_before_canada_fix.csv"

def main():
    df = pd.read_csv(INPUT_PATH, dtype={"Postal Code": str})

    # Keep a backup before changing any coordinates or statuses.
    if not BACKUP_PATH.exists():
        df.to_csv(BACKUP_PATH, index=False)

    canada_mask = (
        df["Country/Region"].eq("Canada")
        & df["Lookup_Status"].eq("Not found")
    )

    session = requests.Session()
    updated = 0

    for index in df.index[canada_mask]:
        postal_prefix = str(df.at[index, "Postal Code"]).strip().upper()

        try:
            response = session.get(
                "https://geolocator.api.geo.ca/",
                params={
                    "q": postal_prefix,
                    "lang": "en",
                    "keys": "fsa",
                },
                timeout=30,
            )
            response.raise_for_status()
            matches = response.json()

            candidates = [
                item for item in matches
                if item.get("key") == "fsa"
                and item.get("category") == "Postal Code"
                and item.get("name", "").upper() == postal_prefix
            ]

            if len(candidates) == 1:
                match = candidates[0]
                df.at[index, "Latitude"] = float(match["lat"])
                df.at[index, "Longitude"] = float(match["lng"])
                df.at[index, "Lookup_Status"] = "Found_Canada_FSA"
                df.at[index, "Match_Display_Name"] = match["name"]
                df.at[index, "Match_Count"] = 1
                updated += 1
            else:
                print(f"Needs manual review: {postal_prefix} ({len(candidates)} matches)")

        except (requests.RequestException, ValueError, KeyError) as exc:
            print(f"Failed {postal_prefix}: {exc}")

        time.sleep(0.3)

    df.to_csv(OUTPUT_PATH, index=False)

    print("\nCanadian postal-area repairs:", updated)
    print("\nUpdated status counts:")
    print(df["Lookup_Status"].value_counts(dropna=False).to_string())
    print(f"\nBackup saved to: {BACKUP_PATH}")
    print(f"Updated results saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()

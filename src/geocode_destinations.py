
from pathlib import Path
import time

import pandas as pd
import requests


def lookup_canadian_fsa(session, postal_prefix):
    """Return a Canadian postal-area centroid from the geo.ca API."""
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
    results = response.json()

    # Only accept an explicit postal-code result.
    candidates = [
        result
        for result in results
        if result.get("key") == "fsa"
        and result.get("category") == "Postal Code"
        and result.get("name", "").upper() == postal_prefix.upper()
    ]

    if not candidates:
        return None

    return candidates[0]


ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "processed" / "unique_destinations.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "geocoded_destinations.csv"

HEADERS = {
    "User-Agent": "NassauCandyRouteAnalysis/1.0 (educational research project)"
}

KEY_COLUMNS = [
    "Country/Region",
    "State/Province",
    "City",
    "Postal Code",
]


def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Destination file not found: {INPUT_PATH}"
        )

    destinations = pd.read_csv(INPUT_PATH, dtype={"Postal Code": str})

    # Resume from existing results if the script has already run.
    if OUTPUT_PATH.exists():
        results = pd.read_csv(
            OUTPUT_PATH,
            dtype={"Postal Code": str},
        )
        completed_keys = {
            tuple(str(row[col]).strip() for col in KEY_COLUMNS)
            for _, row in results.iterrows()
            if row.get("Lookup_Status") in {"Found", "Review", "Not found"}
        }
    else:
        results = pd.DataFrame(
            columns=KEY_COLUMNS
            + [
                "Latitude",
                "Longitude",
                "Lookup_Status",
                "Match_Display_Name",
                "Match_Count",
            ]
        )
        completed_keys = set()

    session = requests.Session()
    session.headers.update(HEADERS)

    total = len(destinations)

    for number, (_, row) in enumerate(destinations.iterrows(), start=1):
        key = tuple(str(row[col]).strip() for col in KEY_COLUMNS)

        if key in completed_keys:
            print(f"{number}/{total}: Already processed; skipping")
            continue

        query = (
            f"{row['Postal Code']}, {row['City']}, "
            f"{row['State/Province']}, {row['Country/Region']}"
        )

        record = {col: row[col] for col in KEY_COLUMNS}

        try:
            response = session.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": query,
                    "format": "jsonv2",
                    "limit": 2,
                    "addressdetails": 1,
                },
                timeout=30,
            )
            response.raise_for_status()
            matches = response.json()

            if len(matches) == 1:
                match = matches[0]
                status = "Found"
            elif len(matches) > 1:
                match = matches[0]
                status = "Review"
            else:
                match = {}
                status = "Not found"

            record.update(
                {
                    "Latitude": float(match["lat"]) if match else pd.NA,
                    "Longitude": float(match["lon"]) if match else pd.NA,
                    "Lookup_Status": status,
                    "Match_Display_Name": match.get("display_name", ""),
                    "Match_Count": len(matches),
                }
            )

        except requests.RequestException as exc:
            record.update(
                {
                    "Latitude": pd.NA,
                    "Longitude": pd.NA,
                    "Lookup_Status": "Error",
                    "Match_Display_Name": str(exc),
                    "Match_Count": 0,
                }
            )

        results = pd.concat(
            [results, pd.DataFrame([record])],
            ignore_index=True,
        )
        results.to_csv(OUTPUT_PATH, index=False)

        print(
            f"{number}/{total}: {query} -> "
            f"{record['Lookup_Status']}"
        )

        # Do not retry errors automatically; respect the public service limit.
        time.sleep(1.1)

    print("\n--- GEOCODING SUMMARY ---")
    print(results["Lookup_Status"].value_counts(dropna=False).to_string())
    print(f"\nSaved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()


from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "processed" / "geocoded_destinations.csv"

df = pd.read_csv(INPUT_PATH, dtype={"Postal Code": str})

unresolved = df[
    df["Lookup_Status"].isin(["Not found", "Error"])
]

print("--- UNRESOLVED DESTINATIONS ---")
print(
    unresolved[
        [
            "Country/Region",
            "State/Province",
            "City",
            "Postal Code",
            "Lookup_Status",
            "Match_Display_Name",
        ]
    ].to_string(index=False)
)

print("\n--- COORDINATE VALIDATION ---")
coordinates = df.dropna(subset=["Latitude", "Longitude"])

print("Rows with coordinates:", len(coordinates))
print(
    "Latitude outside valid range:",
    int((~coordinates["Latitude"].between(-90, 90)).sum()),
)
print(
    "Longitude outside valid range:",
    int((~coordinates["Longitude"].between(-180, 180)).sum()),
)

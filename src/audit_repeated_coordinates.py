
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "data" / "processed" / "geocoded_destinations.csv"
OUTPUT = ROOT / "reports" / "repeated_coordinate_audit.csv"

df = pd.read_csv(INPUT, dtype=str)

df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

repeated = (
    df.groupby(["Latitude", "Longitude"])
    .agg(
        Destination_Count=("Postal Code", "size"),
        Postal_Codes=("Postal Code", lambda x: ", ".join(sorted(set(x.dropna())))),
        Cities=("City", lambda x: ", ".join(sorted(set(x.dropna())))),
        Countries=("Country/Region", lambda x: ", ".join(sorted(set(x.dropna())))),
    )
    .reset_index()
)

repeated = repeated[repeated["Destination_Count"] > 1].copy()

repeated["Audit_Status"] = (
    "Repeated coordinate; independent verification required"
)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
repeated.to_csv(OUTPUT, index=False)

print("REPEATED COORDINATE AUDIT")
print("-------------------------")
print(f"Repeated coordinate groups: {len(repeated)}")
print(
    "Destination records in those groups:",
    repeated["Destination_Count"].sum()
)
print(f"Report saved: {OUTPUT}")
print(repeated.to_string(index=False))


from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

DISTANCE_FILE = (
    ROOT / "data" / "processed" / "factory_destination_distances.csv"
)

VALIDATION_FILE = (
    ROOT / "reports" / "combined_coordinate_validation.csv"
)

OUTPUT_FILE = (
    ROOT / "data" / "processed" / "geographically_audited_distances.csv"
)

distance = pd.read_csv(
    DISTANCE_FILE,
    dtype={"Postal Code": str}
)

validation = pd.read_csv(
    VALIDATION_FILE,
    dtype={"Postal Code": str}
)

join_keys = [
    "Country/Region",
    "State/Province",
    "City",
    "Postal Code"
]

validation_columns = join_keys + [
    "Geographic_Validation_Result"
]

validation = validation[validation_columns].drop_duplicates()

# Ensure the geographic lookup has one record per destination
if validation.duplicated(subset=join_keys).any():
    raise ValueError("Duplicate destination records in validation report.")

audited = distance.merge(
    validation,
    on=join_keys,
    how="left",
    validate="many_to_one",
    indicator=True
)

# Stop if any order line lacks a validation result
if not (audited["_merge"] == "both").all():
    missing = audited[audited["_merge"] != "both"]
    raise ValueError(
        f"{len(missing)} order lines have no geographic validation match."
    )

audited.drop(columns=["_merge"], inplace=True)

audited["Geographic_Validation_Usable"] = (
    audited["Geographic_Validation_Result"]
    == "Inside matching reference area"
)

audited["Distance_Interpretation"] = (
    "Straight-line factory-to-destination distance; "
    "not actual road or carrier route distance"
)

audited.to_csv(OUTPUT_FILE, index=False)

print("GEOGRAPHICALLY AUDITED DISTANCES")
print("--------------------------------")
print("Original order lines:", len(distance))
print("Audited order lines:", len(audited))
print("Unique orders:", audited["Order ID"].nunique())

print("\nGeographic validation:")
print(
    audited["Geographic_Validation_Result"]
    .value_counts(dropna=False)
    .to_string()
)

print("\nMissing validation results:",
      audited["Geographic_Validation_Result"].isna().sum())

print("\nOriginal distance values preserved:",
      audited["Straight_Line_Distance_KM"].equals(
          distance["Straight_Line_Distance_KM"]
      ))

print("\nSaved:", OUTPUT_FILE)


from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

US_INPUT = ROOT / "reports" / "us_coordinate_validation.csv"
CANADA_INPUT = ROOT / "reports" / "canada_coordinate_validation.csv"

ALL_OUTPUT = ROOT / "reports" / "combined_coordinate_validation.csv"
EXCEPTION_OUTPUT = ROOT / "reports" / "combined_coordinate_exceptions.csv"

# Load country-specific validation reports
us = pd.read_csv(US_INPUT, dtype=str)
canada = pd.read_csv(CANADA_INPUT, dtype=str)

# Preserve the original country-specific validation result
us["Validation_Reference"] = "2025 US Census ZCTA"
canada["Validation_Reference"] = "2021 Statistics Canada FSA"

# Standardize the result labels without overwriting the original column
status_mapping = {
    "Inside matching ZCTA": "Inside matching reference area",
    "Inside matching FSA": "Inside matching reference area",
    "Outside matching ZCTA": "Outside matching reference area",
    "Outside matching FSA": "Outside matching reference area",
    "No matching FSA boundary": "No matching reference boundary",
}

# Combine all destination records
combined = pd.concat([us, canada], ignore_index=True, sort=False)

combined["Geographic_Validation_Result"] = (
    combined["Validation_Status"].map(status_mapping)
    .fillna("Unclassified; investigation required")
)

combined["Is_Geographic_Exception"] = (
    combined["Geographic_Validation_Result"]
    != "Inside matching reference area"
)

# Preserve original coordinates and make the verification limitation explicit
combined["Original_Coordinates_Preserved"] = "Yes"

# Save complete register
combined.to_csv(ALL_OUTPUT, index=False)

# Save exceptions separately
exceptions = combined[
    combined["Is_Geographic_Exception"]
].copy()

exceptions.to_csv(EXCEPTION_OUTPUT, index=False)

# Print audit summary
print("COMBINED COORDINATE VALIDATION")
print("-----------------------------")
print("US destination records:", len(us))
print("Canadian destination records:", len(canada))
print("Total destination records:", len(combined))

print("\nGeographic validation results:")
print(
    combined["Geographic_Validation_Result"]
    .value_counts(dropna=False)
    .to_string()
)

print("\nException records:", len(exceptions))
print("Original coordinates preserved: Yes")

print("\nReports saved:")
print(ALL_OUTPUT)
print(EXCEPTION_OUTPUT)

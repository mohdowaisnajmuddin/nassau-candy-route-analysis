
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "reports" / "canada_coordinate_validation.csv"
OUTPUT = ROOT / "reports" / "canada_coordinate_exception_register.csv"

df = pd.read_csv(INPUT, dtype=str)

exceptions = df[
    df["Validation_Status"] != "Inside matching FSA"
].copy()

def classify(row):
    status = row["Validation_Status"]

    if status == "No matching FSA boundary":
        return "Reference boundary unavailable; investigate postal area"

    if row["City"] == "Montreal":
        return "Repeated coordinate across distinct FSAs"

    if row["Lookup_Status"] == "Found_Canada_FSA":
        return "Approximate postal-area geocoding; verify independently"

    return "Outside matching FSA; verify independently"


exceptions["Investigation_Category"] = exceptions.apply(
    classify, axis=1
)

exceptions["Original_Coordinates_Preserved"] = "Yes"

exceptions["Review_Status"] = "Pending"

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
exceptions.to_csv(OUTPUT, index=False)

print("CANADIAN EXCEPTION REGISTER")
print("---------------------------")
print("Total exceptions:", len(exceptions))
print("\nInvestigation categories:")
print(exceptions["Investigation_Category"].value_counts().to_string())
print("\nSaved:", OUTPUT)

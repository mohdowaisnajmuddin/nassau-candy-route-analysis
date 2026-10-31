
from pathlib import Path

import geopandas as gpd
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = ROOT / "data" / "processed" / "geocoded_destinations.csv"

SHAPEFILE_PATH = (
    ROOT
    / "data"
    / "reference"
    / "canada_fsa_2021"
    / "lfsa000a21a_e"
    / "lfsa000a21a_e.shp"
)

OUTPUT_PATH = ROOT / "reports" / "canada_coordinate_validation.csv"


def normalize_fsa(value):
    """Extract the first three characters of a Canadian postal code."""
    if pd.isna(value):
        return None

    value = str(value).strip().upper().replace(" ", "")

    if len(value) < 3:
        return None

    return value[:3]


def main():
    print("Loading Canadian destinations...")

    destinations = pd.read_csv(INPUT_PATH, dtype=str)

    required = [
        "Country/Region",
        "Postal Code",
        "Latitude",
        "Longitude",
    ]

    missing = [column for column in required if column not in destinations.columns]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    destinations["FSA"] = destinations["Postal Code"].apply(normalize_fsa)
    destinations["Latitude"] = pd.to_numeric(
        destinations["Latitude"], errors="coerce"
    )
    destinations["Longitude"] = pd.to_numeric(
        destinations["Longitude"], errors="coerce"
    )

    canada = destinations[
        destinations["Country/Region"].str.strip().str.lower().eq("canada")
    ].copy()

    canada = canada.dropna(subset=["FSA", "Latitude", "Longitude"])

    print(f"Canadian destination records: {len(canada)}")

    print("Loading Statistics Canada FSA boundaries...")

    fsas = gpd.read_file(
        SHAPEFILE_PATH,
        engine="pyogrio",
        columns=["CFSAUID"],
    )

    fsas = fsas.rename(columns={"CFSAUID": "FSA"})
    fsas["FSA"] = fsas["FSA"].astype(str).str.upper()

    print(f"FSA boundaries loaded: {len(fsas)}")

    print("Matching destination FSAs...")

    merged = canada.merge(
        fsas,
        on="FSA",
        how="left",
        indicator=True,
    )

    matched = merged[merged["_merge"] == "both"].copy()
    unmatched = merged[merged["_merge"] == "left_only"].copy()

    print(f"Matching FSA records: {len(matched)}")
    print(f"Unmatched FSA records: {len(unmatched)}")

    print("Checking coordinate containment...")

    points = gpd.GeoDataFrame(
        matched,
        geometry=gpd.points_from_xy(
            matched["Longitude"],
            matched["Latitude"],
        ),
        crs="EPSG:4326",
    )

    # Convert points into the boundary dataset's coordinate system.
    points = points.to_crs(fsas.crs)

    polygons = fsas[["FSA", "geometry"]].copy()

    joined = gpd.sjoin(
        points,
        polygons,
        how="left",
        predicate="within",
        lsuffix="destination",
        rsuffix="boundary",
    )

    joined["Coordinate_In_Matching_FSA"] = (
        joined["FSA_destination"] == joined["FSA_boundary"]
    )

    joined["Validation_Status"] = joined[
        "Coordinate_In_Matching_FSA"
    ].map({
        True: "Inside matching FSA",
        False: "Outside matching FSA",
    })

    unmatched["Coordinate_In_Matching_FSA"] = pd.NA
    unmatched["Validation_Status"] = "No matching FSA boundary"

    results = pd.concat([joined, unmatched], ignore_index=True)

    results["Validation_Method"] = (
        "Point-in-polygon against Statistics Canada 2021 FSA boundaries"
    )

    results["Accuracy_Limitation"] = (
        "FSA containment does not prove exact postal-address accuracy"
    )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    results.drop(
        columns=["geometry"],
        errors="ignore",
    ).to_csv(OUTPUT_PATH, index=False)

    print("\nCANADIAN COORDINATE VALIDATION")
    print("------------------------------")
    print(
        results["Validation_Status"]
        .value_counts(dropna=False)
        .to_string()
    )

    print(f"\nReport saved: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

# Factory-to-Customer Shipping Route Efficiency Analysis

An exploratory data analysis project examining factory-to-customer geographic distribution using the Nassau Candy Distributor dataset.

## Project Overview

This project uses Python to analyze factory-to-destination distances, compare geographic distribution patterns, examine shipping-mode summaries, and identify destination groups for further investigation. An interactive dashboard built with Streamlit presents the findings.

**Important:** The project calculates straight-line geographic distances, not road distances or actual delivery times.

## Technologies Used

- Python
- pandas and NumPy
- Plotly
- Streamlit
- Haversine distance calculation

## Key Dataset Statistics

- 10,194 order-line records
- 8,549 unique orders
- 15 product names
- 5 factories
- 1,386 factory-destination groups

## Project Structure

```text
Nassau Candy Distributor/
├── app.py
├── requirements.txt
├── src/
├── data/
│   ├── raw/
│   └── processed/
├── reports/
└── docs/
    ├── research_paper.md
    └── executive_summary.md
```

## Setup Instructions

### 1. Install Python

Install a compatible Python version if it is not already installed.

### 2. Open the project folder

Open a terminal in the project root directory.

### 3. Create a virtual environment

```powershell
py -m venv .venv
```

### 4. Activate the environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 6. Launch the dashboard

```powershell
python -m streamlit run app.py
```

Open the local URL displayed in the terminal.

## Analysis Workflow

1. Inspect and validate the source dataset.
2. Verify product-to-factory assignments.
3. Geocode customer destinations and record lookup status.
4. Calculate estimated straight-line distances using the Haversine formula.
5. Generate factory-destination and shipping-mode summaries.
6. Prioritize destination groups for further investigation.
7. Explore results in the Streamlit dashboard.

## Data Quality and Limitations

The source data contains an unresolved date anomaly: all 10,194 recorded order-to-ship intervals exceed 365 days, ranging from 904 to 1,642 days. The original dates were preserved because the cause and a valid correction could not be established.

The distance calculations were independently checked for mathematical consistency. This does not prove that every geographic coordinate is accurate.

Some records have ambiguous geocoding results or approximate Canadian postal-area coordinates. The priority report is a screening tool, not proof of inefficient routes.

The project does not establish actual delivery times, road distances, transportation costs, or which shipping mode is fastest.

### Investigation of the Order Date and Ship Date Anomaly

An investigation was conducted after the initial data-quality audit identified unusually large differences between Order Date and Ship Date.

The local dataset was compared against the supplied public reference dataset using Row ID and Order ID as matching keys.

The comparison covered all 10,194 records. All records matched successfully, with no unmatched rows. There were zero differences in Order Date and zero differences in Ship Date between the two datasets.

Further investigation found that all 10,194 records have apparent date intervals exceeding 365 days, ranging from 904 to 1,642 days.

These findings establish that the anomaly is also present in the public reference dataset and is not the result of a discrepancy between the local and reference copies.

However, the available evidence does not establish the cause of the anomaly or identify which date field, if any, contains incorrect values. Therefore, the original dates have been preserved without modification.

Consequently, actual shipping lead-time performance, delivery delays, and time-based route-efficiency rankings cannot be reliably calculated from these date fields. Distance-based analysis is presented separately and must not be interpreted as a measurement of delivery speed or timeliness.

**Status:** Date anomaly confirmed in both datasets; underlying cause unresolved.

## Documentation

See the `docs/` directory for the research paper and executive summary.

## Reproducibility

The `src/` directory contains the analysis and validation scripts. The `reports/` directory contains generated CSV summaries.

##Author

MOHAMMED OWAIS NAJMUDDIN

https://github.com/mohdowaisnajmuddin

## Dashboard setup and filters

The Streamlit dashboard reads `data/processed/geographically_audited_distances.csv`,
`data/raw/Nassau Candy Distributor.csv`, and the reports referenced by `app.py`.
Keep the original project folder structure when running the application.

The sidebar includes factory, geocoding status, country, geographic-validation,
region, and ship-mode filters, plus an Order Date exploration range. Region,
Ship Mode, and date attributes are joined from the source dataset by `Order ID`
after checking that each order has consistent values.

**Important analytical limitation:** the Order Date range is for record
exploration only. All recorded order-to-ship intervals exceed 365 days and the
cause is unresolved. The dashboard therefore does not present lead-time
thresholds, delivery-delay rates, actual delivery timelines, or a delivery
efficiency score. Straight-line distances are geographic screening estimates,
not road distances or actual shipping routes.

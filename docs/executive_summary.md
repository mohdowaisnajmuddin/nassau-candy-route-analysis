# Executive Summary
## Factory-to-Customer Shipping Route Efficiency Analysis
**Project:** Nassau Candy Distributor
**Tools:** Python, pandas, NumPy, Plotly, Streamlit

### 1. Project Overview

This project analyzes the geographic distribution of customer orders associated with five Nassau Candy Distributor factories. The objective was to examine factory-to-destination distances, compare geographic distribution patterns, identify destinations requiring further investigation, and present the results through an interactive dashboard.

The project combines data cleaning, geographic calculations, data-quality checks, analytical reporting, and visualization in a reproducible Python workflow.

### 2. Dataset at a Glance

| Metric | Result |
|---|---:|
| Order-line records | 10,194 |
| Unique orders | 8,549 |
| Factories | 5 |
| Products | 15 |
| Factory-destination groups | 1,386 |
| Missing calculated distances | 0 |

### 3. Methodology

The source dataset was inspected for missing values, duplicate identifiers, and date-parsing problems. Product-to-factory assignments were checked against the supplied project specification.

Customer destination coordinates were processed using a geocoding workflow with explicit statuses for ambiguous results and approximate locations. Straight-line distances were calculated using the Haversine formula with an Earth radius of 6,371 km.

The analysis then generated factory-level comparisons, shipping-mode summaries, destination-level reports, geocoding-quality summaries, and a route-investigation priority report. A Streamlit dashboard provides interactive charts, filters, tables, and a geographic map.

### 4. Key Findings

**Factory-level distance comparison**

| Factory | Order lines | Mean estimated distance |
|---|---:|---:|
| Lot's O' Nuts | 5,692 | 2,145.50 km |
| Wicked Choccy's | 4,152 | 1,863.23 km |
| Sugar Shack | 33 | 1,797.32 km |
| The Other Factory | 100 | 1,643.91 km |
| Secret Factory | 217 | 1,437.03 km |

Lot's O' Nuts has the highest mean estimated straight-line distance in the dataset, while Secret Factory has the lowest. Lot's O' Nuts and Wicked Choccy's account for most recorded order lines.

These findings describe geographic distribution, not actual transportation efficiency or cost.

**Shipping-mode summary**

Standard Class represents the largest volume, with 6,120 order lines. Mean estimated straight-line distances are relatively similar across First Class, Same Day, Second Class, and Standard Class. Because the dataset has an unresolved date anomaly, these figures do not establish which shipping method delivers faster.

**Route-investigation priorities**

The 1,386 factory-destination groups were classified into screening categories:

- Routine screening: 715 groups
- High volume: 263 groups
- Long estimated distance: 217 groups
- High volume and long estimated distance: 108 groups
- Ambiguous geocoding review: 55 groups
- Approximate Canadian postal-area coordinates: 20 groups
- Retry-found coordinates to verify: 8 groups

The priority report helps identify where to investigate further while distinguishing geographic patterns from coordinate-quality concerns.

### 5. Data Quality and Validation

The source and processed distance datasets each contain 10,194 records. Row IDs were unique and complete, and no unmatched records were found during the final validation.

The saved distances were independently recalculated using the Haversine formula. The mean absolute difference was approximately 0.0028 km, and the maximum absolute difference was approximately 0.0071 km. This supports the mathematical consistency of the distance calculations, but does not independently prove the accuracy of every coordinate.

**Important limitation: unresolved date anomaly**

All 10,194 records have recorded order-to-ship intervals exceeding 365 days. The intervals range from 904 to 1,642 days. The cause could not be established from the available evidence, so the original dates were preserved without unsupported corrections.

The calculated intervals must not be treated as verified delivery times. The project does not claim to measure actual delivery speed, road distance, transportation cost, or overall shipping efficiency.

### 6. Deliverables

The project includes:

1. Data cleaning and validation scripts.
2. Destination geocoding and geographic-distance processing.
3. Factory-destination route analysis.
4. Route-investigation priority analysis.
5. Shipping-mode summary analysis.
6. Data-quality and validation reports.
7. An interactive Streamlit dashboard with charts, filters, tables, and a geographic map.
8. Research paper documenting methodology, results, limitations, and recommendations.

### 7. Recommendations

- Obtain authoritative clarification of the date anomaly before analyzing delivery performance.
- Verify ambiguous destination coordinates and approximate Canadian postal-area locations.
- Use a validated routing service if road distance or route-level travel estimates are required.
- Collect verified dispatch and delivery timestamps and transportation-cost data for future operational-efficiency analysis.
- Use the priority report as a screening tool, not as proof that a particular route is inefficient.

### 8. Conclusion

This project demonstrates a complete data-analysis workflow, from source-data validation to geographic calculations, analytical reporting, and interactive visualization. It identifies differences in recorded geographic distribution and provides a structured way to investigate destinations and data-quality issues.

The findings are useful for exploratory distribution analysis, but stronger conclusions about real-world shipping performance require reliable operational timestamps, verified locations, and actual route or cost data.
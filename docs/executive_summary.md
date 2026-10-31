Executive Summary
Factory-to-Customer Shipping Route Efficiency Analysis
Project: Nassau Candy Distributor
Tools: Python, pandas, NumPy, Plotly, Streamlit
1. Project Overview
This project analyzes the geographic distribution of customer orders associated with five Nassau Candy Distributor factories. Its objectives are to examine factory-to-destination distances, compare geographic distribution patterns, identify destinations requiring further investigation, and present the results through an interactive dashboard.

The workflow combines data cleaning, product-to-factory mapping checks, destination geocoding, geographic-distance calculations, data-quality validation, analytical reporting, and visualization.

The results describe the supplied dataset and its mapped factory-destination relationships. They do not establish actual transportation efficiency or delivery performance.
2. Dataset at a Glance
Metric	Result
Order-line records	10,194
Unique orders	8,549
Factories	5
Products	15
Factory-destination groups	1,386
Missing calculated distances	0
Duplicate Row IDs	0


Each of the 8,549 unique orders maps to exactly one factory under the supplied product-to-factory mapping. This does not independently verify the physical dispatch location.
3. Methodology
The source dataset was inspected for missing values, duplicate identifiers, date-parsing problems, and consistency. Product-to-factory assignments were checked against the supplied project specification. A separate audit identified six Division-field mismatches, all involving Fizzy Lifting Drinks; the original source values were preserved.

Customer destination coordinates were processed through a geocoding workflow with explicit statuses for ambiguous results, approximate Canadian postal-area locations, and retry-found coordinates. Straight-line distances were calculated using the Haversine formula with an Earth radius of 6,371.0088 km.

Factory-destination distance statistics were calculated at the unique-order level. Product-line counts were retained separately so that orders containing multiple product lines did not receive disproportionate weight in distance averages.

The analysis generated factory-level comparisons, shipping-mode commercial summaries, destination-level reports, geocoding-quality summaries, and a route-investigation priority report. A Streamlit dashboard provides interactive charts, filters, tables, and a geographic map.
4. Key Findings
Factory-level geographic comparison
Factory	Order lines	Distinct orders	Mean estimated distance
Lot's O' Nuts	5,692	4,760	2,140.14 km
Wicked Choccy's	4,152	3,445	1,871.74 km
Sugar Shack	33	33	1,797.32 km
The Other Factory	100	98	1,631.09 km
Secret Factory	217	213	1,440.29 km


Lot's O' Nuts has the highest mean estimated straight-line distance among the five mapped factories, while Secret Factory has the lowest. Lot's O' Nuts and Wicked Choccy's account for most recorded order lines and unique orders.

These are order-weighted geographic estimates. They are not road distances, actual transportation costs, or measures of delivery efficiency.

Shipping-mode summary
Shipping mode	Unique orders	Order share	Average order value	Gross margin
Standard Class	5,142	60.15%	$16.63	66.00%
Second Class	1,653	19.34%	$16.85	65.71%
First Class	1,312	15.35%	$16.25	65.72%
Same Day	442	5.17%	$16.09	66.08%
Total	8,549	100.00%


Standard Class represents the largest share of orders. Average order values range from $16.09 to $16.85, and gross margins range from 65.71% to 66.08%. These figures describe order distribution and commercial characteristics, not delivery speed or shipping-cost efficiency. Reliable transit durations and shipping charges are unavailable.

Route-investigation priorities

The 1,386 factory-destination groups were classified using distinct-order volume, estimated straight-line distance, and coordinate-quality flags. The 75th-percentile thresholds were 5 distinct orders and 2,711.32 km.
Priority category	Factory-destination groups
Routine screening	703
High volume	275
Long estimated distance	213
High volume + long estimated distance	112
Ambiguous geocoding review	55
Approximate Canadian postal-area coordinates	20
Retry-found coordinates to verify	8
Total	1,386


Coordinate-review categories take precedence over volume and distance categories. Therefore, some groups that also meet high-volume or long-distance thresholds appear under a coordinate-review category. These classifications are screening candidates, not proof of delays, inefficient routes, or operational bottlenecks.
5. Data Quality and Validation
The source and processed distance datasets each contain 10,194 records. Row IDs were unique and complete, with no unmatched identifiers. The processed dataset contains no missing or negative distance values.

An independent WGS84 geodesic implementation was used to validate the saved Haversine distances:
- Records checked: 10,194
- Mean absolute difference: 3.531 km
- Median absolute difference: 2.860 km
- Maximum absolute difference: 10.833 km
- Mean percentage difference: 0.163793%
- Maximum percentage difference: 0.323613%
- Records within the project's 0.5% tolerance: 10,194
- Records requiring distance-calculation review: 0
This validates the numerical consistency of the distance calculations, not the accuracy of the underlying coordinates or factory assignments.

Geocoding limitations

The final record-level geocoding statuses were:
Geocoding status	Order lines
Found	9,375
Found_Canada_FSA	88
Retry_Found	19
Review	712
Total	10,194


Approximate Canadian postal-area coordinates are not exact delivery addresses. Ambiguous and retry-found coordinates require additional verification before detailed operational decisions are made. A successful lookup alone does not guarantee coordinate accuracy.

Important limitation: unresolved date anomaly

Order dates range from 2 January 2024 to 31 December 2025. Ship dates range from 30 June 2026 to 28 June 2030. All 10,194 records have recorded order-to-ship intervals exceeding 365 days. The intervals range from 904 to 1,642 days, with a mean of 1,320.84 days and a median of 1,274 days.

The cause could not be established from the available evidence. The compared public reference copy contains matching date values, but agreement between copies does not establish which dates, if any, are incorrect or explain the anomaly. The original dates were preserved without unsupported corrections.

These intervals must not be treated as verified delivery times. The project does not claim to measure actual delivery speed, delivery timeliness, road distance, transportation cost, or overall shipping efficiency.
6. Deliverables
The project includes:
1. Data cleaning and validation scripts.
2. Date-anomaly investigation.
3. Destination geocoding and geographic-distance processing.
4. Factory-destination route analysis.
5. Route-investigation priority analysis.
6. Shipping-mode commercial summary analysis.
7. Data-quality and independent distance-validation reports.
8. An interactive Streamlit dashboard with charts, filters, tables, and a geographic map.
9. A research paper documenting methodology, results, limitations, and recommendations.

### 10. Recommendations

- Obtain authoritative clarification of the order-date and ship-date anomaly before conducting delivery-performance analysis.
- Review ambiguous destination coordinates and approximate Canadian postal-area locations.
- Use a validated routing service if road distance or route-level travel estimates are required.
- Collect verified dispatch and delivery timestamps, actual transportation charges, and relevant operational measures before evaluating delivery efficiency.
- Use the route-priority report as a screening tool, not as proof that a particular route is inefficient.
- Preserve reproducible scripts, validation reports, and data-quality documentation so that the analysis can be rerun and audited.

### 11. Conclusion

This project developed a reproducible workflow for examining factory-to-customer geographic distribution using the Nassau Candy Distributor dataset. It validated 10,194 order-line records, checked the supplied product-to-factory mapping, calculated straight-line distances for 1,386 factory-destination groups, summarized shipping-mode order and commercial characteristics, and generated a route-investigation priority report and interactive dashboard.

The findings describe differences in estimated geographic distribution and identify destination groups that merit additional review. Independent numerical checks support the mathematical consistency of the Haversine calculations, while geocoding-status analysis highlights remaining uncertainty in some destination coordinates.

The principal limitation is the unresolved date anomaly. Since every recorded order-to-ship interval exceeds 365 days, the available data does not support reliable conclusions about actual delivery times or shipping efficiency. The project should therefore be understood as a geographic distribution and data-quality analysis, providing a foundation for further investigation when validated operational data becomes available.

The findings describe differences in estimated geographic distribution and identify destination groups that merit additional review. Independent numerical checks support the mathematical consistency of the Haversine calculations, while geocoding-status analysis highlights remaining uncertainty in some destination coordinates.

The principal limitation is the unresolved date anomaly. Since every recorded order-to-ship interval exceeds 365 days, the available data does not support reliable conclusions about actual delivery times or shipping efficiency. The project should therefore be understood as a geographic distribution and data-quality analysis, providing a foundation for further investigation when validated operational data becomes available.

### Dashboard controls and interpretation

The dashboard supports factory, geocoding-status, country, geographic-validation, region, and ship-mode filters, plus an Order Date exploration range. The Order Date control is not a delivery-performance measure. A lead-time threshold slider and delivery-efficiency ranking are intentionally omitted because every recorded order-to-ship interval exceeds 365 days and the cause remains unknown. State-level geographic exploration is available; straight-line distance is not road distance.

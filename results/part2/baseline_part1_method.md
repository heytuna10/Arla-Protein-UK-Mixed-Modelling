# Baseline with part 1's attribution method (reference only)

Reproduces `notebooks/01_exploratory_analysis.ipynb` (theta = beta x mean sales / mean spend; contribution = theta x total spend; ROI at the average price).

| channel | beta | contribution_units | pct_of_total_sales | roi |
|---|---|---|---|---|
| tv | 0.0164 | 1,636,298 | 1.6 | 0.23 |
| instagram | 0.3522 | 35,081,546 | 35.2 | 13.24 |
| tiktok | 0.2885 | 28,734,843 | 28.8 | 13.56 |
| influencer | 0.7055 | 70,272,399 | 70.6 | 30.61 |
| pos_promotion | 0.1302 | 12,972,296 | 13.0 | 3.67 |

Sum of channel contributions = 149% of total sales, before any base sales.

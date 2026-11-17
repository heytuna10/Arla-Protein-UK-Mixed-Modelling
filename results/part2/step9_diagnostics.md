# Step 9 – diagnostics for the critical review

Tables behind `step9_critical_review.md`. Final model M14 unless stated; p-values use Newey-West errors. Rebuild: `python scripts/run_review.py`.

## 1. Does spend follow demand?

### 1a. How weekly spend behaves

Log spend (TV: on air yes/no) regressed on the model's demand drivers and last week's log sales.

|  | TV | Instagram | TikTok | Influencer | POS |
|---|---|---|---|---|---|
| autocorrelation, 1 week | 0.592 | 0.249 | 0.351 | 0.144 | 0.184 |
| largest correlation with another channel | 0.125 | 0.125 | 0.119 | 0.119 | 0.053 |
| R² on demand drivers | 0.233 | 0.131 | 0.240 | 0.030 | 0.320 |
| season p | 0.000 | 0.000 | 0.007 | 0.695 | 0.383 |
| trend p | 0.184 | 0.578 | 0.000 | 0.149 | 0.694 |
| promotion depth: coefficient | -0.008 | 0.014 | -0.006 | -0.032 | 0.952 |
| promotion depth p | 0.971 | 0.890 | 0.958 | 0.708 | 0.000 |
| last week's sales: coefficient | 0.160 | -0.041 | 0.014 | 0.020 | 0.071 |
| last week's sales p | 0.283 | 0.407 | 0.855 | 0.681 | 0.356 |

- Digital spend does not rise in promotion weeks (when demand is about 13% higher) and does not respond to last week's sales. Influencer spend is unrelated to anything in the data (R² 0.03) and close to random from week to week.
- POS spend is the exception: it is clearly higher in promotion weeks (coefficient 0.95 on promotion depth: about +30% spend in a 24%-off week). The model controls for promotion depth, so the POS effect is measured on the remaining variation, but POS and price promotions are run together and their effects are harder to separate than the others.
- TV, Instagram and TikTok follow a seasonal calendar; the model has seasonal terms.

### 1b. Placebo at longer horizons: does future spend 'explain' current sales?

| average spend over the | weeks used | joint p (all five channels) | TV p | Instagram p | TikTok p | Influencer p | POS p |
|---|---|---|---|---|---|---|---|
| next 1 week(s) | 154 | 0.780 | 0.334 | 0.818 | 0.697 | 0.207 | 0.849 |
| next 4 week(s) | 151 | 0.290 | 0.064 | 0.630 | 0.776 | 0.743 | 0.250 |
| next 8 week(s) | 147 | 0.126 | 0.005 | 0.470 | 0.207 | 0.184 | 0.785 |

- No signal for any always-on channel at 1, 4 or 8 weeks. TV at 8 weeks is significant (p 0.005) with a small negative sign (sales are slightly *lower* before TV-heavy periods); the joint tests are not significant, and adding the leads leaves every media coefficient unchanged.

### 1c. Slow and fast movements of spend

Each always-on regressor split into its 13-week average (budget level) and the week-to-week deviation.

| channel | final model | slow part (13-week level) | slow se | fast part (week-to-week) | fast se | share of the regressor's variance that is fast % | p (slow = fast) |
|---|---|---|---|---|---|---|---|
| Instagram | 2.15 | 2.63 | 0.36 | 2.11 | 0.13 | 74 | 0.106 |
| TikTok | 1.41 | 1.57 | 0.30 | 1.39 | 0.08 | 76 | 0.554 |
| Influencer | 4.32 | 4.32 | 0.42 | 4.33 | 0.11 | 97 | 0.990 |
| POS | 0.53 | 0.84 | 0.24 | 0.52 | 0.08 | 91 | 0.192 |

- The coefficients on the slow and the fast part do not differ for any channel; for influencer they are identical (4.32 and 4.33). The effect is identified almost entirely from week-to-week movements (74–97% of the variation), which quarterly or monthly budget planning cannot produce.
- The split does not improve the fit (AIC -493.1 against -497.3).

## 2. One shared digital effect?

Correlation of weekly spend between channels:

|  | TV | Instagram | TikTok | Influencer | POS |
|---|---|---|---|---|---|
| TV | 1.00 | -0.13 | 0.08 | 0.10 | 0.04 |
| Instagram | -0.13 | 1.00 | -0.01 | -0.10 | 0.00 |
| TikTok | 0.08 | -0.01 | 1.00 | -0.12 | 0.05 |
| Influencer | 0.10 | -0.10 | -0.12 | 1.00 | 0.03 |
| POS | 0.04 | 0.00 | 0.05 | 0.03 | 1.00 |

Correlation between the estimated media coefficients:

|  | TV | Instagram | TikTok | Influencer | POS |
|---|---|---|---|---|---|
| TV | 1.00 | -0.06 | 0.23 | -0.30 | 0.09 |
| Instagram | -0.06 | 1.00 | -0.39 | 0.00 | -0.45 |
| TikTok | 0.23 | -0.39 | 1.00 | -0.04 | 0.08 |
| Influencer | -0.30 | 0.00 | -0.04 | 1.00 | -0.15 |
| POS | 0.09 | -0.45 | 0.08 | -0.15 | 1.00 |

The model with Instagram, TikTok and influencer spend added into one digital channel:

|  | final model (three digital channels) | one digital channel (decay 0.1) |
|---|---|---|
| parameters | 22.00 | 18.00 |
| AIC | -497.27 | -338.30 |
| BIC | -430.31 | -283.52 |
| hold-out error %, last 26 weeks | 4.22 | 10.92 |
| revenue per extra £ of digital spend | 47.20 | 38.12 |
| revenue per extra £ of TV | 1.72 | 2.16 |
| revenue per extra £ of POS | 5.47 | 6.06 |

- The three digital budgets are uncorrelated (largest |r| 0.12), so there is no common movement to split, and the coefficient for influencer is uncorrelated with those of Instagram and TikTok.
- Forcing one digital effect makes the model far worse (AIC -338 against -497, hold-out error 10.9% against 4.2%). The data insist on three different effects. The return on digital as a whole stays of the same order (£38 against £47 per extra £).

## 3. Sizes in context

- Sum of the five long-term elasticities: **3.36**. The benchmark of 0.24 is for a brand's advertising, so the total is about 14 times it.
- Media spend is 18% of revenue over the three years.
- With the floor reference the model credits media with 79% of sales (five channels; step 6).

## 4. Test design: what can a test detect?

Spread of the average multi-week forecast error (model given the actual inputs), and the smallest change in sales a test of that length can detect (one-sided 5%, 80% power):

| test length | forecasts compared | spread of the average error % | minimum detectable change in sales % |
|---|---|---|---|
| 4 weeks | 101 | 2.83 | 7.30 |
| 8 weeks | 97 | 2.11 | 5.40 |
| 13 weeks | 92 | 1.27 | 3.20 |
| 26 weeks | 79 | 0.75 | 1.89 |

- These use coefficients fitted on all weeks. Five out-of-sample 13-week forecasts (step-8 back-test method) have a spread of 2.5%, which gives a minimum detectable change of 6%. Plan with 3–6% for 13 weeks.

What the first-step plan should do over 13 weeks, by component:

| change | model: units over 13 weeks % | if digital effects were benchmark-sized % |
|---|---|---|
| TV −10% | -1.2 | -1.2 |
| Instagram +10% | 7.4 | 2.4 |
| TikTok +10% | 5.0 | 2.4 |
| Influencer +10% | 15.1 | 2.4 |
| all four (the first-step plan) | 28.3 | 6.0 |

## 5. Profit view

Profit per extra £ of spend = margin × revenue per extra £ − 1. Right-hand block: the same with every channel above the benchmark scaled down to a long-term elasticity of 0.24.

|  | TV | Instagram | TikTok | Influencer | POS |
|---|---|---|---|---|---|
| revenue per extra £ | 1.72 | 30.82 | 24.80 | 74.55 | 5.47 |
| profit per extra £ at 20% margin | -0.66 | 5.16 | 3.96 | 13.91 | 0.09 |
| profit per extra £ at 30% margin | -0.48 | 8.25 | 6.44 | 21.36 | 0.64 |
| profit per extra £ at 40% margin | -0.31 | 11.33 | 8.92 | 28.82 | 1.19 |
| break-even margin % | 58.11 | 3.24 | 4.03 | 1.34 | 18.29 |
| revenue per extra £ if the effect were benchmark-sized | 1.72 | 8.96 | 11.07 | 10.72 | 5.47 |
| same, profit at 20% margin | -0.66 | 0.79 | 1.21 | 1.14 | 0.09 |
| same, profit at 30% margin | -0.48 | 1.69 | 2.32 | 2.22 | 0.64 |
| same, profit at 40% margin | -0.31 | 2.58 | 3.43 | 3.29 | 1.19 |
| effect could be overstated by a factor of … and still pay at 30% | 0.52 | 9.25 | 7.44 | 22.36 | 1.64 |

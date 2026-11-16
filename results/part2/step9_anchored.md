# Step 9 – benchmark-anchored regression: what does plausibility cost?

The final model (M14, carry-over rates and curve scales fixed) re-estimated with a normal prior on each of the five media coefficients, centred on the value that gives the channel the literature's average long-term elasticity of 0.24 (Sethuraman, Tellis & Briesch 2011). All other coefficients are free. The prior's strength is one number: its standard deviation as a percentage of the benchmark-sized coefficient. "±100%" is a loose belief that the true effect is somewhere between zero and twice the benchmark; "±10%" is a firm one; "fixed" forces the benchmark. Closed form (a ridge penalty towards a target), no sampling. Code: `src/arla_mmm/anchored.py`. Figure: `figures/anchored.png`.

Media coefficients:

| channel | estimated | benchmark-sized | standard error (Newey-West) |
|---|---|---|---|
| TV | 1.397 | 2.726 | 0.052 |
| Instagram | 2.147 | 0.624 | 0.139 |
| TikTok | 1.412 | 0.631 | 0.074 |
| Influencer | 4.315 | 0.621 | 0.116 |
| POS | 0.528 | 0.632 | 0.075 |

## Fit and forecast along the sweep

Hold-out error: coefficients re-estimated with the same prior on the weeks before the last 26, then a 26-week forecast. First-step plan: TV −10%, Instagram, TikTok and influencer +10%, replay of 2024.

| prior | R² | residual sd % | Δ AIC vs final model | hold-out error % | lagged sales | first-step plan, Δ revenue % |
|---|---|---|---|---|---|---|
| no prior (final model) | 0.977 | 4.46 | 0.0 | 4.22 | 0.36 | 30.5 |
| ±200% | 0.977 | 4.46 | 0.2 | 4.22 | 0.36 | 30.2 |
| ±100% | 0.977 | 4.49 | 2.4 | 4.21 | 0.36 | 29.5 |
| ±50% | 0.973 | 4.85 | 26.3 | 4.32 | 0.38 | 27.1 |
| ±25% | 0.949 | 6.64 | 123.4 | 4.75 | 0.42 | 21.2 |
| ±10% | 0.885 | 9.97 | 249.5 | 5.77 | 0.47 | 11.9 |
| ±5% | 0.853 | 11.25 | 286.9 | 6.67 | 0.47 | 8.1 |
| ±2% | 0.821 | 12.42 | 317.8 | 9.32 | 0.43 | 5.9 |
| fixed at benchmark | 0.770 | 13.82 | 346.2 | 12.16 | 0.38 | 4.7 |

## Long-term elasticity per channel

| prior | TV | Instagram | TikTok | Influencer | POS |
|---|---|---|---|---|---|
| no prior (final model) | 0.12 | 0.83 | 0.54 | 1.67 | 0.20 |
| ±200% | 0.12 | 0.82 | 0.54 | 1.65 | 0.20 |
| ±100% | 0.12 | 0.81 | 0.54 | 1.61 | 0.21 |
| ±50% | 0.13 | 0.76 | 0.54 | 1.45 | 0.22 |
| ±25% | 0.14 | 0.63 | 0.53 | 1.08 | 0.25 |
| ±10% | 0.16 | 0.42 | 0.44 | 0.53 | 0.29 |
| ±5% | 0.18 | 0.33 | 0.35 | 0.36 | 0.29 |
| ±2% | 0.22 | 0.28 | 0.28 | 0.28 | 0.27 |
| fixed at benchmark | 0.25 | 0.25 | 0.25 | 0.25 | 0.25 |

## Revenue per extra £

| prior | TV | Instagram | TikTok | Influencer | POS | ranking |
|---|---|---|---|---|---|---|
| no prior (final model) | 1.7 | 30.8 | 24.8 | 74.5 | 5.5 | Influencer > Instagram > TikTok > POS > TV |
| ±200% | 1.7 | 30.6 | 24.8 | 73.8 | 5.5 | Influencer > Instagram > TikTok > POS > TV |
| ±100% | 1.7 | 30.1 | 24.9 | 71.6 | 5.6 | Influencer > Instagram > TikTok > POS > TV |
| ±50% | 1.8 | 28.2 | 25.0 | 64.2 | 6.0 | Influencer > Instagram > TikTok > POS > TV |
| ±25% | 2.0 | 23.4 | 24.7 | 46.9 | 6.8 | Influencer > TikTok > Instagram > POS > TV |
| ±10% | 2.2 | 15.3 | 20.3 | 22.6 | 8.0 | Influencer > TikTok > Instagram > POS > TV |
| ±5% | 2.5 | 12.0 | 15.9 | 15.0 | 8.0 | TikTok > Influencer > Instagram > POS > TV |
| ±2% | 3.0 | 10.1 | 12.8 | 11.8 | 7.4 | TikTok > Influencer > Instagram > POS > TV |
| fixed at benchmark | 3.5 | 9.1 | 11.4 | 10.5 | 6.9 | TikTok > Influencer > Instagram > POS > TV |

## Reading

- **An honest prior changes nothing.** Up to ±100% the estimates do not move (influencer 1.67 → 1.61). The data are too informative: the influencer coefficient is measured to within 3%.
- **Plausible sizes have to be forced, and forcing them breaks the model.** Even a prior of ±25% leaves influencer at 1.08 and already costs 123 AIC points. Fixed at the benchmark, R² falls from 0.98 to 0.77 and the forecast error on unseen weeks rises from 4.2% to 12.2%, worse than part 1's model (11.4%). The large effects are a property of the data, not of our specification.
- **The ranking digital > POS > TV holds at every strength.** At the benchmark an extra £ returns about £9–11 on each digital channel, £6.9 on POS and £3.5 on TV, although the prior doubles TV's effect. Equal elasticities give the higher return to the smaller budget.
- **The order among the three digital channels does not hold.** Influencer leads without a prior, TikTok at the benchmark.
- **The gain from the first-step plan ranges from 5% to 30%** of revenue between the two ends. That range, not either number, is what we know before a test.

This differs slightly from the arithmetic in `step9_critical_review.md` (about +6%), which scaled only the three digital channels and left TV as estimated; here all five channels are tied to the benchmark and the rest of the model is re-estimated.

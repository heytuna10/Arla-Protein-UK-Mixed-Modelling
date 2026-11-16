# Step 4 – synergies beyond the multiplicative structure

The model is multiplicative: every driver already scales the effect of every other one (a week with TV on air has more sales for influencer spend to lift). The tests below ask whether a pair of drivers reinforces each other *more* than that. Four pairs were fixed before testing:

- **tv × influencer**: TV makes the brand familiar, so influencer posts convert better while TV is on air.
- **tv × social**: TV drives search and social traffic, so paid Instagram/TikTok works harder during flights.
- **influencer × social**: influencer content is amplified by paid Instagram/TikTok on the same platforms.
- **pos × promo**: in-store displays make a price promotion more visible, so the discount lifts more.

Each interaction is the product of the two transformed media variables (centred at average spend; social = Instagram + TikTok; promo = promo depth), added to M14 with decays re-tuned. Rule: keep only if BIC and hold-out error improve and the sign is stable.

| interaction | coef | t (HAC) | p (HAC) | range across training windows | AIC vs M14 | BIC vs M14 | hold-out MAPE % (M14: 4.22) | rolling MAPE % (M14: 3.88) | kept |
|---|---|---|---|---|---|---|---|---|---|
| tv × influencer | 0.34 | 0.22 | 0.827 | 0.06 to 2.17 | 2.0 | 5.0 | 4.21 | 3.96 | no |
| tv × social | 0.46 | 0.60 | 0.548 | 0.46 to 2.78 | 1.7 | 4.7 | 4.36 | 4.29 | no |
| influencer × social | 2.74 | 1.66 | 0.098 | 2.74 to 7.45 | -0.2 | 2.8 | 4.39 | 3.92 | no |
| pos × promo | -0.81 | -1.64 | 0.101 | -1.38 to -0.81 | 0.1 | 3.2 | 4.50 | 3.96 | no |

All four together: AIC +3.5, BIC +15.6 vs M14, hold-out MAPE 4.68%, rolling 4.36%.

Positive AIC/BIC differences = worse than M14. None is kept.

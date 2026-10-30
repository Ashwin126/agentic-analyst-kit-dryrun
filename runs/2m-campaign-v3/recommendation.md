# $2M month-to-month → 1-year campaign (v3): recommendation

For: VP of Marketing. Bar: **20% ROI** on the $2M cost, i.e. ≥ **$2.40M** in retained revenue within 12 months. Brief: `briefs/2m-campaign-v3.md`.

## Recommendation: **Do not fund** at the base we can see. With a larger base: test first from 35,253 month-to-month customers, fund only from 370,149

At the only base we can see (3,872 month-to-month customers), even the high case returns **$264K** (ROI -87%). To reach $2.40M, **2,760 customers who would have left must stay**. Even if all 1,717 month-to-month churners stayed, that is only $1.49M. The answer depends on the real base size, which is not in the data:

- **Below 35,253:** do not fund. Even the high case misses the bar.
- **35,253 to 370,148:** test first. Pilot: offer the 1-year contract to 4,321 month-to-month customers and hold out 4,321 more, chosen at random, and compare churn over the following 12 months. That size detects the mid case (44.3% → 41.4% churn across everyone offered); the effect needed to clear the bar depends on the real base, so resize the pilot once that number is known.
- **370,149 or more:** fund. It clears the $2.40M bar even under the low-case assumptions.

## What we found

- Month-to-month customers churn at **44.3%** vs **14.5%** on one-year contracts, a 29.8-point gap (chart 1).
- The gap is smaller for longer-tenure customers: 39.4 points at 0–12 months down to 6.9 at 61–72 (chart 2). 61–72 months is the one 12-month bin under 10 points; the brief lists it as a known exception, and it holds 3% of month-to-month customers. Weighted by the month-to-month customers' tenure mix, the gap is 31.0 points, about the same as the raw gap.
- The gap holds within internet types (DSL 21, fiber 33, no internet 17 points) and payment methods (20–34 points).
- A month-to-month churner pays **$72.49/month** on average, so each churner avoided is worth **$870** over 12 months.
- Loyalty app users churn more overall (33.6% vs 24.9%) but less within every contract type. The reversal lines up with contract mix: 86% of users are month-to-month vs 29% of non-users.

## How sure we are

- **Sure:** at this file's scale the answer is no. Even avoiding every month-to-month churner falls short of $2.40M.
- **Not sure:** the base size, the take-up and how much of the gap a contract switch would really change. The data cannot separate who chooses a 1-year contract from what the contract does. Adjusting for the tenure mix leaves the gap about the same (31.0 vs 29.8 points), so the data does not favor the low or the high case.
- **The duplicate choice changes churn levels, not the decision:** keeping the Churn=No copies gives 41.7% vs 10.9% (instead of 44.3% vs 14.5%), and the pilot's baseline would move with it. The gap barely changes, the break-even bases move by -4%, and the recommendation is unchanged.

## Value range (12-month retained revenue vs the $2.40M bar)

| Case | Take-up | Share of gap that's real | Churners avoided | Value (this file) | ROI (this file) | Per 1,000 MTM customers | MTM base to clear the bar |
|---|---|---|---|---|---|---|---|
| Low | 10% | 25% | 29 | $25K | -99% | $6,484 | 370,149 |
| Mid | 20% | 50% | 115 | $100K | -95% | $25,936 | 92,538 |
| High | 35% | 75% | 303 | $264K | -87% | $68,081 | 35,253 |

Formula: MTM customers × take-up × churn gap × share real × avg monthly charge of MTM churners × 12. ROI = (value − $2M) ÷ $2M. Customer counts needed are rounded up so they clear the bar. Assumptions (none measured): take-up and share real are from the brief; each churner avoided pays for 12 full months; the $2M includes the discount; the Churn flag (left in the last month) is treated as a one-time difference, not a monthly rate repeated for 12 months.

## Data issues

- 211 customer IDs appeared twice, with the pairs disagreeing on Churn. We kept the Churn=Yes row (per the brief) and removed 211 rows.
- 200 MonthlyCharges values looked ×100: 197 were divided by 100 and 3 removed because ÷100 didn't match TotalCharges ÷ tenure. Another 66 normal-range values don't match either; per the brief they were flagged and kept, so similar mismatches are handled differently above and below 120 (the effect on the result is negligible). 11 blank TotalCharges (new customers) were set to 0. RetentionOfferAccepted leaks the outcome and was dropped.
- 214 of 7,254 rows removed (3.0%). See `cleaning_log.md`.

## Risks

- **Base size** is the biggest risk: it alone decides between do not fund, test first and fund.
- The gap comes from observational data. Customers moved over by a discount may churn more than those who chose a 1-year contract, and customers who would have stayed anyway may take the discount too.
- Revenue is not profit: clearing the bar on revenue may still lose money once the cost of serving customers is counted.

## Next step

**Give us the real number of month-to-month customers.** We then apply the ranges above. If it is between 35,253 and 370,148, run the pilot before committing $2M.

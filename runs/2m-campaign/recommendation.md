# $2M month-to-month → 1-year campaign: recommendation

For: VP of Marketing. Bar: the campaign must return ≥ $2M in retained revenue within 12 months.

## Recommendation: **Do not fund** at the customer base we can see

In the data we have (3,872 month-to-month customers), even the high case returns **$264K**, well under $2M. To pay back $2M, **2,299 customers must stay** who would otherwise have left. Even if every month-to-month customer who churned (1,717) stayed, that is only $1.49M. **This flips only if the real month-to-month base is much larger than this file:** at least 29,377 customers (high case), 77,114 (mid) or 308,457 (low).

## What we found

- Month-to-month customers churn at **44.3%** vs **14.5%** on one-year contracts, a 29.8-point gap (chart 1).
- The gap is **associated with** tenure: it shrinks from 39.4 points for customers with 0–12 months' tenure to 11.7 points at 49–72 months (chart 2). This suggests part of the gap may reflect who chooses each contract rather than the contract itself.
- A month-to-month churner pays **$72.49/month** on average, so each customer kept is worth **$870** over 12 months.
- Customers kept: low 29, mid 115, high 303, against 2,299 needed (chart 3).
- Loyalty app users churn more overall (33.6% vs 24.9%) but **less** within every contract type (month-to-month: -22.6 points), a reversal that reflects contract mix: 86% of them are month-to-month vs 29% of non-users. Compare within contract before using it for targeting.

## Value range (12-month retained revenue)

| Case | Take-up | Share of gap that's real | Customers kept | Value (this file) | Per 1,000 MTM customers | MTM base to break even |
|---|---|---|---|---|---|---|
| Low | 10% | 25% | 29 | $25K | $6,484 | 308,457 |
| Mid | 20% | 50% | 115 | $100K | $25,936 | 77,114 |
| High | 35% | 75% | 303 | $264K | $68,081 | 29,377 |

Formula: MTM customers × take-up × churn gap × share real × avg monthly charge of MTM churners × 12. Assumptions are from the brief; none are measured. A kept customer is counted as paying for 12 full months, and the $2M already includes the discount.

## How sure we are

- **Sure:** at this file's scale the answer is no. Even keeping every month-to-month churner falls short of $2M.
- **Not sure:** the real size of the base, the take-up rate and how much of the gap is real. None of these is in the data. The tenure pattern suggests the low case is the more likely one.
- **Duplicate choice doesn't matter:** keeping the Churn=No row instead gives a 41.7% vs 10.9% gap and a high case of $274K. Recommendation unchanged.

## Data issues

- 211 customer IDs appeared twice, with the pairs disagreeing on Churn. We kept the Churn=Yes row (your decision) and removed 211 rows.
- 200 MonthlyCharges values looked ×100: 197 were divided by 100 and 3 removed. A further 66 normal-range values don't match TotalCharges ÷ tenure; they were flagged and left unchanged.
- 11 blank TotalCharges (new customers) were set to 0. RetentionOfferAccepted leaks the outcome and was dropped.
- In total 214 of 7,254 rows were removed (3.0%). See `cleaning_log.md`.

## Risks

- **Base size:** if the file is a sample, the answer could change to test_first or fund. This is the biggest risk to this recommendation.
- The 1-year gap comes from observational data. Customers moved over by a discount may churn more than those who chose a 1-year contract, and those who would have stayed anyway may take the discount too.
- Customers who take a 1-year contract can still leave when it ends, so value beyond 12 months is not counted.

## Next step

**Give us the real number of month-to-month customers.** If it is below 29,377, do not fund. If it is above 308,457, the campaign pays back even in the low case. Between the two, run a small pilot to measure take-up and the real churn change before committing $2M.

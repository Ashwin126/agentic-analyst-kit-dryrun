# $2M month-to-month → 1-year campaign: recommendation

For: VP of Marketing. Bar: the campaign must return ≥ $2M in retained revenue within 12 months.

## Recommendation: **Do not fund, unless the month-to-month base is at least 29,377 customers**

At the only base we can see (3,872 month-to-month customers), even the high case returns **$264K**. To pay back $2M, **2,299 customers who would have left must stay**. Even if all 1,717 month-to-month churners stayed, that is only $1.49M. The answer depends on the real base size, which is not in the data:

- **Below 29,377:** do not fund.
- **29,377 to 308,457:** test first. Pilot: offer the 1-year contract to 4,321 month-to-month customers and hold out 4,321 more, chosen at random. That is enough to detect the mid case (44.3% → 41.4% churn across everyone offered).
- **Above 308,457:** fund. It meets the $2M bar even under the low-case assumptions.

## What we found

- Month-to-month customers churn at **44.3%** vs **14.5%** on one-year contracts, a 29.8-point gap (chart 1).
- The gap is smaller for longer-tenure customers: 39.4 points at 0–12 months, 11.7 at 49–72 (chart 2), and 6.9 at 61–72. But half the month-to-month customers (51%) are in their first year, so weighted by their tenure mix the gap is 30.9 points, about the same as the raw gap.
- The gap holds within internet types (DSL 21, fiber 33, no internet 17 points) and payment methods (20–34 points).
- A month-to-month churner pays **$72.49/month** on average, so each churner avoided is worth **$870** over 12 months.
- Loyalty app users churn more overall (33.6% vs 24.9%) but less within every contract type. The reversal lines up with contract mix: 86% of users are month-to-month vs 29% of non-users.

## How sure we are

- **Sure:** at this file's scale the answer is no. Even avoiding every month-to-month churner falls short of $2M.
- **Not sure:** the base size, the take-up and how much of the gap a contract switch would really change. The data cannot separate who chooses a 1-year contract from what the contract does. Tenure does not narrow the gap on average, so the data does not favor the low or the high case.
- **The duplicate choice barely matters:** keeping the Churn=No copies gives 41.7% vs 10.9% and moves the break-even bases by -4%. Recommendation unchanged.

## Value range (12-month retained revenue)

| Case | Take-up | Share of gap that's real | Churners avoided | Value (this file) | Per 1,000 MTM customers | MTM base to break even |
|---|---|---|---|---|---|---|
| Low | 10% | 25% | 29 | $25K | $6,484 | 308,457 |
| Mid | 20% | 50% | 115 | $100K | $25,936 | 77,114 |
| High | 35% | 75% | 303 | $264K | $68,081 | 29,377 |

Formula: MTM customers × take-up × churn gap × share real × avg monthly charge of MTM churners × 12. Assumptions (none measured): take-up and share real are from the brief; each churner avoided pays for 12 full months; the $2M includes the discount; the Churn flag (left in the last month) is treated as a one-time difference, not a monthly rate repeated for 12 months.

## Data issues

- 211 customer IDs appeared twice, with the pairs disagreeing on Churn. We kept the Churn=Yes row (your decision) and removed 211 rows.
- 200 MonthlyCharges values looked ×100: 197 were divided by 100 and 3 removed. Another 66 don't match TotalCharges ÷ tenure; they were flagged and left as is. 11 blank TotalCharges (new customers) were set to 0. RetentionOfferAccepted leaks the outcome and was dropped.
- 214 of 7,254 rows removed (3.0%). See `cleaning_log.md`.

## Risks

- **Base size** is the biggest risk: it alone decides between do not fund, test first and fund.
- The gap comes from observational data. Customers moved over by a discount may churn more than those who chose a 1-year contract, and customers who would have stayed anyway may take the discount too.
- Customers can leave when the 1-year contract ends; value beyond 12 months is not counted.

## Next step

**Give us the real number of month-to-month customers.** We then apply the ranges above. If it is between 29,377 and 308,457, run the pilot before committing $2M.

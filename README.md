# Should we fund the $2M campaign?

**Question:** Should we spend $2M to move month-to-month customers to 1-year contracts?
**Decision maker:** VP of Marketing. **Bar:** a 20% ROI, i.e. at least **$2.4M** of revenue retained within 12 months.

## Answer: Do not fund at the base we can see

At the **3,872** month-to-month customers in the data, even the most optimistic case keeps only **$264K** of revenue (ROI −87%). Reaching $2.4M needs **2,760** customers who would have left to stay, more than the **1,717** month-to-month customers who churned in total.

Only a much larger month-to-month base could change this:

| Real month-to-month base | Recommendation |
|---|---|
| Below 35,253 | **Do not fund**: even the high case misses the bar |
| 35,253 to 370,148 | **Test first**: offer the 1-year contract to 4,321 customers, hold out 4,321, compare churn over 12 months |
| 370,149 or more | **Fund**: clears the bar even in the low case |

**Next step:** confirm the real number of month-to-month customers.

![At 3,872 customers, even the high case misses the $2.4M bar](runs/2m-campaign-v3/chart3_value.png)

## Value range (at the file's 3,872 customers)

| Case | Take-up | Share of churn gap that's real | Churners avoided | Revenue kept | ROI | Base needed to clear $2.4M |
|---|---|---|---|---|---|---|
| Low | 10% | 25% | 29 | $25K | −99% | 370,149 |
| Mid | 20% | 50% | 115 | $100K | −95% | 92,538 |
| High | 35% | 75% | 303 | $264K | −87% | 35,253 |

Take-up and the real share of the gap are assumptions from the brief; nothing in the data measures them. Each churner avoided is worth $870 (12 months at $72.49).

## What the data shows

Month-to-month customers churn at **44.3%**, about 3× the **14.5%** of 1-year customers:

![Month-to-month customers churn at 44.3%, 3.1x the one-year rate](runs/2m-campaign-v3/chart1_contract.png)

The gap is **associated with** tenure: it is largest for newer customers and smallest for the longest-tenure group (61–72 months, a known exception under 10 points). Half of month-to-month customers are in their first year, so adjusting for the tenure mix leaves the gap about the same (31.0 vs 29.8 points). The data cannot tell how much of the gap a contract switch would actually remove.

![The churn gap is smaller in longer-tenure groups](runs/2m-campaign-v3/chart2_tenure_gap.png)

## Data issues (all logged in [cleaning_log.md](runs/2m-campaign-v3/cleaning_log.md))
- 211 customer IDs appear twice, disagreeing on `Churn`. Kept the Churn = Yes row; keeping the No row instead changes churn levels (41.7% vs 10.9%) but not the recommendation.
- 200 `MonthlyCharges` values look ×100: 197 divided by 100, 3 removed. 66 normal-range values that don't match TotalCharges ÷ tenure are flagged and kept.
- 11 blank `TotalCharges` (new customers) set to 0. `RetentionOfferAccepted` leaks the answer and is not used.
- 214 of 7,254 rows removed (3.0%).

## Files
- **Brief:** [briefs/2m-campaign-v3.md](briefs/2m-campaign-v3.md)
- **Full write-up:** [recommendation.md](runs/2m-campaign-v3/recommendation.md). Every number comes from [analysis.py](runs/2m-campaign-v3/analysis.py), which reruns from the raw data.
- **Independent review:** [review-v3.md](runs/telco/review-v3.md). It rated the first draft *fix before sending*; all its findings have since been fixed, but not yet re-reviewed.
- **Earlier versions:** [v1](runs/2m-campaign/recommendation.md) (break-even bar) and [v2](runs/2m-campaign-v2/recommendation.md) (break-even, by conversion rate) also reach *do not fund*.

Findings are associations from observational data, not causes. Revenue is not profit, so clearing the bar on revenue alone could still lose money.

**Data source:** IBM Telco Customer Churn sample data (a fictional company), modified for teaching. File: `data/raw/telco_v2.csv`.

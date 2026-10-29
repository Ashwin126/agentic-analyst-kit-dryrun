# Recommendation: do not fund the $2M campaign

**For:** Ashwin (decision Fri Oct 30, 2026). **Brief:** `briefs/2m-campaign-v2.md`. **Recommendation:** `do_not_fund`.
**Data source:** IBM Telco Customer Churn sample data (a fictional company), modified for teaching; file `data/raw/telco_v2.csv`.

## Recommendation
Do not fund. To keep $2M of revenue within 12 months, **421% of month-to-month customers would have to convert** (mid case, 50% of the churn gap real), against an assumed 5–20%. Even if all 3,875 converted and the whole gap were real, 12-month revenue kept would be $951K.

## What we found
- 3,875 month-to-month customers churn 41.7% vs 10.9% on 1-year contracts: a 30.8-point gap. Average monthly charge $66.44. $2M is $516 per month-to-month customer.
- Month-to-month is associated with higher churn inside every tenure, internet and payment group (gap 13 pts at 49–72 months to 40 pts at 0–12 months).
- How much of the 30.8-pt gap is about the contract itself? Comparing like with like on tenure alone leaves 20.6–31.5 pts (1-year vs month-to-month customer mix). Adding internet and payment method cuts it to 9.4–16.0 pts (cells with 10+ customers on each contract; 59%–87% of customers). So much of the raw gap goes with who is on month-to-month, and per the brief the 25%-real case deserves more weight. That only moves breakeven further out of reach.

## How sure we are
Very sure. Breakeven conversion is at least 57% in every data version and gap share tested, and above 210% once the flagged charges are left out, all far above 20%. Only base size could change this: the mid case needs about **130,421 month-to-month customers**, 34× this file.

## Value range (12-month revenue kept, headline data)
| Case | Conversion | Gap real | Revenue kept | Short of $2M by |
|---|---|---|---|---|
| Low | 5% | 25% | $12K | $1.99M |
| Mid | 12.5% | 50% | $59K | $1.94M |
| High | 20% | 100% | $190K | $1.81M |

| Data version | Gap | Avg charge | Breakeven at 100% / 50% / 25% gap real | Result |
|---|---|---|---|---|
| Keep Churn = No, flagged charges out (headline) | 30.8 pts | $66.44 | 210% / 421% / 841% | `do_not_fund` |
| Keep Churn = No, flagged charges in | 30.8 pts | $243.64 | 57% / 115% / 229% | `do_not_fund` |
| Keep Churn = Yes, flagged charges out | 29.8 pts | $66.44 | 217% / 434% / 869% | `do_not_fund` |
| Keep Churn = Yes, flagged charges in | 29.8 pts | $243.64 | 59% / 118% / 237% | `do_not_fund` |

Assumptions (none measured): conversion and gap share as above; a saved customer pays 12 months at the average charge; $2M is all-in. Full conversion × gap grid: `results.json`.

**Top 3 segments** (revenue kept per converted customer, mid case). None breaks even alone:
| Month-to-month segment | Customers | Gap vs 1-year | Kept per convert | Breakeven if all $2M spent here |
|---|---|---|---|---|
| Monthly charge $70.45–$89.90 | 1,146 | 41 pts | $197 | 884% |
| Senior citizens | 807 | 39 pts | $184 | 1349% |
| Fiber optic internet | 2,128 | 35 pts | $182 | 517% |

## Data issues
211 duplicate IDs with conflicting Churn (kept Churn = No; reran the other way). 200 `MonthlyCharges` above $200 look ×100; rows kept, charges left out of averages in the headline. 11 blank `TotalCharges` set to 0. `RetentionOfferAccepted` leaks the answer; dropped. `LoyaltyAppUser`: users churn +9.6 pts overall but -21.9, -5.2, -1.9 pts within each contract type; not used for targeting. See `cleaning_log.md`.

## Risks
Observational data: the gap may reflect who chooses contracts on factors not in the file. Revenue, not profit, is the bar; profit would make the case weaker.

## Next step
Confirm the real month-to-month count. Near 3,875: close as no. Above about 130,421: rerun `analysis.py` with that count.

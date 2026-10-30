# Brief: $2M month-to-month → 1-year contract campaign (v3)

Data: `data/raw/telco_v2.csv`. Output folder: `runs/2m-campaign-v3/`. Follow `CLAUDE.md` throughout.
This brief replaces nothing: `briefs/2m-campaign.md`, `briefs/2m-campaign-v2.md` and their `runs/` folders stay as they are.

## 1. The decision
- **Decision maker:** VP of Marketing.
- **Question:** Should we fund a $2M campaign to move month-to-month customers to 1-year contracts?
- **Bar to fund:** **ROI of at least 20%** on 12-month retained **revenue**: (retained revenue − $2M) ÷ $2M ≥ 20%, so retained revenue must be **≥ $2.4M** within **12 months**. Break-even is not enough.
- **Cost:** the $2M is **all-in**, including the contract discount. Add nothing on top.
- **Scope:** target **all** month-to-month customers.

## 2. Questions to answer
1. How much more do month-to-month customers churn than 1-year customers, and does the gap hold within tenure, internet service and payment method groups?
2. What is the low, mid and high 12-month retained revenue?
3. **How many customers who would have left must stay** to reach $2.4M?
4. **Break-even base size:** how many month-to-month customers does each case need to reach $2.4M? The real base size is unknown, so this is the key output.
5. Which variables are associated with churn, overall and within contract type? (For `findings.json`.)

## 3. Data checks
Profile first, as `CLAUDE.md` requires. Known issues, and the agreed rule for each:

| # | Issue | Rule |
|---|---|---|
| 1 | 211 `customerID`s appear twice (422 rows). Each pair is identical except `Churn` (one Yes, one No) and `RetentionOfferAccepted`. | **Keep the `Churn = Yes` row.** Rerun the headline result keeping the `Churn = No` row, and report whether the answer changes. Log all 211. |
| 2 | 200 `MonthlyCharges` values > 120 (max 11,515); they look ×100 | Divide by 100 if the result is within ±20% of `TotalCharges ÷ tenure`. Otherwise remove the row. Log each one. |
| 3 | 11 `TotalCharges` are a single space, all with tenure 0 | Set to 0 (new customers, not yet billed). Log them. |
| 4 | `RetentionOfferAccepted` is filled only for churners (leaks the answer) | Leave it out of the analysis. Report it as a data issue. |
| 5 | Normal-range `MonthlyCharges` more than 20% away from `TotalCharges ÷ tenure` | Flag them; don't change them. Log them. |

Every removal or change goes in `cleaning_log.md` with the reason. Raw data is never changed.

## 4. Analysis
**Formula:** 12-month retained revenue = month-to-month customers × take-up × (MTM churn − 1-year churn) × share of gap that's real × average monthly charge of month-to-month churners × 12.

**Assumptions** (none measured):

| Input | Low | Mid | High |
|---|---|---|---|
| Take-up of the 1-year offer | 10% | 20% | 35% |
| Share of the MTM vs 1-year churn gap that's real | 25% | 50% | 75% |

- Churn rates and average monthly charges come from the cleaned data.
- The `Churn` flag (left in the last month) is treated as a **one-time** churn difference, not a monthly rate repeated for 12 months. Each churner avoided is counted as paying 12 full months. State both as assumptions.
- **Customers who must stay** = $2.4M ÷ (average monthly charge of MTM churners × 12). Show it next to the churners avoided in each case and the most that could possibly be saved (every MTM churner).
- **Break-even base** = $2.4M ÷ value per month-to-month customer, for each case.
- **Confounding check:** compare month-to-month vs 1-year churn within 12-month tenure bins (0–12, 13–24, 25–36, 37–48, 49–60, 61–72), internet service types and payment methods. Report the gap weighted by the month-to-month customers' tenure mix.
- Describe findings as "associated with", never "causes". The data is observational.

## 5. When to stop and ask
Stop and ask the user when:
1. Cleaning **removes** more than 5% of rows. Planned fixes (÷100, blank to 0) don't count, but they are logged.
2. The month-to-month vs 1-year gap is **under 10 points in any 12-month tenure bin**. **Known exception:** 61–72 months is already about 7 points. Disclose it in `recommendation.md` and continue; any other bin under 10 points is a stop.
3. Anything forces a change to the rules or assumptions above.
4. The analysis is done: report the break-even base sizes and ask for the real number of month-to-month customers before the recommendation is final.

**Recommendation rule:**
- `fund`: even the **low** case reaches $2.4M.
- `do_not_fund`: even the **high** case falls short of $2.4M.
- `test_first`: $2.4M falls between the low and high cases. Give a pilot size.

The real base is unknown, so `recommendation.md` opens with the answer for each base-size range (below the high-case break-even, between high and low, above the low-case break-even). `findings.json` uses the answer at the file's base size.

## 6. Deliverables (in `runs/2m-campaign-v3/`)
- `recommendation.md`: 1 page, in the order `CLAUDE.md` sets. It includes the base-size ranges, customers who must stay, and the low, mid and high value range.
- `cleaning_log.md`
- `findings.json` in the `CLAUDE.md` format.
- Charts (PNG). Each title states the finding, and everything else is grayed out:
  1. Churn rate by contract type.
  2. Month-to-month vs 1-year churn gap within tenure groups.
  3. Low, mid and high 12-month retained revenue and churners avoided, against the $2.4M bar.
- The code that makes every number, so it can be run again.

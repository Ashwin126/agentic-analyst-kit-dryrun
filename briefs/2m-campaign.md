# Brief: $2M month-to-month → 1-year contract campaign

Data: `data/raw/telco_v2.csv`. Output folder: `runs/2m-campaign/`. Follow `CLAUDE.md` throughout.

## 1. The decision
- **Decision maker:** VP of Marketing.
- **Question:** Should we fund a $2M campaign to move month-to-month customers to 1-year contracts?
- **Bar to fund:** the campaign must at least break even, meaning retained **revenue** within **12 months** is at least $2M.
- **Campaign scope:** target **all** month-to-month customers. The $2M **includes** the contract discount, so no extra revenue loss is added on top.

## 2. Questions to answer
1. How much more do month-to-month customers churn than 1-year customers, and does the gap hold within tenure, internet service and payment method groups?
2. What 12-month retained revenue does the campaign produce in the low, mid and high cases?
3. **Break-even base size:** how many month-to-month customers do we need for the mid case (and the low and high cases) to reach $2M? The real size of the base is unknown, so this number is the key output.
4. Which variables are associated with churn, overall and within contract type? (Used for `findings.json`.)

## 3. Data checks
Profile first, as `CLAUDE.md` requires. Known issues from the first profile, and the agreed rule for each:

| # | Issue | Rule |
|---|---|---|
| 1 | 211 `customerID`s appear twice (422 rows), and every pair differs in some column | If a pair differs in `Churn` or `Contract`: **stop and ask**. Otherwise keep the first row. Log all 211. |
| 2 | 200 `MonthlyCharges` values > 120 (look ×100) | Divide by 100 if the result is within ±20% of `TotalCharges ÷ tenure`. Otherwise remove the row. Log each one. |
| 3 | 11 `TotalCharges` are a single space, all with tenure 0 | Set to 0 (new customers, not yet billed). Log them. |
| 4 | `RetentionOfferAccepted` is filled only for churners (leaks the answer) | Leave it out of the analysis. Report it as a data issue. |

Every removal or change goes in `cleaning_log.md` with the reason. Raw data is never changed.

## 4. Analysis
**Formula:** 12-month retained revenue = month-to-month customers × take-up × (MTM churn − 1-year churn) × share of gap that's real × average monthly charge of month-to-month churners × 12.

**Assumptions** (none measured; the user has no internal numbers):

| Input | Low | Mid | High |
|---|---|---|---|
| Take-up of the 1-year offer | 10% | 20% | 35% |
| Share of the MTM vs 1-year churn gap that's real | 25% | 50% | 75% |

- The 1-year churn rate, the month-to-month churn rate and average monthly charges come from the cleaned data.
- A saved customer is counted as keeping 12 full months of revenue. State this as an assumption.
- **Confounding check:** compare month-to-month vs 1-year churn within tenure groups, internet service types and payment methods. If the gap shrinks a lot, give the low case more weight.
- Describe all findings as "associated with", never "causes". The data is observational.

## 5. When to stop and ask
Stop and ask the user when:
- A duplicate pair differs in `Churn` or `Contract`.
- Cleaning **removes** more than 5% of rows. Planned fixes (÷100, blank to 0) don't count, but they are logged.
- The month-to-month vs 1-year churn gap falls below 10 points within tenure groups.
- Anything forces a change to the assumptions or cleaning rules above.
- The analysis is done: report the break-even base size and ask for the real number of month-to-month customers before the recommendation is final.

**Recommendation rule:**
- `fund`: even the **low** case reaches $2M.
- `do_not_fund`: even the **high** case falls below $2M.
- `test_first`: $2M falls between low and high. Suggest a pilot size.

## 6. Deliverables (in `runs/2m-campaign/`)
- `recommendation.md`: 1 page, in the order `CLAUDE.md` sets. It includes the break-even base size and the low, mid and high value range.
- `cleaning_log.md`
- `findings.json` in the `CLAUDE.md` format.
- Charts (PNG). Each title states the finding, and everything else is grayed out:
  1. Churn rate by contract type.
  2. Month-to-month vs 1-year churn gap within tenure groups.
  3. Low, mid and high 12-month retained revenue against the $2M line.
- The code that makes every number, so it can be run again.

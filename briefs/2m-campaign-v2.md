# Brief: $2M month-to-month → 1-year contract campaign (v2)

Data: `data/raw/telco_v2.csv`. Output folder: `runs/2m-campaign-v2/`. Follow `CLAUDE.md` throughout.
This brief replaces nothing: `briefs/2m-campaign.md` and `runs/2m-campaign/` stay as they are.

## 1. The decision
- **Decision maker:** Ashwin.
- **Decision date:** Friday, October 30, 2026. Deliverables are due **Thursday, October 29, evening**.
- **Question:** Should we fund a $2M campaign to move month-to-month customers to 1-year contracts?
- **Bar to fund:** at least breakeven. Expected **revenue** retained within **12 months** must be **≥ $2M**.
- **Cost:** the $2M is **all-in**, including any discount or incentive to customers who switch. Add nothing on top.
- Revenue overstates profit (no margin is applied), and that favors funding. Treat a result that only just clears $2M as weak.

## 2. Questions to answer
1. How many month-to-month customers can the campaign realistically reach? (About 3,900 in the data, so $2M is more than $500 per customer.)
2. What conversion rate does breakeven require, and is it believable against the 5–20% range?
3. Does a 1-year contract actually lower churn, or do customers who choose 1-year contracts churn less anyway? How much of the month-to-month vs 1-year gap is real?
4. Which month-to-month segments are worth targeting (for example high charges, short tenure, electronic check), and what is each one's breakeven rate?

## 3. Data checks
Profile first, as `CLAUDE.md` requires. Known issues from the first profile, and the agreed rule for each:

| # | Issue | Rule |
|---|---|---|
| 1 | 211 `customerID`s appear twice (422 rows). In every pair, one row says churned and the other says stayed. | **Keep the `Churn = No` row** (this makes the campaign look worse, which is the cautious choice). Rerun the headline result keeping the `Churn = Yes` row instead, and report both. Log all 211. |
| 2 | 200 `MonthlyCharges` values > 200 (max 11,515). They look ×100. | **Do not fix them.** Flag them, and run the headline result with and without these rows. Log them. |
| 3 | 11 `TotalCharges` are a single space, all with tenure 0 | Treat as 0 (new customers, not yet billed). Log them. |
| 4 | `RetentionOfferAccepted` is filled only for churners (leaks the answer) | Leave it out of the analysis. Report it as a data issue. |
| 5 | `LoyaltyAppUser` users churn more (32.7% vs 24.1%) | Flag it. Do not use it to choose targets. |

Every removal or change goes in `cleaning_log.md` with the reason. Raw data is never changed.

## 4. Analysis
**Formula:** 12-month retained revenue = month-to-month customers targeted × conversion × (MTM churn − 1-year churn) × share of gap that's real × average monthly charge × 12.

**Steps:**
1. Compute month-to-month revenue at risk over 12 months, by segment.
2. Solve for the **breakeven conversion rate**: the share who must switch for retained revenue to reach $2M.
3. Assume a converted customer's churn falls only part of the way to the 1-year rate. Test **25%, 50% and 100%** of the gap.
4. Repeat steps 1–3 for the best target segments.
5. **Confounding check:** compare month-to-month vs 1-year churn within tenure groups, internet service types and payment methods. If the gap shrinks a lot, give the 25% case more weight.

**Assumptions** (none measured; there is no past campaign or benchmark):

| Input | Low | Mid | High |
|---|---|---|---|
| Conversion to 1-year | 5% | 12.5% | 20% |
| Share of the churn gap that's real | 25% | 50% | 100% |

- The churn rates and average monthly charges come from the cleaned data.
- A saved customer is counted as keeping 12 full months of revenue. State this as an assumption.
- Describe findings as "associated with", never "causes". The data is observational.

## 5. When to stop and ask
Ask Ashwin **in this chat** when:
1. **The result is borderline:** the breakeven conversion rate falls inside the 5–20% range.
2. **The duplicate rule flips the answer:** fund under one rule and don't fund under the other.
3. **The `MonthlyCharges` outliers flip the answer:** the result changes when the 200 rows are left out.
4. **A data problem not listed here** turns up and moves any churn rate by more than about 2 points.
5. **Thursday evening is at risk:** the analysis can't finish in time for a Friday decision.

**Recommendation rule** (`findings.json`):
- `fund`: breakeven conversion is **≤ 5%** at the 50% gap share, under both duplicate rules, with and without the outliers.
- `do_not_fund`: breakeven conversion is **> 20%** even at the 100% gap share.
- `test_first`: anything in between. Stop and ask (trigger 1) before finalizing, and suggest a pilot size.

## 6. Deliverables (in `runs/2m-campaign-v2/`, per `CLAUDE.md`)
1. `recommendation.md`: 1 page, in the order `CLAUDE.md` sets. Open with Fund / Don't fund / Test first, and the breakeven conversion rate compared with the 5–20% range.
2. **Sensitivity table** (in `recommendation.md`): results across conversion 5–20%, gap share 25/50/100%, both duplicate rules, and with and without the outliers.
3. **Top 3 target segments**, each with its own breakeven conversion rate.
4. `cleaning_log.md`: every check, what was found, and how it was handled.
5. `findings.json` in the `CLAUDE.md` format.
6. Charts (PNG). Each title states the finding:
   1. Churn rate by contract type.
   2. Month-to-month vs 1-year churn gap within tenure groups.
   3. Breakeven conversion rate against the 5–20% range.
7. The script that produces every number. It reads `data/raw/telco_v2.csv` and never changes it.
8. A short summary section added to `README.md` that links to `recommendation.md`.

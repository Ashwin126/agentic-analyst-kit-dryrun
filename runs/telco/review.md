# Review: `runs/2m-campaign/` ($2M MTM to 1-year campaign)

Reviewer: independent check. Folder reviewed: `runs/2m-campaign/`, as instructed by the caller. Brief: `briefs/2m-campaign.md`. Standards: `CLAUDE.md`. Raw data: `data/raw/telco_v2.csv`.
Every number below was recomputed with my own pandas code from the raw CSV. I did not run or import `analysis.py`; I only read it.

## 1. Verdict

**Fix before sending.** Every number in `recommendation.md` reproduces exactly. But the headline and `findings.json` give a final `do_not_fund` based on the 3,872 customers in this file, when the brief says the real base size is unknown and the recommendation should not be final until we have it. The deck also says the tenure pattern points to the low case, and my check does not support that.

## 2. Must fix

1. **The recommendation is stated as final, but the brief says it can't be yet.** The brief (section 2 Q3 and section 5) says "The real size of the base is unknown, so this number [break-even base] is the key output" and to "ask for the real number of month-to-month customers before the recommendation is final." The deck's headline is "**Do not fund** at the customer base we can see," and `findings.json` says `"recommendation": "do_not_fund"` with nothing to show it is conditional. That verdict only holds if the base is the 3,872 customers in this file. Under the brief's own rule, the answer is `do_not_fund` below 29,377 MTM customers, `test_first` from 29,377 to 308,457, and `fund` above 308,457. The "Next step" section says this correctly, but the headline and the JSON do not.
   *Fix:* Open with the break-even bases as the main result, and label the recommendation "provisional: do not fund unless the MTM base is at least 29,377." Add the same caveat wherever `findings.json` is passed on, or hold `findings.json` until the base is known. The brief also asks for a pilot size in the `test_first` range, and none is given.

2. **"The tenure pattern suggests the low case is the more likely one" is not supported.** (How sure we are section; line 12 says something similar.) The gap does shrink in the high-tenure groups. But only 342 of the 3,872 MTM customers (8.8%) are in the 49–72 month group, and 1,991 (51%) are in 0–12, where the gap is largest at 39.4 points. If you weight the within-tenure gaps by the MTM customers' own tenure mix, the tenure-adjusted gap is **30.9 points**, slightly *larger* than the raw 29.8. Weighted by the 1-year mix it is 19.3 points. The campaign targets MTM customers, so the MTM weighting is the relevant one. So the tenure check does not show that the gap shrinks for the people the campaign targets. The brief says to weight the low case more only "if the gap shrinks a lot." Saying "low is more likely" moves the decision maker's break-even figure from 77,114 (mid) to 308,457 (low), with no evidence behind it.
   *Fix:* Report the adjusted gap. Say that, within tenure groups, the MTM vs 1-year gap is about as large for the MTM population as the raw gap. Self-selection on things we can't measure is still possible, but tenure doesn't show it. Drop "low case more likely," or give a reason that isn't tenure.

3. **The brief's stop rule (gap below 10 points within tenure groups) passes only narrowly, and it depends on the bins chosen.** With the 4 bins used (0–12, 13–24, 25–48, 49–72), the smallest gap is 11.7 points, just 1.7 points above the threshold. With 12-month bins, the 61–72 group has a gap of **6.9 points** (MTM 23.1%, n=108; 1-year 16.3%, n=313), which would trigger "stop and ask." The brief doesn't set the bins, so this isn't a rule breach. But the deck doesn't mention it, and the user should decide.
   *Fix:* Disclose the sensitivity to binning in "How sure we are" and raise it with the user, as the stop rule intends.

No ❌ numbers. I found no causal claims serious enough to block sending, and no missed data problems (see sections 3–5).

## 3. Number check table

Recomputed with my own cleaning: keep the Churn=Yes row of each duplicate pair; set the 11 blank TotalCharges to 0; for MonthlyCharges > 120, divide by 100 if the result is within ±20% of TotalCharges ÷ tenure, else remove the row.

| Claim | Where | Stated | Recomputed | Status |
|---|---|---|---|---|
| MTM customers in file | rec. headline, table, chart 3 | 3,872 | 3,872 | ✅ |
| High case value | rec. headline, table, chart 3 | $264K | $263,609 | ✅ |
| Customers who must stay to repay $2M | rec. headline, findings, chart 3 | 2,299 | 2,299.2 (2,000,000 / 869.86) | ✅ |
| MTM churners | rec. headline, chart 3 | 1,717 | 1,717 | ✅ |
| Value if every MTM churner stayed | rec. headline | $1.49M | $1,493,546 | ✅ |
| Break-even MTM base, high / mid / low | rec. headline, table, next step | 29,377 / 77,114 / 308,457 | 29,376.9 / 77,114.3 / 308,457.1 | ✅ |
| MTM churn rate | rec. findings, chart 1 | 44.3% | 44.344% (1,717/3,872) | ✅ |
| 1-year churn rate | rec. findings, chart 1 | 14.5% | 14.528% (214/1,473) | ✅ |
| MTM vs 1-year gap | rec. findings | 29.8 pts | 29.82 pts | ✅ |
| 2-year churn rate | chart 1 | 6.0% | 5.96% (101/1,695) | ✅ |
| MTM / 1-year ratio | chart 1 title | 3.1x | 3.05x | ✅ (rounding) |
| Gap at 0–12 months tenure | rec. findings, chart 2 | 39.4 pts (chart: 39) | 39.38 pts | ✅ |
| Gap at 49–72 months tenure | rec. findings, chart 2 | 11.7 pts (chart: 12) | 11.69 pts | ✅ |
| Gaps at 13–24 / 25–48 | chart 2 | 29 / 20 pts | 28.65 / 20.31 pts | ✅ |
| Average monthly charge of MTM churners | rec. findings | $72.49 | $72.4881 | ✅ |
| 12-month value per kept customer | rec. findings | $870 | $869.86 | ✅ |
| Customers kept, low / mid / high | rec. findings, table, chart 3 | 29 / 115 / 303 | 28.86 / 115.45 / 303.05 | ✅ |
| Loyalty app churn, users vs non-users | rec. findings | 33.6% vs 24.9% | 33.56% vs 24.87% | ✅ |
| Loyalty app within-MTM difference | rec. findings | -22.6 pts | -22.58 pts (1-yr -5.2, 2-yr -2.9) | ✅ |
| Share of app users / non-users on MTM | rec. findings | 86% / 29% | 85.75% / 28.84% | ✅ |
| Take-up 10/20/35%, share real 25/50/75% | rec. table | as brief | as brief | ✅ |
| Value low / mid | rec. table, chart 3 | $25K / $100K | $25,106 / $100,422 | ✅ |
| Value per 1,000 MTM customers, low / mid / high | rec. table | $6,484 / $25,936 / $68,081 | $6,483.88 / $25,935.54 / $68,080.78 | ✅ |
| Sensitivity (keep Churn=No): MTM vs 1-year churn | rec. how sure | 41.7% vs 10.9% | 41.71% vs 10.93% (gap 30.78 pts) | ✅ |
| Sensitivity high case | rec. how sure | $274K | $274,170 | ✅ |
| Sensitivity recommendation at file size | rec. how sure | unchanged | do_not_fund at 3,872 | ✅ |
| Duplicate IDs / rows removed | rec. data issues, findings, log | 211 / 211 (422 rows) | 211 IDs, 422 rows, max 2 per ID; 211 removed (all Churn=No) | ✅ |
| MonthlyCharges > 120 / divided / removed | rec., findings, log | 200 / 197 / 3 | 200 / 197 / 3 (lines 81, 610, 1550) | ✅ |
| Normal-range MC off TC÷tenure by >20% | rec., findings, log | 66 | 66 after dedup (67 raw rows; one duplicate pair counted twice) | ✅ |
| Blank TotalCharges, all tenure 0 | rec., findings, log | 11 | 11 (all tenure 0, all Churn=No) | ✅ |
| Rows removed | rec., log | 214 of 7,254 (3.0%; log 2.95%) | 214 (2.950%) | ✅ |
| Clean rows | log | 7,040 | 7,040 | ✅ |
| RetentionOfferAccepted filled for churners / non-churners | log | 2,033 / 0 | 2,033 / 0 (every raw churner filled) | ✅ |
| `findings.json` rows_affected for RetentionOfferAccepted | findings | 7,254 | Column dropped for all 7,254 rows; 2,033 filled | ⚠️ defensible, but 2,033 says more about the leak |
| `findings.json` drivers (20 variables, both directions) | findings | see file | All 40 direction labels reproduce with the same focus groups and 2-point band | ✅ |

`findings.json` and the chart titles agree with `recommendation.md`. Chart 1: "44.3%, 3.1x". Chart 2: "39 to 12 points". Chart 3: "303 ... 2,299".

## 4. Causal language

There are no "causes", "drives" or "will reduce" claims, and chart 1 is labelled "associated, not causal". A few phrases are stronger than the evidence:

| Quote | Where | Suggested rewording |
|---|---|---|
| "a reversal that reflects contract mix" | rec. line 15 | "a reversal consistent with contract mix" |
| "Even the high case keeps 303 customers" | chart 3 title | "Even the high case would keep about 303 customers (modelled from brief assumptions); 2,299 needed to repay $2M" |
| "Customers kept: low 29, mid 115, high 303" / "Customers kept" column | rec. findings and table | "Customers modelled as kept (under the take-up and share-real assumptions)" |
| "the campaign pays back even in the low case" | rec. next step | "the low-case model reaches $2M" |

## 5. Data problems missed or mishandled

My profile of the raw file: 7,254 rows, 23 columns, 7,043 unique IDs. No leading or trailing whitespace in any column. All customerIDs match `####-XXXXX`. No IDs are hidden duplicates after case or whitespace normalising. Every categorical column holds only the expected values. No negative numbers. tenure runs 0–72. TotalCharges is text because of its 11 single-space blanks. No row with tenure of at least 1 has TotalCharges below MonthlyCharges.

- **Nothing material was missed.** All four known issues in the brief were found, applied by the brief's rules and logged. I checked all 488 log rows against the raw line numbers and IDs, with 0 mismatches. The extra 66 flag (normal-range MC inconsistent with TC÷tenure) was not in the brief, was correctly left unchanged and was disclosed.
- **Duplicates, the user's decision:** applied correctly. All 211 pairs are one Yes and one No, and differ only in Churn and RetentionOfferAccepted (I checked every other column: 0 differences, Contract included). All 211 removed rows are the Churn=No copies. The sensitivity run is reported honestly at the headline level. Two things are not reported:
  - The choice moves the break-even bases (Churn=No gives 296,575 / 74,143 / 28,245 for low / mid / high). Those bases are the key output, so this should be stated. It's about 4%, so the conclusion holds.
  - The choice changes overall churn (28.9% vs 25.9%) and 2-year churn (6.0% vs 2.7%), which appear in chart 1. Keeping Churn=Yes adds 53 churners to 1-year and 102 to MTM, so it slightly *narrows* the gap. One line in Data issues would cover it.
- **The 3 removed MonthlyCharges rows:** this follows the brief's rule. All 3 have tenure 2, as do most of the 66 flagged rows (median tenure 3). This suggests the ±20% test is unreliable at low tenure, probably because of partial first-month billing, and the 3 removed rows may well be real ×100 errors. The effect is negligible. No action needed beyond a note.
- **LoyaltyAppUser:** I checked whether it leaks the outcome. It is filled for every row and both values appear for churners and non-churners, so it is not a leak.

## 6. Other notes

- **Section order:** `CLAUDE.md` and the brief require: recommendation, what we found, how sure we are, value range, data issues, risks, next step. The deck puts "Value range" before "How sure we are."
- **Brief Q1 is only partly answered in the deck.** The internet service and payment method gaps were computed (results.json) and they hold: DSL 20.7, Fiber 33.3, No internet 17.2; bank transfer 22.9, credit card 20.4, e-check 34.0, mailed check 23.8 points. None of this reaches `recommendation.md`. Add one line.
- **"mixed" in `findings.json` overstates disagreement.** PhoneService (+2.9/+2.3/+1.8), PaperlessBilling (+15.2/+7.9/+1.5), OnlineBackup (+18.2/+4.1/+1.7) and DeviceProtection (+12.0/+3.1/+0.4) are all positive in every contract. They are labelled "mixed" only because one contract falls under the 2-point "none" band. Consider "higher" when no contract goes the other way, or define "mixed" in a note.
- **`findings.json` doesn't name the comparison group.** "OnlineSecurity: higher" means OnlineSecurity = **No** churns more. For InternetService and PaymentMethod, it means Fiber optic and Electronic check against all other values. The format is fixed by `CLAUDE.md`, so state the focus groups in `recommendation.md` or the log.
- **Chart 3** has two panels, and its title states the right panel's finding (customers), not the brief's chart 3 finding (revenue against the $2M line). It also shows values only at the file's base size, so it reinforces the unconditional "do not fund" (must-fix 1). Consider showing the three break-even bases.
- **The 0–12 tenure 1-year cell is small** (n=124; n=39 for 0–6 months), so the 39.4-point gap there is noisy. No confidence intervals are given anywhere. With these sample sizes the main gap is clearly significant, but the tenure-group gaps should come with a range.
- **The value per kept customer** uses the MTM churners' current monthly charge for 12 months, with no allowance for a discount. That follows the brief ("$2M includes the discount") and is stated, so it's fine.
- `results.json` `profile_raw.text_columns` lists a made-up entry, "TotalCharges (blanks stored as ' ')". This is cosmetic.

## 7. How I checked

Checked: every number in `recommendation.md`, `findings.json` (format, data_issues, all 40 driver directions), the cleaning-log rows against raw line numbers, the chart titles and labels (viewed the PNGs), a raw-data profile of blanks, whitespace, ID format, types, ranges, categories, duplicates, leakage and MC vs TC÷tenure, the sensitivity run, and the confounding checks (re-done, plus a tenure-standardised gap and finer bins).

**Not checked:**
- Whether the plan was shown before code ran (`CLAUDE.md` rule). There is no record in the folder.
- Whether the user has already given the real MTM base size.
- The correctness of `clean.csv` beyond its shape (7,040 × 22), ID uniqueness and max MC of 118.75. My numbers come from my own cleaning, not from that file.

Code, run with `python3 -I` from any directory:

```python
import pandas as pd, numpy as np
RAW='/home/user/agentic-analyst-kit-dryrun/data/raw/telco_v2.csv'
def build(keep):                                   # keep = 'Yes' (main) or 'No' (sensitivity)
    r = pd.read_csv(RAW, dtype=str, keep_default_na=False)
    dup = r.customerID.duplicated(keep=False)
    r = r[~(dup & (r.Churn != keep))].copy(); assert r.customerID.is_unique
    r['ten'] = r.tenure.astype(int); r['mc'] = r.MonthlyCharges.astype(float)
    r['tc'] = pd.to_numeric(r.TotalCharges.str.strip().replace('', '0'))
    imp = r.tc / r.ten.where(r.ten > 0); hi = r.mc > 120
    fix = hi & ((r.mc/100 - imp).abs() <= 0.2*imp)
    r.loc[fix, 'mc'] /= 100; r = r[~(hi & ~fix)].copy(); r['y'] = r.Churn.eq('Yes')
    return r
for keep in ['Yes', 'No']:
    d = build(keep); m = d[d.Contract=='Month-to-month']; o = d[d.Contract=='One year']
    gap = m.y.mean() - o.y.mean(); v = m.loc[m.y,'mc'].mean()*12
    print(keep, len(d), m.y.mean(), o.y.mean(), gap, v/12, 2e6/v, m.y.sum()*v)
    for k,(t,s) in {'low':(.1,.25),'mid':(.2,.5),'high':(.35,.75)}.items():
        p = t*gap*s; print(k, len(m)*p, len(m)*p*v, 1000*p*v, 2e6/(p*v))
# confounding: within-tenure gaps and the MTM-weighted adjusted gap
d = build('Yes'); d['tg'] = pd.cut(d.ten, [-1,12,24,48,72])
t = d[d.Contract.isin(['Month-to-month','One year'])].groupby(['tg','Contract'], observed=True).y.mean().unstack()
g = t['Month-to-month'] - t['One year']
w = d[d.Contract=='Month-to-month'].tg.value_counts(normalize=True)
print(g, (g*w).sum())                              # 0.394/0.287/0.203/0.117; adjusted 0.309
d['tg12'] = pd.cut(d.ten, [-1,12,24,36,48,60,72])  # finer bins: 61-72 gap = 0.069
```

I also ran separate scripts for the raw profile (blanks, whitespace, categories, ID pattern, numeric ranges), duplicate-pair differences across all columns, RetentionOfferAccepted and LoyaltyAppUser against Churn, the 20 driver directions compared with `findings.json`, and the 488 cleaning-log rows matched to raw line numbers. Each is short and follows the same pattern as above.

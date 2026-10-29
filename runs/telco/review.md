# Review: `runs/2m-campaign-v2/` ($2M MTM to 1-year campaign, v2 brief), second review after fixes

Reviewer: independent check. Folder reviewed: `runs/2m-campaign-v2/`. Brief: `briefs/2m-campaign-v2.md` (not the older `briefs/2m-campaign.md`). Standards: `CLAUDE.md`. Raw data: `data/raw/telco_v2.csv`. Also checked: the "$2M campaign, v2 brief" section of `README.md`, `findings.json`, `cleaning_log.md`, the three charts (viewed) and `analysis.py` (read only; not run or imported).

## 1. Verdict

**Ready to send.** All 73 numbers in `recommendation.md`, the README and chart titles reproduce from the raw file. `do_not_fund` follows the brief's rule in all four data versions. The six earlier findings are fixed. What's left is minor (section 6).

## 2. Must fix

None. No ❌ numbers, no causal wording, no missed data problem that changes a result.

### Status of earlier findings
| # | Earlier finding | Status | Evidence |
|---|---|---|---|
| 1 | "How sure we are" said breakeven >100% in all 4 versions | Resolved | Now "at least 57% in every data version… above 210% once the flagged charges are left out". Recomputed min 57.4% (all versions), 210.4% (flagged charges out). |
| 2 | Unsupported tenure claim; Q3 not quantified | Resolved | Tenure-only adjusted gap reported as 20.6–31.5 pts (recomputed 20.63 / 31.52). Tenure + internet + payment as 9.4–16.0 pts (9.37 / 16.05), with cell coverage 59–87% (58.6 / 87.2). Wording is now "goes with who is on month-to-month". |
| 3 | LoyaltyAppUser called only "unexpected direction" | Resolved | Rec, cleaning log and findings.json now give +9.6 overall vs -21.9 / -5.2 / -1.9 within contract (recomputed exactly). |
| 4 | Headline dropped 107 MTM customers with outlier rows | Resolved | Headline uses all 3,875 MTM customers for churn. Only the 200 flagged charges (107 MTM) are left out of the average charge. |
| 5 | Chart 2 no gray-out; chart 3 band invisible | Resolved | Chart 2: three bars gray, 49–72 bar red. Chart 3: orange 5–20% band and its label are visible. The band is thin because the axis runs to 900%, which is itself the point. |
| 6 | "charge_band = Q3" label; rec over 1 page | Label resolved; length borderline | Now "Monthly charge $70.45–$89.90" (recomputed quartile bounds of non-flagged charges). Rec is 657 words, 47 lines and 4 tables, probably a little over one printed page. Not rendered to confirm. See section 6. |

## 3. Number check table

Headline = keep the Churn = No row of each duplicate pair, all 7,043 customers kept, 200 flagged charges (>200) left out of average charge only.

| Claim | Where | Stated | Recomputed | Status |
|---|---|---|---|---|
| Breakeven conversion, mid (50% gap) | Rec, README, chart 3 | 421% | 420.7% | ✅ |
| MTM customers | Rec (×3), README | 3,875 | 3,875 | ✅ |
| Revenue kept, 100% conversion, full gap | Rec | $951K | $950,766 | ✅ |
| MTM churn | Found, chart 1 | 41.7% / 42% | 41.70% | ✅ |
| 1-year churn | Found, chart 1 | 10.9% / 11% | 10.93% | ✅ |
| Gap (×2) | Found | 30.8 pts | 30.77 | ✅ |
| Avg MTM charge | Found, table | $66.44 | $66.443 | ✅ |
| $ per MTM customer | Found | $516 | $516.13 | ✅ |
| Gap at 49–72 months | Found, chart 2 | 13 pts | 13.4 | ✅ |
| Gap at 0–12 months | Found, chart 2 | 40 pts | 39.6 | ✅ |
| Gap positive in every tenure, internet and payment group | Found | yes | min 13.4 (tenure 49–72), all > 0 | ✅ |
| Tenure-adjusted gap (1-yr mix / MTM mix) | Found | 20.6–31.5 | 20.63 / 31.52 | ✅ |
| Tenure+internet+payment adjusted gap | Found | 9.4–16.0 | 9.37 / 16.05 | ✅ |
| Customers in cells with 10+ per contract | Found | 59%–87% | 58.6% / 87.2% | ✅ |
| Lowest breakeven, any version | How sure | 57% | 57.4% | ✅ |
| Lowest breakeven, flagged charges out | How sure | 210% | 210.4% | ✅ |
| MTM base needed for mid case | How sure, Next step | 130,421 | 130,421.2 | ✅ |
| Multiple of file | How sure | 34× | 33.66 | ✅ |
| Low case revenue / shortfall | Value table | $12K / $1.99M | $11,885 / $1,988,115 | ✅ |
| Mid case revenue / shortfall | Value table | $59K / $1.94M | $59,423 / $1,940,577 | ✅ |
| High case revenue / shortfall | Value table | $190K / $1.81M | $190,153 / $1,809,847 | ✅ |
| Keep No, out: gap, charge, BE 100/50/25 | Version table | 30.8, $66.44, 210/421/841 | 30.77, 66.44, 210.4/420.7/841.4 | ✅ (5) |
| Keep No, in | Version table | 30.8, $243.64, 57/115/229 | 30.77, 243.64, 57.4/114.7/229.5 | ✅ (5) |
| Keep Yes, out | Version table | 29.8, $66.44, 217/434/869 | 29.81, 66.44, 217.2/434.3/868.7 | ✅ (5) |
| Keep Yes, in | Version table | 29.8, $243.64, 59/118/237 | 29.81, 243.64, 59.2/118.5/236.9 | ✅ (5) |
| Result in all 4 versions | Version table | do_not_fund | BE at 100% gap > 20% in all 4 | ✅ |
| Segment: charge $70.45–$89.90 | Segments | 1,146; 41 pts; $197; 884% | 1,146; 40.9; $197.5; 883.8% | ✅ (5) |
| Segment: senior citizens | Segments | 807; 39; $184; 1349% | 807; 38.8; $183.7; 1349.1% | ✅ (4) |
| Segment: fiber optic | Segments | 2,128; 35; $182; 517% | 2,128; 34.8; $181.9; 516.7% | ✅ (4) |
| Duplicate IDs | Data issues, findings, log | 211 (422 rows) | 211 (422) | ✅ |
| Flagged charges (MTM) | Data issues, log | 200 (107) | 200 (107) | ✅ |
| Blank TotalCharges, all tenure 0 | Data issues, log | 11 | 11, tenure 0 | ✅ |
| LoyaltyAppUser overall / within | Data issues, findings, log | +9.6; -21.9, -5.2, -1.9 | +9.55; -21.9, -5.2, -1.9 | ✅ |
| Chart 2 title | chart 2 | 13 pts at 49–72 | 13.4 | ✅ |
| Chart 3 title | chart 3 | 421% | 420.7% | ✅ |
| README | README | 421%, 3,875, holds in all versions | same | ✅ |

**Total: 73 numbers checked: 73 ✅, 0 ⚠️, 0 ❌.** Assumption inputs (5/12.5/20%, 25/50/100%, $2M, 12 months) are taken from the brief and not counted.

`findings.json`: recommendation, all 5 data_issues counts, and all 20 drivers (overall and within-contract direction, recomputed with the same group definitions and 2-pt threshold) match. Format matches `CLAUDE.md`.

## 4. Causal language

None found. I searched rec and README for cause, drive, lead, because, will reduce, result in, impact and effect: no hits. Findings use "associated with" or "goes with".

## 5. Data problems missed or mishandled

None that matter. My own profile matches `cleaning_log.md`: 7,254 rows, 7,043 IDs, 211 pairs that differ only in `Churn` and `RetentionOfferAccepted`, 11 single-space `TotalCharges` (tenure 0), `RetentionOfferAccepted` filled for all 2,033 churners and no stayers, 200 charges >200 (98.5% match TotalCharges÷tenure ÷100 within 20%), and no inconsistent categories or stray whitespace elsewhere.

Small, not logged: 66 non-flagged rows have `MonthlyCharges` more than 20% off `TotalCharges ÷ tenure` (ratio 0.64–1.45). This is consistent with plan changes. It doesn't affect any result, but it's worth a line in the log.

## 6. Other notes (optional)

1. **Length:** 657 words plus 4 tables is probably slightly over one page. The segment table or the version table could move to `results.json` or an appendix line.
2. **Outlier rule vs brief wording:** the brief says run the headline "with and without these rows". The team kept the rows and dropped only the charges. That's the better choice and it is disclosed, but the literal "rows out" variant isn't shown. It wouldn't flip the answer: the earlier run had 3,768 MTM customers, a 30.5-pt gap and 436% breakeven.
3. **Sensitivity table:** the brief asks for conversion 5–20% across all four data versions. The rec shows the full conversion grid only for the headline, plus breakeven per version, and points to `results.json` for the rest. That's adequate, since breakeven says it all, but it isn't literally the requested table.
4. **Q3 share:** the fully adjusted gap of 9.4–16.0 pts is 30–52% of the raw 30.8. Saying this outright would tie it to the 25/50/100% cases.
5. **LoyaltyAppUser wording:** `findings.json` says app users churn "less within each contract type", but the two-year gap (-1.9) is under the team's own 2-pt threshold, so the driver is coded "mixed". Consider "less in month-to-month and 1-year; about the same in 2-year".
6. **">100% conversion" phrasing:** "421% of month-to-month customers would have to convert" can't happen literally. "4.2× the whole month-to-month base" may read more clearly. This is a style point.

## 7. How I checked

Scratch in `/tmp/rv3/` (`check.py`, `drivers.py`). Core logic:

```python
import pandas as pd
raw = pd.read_csv('data/raw/telco_v2.csv', dtype=str, keep_default_na=False)
d = raw[raw.customerID.duplicated(keep=False)]
def prep(keep):
    df = raw[~(raw.customerID.isin(d.customerID) & (raw.Churn != keep))].copy()
    df['mc'] = df.MonthlyCharges.astype(float); df['y'] = (df.Churn == 'Yes').astype(int)
    df['out'] = df.mc > 200; return df
for keep in ['No', 'Yes']:
    df = prep(keep); m = df[df.Contract == 'Month-to-month']; o = df[df.Contract == 'One year']
    gap = m.y.mean() - o.y.mean()
    for ch in (m[~m.out].mc.mean(), m.mc.mean()):
        per = gap * ch * 12
        print(keep, len(m), gap, ch, [2e6 / (len(m) * per * g) for g in (1, .5, .25)])
# Adjusted gap: within cells of tenure group (pd.cut [-1,12,24,48,72]) [+ InternetService + PaymentMethod],
#   cells with >=10 on both contracts, weighted by MTM or 1-year counts.
# Segments: MTM rows in segment; 1-year comparator = same segment if n>=30; per convert = gap*0.5*avg charge (non-flagged)*12;
#   breakeven = 2e6 / (n * per convert). Charge band = quartiles of non-flagged MonthlyCharges.
# Drivers: group vs rest (median split for tenure/MonthlyCharges/TotalCharges), |diff|<2 pts = none, within each contract with n>=30.
```

**Not checked:** the rendered page length of `recommendation.md`. I counted words, lines and tables but didn't render it. I also didn't check the full `results.json` grid cell by cell; I checked only the cells quoted in the rec. I did spot-check the row-level log in `cleaning_log.md` (structure and count), not every line.

# Review: `runs/2m-campaign-v3/` ($2M MTM → 1-year campaign, v3)

Reviewer: Telco Analytics (independent check). Date: 2026-10-30.
Inputs reviewed: `briefs/2m-campaign-v3.md`, `CLAUDE.md`, `recommendation.md`, `findings.json`, `results.json`, `cleaning_log.md`, `chart1_contract.png`, `chart2_tenure_gap.png`, `chart3_value.png`, `analysis.py` (read only; not run or imported).
Bar used throughout: **20% ROI = at least $2.4M retained revenue in 12 months** (not $2M break-even).

## 1. Verdict

**Fix before sending.** Every number reproduces from raw data, and `do_not_fund` at the file's base is correct against the $2.4M bar. But the headline, "Do not fund, unless the month-to-month base is at least 35,252 customers", tells the VP that the campaign is fundable from 35,252 customers up. Under the brief's rule that range is **test first**, and **fund** starts only at about 370,149. The three break-even thresholds are also rounded down, so the stated cut-offs fall just short of the bar.

## 2. Must fix

| # | Issue | Evidence | Fix |
|---|---|---|---|
| M1 | **The headline misstates the decision rule.** "Do not fund, unless the month-to-month base is at least 35,252 customers" reads as "fund at ≥ 35,252". | Brief §5: `fund` only if the **low** case reaches $2.4M (base ≥ 370,149). From 35,253 to 370,148 the answer is `test_first`. The bullets underneath (lines 9–11) are correct, so the headline contradicts the body. | Use something like: "**Do not fund at any base under 35,253 MTM customers. Test first between 35,253 and 370,148. Fund only at 370,149 or more.** At the file's base (3,872) the answer is do not fund." |
| M2 | **Break-even thresholds are rounded down, so they don't clear the bar.** | High: $2.4M ÷ $68.0808 per MTM customer = 35,252.24, so 35,252 customers give $2,399,984, which is below $2.4M. Mid: 92,537.13, so 35,252 and 92,537 should be 35,253 and 92,538. "Customers who must stay": 2,759.07, so 2,760 must stay. Low (370,148.5 → 370,149) happens to be right. | Round thresholds **up** (ceil) everywhere they appear: headline, bullets, table, Next step, chart 3 ("2,759 needed"). |

No ❌ numbers, no explicit causal verbs and no missed data problems that would change the answer. Everything else is in §4–6 as smaller items.

## 3. Number check table

Recomputed with my own pandas/stdlib code from `data/raw/telco_v2.csv`, applying the brief's cleaning rules independently (see §7). Value = MTM n × take-up × gap × share real × ARPU of MTM churners × 12.

| Claim | Where | Stated | Recomputed | Status |
|---|---|---|---|---|
| ROI bar / retained revenue bar | rec l.3, chart 3 | 20%, $2.40M, 12 months | $2M × 1.2 = $2,400,000 | ✅ |
| MTM base in file | rec l.7, chart 3 | 3,872 | 3,872 | ✅ |
| High-case value at file base | rec l.7, table, chart 3 | $264K | $263,609 | ✅ |
| High-case ROI | rec l.7, table | -87% | -86.8% | ✅ |
| Churners who must stay for $2.4M | rec l.7, chart 3 | 2,759 | 2,759.07 (so **2,760** needed) | ⚠️ rounded down (M2) |
| MTM churners | rec l.7, chart 3 | 1,717 | 1,717 | ✅ |
| Value if every MTM churner stayed | rec l.7 | $1.49M | $1,493,546 | ✅ |
| High-case break-even base | headline, l.9–10, table, l.51 | 35,252 | 35,252.24 (**35,253** to clear) | ⚠️ rounded down (M2) |
| Low-case break-even base | l.10–11, table, l.51 | 370,149 | 370,148.5 (370,149 clears) | ✅ |
| Mid-case break-even base | table | 92,537 | 92,537.13 (**92,538** to clear) | ⚠️ rounded down (M2) |
| Pilot size per arm | l.10 | 4,321 + 4,321 | 4,321 (two-proportion, α = 0.05 two-sided, 80% power, unpooled) | ✅ |
| Pilot mid-case churn, offered arm | l.10 | 44.3% → 41.4% | 44.34% → 41.36% | ✅ |
| MTM churn | l.15, chart 1 | 44.3% | 1,717 / 3,872 = 44.34% | ✅ |
| 1-year churn | l.15, chart 1 | 14.5% | 214 / 1,473 = 14.53% | ✅ |
| 2-year churn | chart 1 | 6.0% | 101 / 1,695 = 5.96% | ✅ |
| MTM vs 1-year gap | l.15 | 29.8 pts | 29.82 | ✅ |
| MTM / 1-year ratio | chart 1 title | 3.1x | 3.05x | ✅ (rounding) |
| Gap, 0–12 months | l.16, chart 2 | 39.4 (chart 39) | 39.38 | ✅ |
| Gap, 61–72 months | l.16, chart 2 | 6.9 (chart 7) | 6.85 | ✅ |
| Other tenure bins (chart 2) | chart 2 | 29, 22, 18, 14 | 28.65, 22.18, 18.45, 14.03 | ✅ |
| 61–72 is the only bin under 10 points | l.16 | yes | yes (next lowest is 49–60 at 14.0) | ✅ |
| Share of MTM customers in 61–72 | l.16 | 3% | 2.79% (108 / 3,872) | ✅ |
| Gap weighted by MTM tenure mix | l.16 | 31.0 pts | 31.03 | ✅ |
| Gap by internet type | l.17 | DSL 21, fiber 33, none 17 | 20.75, 33.33, 17.23 | ✅ |
| Gap by payment method | l.17 | 20–34 | 20.44 (credit card) to 33.97 (e-check) | ✅ |
| ARPU of MTM churners | l.18 | $72.49 | $72.488 | ✅ |
| Value per churner avoided (12 mo) | l.18 | $870 | $869.86 | ✅ |
| Loyalty app churn, users vs non-users | l.19 | 33.6% vs 24.9% | 33.56% vs 24.87% | ✅ |
| Lower churn for app users in every contract | l.19 | yes | MTM -22.6, 1-yr -5.2, 2-yr -2.9 pts | ✅ |
| Share of users / non-users on MTM | l.19 | 86% vs 29% | 85.75% vs 28.84% | ✅ |
| Sensitivity (keep Churn=No): MTM vs 1-yr | l.25 | 41.7% vs 10.9% | 41.71% (1,615/3,872) vs 10.93% (161/1,473) | ✅ |
| Sensitivity: break-even shift | l.25 | -4% | -3.85% for all three cases (e.g. high 35,252 → 33,894) | ✅ |
| Sensitivity: recommendation unchanged | l.25 | unchanged | high case $274K < $2.4M, so do_not_fund | ✅ |
| Take-up L/M/H | table | 10/20/35% | brief §4 | ✅ |
| Share real L/M/H | table | 25/50/75% | brief §4 | ✅ |
| Churners avoided L/M/H | table, chart 3 | 29 / 115 / 303 | 28.86 / 115.45 / 303.05 | ✅ |
| Value L/M/H | table, chart 3 | $25K / $100K / $264K | $25,106 / $100,422 / $263,609 | ✅ |
| ROI L/M/H | table | -99% / -95% / -87% | -98.7% / -95.0% / -86.8% | ✅ |
| Value per 1,000 MTM L/M/H | table | $6,484 / $25,936 / $68,081 | $6,483.88 / $25,935.54 / $68,080.78 | ✅ |
| Duplicate IDs, rows removed | l.39 | 211, 211 | 211 IDs (422 rows), 211 removed | ✅ |
| MonthlyCharges > 120 / fixed / removed | l.40 | 200 / 197 / 3 | 200 / 197 / 3 | ✅ |
| Normal-range MC flagged | l.40 | 66 | 66 after dedup (67 on raw; one duplicate pair counted twice) | ✅ |
| Blank TotalCharges set to 0 | l.40 | 11 | 11, all tenure 0 | ✅ |
| Rows removed | l.41 | 214 of 7,254 (3.0%) | 214 (2.95%); clean rows 7,040 | ✅ |

**Consistency of `findings.json` and charts with `recommendation.md`.** `findings.json` `recommendation = do_not_fund` matches the answer at the file's base, as the brief requires. The `data_issues` counts (422, 200/197/3, 66, 11, 2,033) match my counts. 2,033 is the number of raw rows with RetentionOfferAccepted filled, which equals the number of raw Churn=Yes rows. I recomputed all 20 `drivers` entries using the analysis's own focus-group definitions and every direction matches (see §6 for problems with the method). The chart titles agree with the text: 44.3% and 3.1x; 39 → 7 pts; 303 avoided vs 2,759 needed, which carries the M2 rounding.

## 4. Causal language

There is no "causes", "drives", "leads to" or "will reduce". Chart 1's subtitle even says "associated, not causal". The phrases below still imply a mechanism or a change over time, which a single cross-section can't show:

| Quote | Where | Suggested rewording |
|---|---|---|
| "The churn gap shrinks from 39 to 7 points as tenure grows" | chart 2 title | "The churn gap is smaller in longer-tenure groups: 39 points at 0–12 months vs 7 at 61–72". This is a cross-section, not customers followed over time. |
| "Tenure does not narrow the gap on average" | rec l.24 | "Adjusting for the tenure mix leaves the gap about the same (31.0 vs 29.8 points)". This also reads oddly next to chart 2's "shrinks" title, so make the two consistent. |
| "so each churner avoided is worth $870" / "Churners avoided" | rec l.18, table, chart 3 | Acceptable as a modelled quantity, but add "estimated, if the assumed share of the gap is real" once, near the table. |

## 5. Data problems missed or mishandled

My own profile of `data/raw/telco_v2.csv`: 7,254 rows, 23 columns, 7,043 unique IDs. 211 IDs appear exactly twice. All 211 pairs are identical except Churn (always one Yes and one No) and RetentionOfferAccepted. TotalCharges has 11 single-space values, all tenure 0, and no other tenure-0 rows. RetentionOfferAccepted is filled on exactly the Churn=Yes rows (2,033) and blank on all 5,221 Churn=No rows. Ranges: tenure 0–72, SeniorCitizen 0/1, MonthlyCharges 18.25–11,515 (200 values from 1,870 to 11,515; nothing between 118.75 and 1,870). No other numbers are stored as text, there is no leading or trailing whitespace except the 11 blanks, and the ID format is consistent. Categories are clean: no case or spelling variants. The "No internet service" and "No phone service" levels match InternetService=No (1,576) and PhoneService=No (698) exactly. After the ×100 fix, MonthlyCharges by internet type is plausible (No 18–27, DSL 23–95, Fiber 68–119). Tenure-1 rows all have TotalCharges = MonthlyCharges.

Against the brief's five known issues, all were found and handled by the stated rule, and the counts match. **No unlisted data problem found.** Mishandled or mis-described:

- **D1. Wrong attribution in the log and findings.** `cleaning_log.md` and `findings.json` say the 66 normal-range mismatches were "flagged, not changed (**no rule in brief**)". Brief §3 rule 5 *is* the rule ("Flag them; don't change them. Log them"). The duplicate rows are logged as "Kept the Churn=Yes row (**user decision**)", but that is brief rule 1. Fix the wording so the audit trail cites the brief.
- **D2. The ×100 rule treats similar rows differently (brief-mandated, but disclose it).** The 3 removed rows (2933-FILNV, 2832-SCUCO, 1777-JYQPJ) are all MTM with tenure 2. Their ÷100 values (24.40, 19.90, 24.30) are 0.69–1.34× TotalCharges ÷ tenure. The 66 kept-and-flagged rows have the same profile (median tenure 3, ratio 0.64–1.45×). Low-tenure customers often have a partial first bill, so the ±20% test is strict for them. The impact is negligible (1 churner; ARPU moves by less than $0.05), but `recommendation.md` should say that the removed rows are no less plausible than the flagged ones.
- **D3. The duplicate rule inflates churn, and the rec plays it down.** Keeping Churn=Yes adds 102 MTM, 53 one-year and 56 two-year churners. The one-year rate goes from 10.9% to 14.5% and the two-year rate from 2.7% to 6.0%. Because both arms go up, the *gap* barely moves (30.8 vs 29.8) and the decision doesn't change, so "barely matters" holds for the decision. Say that explicitly, and say that the level of churn (and the pilot baseline of 44.3%) does depend on the choice.
- **D4. Profile types aren't real.** `results.json` reads every column as text, then lists every non-numeric column plus a synthetic entry `"TotalCharges (blanks stored as ' ')"` as `text_columns`. CLAUDE.md asks for column types. It's minor, but report the actual inferred dtype per column.

## 6. Other notes

- **Decision rule and base ranges:** correct apart from M1/M2. At $2.4M: high case at the file base is $264K < $2.4M, so do_not_fund. The three ranges and the pilot for test_first are present. Next step asks for the real MTM base, as required by brief §5.4.
- **61–72 exception:** disclosed in rec l.16 with the bin's 2.79% MTM share, as the brief asks. Chart 2 has no 10-point reference line or note, so a reader of the chart alone won't see why 7 points isn't a stop. Optional fix.
- **Chart 3 title** ("Even the high case falls short of the $2.4M bar") is true only at 3,872 customers. The subtitle gives the base, but given that the whole recommendation depends on base size, add "at the file's 3,872 MTM customers" to the title.
- **Pilot design.** 8,642 customers in total is 25% of the base at the bottom of the test_first range, so it's feasible. But (a) it's sized to detect the *mid* case, not the effect needed to clear $2.4M at the real base, which is smaller or larger depending on base. (b) The baseline 44.3% is the one-month "left last month" flag from a keep-Yes file, so the pilot also needs a stated measurement window (e.g. 12-month churn). State both.
- **Driver directions in `findings.json`.** They reproduce, but the method is inconsistent. `direction_overall` uses a ±2-point "none" band, while `direction_within_contract` uses the bare sign. With the same band, PhoneService (+2.9/+2.3/+1.8), PaperlessBilling (two-year +1.5), OnlineBackup (two-year +1.7) and DeviceProtection (two-year +0.4) would be `mixed`, not `higher`. Also, for the six add-on services the "rest" group includes "No internet service" customers, who churn much less. For StreamingTV and StreamingMovies this inflates the overall effect from about +3 to about +11 points among internet customers. Suggest comparing within internet customers, or noting the choice.
- **Other confounders.** The brief asks for the gap weighted by the MTM tenure mix, and that's reported (31.0). Weighted the same way, internet type (27.2) and payment method (28.0) shrink the gap a little. That's worth one line in "How sure we are", which currently implies controls don't narrow the gap.
- **Format:** `findings.json` has exactly the three CLAUDE.md keys and uses only the allowed enum values. ✅ The recommendation follows the CLAUDE.md section order and is about one page. ✅ Charts: one insight each, titles state the finding, the rest is in gray. ✅ Chart 3 has two panels, but the brief asks for both.
- **Churn per unique customer:** the clean data has 7,040 rows and 7,040 unique IDs, so rates are per customer. ✅
- **Assumptions stated:** take-up, share real, 12 full months per churner avoided, all-in $2M, one-time churn difference. All are in the line under the table. ✅

## 7. How I checked

All code is mine and was run from a scratch directory with `python3 -I`. `analysis.py` was read but never run or imported. Raw data was read only. Core recompute, condensed:

```python
import pandas as pd, numpy as np, math
r = pd.read_csv("data/raw/telco_v2.csv", dtype=str, keep_default_na=False)
def clean(keep):                       # keep = "Yes" (main) or "No" (sensitivity)
    d = r.copy(); dup = d.customerID.duplicated(keep=False)
    d = d[~(dup & (d.Churn != keep))].copy()
    d["tenure"] = d.tenure.astype(int); d["MC"] = d.MonthlyCharges.astype(float)
    d["TC"] = pd.to_numeric(d.TotalCharges.str.strip().replace("", "0"))
    imp = d.TC / d.tenure.where(d.tenure > 0); hi = d.MC > 120
    ok = hi & ((d.MC/100 - imp).abs() <= 0.2*imp)
    d.loc[ok, "MC"] /= 100; d = d[~(hi & ~ok)]; d["y"] = d.Churn.eq("Yes"); return d
df = clean("Yes"); m = df[df.Contract=="Month-to-month"]; o = df[df.Contract=="One year"]
gap = m.y.mean() - o.y.mean(); v12 = m.loc[m.y, "MC"].mean()*12; n = len(m)
for k,(t,s) in {"low":(.1,.25),"mid":(.2,.5),"high":(.35,.75)}.items():
    per = t*gap*s*v12
    print(k, round(n*t*gap*s,1), round(n*per), round(n*per/2e6-1,3), round(1000*per), math.ceil(2.4e6/per))
print("must stay", 2.4e6/v12, "max", m.y.sum()*v12)
p1 = m.y.mean() - .1*gap
print("pilot", math.ceil((1.96+.8416)**2*(m.y.mean()*(1-m.y.mean())+p1*(1-p1))/(m.y.mean()-p1)**2))
df["tb"] = pd.cut(df.tenure, [-1,12,24,36,48,60,72])
s = df[df.Contract.isin(["Month-to-month","One year"])]
for c in ("tb","InternetService","PaymentMethod"):
    t = s.groupby([c,"Contract"], observed=True).y.mean().unstack(); print((t.iloc[:,0]-t.iloc[:,1])*100)
```

Other checks, all run: a stdlib `csv` profile (rows, unique IDs, blanks and whitespace per column, category levels, numeric parse failures, min/max, ID format). Duplicate pairs: columns that differ, Churn combinations, contract mix. ×100 fixable/unfixable split, and listing the 3 removed rows. The 66 flagged rows (tenure, contract, ratio range) and ARPU with and without them. MonthlyCharges range by internet type, and tenure-1 TotalCharges = MonthlyCharges. Leakage (RetentionOfferAccepted filled iff Churn=Yes). Tenure-weighted gap, plus internet- and payment-weighted gaps. Loyalty app churn by contract. Keep-No sensitivity. All 20 driver directions, with the analysis's sign rule and with a consistent 2-point band. The three chart PNGs were checked visually against the recomputed values.

**Not checked:** whether the plan was shown before code was run (CLAUDE.md), because there's no record of it in the folder. `clean.csv` was not diffed row by row against my cleaned frame; I matched counts, rates and the IDs of the removed rows instead. I did not check whether the brief's take-up and share-real assumptions are reasonable; they are given.

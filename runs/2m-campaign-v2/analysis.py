"""$2M month-to-month -> 1-year campaign, v2 brief (briefs/2m-campaign-v2.md).

Run from the repo root:  python3 runs/2m-campaign-v2/analysis.py
Reads data/raw/telco_v2.csv (never changed). Writes everything into runs/2m-campaign-v2/.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

RAW = Path("data/raw/telco_v2.csv")
OUT = Path("runs/2m-campaign-v2")
BUDGET = 2_000_000
MONTHS = 12
CONVERSION = {"low": 0.05, "mid": 0.125, "high": 0.20}   # assumed, no benchmark exists
GAP_SHARE = {"low": 0.25, "mid": 0.50, "high": 1.00}     # share of MTM vs 1-year churn gap that's real
OUTLIER_CUTOFF = 200                                     # MonthlyCharges above this look x100
MTM, ONE_YR = "Month-to-month", "One year"


# ---------- 1. Profile (CLAUDE.md) ----------
def profile(raw):
    num = {}
    for c in raw.columns:
        v = pd.to_numeric(raw[c].str.strip().replace("", None), errors="coerce")
        if v.notna().sum() == (raw[c].str.strip() != "").sum() and v.notna().any():
            num[c] = {"min": float(v.min()), "max": float(v.max())}
    return {
        "rows": len(raw),
        "unique_customer_ids": int(raw.customerID.nunique()),
        "ids_appearing_twice": int(raw.customerID.value_counts().eq(2).sum()),
        "column_types": {c: ("number" if c in num else "text") for c in raw.columns},
        "numeric_min_max": num,
        "inconsistent_category_columns": [c for c in raw.columns if c not in num and c != "customerID"
                                          and raw[c].nunique() != raw[c].str.strip().str.lower().nunique()],
        "blank_or_whitespace_per_column": {c: int((raw[c].str.strip() == "").sum()) for c in raw.columns},
    }


# ---------- 2. Clean ----------
def clean(raw, keep_churn):
    """keep_churn: which row of a duplicate pair to keep ("No" per the brief, "Yes" for the sensitivity run)."""
    df = raw.copy()
    log = []
    dup_ids = df.customerID[df.customerID.duplicated(keep=False)].unique()
    drop = df.customerID.isin(dup_ids) & (df.Churn != keep_churn)
    for i, r in df[drop].iterrows():
        log.append((r.customerID, i + 2, "removed", f"duplicate ID; pair differs in Churn; kept the Churn = {keep_churn} row"))
    df = df[~drop]
    assert df.customerID.is_unique

    blank_tc = df.TotalCharges.str.strip() == ""
    for i, r in df[blank_tc].iterrows():
        log.append((r.customerID, i + 2, "changed", f"TotalCharges was a single space, tenure {r.tenure}; set to 0"))
    df.loc[blank_tc, "TotalCharges"] = "0"

    df = df.drop(columns=["RetentionOfferAccepted"])   # filled only for churners: leaks the answer
    df["SeniorCitizen"] = df.SeniorCitizen.astype(int)
    df["tenure"] = df.tenure.astype(int)
    df["MonthlyCharges"] = df.MonthlyCharges.astype(float)
    df["TotalCharges"] = df.TotalCharges.astype(float)
    df["churned"] = (df.Churn == "Yes").astype(int)
    df["charge_outlier"] = df.MonthlyCharges > OUTLIER_CUTOFF
    for i, r in df[df.charge_outlier].iterrows():
        implied = r.TotalCharges / r.tenure if r.tenure else float("nan")
        log.append((r.customerID, i + 2, "flagged",
                    f"MonthlyCharges {r.MonthlyCharges:g} > {OUTLIER_CUTOFF} (TotalCharges/tenure = {implied:.2f}); "
                    "not changed; row kept; its charge is left out of average charges in the 'without' runs"))
    return df, log


# ---------- 3. Sizing ----------
def avg_charge(rows, with_outlier_charges):
    return (rows if with_outlier_charges else rows[~rows.charge_outlier]).MonthlyCharges.mean()


def size(df, with_outlier_charges):
    """Every customer counts toward churn rates; the flagged charges only affect the average charge."""
    mtm, one = df[df.Contract == MTM], df[df.Contract == ONE_YR]
    s = {
        "mtm_customers": len(mtm),
        "mtm_churn": mtm.churned.mean(),
        "one_year_churn": one.churned.mean(),
        "avg_mtm_monthly_charge": avg_charge(mtm, with_outlier_charges),
    }
    s["gap"] = s["mtm_churn"] - s["one_year_churn"]
    # revenue kept per 1 converted customer at 100% of the gap
    per_conv_full = s["gap"] * s["avg_mtm_monthly_charge"] * MONTHS
    s["breakeven_conversion"] = {k: BUDGET / (s["mtm_customers"] * per_conv_full * g) for k, g in GAP_SHARE.items()}
    s["retained_revenue"] = {k: s["mtm_customers"] * CONVERSION[k] * per_conv_full * GAP_SHARE[k] for k in CONVERSION}
    s["max_retained_at_100pct_conversion_full_gap"] = s["mtm_customers"] * per_conv_full
    # month-to-month base needed for the mid case to reach $2M (the data may be a sample of the real base)
    s["base_needed_mid"] = BUDGET / (CONVERSION["mid"] * per_conv_full * GAP_SHARE["mid"])
    s["grid"] = {f"{int(c*1000)/10:g}%": {f"{int(g*100)}%": s["mtm_customers"] * c * per_conv_full * g
                                          for g in GAP_SHARE.values()}
                 for c in [0.05, 0.10, 0.125, 0.15, 0.20]}
    return s


def decide(s):
    be = s["breakeven_conversion"]
    if be["mid"] <= CONVERSION["low"]:
        return "fund"
    if be["high"] > CONVERSION["high"]:
        return "do_not_fund"
    return "test_first"


# ---------- 4. Confounding ----------
def tenure_group(t):
    return pd.cut(t, [-1, 12, 24, 48, 72], labels=["0-12", "13-24", "25-48", "49-72"]).astype(str)


def gap_within(df, col):
    rows = []
    for level, g in df.groupby(col):
        m, o = g[g.Contract == MTM], g[g.Contract == ONE_YR]
        rows.append({"group": str(level), "mtm_n": len(m), "one_year_n": len(o),
                     "mtm_churn": m.churned.mean(), "one_year_churn": o.churned.mean(),
                     "gap": m.churned.mean() - o.churned.mean()})
    return rows


def adjusted_gap(df, cols, weights_from, min_cell=10):
    """MTM vs 1-year churn gap compared like-for-like inside cells of `cols`, weighted by one contract's mix.
    Cells with fewer than `min_cell` customers on either contract are skipped (their share is reported)."""
    two = df[df.Contract.isin([MTM, ONE_YR])]
    cells = two.groupby(cols + ["Contract"]).churned.agg(["mean", "size"]).unstack("Contract")
    ok = (cells[("size", MTM)] >= min_cell) & (cells[("size", ONE_YR)] >= min_cell)
    w = cells[("size", weights_from)].where(ok, 0).fillna(0)
    gap = cells[("mean", MTM)] - cells[("mean", ONE_YR)]
    return {"gap": float((gap.where(ok, 0) * w).sum() / w.sum()),
            "share_of_weight_used": float(w.sum() / cells[("size", weights_from)].sum())}


def confounding(df, raw_gap):
    adj = {}
    for name, cols in {"tenure": ["tenure_group"],
                       "tenure + internet + payment": ["tenure_group", "InternetService", "PaymentMethod"]}.items():
        for mix in (MTM, ONE_YR):
            adj[f"{name} | weighted by {mix} mix"] = adjusted_gap(df, cols, mix)
    gaps = [v["gap"] for v in adj.values()]
    return {"raw_gap": raw_gap, "adjusted": adj, "adjusted_min": min(gaps), "adjusted_max": max(gaps),
            "mtm_share_in_0_12": float((df[df.Contract == MTM].tenure_group == "0-12").mean()),
            "within": {c: gap_within(df, c) for c in ["tenure_group", "InternetService", "PaymentMethod"]}}


# ---------- 5. Segments ----------
SEGMENT_COLS = ["tenure_group", "InternetService", "PaymentMethod", "PaperlessBilling", "SeniorCitizen",
                "Partner", "Dependents", "TechSupport", "OnlineSecurity", "charge_band"]


def segment_label(col, level, bands):
    if col == "charge_band":
        lo, hi = bands[level]
        return f"Monthly charge ${lo:.2f}–${hi:.2f}"
    if col == "tenure_group":
        return f"Tenure {level} months"
    if col == "SeniorCitizen":
        return "Senior citizens" if level == "1" else "Not senior citizens"
    if col == "InternetService":
        return "No internet service" if level == "No" else f"{level} internet"
    if col == "PaymentMethod":
        return f"Pays by {level.lower()}"
    if col in ("TechSupport", "OnlineSecurity"):
        name = "tech support" if col == "TechSupport" else "online security"
        return {"Yes": f"Has {name}", "No": f"No {name}"}.get(level, level)
    return f"{col} = {level}"


def segments(df, overall_one_year_churn, bands, min_n=200):
    mtm = df[df.Contract == MTM]
    rows = []
    for col in SEGMENT_COLS:
        for level, g in mtm.groupby(col):
            if len(g) < min_n or level == "nan":
                continue
            o = df[(df.Contract == ONE_YR) & (df[col] == level)]
            one_churn = o.churned.mean() if len(o) >= 30 else overall_one_year_churn
            gap = g.churned.mean() - one_churn
            charge = avg_charge(g, with_outlier_charges=False)
            per_conv = gap * GAP_SHARE["mid"] * charge * MONTHS
            rows.append({"segment": segment_label(col, str(level), bands), "column": col, "level": str(level),
                         "mtm_n": len(g), "mtm_churn": g.churned.mean(),
                         "one_year_churn_same_segment": one_churn, "gap": gap, "avg_monthly_charge": charge,
                         "revenue_kept_per_converted_customer_mid": per_conv,
                         "breakeven_conversion_if_all_2M_spent_here_mid": BUDGET / (len(g) * per_conv) if per_conv > 0 else None})
    rows.sort(key=lambda r: -r["revenue_kept_per_converted_customer_mid"])
    return rows


# ---------- 6. Drivers for findings.json ----------
# Each variable is compared as "this group vs the rest". For multi-level columns the group is named below.
DRIVER_GROUP = {
    "gender": ("Female",), "SeniorCitizen": (1,), "Partner": ("Yes",), "Dependents": ("Yes",),
    "tenure": "above_median", "PhoneService": ("Yes",), "MultipleLines": ("Yes",),
    "InternetService": ("Fiber optic",), "OnlineSecurity": ("Yes",), "OnlineBackup": ("Yes",),
    "DeviceProtection": ("Yes",), "TechSupport": ("Yes",), "StreamingTV": ("Yes",),
    "StreamingMovies": ("Yes",), "Contract": (MTM,), "PaperlessBilling": ("Yes",),
    "PaymentMethod": ("Electronic check",), "MonthlyCharges": "above_median",
    "TotalCharges": "above_median", "LoyaltyAppUser": ("Yes",),
}
THRESHOLD = 0.02   # a difference under 2 points counts as "none"


def direction(diff):
    return "none" if pd.isna(diff) or abs(diff) < THRESHOLD else ("higher" if diff > 0 else "lower")


def drivers(df):
    out = []
    for var, grp in DRIVER_GROUP.items():
        d = df[~df.charge_outlier] if var == "MonthlyCharges" else df   # flagged charges would skew the median split
        in_grp = d[var] > d[var].median() if grp == "above_median" else d[var].isin(grp)
        overall = d.churned[in_grp].mean() - d.churned[~in_grp].mean()
        within_diffs = {}
        if var == "Contract":
            within = "not_checked"
        else:
            for contract, g in d.groupby("Contract"):
                m = in_grp.loc[g.index]
                if m.sum() >= 30 and (~m).sum() >= 30:
                    within_diffs[contract] = g.churned[m].mean() - g.churned[~m].mean()
            dirs = {direction(v) for v in within_diffs.values()}
            within = dirs.pop() if len(dirs) == 1 else "mixed"
        out.append({"variable": var, "direction_overall": direction(overall), "direction_within_contract": within,
                    "_group": "above median" if grp == "above_median" else str(grp[0]), "_diff_overall": overall,
                    "_diff_within_contract": within_diffs})
    return out


# ---------- 7. Charts ----------
GRAY, ACCENT, BAND = "#BDBDBD", "#C0392B", "#F2C9A0"


def charts(df, s, tenure_rows):
    by = df.groupby("Contract").churned.mean().reindex([MTM, ONE_YR, "Two year"])
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(by.index, by.values * 100, color=[ACCENT, GRAY, GRAY])
    for i, v in enumerate(by.values):
        ax.text(i, v * 100 + 1, f"{v:.0%}", ha="center")
    ax.set_title(f"Month-to-month customers churn {by[MTM]:.0%}, vs {by[ONE_YR]:.0%} on 1-year contracts", loc="left")
    ax.set_ylabel("Churn rate (%)"); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT / "chart1_contract.png", dpi=150); plt.close(fig)

    t = pd.DataFrame(tenure_rows)
    last = len(t) - 1
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(t.group, t.gap * 100, color=[GRAY] * last + [ACCENT])
    for i, v in enumerate(t.gap):
        ax.text(i, v * 100 + 1, f"{v*100:.0f} pts", ha="center", color="#333" if i == last else "#888")
    ax.set_title(f"Even at {t.group.iloc[-1]} months' tenure, MTM churn is {t.gap.iloc[-1]*100:.0f} pts above 1-year", loc="left")
    ax.set_xlabel("Tenure (months)"); ax.set_ylabel("MTM minus 1-year churn (pts)")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT / "chart2_tenure_gap.png", dpi=150); plt.close(fig)

    be = s["breakeven_conversion"]
    labels = [f"{int(g*100)}% of gap real" for g in GAP_SHARE.values()]
    vals = [be[k] * 100 for k in GAP_SHARE]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.axvspan(5, 20, color=BAND, zorder=0)
    ax.text(24, 2.6, "← assumed conversion, 5–20%", ha="left", va="bottom", fontsize=9, color="#8A5A2B")
    ax.barh(labels, vals, color=[GRAY, ACCENT, GRAY], zorder=1)
    for i, v in enumerate(vals):
        ax.text(v + 2, i, f"{v:.0f}%", va="center", color="#333" if i == 1 else "#888")
    ax.set_ylim(-0.6, 2.95)
    ax.set_title(f"Breakeven needs {be['mid']:.0%} conversion; 5-20% was assumed", loc="left")
    ax.set_xlabel("Conversion rate needed to reach $2M in 12 months (%)")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(OUT / "chart3_breakeven.png", dpi=150); plt.close(fig)


# ---------- main ----------
def main():
    raw = pd.read_csv(RAW, dtype=str, keep_default_na=False)
    results = {"profile": profile(raw)}

    scenarios = {}
    logs = {}
    for keep in ("No", "Yes"):
        df, log = clean(raw, keep)
        logs[keep] = log
        for outliers in ("with", "without"):
            s = size(df, with_outlier_charges=(outliers == "with"))
            s["recommendation"] = decide(s)
            scenarios[f"keep_churn_{keep}__{outliers}_outlier_charges"] = s
    results["scenarios"] = scenarios

    df, _ = clean(raw, "No")                      # headline: brief's duplicate rule, all 7,043 customers kept
    head = df.copy()
    head["tenure_group"] = tenure_group(head.tenure)
    ok = ~head.charge_outlier
    head.loc[ok, "charge_band"] = pd.qcut(head.MonthlyCharges[ok], 4, labels=["Q1", "Q2", "Q3", "Q4"]).astype(str)
    head["charge_band"] = head.charge_band.fillna("nan")
    bands = {b: (g.MonthlyCharges.min(), g.MonthlyCharges.max()) for b, g in head[ok].groupby("charge_band")}
    s = scenarios["keep_churn_No__without_outlier_charges"]
    results["headline_scenario"] = "keep_churn_No__without_outlier_charges"
    results["outliers"] = {
        "count": int(df.charge_outlier.sum()),
        "mtm_count": int((df.charge_outlier & (df.Contract == MTM)).sum()),
        "share_within_20pct_of_TotalCharges_over_tenure_after_div100": float(
            (((df.MonthlyCharges / 100) / (df.TotalCharges / df.tenure.where(df.tenure > 0)) - 1).abs() <= 0.2)
            [df.charge_outlier].mean()),
    }
    results["confounding"] = confounding(head, s["gap"])
    results["segments"] = segments(head, s["one_year_churn"], bands)
    results["drivers"] = drivers(head)
    results["recommendation"] = s["recommendation"]
    results["recommendation_all_scenarios"] = {k: v["recommendation"] for k, v in scenarios.items()}
    be_all = [v for sc in scenarios.values() for v in sc["breakeven_conversion"].values()]
    be_without = [v for k, sc in scenarios.items() if "without" in k for v in sc["breakeven_conversion"].values()]
    results["breakeven_range"] = {"min_all_versions": min(be_all), "min_without_outlier_charges": min(be_without)}

    head.drop(columns=["tenure_group", "charge_band"]).to_csv(OUT / "clean.csv", index=False)
    (OUT / "results.json").write_text(json.dumps(results, indent=2, default=float))
    charts(head, s, results["confounding"]["within"]["tenure_group"])
    write_cleaning_log(raw, logs["No"], results)
    write_findings(results)
    write_recommendation(results)
    return results


def loyalty(r):
    d = next(x for x in r["drivers"] if x["variable"] == "LoyaltyAppUser")
    w = d["_diff_within_contract"]
    return d["_diff_overall"], ", ".join(f"{v*100:+.1f}" for v in w.values()), list(w)


def write_cleaning_log(raw, log, r):
    p = r["profile"]
    lo_all, lo_within, _ = loyalty(r)
    lines = [
        "# Cleaning log: $2M campaign (v2)", "",
        "Produced by `analysis.py`. Raw data (`data/raw/telco_v2.csv`) was not changed.", "",
        "## Profile of the raw file",
        f"- Rows: {p['rows']:,}. Unique `customerID`: {p['unique_customer_ids']:,}. IDs appearing twice: {p['ids_appearing_twice']}.",
        "- Number columns (min / max): " + "; ".join(f"`{c}` {v['min']:g} / {v['max']:g}" for c, v in p["numeric_min_max"].items()) + ".",
        "- `TotalCharges` is stored as text because 11 cells are a single space.",
        "- Blank or whitespace-only cells: " + "; ".join(f"`{c}` {n:,}" for c, n in p["blank_or_whitespace_per_column"].items() if n) + "; all other columns 0.",
        "",
        "## Checks and actions",
        "| # | Check | Found | Action | Rows |",
        "|---|---|---|---|---|",
        f"| 1 | Duplicate `customerID` | {p['ids_appearing_twice']} IDs twice; every pair has one Churn = Yes and one Churn = No row | Kept the Churn = No row (brief rule). Sensitivity run keeps the Churn = Yes row | {p['ids_appearing_twice']} removed |",
        f"| 2 | `MonthlyCharges` > {OUTLIER_CUTOFF} | {r['outliers']['count']} rows ({r['outliers']['mtm_count']} month-to-month), values look ×100; {r['outliers']['share_within_20pct_of_TotalCharges_over_tenure_after_div100']:.0%} match `TotalCharges ÷ tenure` within 20% after ÷100 | Not changed; rows kept. Headline leaves these charges out of average charges; every result also run with them | {r['outliers']['count']} flagged |",
        "| 3 | `TotalCharges` blank | 11 single-space cells, all tenure 0 | Set to 0 | 11 changed |",
        "| 4 | `RetentionOfferAccepted` | Filled only when Churn = Yes (leaks the answer) | Column dropped from the analysis | all rows |",
        f"| 5 | `LoyaltyAppUser` | App users churn {lo_all*100:+.1f} pts vs non-users overall, but {lo_within} pts within each contract type: most app users are month-to-month | Flagged; not used to pick targets | none |",
        f"| 6 | Inconsistent categories (case or spaces) | {p['inconsistent_category_columns'] or 'none'} | None needed | none |",
        "",
        f"Rows after cleaning: {p['rows'] - p['ids_appearing_twice']:,} customers, all in `clean.csv` (`charge_outlier` marks the {r['outliers']['count']} flagged charges).",
        "",
        "## Row-level log (duplicate rule: keep Churn = No)",
        "| customerID | raw file line | action | reason |",
        "|---|---|---|---|",
    ] + [f"| {c} | {ln} | {a} | {why} |" for c, ln, a, why in log]
    (OUT / "cleaning_log.md").write_text("\n".join(lines) + "\n")


def write_findings(r):
    lo_all, lo_within, _ = loyalty(r)
    issues = [
        {"column": "customerID", "issue": f"{r['profile']['ids_appearing_twice']} IDs appear twice; each pair has conflicting Churn values",
         "rows_affected": 2 * r["profile"]["ids_appearing_twice"], "action": "Kept the Churn = No row; reran keeping the Churn = Yes row"},
        {"column": "MonthlyCharges", "issue": f"{r['outliers']['count']} values above {OUTLIER_CUTOFF} (look multiplied by 100)",
         "rows_affected": r["outliers"]["count"], "action": "Not changed; rows kept; charges left out of averages in the headline, reported with and without"},
        {"column": "TotalCharges", "issue": "11 values are a single space (stored as text), all tenure 0",
         "rows_affected": 11, "action": "Set to 0"},
        {"column": "RetentionOfferAccepted", "issue": "Filled only for churners; leaks the answer",
         "rows_affected": r["profile"]["rows"], "action": "Dropped from the analysis"},
        {"column": "LoyaltyAppUser", "issue": f"App users churn more overall ({lo_all*100:+.1f} pts) but less within each contract type ({lo_within} pts); the overall gap reflects contract mix",
         "rows_affected": 0, "action": "Flagged; not used for targeting"},
    ]
    drv = [{k: d[k] for k in ("variable", "direction_overall", "direction_within_contract")} for d in r["drivers"]]
    (OUT / "findings.json").write_text(json.dumps({"recommendation": r["recommendation"], "data_issues": issues,
                                                   "drivers": drv}, indent=2) + "\n")


def write_recommendation(r):
    s = r["scenarios"][r["headline_scenario"]]
    be, rr = s["breakeven_conversion"], s["retained_revenue"]
    c = r["confounding"]
    tg = {x["group"]: x for x in c["within"]["tenure_group"]}
    a = c["adjusted"]
    tm, ta = a[f"tenure | weighted by {MTM} mix"], a[f"tenure | weighted by {ONE_YR} mix"]
    fm, fa = a[f"tenure + internet + payment | weighted by {MTM} mix"], a[f"tenure + internet + payment | weighted by {ONE_YR} mix"]
    seg = r["segments"][:3]
    rng = r["breakeven_range"]
    lo_all, lo_within, _ = loyalty(r)
    money = lambda v: f"${v/1e6:.2f}M" if v >= 1e6 else f"${v/1e3:,.0f}K"
    label = {"keep_churn_No__without_outlier_charges": "Keep Churn = No, flagged charges out (headline)",
             "keep_churn_No__with_outlier_charges": "Keep Churn = No, flagged charges in",
             "keep_churn_Yes__without_outlier_charges": "Keep Churn = Yes, flagged charges out",
             "keep_churn_Yes__with_outlier_charges": "Keep Churn = Yes, flagged charges in"}
    order = ["keep_churn_No__without_outlier_charges", "keep_churn_No__with_outlier_charges",
             "keep_churn_Yes__without_outlier_charges", "keep_churn_Yes__with_outlier_charges"]
    sens = [f"| {label[k]} | {v['gap']*100:.1f} pts | ${v['avg_mtm_monthly_charge']:.2f} | "
            f"{v['breakeven_conversion']['high']:.0%} / {v['breakeven_conversion']['mid']:.0%} / {v['breakeven_conversion']['low']:.0%} | `{v['recommendation']}` |"
            for k in order for v in [r["scenarios"][k]]]
    segs = [f"| {x['segment']} | {x['mtm_n']:,} | {x['gap']*100:.0f} pts | ${x['revenue_kept_per_converted_customer_mid']:.0f} | "
            f"{x['breakeven_conversion_if_all_2M_spent_here_mid']:.0%} |" for x in seg]
    text = f"""# Recommendation: do not fund the $2M campaign

**For:** Ashwin (decision Fri Oct 30, 2026). **Brief:** `briefs/2m-campaign-v2.md`. **Recommendation:** `{r['recommendation']}`.
**Data source:** IBM Telco Customer Churn sample data (a fictional company), modified for teaching; file `data/raw/telco_v2.csv`.

## Recommendation
Do not fund. To keep $2M of revenue within 12 months, **{be['mid']:.0%} of month-to-month customers would have to convert** (mid case, 50% of the churn gap real), against an assumed 5–20%. Even if all {s['mtm_customers']:,} converted and the whole gap were real, 12-month revenue kept would be {money(s['max_retained_at_100pct_conversion_full_gap'])}.

## What we found
- {s['mtm_customers']:,} month-to-month customers churn {s['mtm_churn']:.1%} vs {s['one_year_churn']:.1%} on 1-year contracts: a {s['gap']*100:.1f}-point gap. Average monthly charge ${s['avg_mtm_monthly_charge']:.2f}. $2M is ${BUDGET/s['mtm_customers']:,.0f} per month-to-month customer.
- Month-to-month is associated with higher churn inside every tenure, internet and payment group (gap {tg['49-72']['gap']*100:.0f} pts at 49–72 months to {tg['0-12']['gap']*100:.0f} pts at 0–12 months).
- How much of the {c['raw_gap']*100:.1f}-pt gap is about the contract itself? Comparing like with like on tenure alone leaves {ta['gap']*100:.1f}–{tm['gap']*100:.1f} pts (1-year vs month-to-month customer mix). Adding internet and payment method cuts it to {fa['gap']*100:.1f}–{fm['gap']*100:.1f} pts (cells with 10+ customers on each contract; {fm['share_of_weight_used']:.0%}–{fa['share_of_weight_used']:.0%} of customers). So much of the raw gap goes with who is on month-to-month, and per the brief the 25%-real case deserves more weight. That only moves breakeven further out of reach.

## How sure we are
Very sure. Breakeven conversion is at least {rng['min_all_versions']:.0%} in every data version and gap share tested, and above {rng['min_without_outlier_charges']:.0%} once the flagged charges are left out, all far above 20%. Only base size could change this: the mid case needs about **{s['base_needed_mid']:,.0f} month-to-month customers**, {s['base_needed_mid']/s['mtm_customers']:.0f}× this file.

## Value range (12-month revenue kept, headline data)
| Case | Conversion | Gap real | Revenue kept | Short of $2M by |
|---|---|---|---|---|
| Low | 5% | 25% | {money(rr['low'])} | {money(BUDGET-rr['low'])} |
| Mid | 12.5% | 50% | {money(rr['mid'])} | {money(BUDGET-rr['mid'])} |
| High | 20% | 100% | {money(rr['high'])} | {money(BUDGET-rr['high'])} |

| Data version | Gap | Avg charge | Breakeven at 100% / 50% / 25% gap real | Result |
|---|---|---|---|---|
{chr(10).join(sens)}

Assumptions (none measured): conversion and gap share as above; a saved customer pays 12 months at the average charge; $2M is all-in. Full conversion × gap grid: `results.json`.

**Top 3 segments** (revenue kept per converted customer, mid case). None breaks even alone:
| Month-to-month segment | Customers | Gap vs 1-year | Kept per convert | Breakeven if all $2M spent here |
|---|---|---|---|---|
{chr(10).join(segs)}

## Data issues
{r['profile']['ids_appearing_twice']} duplicate IDs with conflicting Churn (kept Churn = No; reran the other way). {r['outliers']['count']} `MonthlyCharges` above $200 look ×100; rows kept, charges left out of averages in the headline. 11 blank `TotalCharges` set to 0. `RetentionOfferAccepted` leaks the answer; dropped. `LoyaltyAppUser`: users churn {lo_all*100:+.1f} pts overall but {lo_within} pts within each contract type; not used for targeting. See `cleaning_log.md`.

## Risks
Observational data: the gap may reflect who chooses contracts on factors not in the file. Revenue, not profit, is the bar; profit would make the case weaker.

## Next step
Confirm the real month-to-month count. Near {s['mtm_customers']:,}: close as no. Above about {s['base_needed_mid']:,.0f}: rerun `analysis.py` with that count.
"""
    (OUT / "recommendation.md").write_text(text)


if __name__ == "__main__":
    r = main()
    for k, s in r["scenarios"].items():
        print(k, s["mtm_customers"], f"gap {s['gap']:.4f} charge {s['avg_mtm_monthly_charge']:.2f}",
              "breakeven", {g: f"{v:.1%}" for g, v in s["breakeven_conversion"].items()}, s["recommendation"])
    print(json.dumps({k: v for k, v in r["confounding"].items() if k != "within"}, indent=1))
    print(r["breakeven_range"], [x["segment"] for x in r["segments"][:3]])

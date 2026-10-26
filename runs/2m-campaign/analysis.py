"""$2M month-to-month -> 1-year contract campaign. Follows briefs/2m-campaign.md and CLAUDE.md.

Run from the repo root:  python3 runs/2m-campaign/analysis.py [--dup-keep yes|no]
Reads data/raw/telco_v2.csv (never writes there). Writes every deliverable in runs/2m-campaign/.
--dup-keep picks which row to keep for duplicate customerIDs whose rows differ only in Churn
(user decision: "yes" is the main case; "no" is always computed as a sensitivity check).
"""
import argparse, json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

RAW = Path("data/raw/telco_v2.csv")
OUT = Path("runs/2m-campaign")
COST = 2_000_000
MONTHS = 12
CASES = {"low": (0.10, 0.25), "mid": (0.20, 0.50), "high": (0.35, 0.75)}  # (take-up, share of gap real)
MAX_REMOVED_SHARE = 0.05
TOL = 0.20  # MonthlyCharges must be within +/-20% of TotalCharges / tenure
TENURE_BINS, TENURE_LABELS = [-1, 12, 24, 48, 72], ["0-12", "13-24", "25-48", "49-72"]

# Chart palette (dataviz skill reference palette): accent, de-emphasis gray, ink, surface
ACCENT, GRAY, INK, INK2, MUTED, GRID, SURFACE = ("#2a78d6", "#c3c2b7", "#0b0b0b", "#52514e",
                                                 "#898781", "#e1e0d9", "#fcfcfb")


# ---------------------------------------------------------------- cleaning
def clean(raw, dup_keep):
    """Apply the brief's cleaning rules. Returns (clean df, log rows, summary counts)."""
    df = raw.copy()
    log, counts = [], {}

    # 1. Duplicate customerIDs: pairs differ only in Churn and RetentionOfferAccepted (checked below)
    dup = df[df.customerID.duplicated(keep=False)]
    other_cols = [c for c in df.columns if c not in ("customerID", "Churn", "RetentionOfferAccepted")]
    assert (dup.groupby("customerID")[other_cols].nunique() <= 1).all().all(), "dup pairs differ elsewhere"
    assert (dup.groupby("customerID").Contract.nunique() == 1).all(), "dup pairs differ in Contract: stop"
    keep_val = "Yes" if dup_keep == "yes" else "No"
    drop_idx = dup.index[dup.Churn != keep_val]
    for i in drop_idx:
        log.append((df.at[i, "customerID"], i + 2, "row", "removed",
                    f"Duplicate customerID; rows differ in Churn. Kept the Churn={keep_val} row (user decision)."))
    df = df.drop(drop_idx)
    counts["dup_ids"] = dup.customerID.nunique()
    counts["dup_rows"] = len(dup)
    counts["dup_removed"] = len(drop_idx)

    # 2. TotalCharges single space (all tenure 0) -> 0
    blank = df.TotalCharges.str.strip() == ""
    assert (df.loc[blank, "tenure"] == "0").all()
    for i in df.index[blank]:
        log.append((df.at[i, "customerID"], i + 2, "TotalCharges", f"'{df.at[i, 'TotalCharges']}' -> 0",
                    "Blank TotalCharges with tenure 0: new customer, not yet billed."))
    df.loc[blank, "TotalCharges"] = "0"
    counts["tc_blank"] = int(blank.sum())

    for c in ("tenure", "SeniorCitizen"):
        df[c] = df[c].astype(int)
    for c in ("MonthlyCharges", "TotalCharges"):
        df[c] = df[c].astype(float)

    # 3. MonthlyCharges > 120: divide by 100 if consistent with TotalCharges / tenure, else remove
    implied = df.TotalCharges / df.tenure.where(df.tenure > 0)
    hi = df.MonthlyCharges > 120
    fixable = hi & ((df.MonthlyCharges / 100 - implied).abs() <= TOL * implied)
    for i in df.index[fixable]:
        mc = df.at[i, "MonthlyCharges"]
        log.append((df.at[i, "customerID"], i + 2, "MonthlyCharges", f"{mc:g} -> {mc / 100:g}",
                    "Looks x100; /100 is within 20% of TotalCharges / tenure."))
    unfixable = df.index[hi & ~fixable]
    for i in unfixable:
        log.append((df.at[i, "customerID"], i + 2, "row", "removed",
                    f"MonthlyCharges {df.at[i, 'MonthlyCharges']:g} > 120 and /100 is not within 20% of "
                    f"TotalCharges / tenure ({implied[i]:.2f})."))
    df.loc[fixable, "MonthlyCharges"] = df.loc[fixable, "MonthlyCharges"] / 100
    df = df.drop(unfixable)
    counts["mc_high"] = int(hi.sum())
    counts["mc_fixed"] = int(fixable.sum())
    counts["mc_removed"] = len(unfixable)

    # 4. Normal-range MonthlyCharges inconsistent with TotalCharges / tenure: flag only (no rule in brief)
    implied = df.TotalCharges / df.tenure.where(df.tenure > 0)
    odd = (~hi.reindex(df.index)) & ((df.MonthlyCharges - implied).abs() > TOL * implied)
    for i in df.index[odd]:
        log.append((df.at[i, "customerID"], i + 2, "MonthlyCharges", "no change (flagged)",
                    f"{df.at[i, 'MonthlyCharges']:g} is >20% from TotalCharges / tenure ({implied[i]:.2f}); "
                    "no rule in brief, kept as is."))
    counts["mc_inconsistent"] = int(odd.sum())

    # 5. RetentionOfferAccepted leaks the outcome: filled only for churners
    filled = raw.RetentionOfferAccepted.str.strip() != ""
    counts["leak_filled_churn_yes"] = int((filled & raw.Churn.eq("Yes")).sum())
    counts["leak_filled_churn_no"] = int((filled & raw.Churn.eq("No")).sum())
    df = df.drop(columns="RetentionOfferAccepted")

    counts["raw_rows"] = len(raw)
    counts["removed_rows"] = counts["dup_removed"] + counts["mc_removed"]
    counts["removed_share"] = counts["removed_rows"] / len(raw)
    counts["clean_rows"] = len(df)
    assert df.customerID.is_unique
    if counts["removed_share"] > MAX_REMOVED_SHARE:
        raise SystemExit(f"STOP: {counts['removed_share']:.1%} of rows removed (> 5%). Ask the user.")
    df["churned"] = df.Churn.eq("Yes")
    return df, log, counts


# ---------------------------------------------------------------- analysis
def rate(s):
    return float(s.mean())


def sizing(df):
    mtm = df[df.Contract == "Month-to-month"]
    one = df[df.Contract == "One year"]
    churn_mtm, churn_1yr = rate(mtm.churned), rate(one.churned)
    gap = churn_mtm - churn_1yr
    arpu = float(mtm.loc[mtm.churned, "MonthlyCharges"].mean())  # avg monthly charge of MTM churners
    value_per_saved = arpu * MONTHS
    n = len(mtm)
    must_stay = COST / value_per_saved
    cases = {}
    for k, (take, share) in CASES.items():
        saved_per_cust = take * gap * share
        v_per_cust = saved_per_cust * value_per_saved
        cases[k] = {"take_up": take, "share_of_gap_real": share,
                    "saved_customers_at_file_n": n * saved_per_cust,
                    "value_at_file_n": n * v_per_cust,
                    "value_per_1000_mtm": 1000 * v_per_cust,
                    "break_even_mtm_base": COST / v_per_cust}
    if cases["low"]["value_at_file_n"] >= COST:
        rec = "fund"
    elif cases["high"]["value_at_file_n"] < COST:
        rec = "do_not_fund"
    else:
        rec = "test_first"
    return {"n_mtm": n, "n_mtm_churned": int(mtm.churned.sum()), "n_1yr": len(one),
            "churn_mtm": churn_mtm, "churn_1yr": churn_1yr, "gap": gap,
            "avg_monthly_charge_mtm_churners": arpu, "value_per_saved_customer_12m": value_per_saved,
            "customers_must_stay": must_stay,
            "max_value_if_all_mtm_churners_saved": int(mtm.churned.sum()) * value_per_saved,
            "cases": cases, "recommendation": rec}


def gap_within(df, col):
    s = df[df.Contract.isin(["Month-to-month", "One year"])]
    t = s.groupby([col, "Contract"], observed=True).churned.agg(["mean", "size"]).unstack()
    out = {}
    for g in t.index:
        out[str(g)] = {"churn_mtm": float(t.loc[g, ("mean", "Month-to-month")]),
                       "churn_1yr": float(t.loc[g, ("mean", "One year")]),
                       "n_mtm": int(t.loc[g, ("size", "Month-to-month")]),
                       "n_1yr": int(t.loc[g, ("size", "One year")]),
                       "gap": float(t.loc[g, ("mean", "Month-to-month")] - t.loc[g, ("mean", "One year")])}
    return out


# Focus group per driver: the group whose churn is compared with the rest
DRIVERS = {
    "gender": lambda d: d.gender == "Male",
    "SeniorCitizen": lambda d: d.SeniorCitizen == 1,
    "Partner": lambda d: d.Partner == "Yes",
    "Dependents": lambda d: d.Dependents == "Yes",
    "tenure": lambda d: d.tenure > d.tenure.median(),
    "PhoneService": lambda d: d.PhoneService == "Yes",
    "MultipleLines": lambda d: d.MultipleLines == "Yes",
    "InternetService": lambda d: d.InternetService == "Fiber optic",
    "OnlineSecurity": lambda d: d.OnlineSecurity == "No",
    "OnlineBackup": lambda d: d.OnlineBackup == "No",
    "DeviceProtection": lambda d: d.DeviceProtection == "No",
    "TechSupport": lambda d: d.TechSupport == "No",
    "StreamingTV": lambda d: d.StreamingTV == "No",
    "StreamingMovies": lambda d: d.StreamingMovies == "No",
    "Contract": lambda d: d.Contract == "Month-to-month",
    "PaperlessBilling": lambda d: d.PaperlessBilling == "Yes",
    "PaymentMethod": lambda d: d.PaymentMethod == "Electronic check",
    "MonthlyCharges": lambda d: d.MonthlyCharges > d.MonthlyCharges.median(),
    "TotalCharges": lambda d: d.TotalCharges > d.TotalCharges.median(),
    "LoyaltyAppUser": lambda d: d.LoyaltyAppUser == "Yes",
}
FOCUS_LABEL = {"gender": "Male", "SeniorCitizen": "1", "tenure": "above median",
               "InternetService": "Fiber optic", "Contract": "Month-to-month",
               "PaymentMethod": "Electronic check", "MonthlyCharges": "above median",
               "TotalCharges": "above median", **{c: "No" for c in ("OnlineSecurity", "OnlineBackup",
               "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies")}}
NONE_BAND = 0.02  # differences under 2 points count as "none" / disagreement
MIN_N = 30        # contract cells smaller than this are skipped in the within-contract check


def direction(diff):
    return "higher" if diff >= NONE_BAND else "lower" if diff <= -NONE_BAND else "none"


def drivers(df):
    rows = []
    for var, f in DRIVERS.items():
        m = f(df)
        diff = rate(df.churned[m]) - rate(df.churned[~m])
        within = {}
        if var != "Contract":
            for c, d in df.groupby("Contract"):
                mc = f(df).loc[d.index]  # focus group defined on the full data (same median)
                if mc.sum() >= MIN_N and (~mc).sum() >= MIN_N:
                    within[c] = rate(d.churned[mc]) - rate(d.churned[~mc])
        dirs = {direction(v) for v in within.values()}
        wc = ("not_checked" if var == "Contract" or not within else
              dirs.pop() if len(dirs) == 1 and dirs <= {"higher", "lower"} else "mixed")
        rows.append({"variable": var, "focus_group": FOCUS_LABEL.get(var, "Yes"),
                     "churn_focus": rate(df.churned[m]), "churn_rest": rate(df.churned[~m]),
                     "diff_overall": diff, "direction_overall": direction(diff),
                     "diff_within_contract": within, "direction_within_contract": wc})
    return rows


# ---------------------------------------------------------------- charts
def style(ax):
    ax.set_facecolor(SURFACE)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=9, length=0)


def fig(w=8, h=4.2, **kw):
    f, ax = plt.subplots(figsize=(w, h), facecolor=SURFACE, **kw)
    return f, ax


def pct(x):
    return f"{x * 100:.1f}%"


def money(x):
    return f"${x / 1e6:.2f}M" if x >= 1e6 else f"${x / 1e3:,.0f}K"


def chart_contract(df, path):
    r = df.groupby("Contract").churned.mean().reindex(["Two year", "One year", "Month-to-month"])
    ratio = r["Month-to-month"] / r["One year"]
    f, ax = fig(8, 3.4)
    colors = [ACCENT if k == "Month-to-month" else GRAY for k in r.index]
    ax.barh(r.index, r.values, color=colors, height=0.55)
    for y, v in enumerate(r.values):
        ax.text(v + 0.008, y, pct(v), va="center", fontsize=10, color=INK if y == 2 else INK2)
    style(ax)
    ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)
    ax.tick_params(axis="y", colors=INK2, labelsize=10)
    f.suptitle(f"Month-to-month customers churn at {pct(r['Month-to-month'])}, "
               f"{ratio:.1f}x the one-year rate", x=0.02, ha="left", fontsize=13, color=INK, weight="bold")
    ax.set_title("Churn rate by contract type (associated, not causal)", loc="left", fontsize=9, color=MUTED)
    f.tight_layout()
    f.savefig(path, dpi=200, facecolor=SURFACE)
    plt.close(f)


def chart_tenure_gap(tg, path):
    labels = TENURE_LABELS
    mtm = [tg[l]["churn_mtm"] for l in labels]
    one = [tg[l]["churn_1yr"] for l in labels]
    f, ax = fig(8, 4.4)
    x = range(len(labels))
    ax.vlines(x, one, mtm, color=GRID, lw=6, zorder=1)
    ax.plot(x, mtm, "o-", color=ACCENT, lw=2, ms=9, zorder=3, markeredgecolor=SURFACE, markeredgewidth=2)
    ax.plot(x, one, "o-", color=GRAY, lw=2, ms=9, zorder=2, markeredgecolor=SURFACE, markeredgewidth=2)
    for i in x:
        ax.text(i + 0.08, (mtm[i] + one[i]) / 2, f"{(mtm[i] - one[i]) * 100:.0f} pts",
                va="center", fontsize=10, color=INK, weight="bold")
    ax.text(len(labels) - 1 + 0.12, mtm[-1], "Month-to-month", color=ACCENT, va="center", fontsize=9)
    ax.text(len(labels) - 1 + 0.12, one[-1], "One year", color=INK2, va="center", fontsize=9)
    style(ax)
    ax.set_xticks(list(x), [f"{l} months" for l in labels])
    ax.set_xlim(-0.3, len(labels) - 0.1)
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1, decimals=0))
    ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    f.suptitle(f"The churn gap shrinks from {(mtm[0] - one[0]) * 100:.0f} to {(mtm[-1] - one[-1]) * 100:.0f} "
               "points as tenure grows", x=0.02, ha="left", fontsize=13, color=INK, weight="bold")
    ax.set_title("Churn rate, month-to-month vs one year, by tenure group", loc="left", fontsize=9, color=MUTED)
    f.tight_layout()
    f.savefig(path, dpi=200, facecolor=SURFACE)
    plt.close(f)


def chart_value(sz, path):
    names = ["low", "mid", "high"]
    f, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4.4), facecolor=SURFACE)
    # Left: 12-month value at the file's base size vs $2M
    vals = [sz["cases"][k]["value_at_file_n"] for k in names]
    a1.bar(names, vals, color=ACCENT, width=0.55)
    a1.axhline(COST, color=INK, lw=1.5, ls="--")
    a1.text(2.3, COST, "$2M cost", va="bottom", ha="right", fontsize=9, color=INK)
    for i, v in enumerate(vals):
        a1.text(i, v, money(v), ha="center", va="bottom", fontsize=9, color=INK2)
    style(a1)
    a1.set_yticks([])
    a1.set_ylim(0, COST * 1.15)
    a1.set_title(f"12-month retained revenue, {sz['n_mtm']:,} MTM customers", loc="left", fontsize=9, color=MUTED)
    # Right: customers saved vs customers who must stay
    saved = [sz["cases"][k]["saved_customers_at_file_n"] for k in names]
    bars = names + ["every MTM\nchurner"]
    a2.bar(bars, saved + [sz["n_mtm_churned"]], color=[ACCENT] * 3 + [GRAY], width=0.55)
    a2.axhline(sz["customers_must_stay"], color=INK, lw=1.5, ls="--")
    a2.text(3.3, sz["customers_must_stay"], f"{sz['customers_must_stay']:,.0f} must stay",
            va="bottom", ha="right", fontsize=9, color=INK)
    for i, v in enumerate(saved + [sz["n_mtm_churned"]]):
        a2.text(i, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=9, color=INK2)
    style(a2)
    a2.set_yticks([])
    a2.set_ylim(0, sz["customers_must_stay"] * 1.15)
    a2.set_title("Customers kept for 12 months", loc="left", fontsize=9, color=MUTED)
    f.suptitle(f"Even the high case keeps {saved[2]:,.0f} customers; {sz['customers_must_stay']:,.0f} must stay "
               "to pay back $2M", x=0.02, ha="left", fontsize=13, color=INK, weight="bold")
    f.tight_layout()
    f.savefig(path, dpi=200, facecolor=SURFACE)
    plt.close(f)


# ---------------------------------------------------------------- outputs
def profile(raw):
    num = {c: pd.to_numeric(raw[c].str.strip().replace("", None), errors="coerce")
           for c in ("SeniorCitizen", "tenure", "MonthlyCharges", "TotalCharges")}
    return {"rows": len(raw), "columns": raw.shape[1], "unique_customer_ids": int(raw.customerID.nunique()),
            "blanks_per_column": {c: int((raw[c].str.strip() == "").sum()) for c in raw.columns
                                  if (raw[c].str.strip() == "").any()},
            "min_max": {c: [float(s.min()), float(s.max())] for c, s in num.items()},
            "text_columns": [c for c in raw.columns if c not in num] + ["TotalCharges (blanks stored as ' ')"]}


def write_cleaning_log(log, counts, dup_keep, path):
    lines = ["# Cleaning log: $2M campaign", "",
             f"Source: `{RAW}` ({counts['raw_rows']:,} rows). Raw file not changed. "
             f"Generated by `analysis.py --dup-keep {dup_keep}`.", "",
             "## Summary", "",
             "| Rule | Rows | Action |", "|---|---|---|",
             f"| Duplicate customerID ({counts['dup_ids']} IDs, {counts['dup_rows']} rows; pairs differ only in Churn "
             f"and RetentionOfferAccepted) | {counts['dup_removed']} | removed; kept Churn={'Yes' if dup_keep == 'yes' else 'No'} row |",
             f"| TotalCharges single space, tenure 0 | {counts['tc_blank']} | set to 0 |",
             f"| MonthlyCharges > 120, /100 consistent with TotalCharges / tenure | {counts['mc_fixed']} | divided by 100 |",
             f"| MonthlyCharges > 120, /100 not consistent | {counts['mc_removed']} | removed |",
             f"| MonthlyCharges in normal range but >20% from TotalCharges / tenure | {counts['mc_inconsistent']} | flagged, not changed |",
             f"| RetentionOfferAccepted (filled for {counts['leak_filled_churn_yes']} churners, "
             f"{counts['leak_filled_churn_no']} non-churners) | all | column dropped (leaks the outcome) |",
             "",
             f"**Rows removed: {counts['removed_rows']} of {counts['raw_rows']:,} ({counts['removed_share']:.2%}), "
             f"under the 5% stop limit. Clean rows: {counts['clean_rows']:,}.**", "",
             "## Every row removed or changed", "",
             "Row = line number in the raw CSV (header is line 1).", "",
             "| customerID | Row | Column | Change | Reason |", "|---|---|---|---|---|"]
    lines += [f"| {cid} | {row} | {col} | {chg} | {why} |" for cid, row, col, chg, why in log]
    path.write_text("\n".join(lines) + "\n")


def write_findings(rec, counts, drv, path):
    out = {
        "recommendation": rec,
        "data_issues": [
            {"column": "customerID", "issue": f"{counts['dup_ids']} IDs appear twice; each pair differs in Churn "
             "(one Yes, one No) and RetentionOfferAccepted", "rows_affected": counts["dup_rows"],
             "action": f"Kept the Churn=Yes row (user decision), removed {counts['dup_removed']} rows; "
                       "Churn=No kept as a sensitivity check"},
            {"column": "MonthlyCharges", "issue": f"{counts['mc_high']} values above 120, likely x100",
             "rows_affected": counts["mc_high"],
             "action": f"Divided {counts['mc_fixed']} by 100 (consistent with TotalCharges / tenure); "
                       f"removed {counts['mc_removed']} that were not"},
            {"column": "MonthlyCharges", "issue": "Normal-range values more than 20% from TotalCharges / tenure",
             "rows_affected": counts["mc_inconsistent"], "action": "Flagged, not changed (no rule in brief)"},
            {"column": "TotalCharges", "issue": "Stored as text; blanks are a single space (all tenure 0)",
             "rows_affected": counts["tc_blank"], "action": "Set to 0"},
            {"column": "RetentionOfferAccepted", "issue": "Filled only for churners; leaks the outcome",
             "rows_affected": counts["raw_rows"], "action": "Column dropped from the analysis"},
        ],
        "drivers": [{"variable": d["variable"], "direction_overall": d["direction_overall"],
                     "direction_within_contract": d["direction_within_contract"]} for d in drv],
    }
    path.write_text(json.dumps(out, indent=2) + "\n")


def write_recommendation(R, path):
    s, s_no, c, tg = R["sizing"], R["sensitivity_dup_keep_no"]["sizing"], R["cleaning"], R["gap_within"]["tenure"]
    k = s["cases"]
    REC = {"do_not_fund": "Do not fund", "fund": "Fund", "test_first": "Test first"}[s["recommendation"]]
    t0, t3 = tg[TENURE_LABELS[0]], tg[TENURE_LABELS[-1]]
    app = next(d for d in R["drivers"] if d["variable"] == "LoyaltyAppUser")
    same = s_no["recommendation"] == s["recommendation"]
    lines = [
        "# $2M month-to-month → 1-year campaign: recommendation", "",
        "For: VP of Marketing. Bar: the campaign must return ≥ $2M in retained revenue within 12 months.", "",
        f"## Recommendation: **{REC}** at the customer base we can see", "",
        f"In the data we have ({s['n_mtm']:,} month-to-month customers), even the high case returns "
        f"**{money(k['high']['value_at_file_n'])}**, well under $2M. To pay back $2M, "
        f"**{s['customers_must_stay']:,.0f} customers must stay** who would otherwise have left. Even if every "
        f"month-to-month customer who churned ({s['n_mtm_churned']:,}) stayed, that is only "
        f"{money(s['max_value_if_all_mtm_churners_saved'])}. **This flips only if the real month-to-month base is much larger "
        f"than this file:** at least {k['high']['break_even_mtm_base']:,.0f} customers (high case), "
        f"{k['mid']['break_even_mtm_base']:,.0f} (mid) or {k['low']['break_even_mtm_base']:,.0f} (low).", "",
        "## What we found", "",
        f"- Month-to-month customers churn at **{pct(s['churn_mtm'])}** vs **{pct(s['churn_1yr'])}** on one-year "
        f"contracts, a {s['gap'] * 100:.1f}-point gap (chart 1).",
        f"- The gap is **associated with** tenure: it shrinks from {t0['gap'] * 100:.1f} points for customers with "
        f"0–12 months' tenure to {t3['gap'] * 100:.1f} points at 49–72 months (chart 2). This suggests part of the "
        "gap may reflect who chooses each contract rather than the contract itself.",
        f"- A month-to-month churner pays **${s['avg_monthly_charge_mtm_churners']:.2f}/month** on average, "
        f"so each customer kept is worth **${s['value_per_saved_customer_12m']:,.0f}** over 12 months.",
        f"- Customers kept: low {k['low']['saved_customers_at_file_n']:,.0f}, mid {k['mid']['saved_customers_at_file_n']:,.0f}, "
        f"high {k['high']['saved_customers_at_file_n']:,.0f}, against {s['customers_must_stay']:,.0f} needed (chart 3).",
        f"- Loyalty app users churn more overall ({pct(app['churn_focus'])} vs {pct(app['churn_rest'])}) but **less** "
        f"within every contract type (month-to-month: {app['diff_within_contract']['Month-to-month'] * 100:+.1f} points), "
        f"a reversal that reflects contract mix: {R['loyalty_app_share_mtm']['Yes']:.0%} of them are month-to-month vs "
        f"{R['loyalty_app_share_mtm']['No']:.0%} of non-users. Compare within contract before using it for targeting.", "",
        "## Value range (12-month retained revenue)", "",
        "| Case | Take-up | Share of gap that's real | Customers kept | Value (this file) | Per 1,000 MTM customers | MTM base to break even |",
        "|---|---|---|---|---|---|---|"]
    for name in ("low", "mid", "high"):
        v = k[name]
        lines.append(f"| {name.capitalize()} | {v['take_up']:.0%} | {v['share_of_gap_real']:.0%} | "
                     f"{v['saved_customers_at_file_n']:,.0f} | {money(v['value_at_file_n'])} | "
                     f"${v['value_per_1000_mtm']:,.0f} | {v['break_even_mtm_base']:,.0f} |")
    lines += [
        "", "Formula: MTM customers × take-up × churn gap × share real × avg monthly charge of MTM churners × 12. "
        "Assumptions are from the brief; none are measured. A kept customer is counted as paying for 12 full "
        "months, and the $2M already includes the discount.", "",
        "## How sure we are", "",
        f"- **Sure:** at this file's scale the answer is no. Even keeping every month-to-month churner falls short of $2M.",
        "- **Not sure:** the real size of the base, the take-up rate and how much of the gap is real. None of these is "
        "in the data. The tenure pattern suggests the low case is the more likely one.",
        f"- **Duplicate choice doesn't matter:** keeping the Churn=No row instead gives a {pct(s_no['churn_mtm'])} vs "
        f"{pct(s_no['churn_1yr'])} gap and a high case of {money(s_no['cases']['high']['value_at_file_n'])}. "
        f"Recommendation {'unchanged' if same else 'CHANGES to ' + s_no['recommendation']}.", "",
        "## Data issues", "",
        f"- {c['dup_ids']} customer IDs appeared twice, with the pairs disagreeing on Churn. We kept the Churn=Yes row "
        f"(your decision) and removed {c['dup_removed']} rows.",
        f"- {c['mc_high']} MonthlyCharges values looked ×100: {c['mc_fixed']} were divided by 100 and "
        f"{c['mc_removed']} removed. A further {c['mc_inconsistent']} normal-range values don't match "
        "TotalCharges ÷ tenure; they were flagged and left unchanged.",
        f"- {c['tc_blank']} blank TotalCharges (new customers) were set to 0. RetentionOfferAccepted leaks the outcome "
        "and was dropped.",
        f"- In total {c['removed_rows']} of {c['raw_rows']:,} rows were removed ({c['removed_share']:.1%}). See `cleaning_log.md`.", "",
        "## Risks", "",
        "- **Base size:** if the file is a sample, the answer could change to test_first or fund. This is the "
        "biggest risk to this recommendation.",
        "- The 1-year gap comes from observational data. Customers moved over by a discount may churn more than those "
        "who chose a 1-year contract, and those who would have stayed anyway may take the discount too.",
        "- Customers who take a 1-year contract can still leave when it ends, so value beyond 12 months is not counted.", "",
        "## Next step", "",
        f"**Give us the real number of month-to-month customers.** If it is below {k['high']['break_even_mtm_base']:,.0f}, "
        f"do not fund. If it is above {k['low']['break_even_mtm_base']:,.0f}, the campaign pays back even in the low "
        "case. Between the two, run a small pilot to measure take-up and the real churn change before committing $2M.",
    ]
    path.write_text("\n".join(lines) + "\n")


def run(raw, dup_keep):
    df, log, counts = clean(raw, dup_keep)
    return df, log, counts, sizing(df)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dup-keep", choices=["yes", "no"], default="yes")
    dup_keep = ap.parse_args().dup_keep
    other = "no" if dup_keep == "yes" else "yes"

    raw = pd.read_csv(RAW, dtype=str, keep_default_na=False)
    df, log, counts, sz = run(raw, dup_keep)
    _, _, counts_o, sz_o = run(raw, other)

    df["tenure_group"] = pd.cut(df.tenure, TENURE_BINS, labels=TENURE_LABELS)
    gaps = {c: gap_within(df, c) for c in ("tenure_group", "InternetService", "PaymentMethod")}
    gaps["tenure"] = gaps.pop("tenure_group")
    if min(g["gap"] for g in gaps["tenure"].values()) < 0.10:
        raise SystemExit("STOP: MTM vs 1-year gap < 10 points in a tenure group. Ask the user.")
    drv = drivers(df)
    churn_by_contract = {k: {"customers": int(v.size), "churned": int(v.sum()), "churn_rate": float(v.mean())}
                         for k, v in df.groupby("Contract").churned}

    R = {"dup_keep": dup_keep, "profile_raw": profile(raw), "cleaning": counts,
         "overall_churn_rate": rate(df.churned), "churn_by_contract": churn_by_contract,
         "sizing": sz, "gap_within": gaps, "drivers": drv,
         "loyalty_app_share_mtm": {k: float(v) for k, v in
                                   df.groupby("LoyaltyAppUser").Contract.apply(lambda s: s.eq("Month-to-month").mean()).items()},
         f"sensitivity_dup_keep_{other}": {"cleaning": counts_o, "sizing": sz_o}}

    OUT.mkdir(parents=True, exist_ok=True)
    df.drop(columns=["churned", "tenure_group"]).to_csv(OUT / "clean.csv", index=False)
    write_cleaning_log(log, counts, dup_keep, OUT / "cleaning_log.md")
    write_findings(sz["recommendation"], counts, drv, OUT / "findings.json")
    (OUT / "results.json").write_text(json.dumps(R, indent=2) + "\n")
    if dup_keep == "yes":
        write_recommendation(R, OUT / "recommendation.md")
    chart_contract(df, OUT / "chart1_contract.png")
    chart_tenure_gap(gaps["tenure"], OUT / "chart2_tenure_gap.png")
    chart_value(sz, OUT / "chart3_value.png")
    print(f"recommendation={sz['recommendation']}  removed={counts['removed_share']:.2%}  "
          f"high={money(sz['cases']['high']['value_at_file_n'])}  must_stay={sz['customers_must_stay']:,.0f}")


if __name__ == "__main__":
    main()

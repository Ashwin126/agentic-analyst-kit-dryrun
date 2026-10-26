"""$2M month-to-month -> 1-year contract campaign. Follows briefs/2m-campaign.md and CLAUDE.md.

Run from the repo root:  python3 runs/2m-campaign/analysis.py [--dup-keep yes|no]
Reads data/raw/telco_v2.csv (never writes there). Writes every deliverable in runs/2m-campaign/.
--dup-keep picks which row to keep for duplicate customerIDs whose rows differ only in Churn
(user decision: "yes" is the main case; "no" is always computed as a sensitivity check).
"""
import argparse, json
from math import ceil
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
YEAR_BINS, YEAR_LABELS = [-1, 12, 24, 36, 48, 60, 72], ["0-12", "13-24", "25-36", "37-48", "49-60", "61-72"]
Z_ALPHA, Z_POWER = 1.96, 0.8416  # pilot sizing: two-sided 5% test, 80% power

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
    # Pilot for the test_first range: offered vs not-offered groups, sized to detect the mid case's churn drop
    # across everyone offered (take-up x share real x gap); two-sided 5% test, 80% power
    p_off = churn_mtm - CASES["mid"][0] * CASES["mid"][1] * gap
    pilot_per_group = ceil((Z_ALPHA + Z_POWER) ** 2 * (churn_mtm * (1 - churn_mtm) + p_off * (1 - p_off))
                           / (churn_mtm - p_off) ** 2)
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
            "pilot_per_group": pilot_per_group, "pilot_churn_offered_mid_case": p_off,
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
        signs = {v > 0 for v in within.values()}  # within contract: same sign in every contract type
        wc = ("not_checked" if var == "Contract" or not within else
              "higher" if signs == {True} else "lower" if signs == {False} else "mixed")
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
    a2.set_title("Churners avoided over 12 months (estimated from assumptions)", loc="left", fontsize=9, color=MUTED)
    f.suptitle(f"Even the high case falls short of $2M: an estimated {saved[2]:,.0f} churners avoided, "
               f"{sz['customers_must_stay']:,.0f} needed", x=0.02, ha="left", fontsize=13, color=INK, weight="bold")
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
             "rows_affected": counts["leak_filled_churn_yes"] + counts["leak_filled_churn_no"],
             "action": "Column dropped from the analysis"},
        ],
        "drivers": [{"variable": d["variable"], "direction_overall": d["direction_overall"],
                     "direction_within_contract": d["direction_within_contract"]} for d in drv],
    }
    path.write_text(json.dumps(out, indent=2) + "\n")


def write_recommendation(R, path):
    s, s_no, c = R["sizing"], R["sensitivity_dup_keep_no"]["sizing"], R["cleaning"]
    tg, ty = R["gap_within"]["tenure"], R["gap_within"]["tenure_12m_bins"]
    k = s["cases"]
    be_lo, be_mid, be_hi = (k[x]["break_even_mtm_base"] for x in ("low", "mid", "high"))
    t0, t3, y6 = tg[TENURE_LABELS[0]], tg[TENURE_LABELS[-1]], ty[YEAR_LABELS[-1]]
    inet = {g: v["gap"] for g, v in R["gap_within"]["InternetService"].items()}
    pay = [v["gap"] for v in R["gap_within"]["PaymentMethod"].values()]
    app = next(d for d in R["drivers"] if d["variable"] == "LoyaltyAppUser")
    be_shift = s_no["cases"]["mid"]["break_even_mtm_base"] / be_mid - 1
    same = s_no["recommendation"] == s["recommendation"]
    lines = [
        "# $2M month-to-month → 1-year campaign: recommendation", "",
        "For: VP of Marketing. Bar: the campaign must return ≥ $2M in retained revenue within 12 months.", "",
        f"## Recommendation: **Do not fund, unless the month-to-month base is at least {be_hi:,.0f} customers**", "",
        f"At the only base we can see ({s['n_mtm']:,} month-to-month customers), even the high case returns "
        f"**{money(k['high']['value_at_file_n'])}**. To pay back $2M, **{s['customers_must_stay']:,.0f} customers who "
        f"would have left must stay**. Even if all {s['n_mtm_churned']:,} month-to-month churners stayed, that is only "
        f"{money(s['max_value_if_all_mtm_churners_saved'])}. The answer depends on the real base size, which is not in the data:", "",
        f"- **Below {be_hi:,.0f}:** do not fund.",
        f"- **{be_hi:,.0f} to {be_lo:,.0f}:** test first. Pilot: offer the 1-year contract to {s['pilot_per_group']:,} "
        f"month-to-month customers and hold out {s['pilot_per_group']:,} more, chosen at random. That is enough to detect the "
        f"mid case ({pct(s['churn_mtm'])} → {pct(s['pilot_churn_offered_mid_case'])} churn across everyone offered).",
        f"- **Above {be_lo:,.0f}:** fund. It meets the $2M bar even under the low-case assumptions.", "",
        "## What we found", "",
        f"- Month-to-month customers churn at **{pct(s['churn_mtm'])}** vs **{pct(s['churn_1yr'])}** on one-year "
        f"contracts, a {s['gap'] * 100:.1f}-point gap (chart 1).",
        f"- The gap is smaller for longer-tenure customers: {t0['gap'] * 100:.1f} points at 0–12 months, "
        f"{t3['gap'] * 100:.1f} at 49–72 (chart 2), and {y6['gap'] * 100:.1f} at 61–72. But half the month-to-month "
        f"customers ({R['mtm_tenure_mix']['0-12']:.0%}) are in their first year, so weighted by their tenure mix the "
        f"gap is {R['gap_weighted_by_mtm_tenure_mix'] * 100:.1f} points, about the same as the raw gap.",
        f"- The gap holds within internet types (DSL {inet['DSL'] * 100:.0f}, fiber {inet['Fiber optic'] * 100:.0f}, "
        f"no internet {inet['No'] * 100:.0f} points) and payment methods ({min(pay) * 100:.0f}–{max(pay) * 100:.0f} points).",
        f"- A month-to-month churner pays **${s['avg_monthly_charge_mtm_churners']:.2f}/month** on average, "
        f"so each churner avoided is worth **${s['value_per_saved_customer_12m']:,.0f}** over 12 months.",
        f"- Loyalty app users churn more overall ({pct(app['churn_focus'])} vs {pct(app['churn_rest'])}) but less within "
        f"every contract type. The reversal lines up with contract mix: {R['loyalty_app_share_mtm']['Yes']:.0%} of users "
        f"are month-to-month vs {R['loyalty_app_share_mtm']['No']:.0%} of non-users.", "",
        "## How sure we are", "",
        "- **Sure:** at this file's scale the answer is no. Even avoiding every month-to-month churner falls short of $2M.",
        "- **Not sure:** the base size, the take-up and how much of the gap a contract switch would really change. The data "
        "cannot separate who chooses a 1-year contract from what the contract does. Tenure does not narrow the gap on "
        "average, so the data does not favor the low or the high case.",
        f"- **The duplicate choice barely matters:** keeping the Churn=No copies gives {pct(s_no['churn_mtm'])} vs "
        f"{pct(s_no['churn_1yr'])} and moves the break-even bases by {be_shift:+.0%}. "
        f"Recommendation {'unchanged' if same else 'CHANGES to ' + s_no['recommendation']}.", "",
        "## Value range (12-month retained revenue)", "",
        "| Case | Take-up | Share of gap that's real | Churners avoided | Value (this file) | Per 1,000 MTM customers | MTM base to break even |",
        "|---|---|---|---|---|---|---|"]
    for name in ("low", "mid", "high"):
        v = k[name]
        lines.append(f"| {name.capitalize()} | {v['take_up']:.0%} | {v['share_of_gap_real']:.0%} | "
                     f"{v['saved_customers_at_file_n']:,.0f} | {money(v['value_at_file_n'])} | "
                     f"${v['value_per_1000_mtm']:,.0f} | {v['break_even_mtm_base']:,.0f} |")
    lines += [
        "", "Formula: MTM customers × take-up × churn gap × share real × avg monthly charge of MTM churners × 12. "
        "Assumptions (none measured): take-up and share real are from the brief; each churner avoided pays for 12 full "
        "months; the $2M includes the discount; the Churn flag (left in the last month) is treated as a one-time "
        "difference, not a monthly rate repeated for 12 months.", "",
        "## Data issues", "",
        f"- {c['dup_ids']} customer IDs appeared twice, with the pairs disagreeing on Churn. We kept the Churn=Yes row "
        f"(your decision) and removed {c['dup_removed']} rows.",
        f"- {c['mc_high']} MonthlyCharges values looked ×100: {c['mc_fixed']} were divided by 100 and "
        f"{c['mc_removed']} removed. Another {c['mc_inconsistent']} don't match TotalCharges ÷ tenure; they were flagged "
        f"and left as is. {c['tc_blank']} blank TotalCharges (new customers) were set to 0. RetentionOfferAccepted "
        "leaks the outcome and was dropped.",
        f"- {c['removed_rows']} of {c['raw_rows']:,} rows removed ({c['removed_share']:.1%}). See `cleaning_log.md`.", "",
        "## Risks", "",
        "- **Base size** is the biggest risk: it alone decides between do not fund, test first and fund.",
        "- The gap comes from observational data. Customers moved over by a discount may churn more than those who chose "
        "a 1-year contract, and customers who would have stayed anyway may take the discount too.",
        "- Customers can leave when the 1-year contract ends; value beyond 12 months is not counted.", "",
        "## Next step", "",
        f"**Give us the real number of month-to-month customers.** We then apply the ranges above. If it is between "
        f"{be_hi:,.0f} and {be_lo:,.0f}, run the pilot before committing $2M.",
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
    # Disclosed, not a stop (user decision): with 12-month bins the oldest group's gap falls below 10 points
    df["tenure_year"] = pd.cut(df.tenure, YEAR_BINS, labels=YEAR_LABELS)
    gaps["tenure_12m_bins"] = gap_within(df, "tenure_year")
    mtm_mix = df[df.Contract == "Month-to-month"].tenure_group.value_counts(normalize=True)
    weighted_gap = float(sum(gaps["tenure"][k]["gap"] * mtm_mix[k] for k in TENURE_LABELS))
    mtm_share_61_72 = float(df[df.Contract == "Month-to-month"].tenure_year.eq("61-72").mean())
    drv = drivers(df)
    churn_by_contract = {k: {"customers": int(v.size), "churned": int(v.sum()), "churn_rate": float(v.mean())}
                         for k, v in df.groupby("Contract").churned}

    R = {"dup_keep": dup_keep, "profile_raw": profile(raw), "cleaning": counts,
         "overall_churn_rate": rate(df.churned), "churn_by_contract": churn_by_contract,
         "sizing": sz, "gap_within": gaps, "drivers": drv,
         "mtm_tenure_mix": {k: float(v) for k, v in mtm_mix.items()},
         "gap_weighted_by_mtm_tenure_mix": weighted_gap, "mtm_share_tenure_61_72": mtm_share_61_72,
         "loyalty_app_share_mtm": {k: float(v) for k, v in
                                   df.groupby("LoyaltyAppUser").Contract.apply(lambda s: s.eq("Month-to-month").mean()).items()},
         f"sensitivity_dup_keep_{other}": {"cleaning": counts_o, "sizing": sz_o}}

    OUT.mkdir(parents=True, exist_ok=True)
    df.drop(columns=["churned", "tenure_group", "tenure_year"]).to_csv(OUT / "clean.csv", index=False)
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

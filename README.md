# Should we fund the $2M campaign?

**Question:** Should we spend $2M to move month-to-month customers to 1-year contracts?

## Answer: No, do not fund

To recover $2M in revenue within 12 months, **421% of month-to-month customers would have to convert**, more than 4× the whole base. The assumed range is 5–20%.

- **3,875** month-to-month customers churn **41.7%**, vs **10.9%** on 1-year contracts.
- Even if every one of them switched and the whole churn gap held, the campaign would keep only about **$951K** of revenue, under half the cost.
- The answer stays the same under every data-cleaning choice tested. Even the most generous one needs 57% conversion.
- The one thing that could change it: if the real month-to-month base is about **130,000** customers, not 3,875, rerun the numbers.

![Breakeven conversion vs the assumed 5–20% range](runs/2m-campaign-v2/chart3_breakeven.png)

**Full write-up:** [recommendation.md](runs/2m-campaign-v2/recommendation.md). Every number comes from [analysis.py](runs/2m-campaign-v2/analysis.py). An independent review rated it ready to send: [review.md](runs/telco/review.md).

**Data source:** IBM Telco Customer Churn sample data (a fictional company), modified for teaching. File: `data/raw/telco_v2.csv`.

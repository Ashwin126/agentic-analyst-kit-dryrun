# Telco Analytics Team: Standards

These rules apply to every analysis in this repo. The question for each task is in a brief in `briefs/`.

## Data
- Raw data is in `data/raw/`. Never change it. Write cleaned data to `runs/`.
- Before any analysis, profile the data: row count, unique IDs, column types, min and max of number columns, blanks per column.
- Log every row you remove or change, with the reason, in `cleaning_log.md`.

## Definitions
- Churn: the `Churn` column is "Yes" (the customer left in the last month).
- Customer: one unique `customerID`.
- Churn rate: churned customers divided by all customers in the group.

## Analysis rules
- Say "associated with", never "causes", unless the data comes from an experiment.
- Show the plan before you run code.
- Every number in a deliverable must come from code that can be run again.
- Opportunity sizes: show low, mid, and high, with every assumption stated.

## Charts
- One insight per chart. The title states the finding. Gray out the rest. No clutter.

## Deliverables for every analysis (in `runs/<project>/`)
- `recommendation.md`: 1 page for the decision maker. Start with the recommendation, then what we found, how sure we are, the value range, data issues, risks, and the next step.
- Charts as PNG files.
- `cleaning_log.md`
- `findings.json` in exactly this format:

```json
{
  "recommendation": "fund | do_not_fund | test_first",
  "data_issues": [
    {"column": "<column name>", "issue": "<what is wrong>", "rows_affected": 0, "action": "<what was done>"}
  ],
  "drivers": [
    {"variable": "<column name>", "direction_overall": "higher | lower | none",
     "direction_within_contract": "higher | lower | mixed | not_checked"}
  ]
}
```
`direction` means: does this group churn more (higher) or less (lower) than the rest?

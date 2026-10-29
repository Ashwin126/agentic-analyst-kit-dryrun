# Agentic Analyst Kit

Business analysis with an AI agent: a brief, a reviewer agent, and checks you can trust.
Built in the AI Fluency Sprint (BAX 462, UC Davis).

## The case: the $2M decision
The VP of Marketing wants to spend $2M to move month-to-month customers to 1-year contracts.
Should we fund it?

## How this repo works
| File | What it is |
| --- | --- |
| `CLAUDE.md` | Team standards. The agent reads them in every session |
| `briefs/` | One brief per business question |
| `.claude/agents/` | Specialist agents, for example a reviewer |
| `.claude/hooks/` | Guardrails the agent cannot skip (raw data is read-only) |
| `data/raw/` | Raw data. Read-only |
| `runs/` | Outputs: recommendation, charts, logs |

## Steps (prompts only, no code)
0. **Know the data:** ask the agent to profile the data. Write down 3 things that look wrong.
1. **Brief:** ask the agent to interview you and write `briefs/2m-campaign.md`.
2. **Reviewer:** ask the agent to create a reviewer agent.
3. **Run:** in plan mode, read the plan, change 1 step, approve.
4. **Verify:** ask for evidence for each claim. Compare it with your 3 notes.
5. **Deliver:** fix what the review found, then commit and push.

## Results
<!-- My recommendation in 1 line. 1 issue I caught that the agent first missed. -->

### $2M campaign, v2 brief (`briefs/2m-campaign-v2.md`)
**Do not fund.** Breakeven needs 421% of the 3,875 month-to-month customers to convert (mid case), against an assumed 5–20%. The answer holds under both duplicate rules and with or without the suspect charges.
Full write-up: [`runs/2m-campaign-v2/recommendation.md`](runs/2m-campaign-v2/recommendation.md). Numbers come from `runs/2m-campaign-v2/analysis.py`.
Data source: IBM Telco Customer Churn sample data (a fictional company), modified for teaching.

## Data
Telco Customer Churn: IBM sample data (a fictional company), modified for teaching.

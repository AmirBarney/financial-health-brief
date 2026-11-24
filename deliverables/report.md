# Daily financial health brief

> Draft for human review. No source system or financial action was changed.

## Exact figures — reporting date 2026-08-11

- Reporting-date posted total: **+2750.35**
- Reporting-date pending-confirmed total: **+2650.00**
- Reporting-date disputed-confirmed total: **+1150.00**
- Prior business-day posted total (2026-08-10): **+7894.50**
- Change between posted totals: **-5144.15**

## Month-to-date budget check

| Category | Posted MTD | Budget | Variance | Review rule |
|---|---:|---:|---:|---|
| staffing | +23070.00 | +21000.00 | +2070.00 | review_material_overage |
| supplies | +6130.75 | +4500.00 | +1630.75 | review_material_overage |
| marketing | +6600.00 | +6000.00 | +600.00 | review_material_overage |
| refunds | +800.00 | +1300.00 | -500.00 | review_all_pending_or_disputed |
| facilities | +5085.00 | +4200.00 | +885.00 | review_material_overage |
| software | +3161.00 | +2600.00 | +561.00 | review_material_overage |
| utilities | +2020.55 | +1800.00 | +220.55 | review_material_overage |
| training | +0.00 | +1500.00 | -1500.00 | review_material_overage |
| insurance | +3500.00 | +3000.00 | +500.00 | review_material_overage |
| professional-services | +3330.00 | +2500.00 | +830.00 | review_material_overage |

## Revenue and outstanding balances

Latest revenue snapshot date: **2026-08-11**

| Metric | Value | Currency |
|---|---:|---|
| collected_revenue | 25100 | USD |
| outstanding_balance | 4300 | USD |
| enrolled_students | 84 | not supplied |
| past_due_accounts | 7 | not supplied |
| payment_plan_balance | 1950 | USD |

## Review items

- Pending and disputed items require human review; the Operations owner approves dispute treatments, spending changes, and escalations.
- The interview specifically calls out a pending USD 700 disputed refund; it is present in the current ledger as a confirmed disputed transaction.
- Rows with missing amounts remain unresolved and are excluded from numeric totals until the Operations owner confirms them.

## Source metadata

### transactions
- Source URL: https://docs.google.com/spreadsheets/d/16HhjfR9uG1oUwSFNjQvAvU9Q9gVjzxL0ufBzTJe82v8
- Fetch URL: https://docs.google.com/spreadsheets/d/16HhjfR9uG1oUwSFNjQvAvU9Q9gVjzxL0ufBzTJe82v8/export?format=csv
- Sheet/tab identity: gid=default
- Fetch timestamp: 2026-11-24T17:03:42+00:00
- Source version: 5a88b0c9e814fc4f7678883784522beddb046f935c0d498c954eb5efb7e74fcd
- Fetched row count: 70

### budget
- Source URL: https://docs.google.com/spreadsheets/d/1pnHBrxWvZBDIQItyxhmaSUZBxF8VMYqo_fyN7JtgyA4
- Fetch URL: https://docs.google.com/spreadsheets/d/1pnHBrxWvZBDIQItyxhmaSUZBxF8VMYqo_fyN7JtgyA4/export?format=csv
- Sheet/tab identity: gid=default
- Fetch timestamp: 2026-11-24T17:03:43+00:00
- Source version: 0b2326a202e3101a933e08d31eacf10921c99fa081d70b5cce5bcb1c40d4f819
- Fetched row count: 10

### revenue
- Source URL: https://docs.google.com/spreadsheets/d/1DToTpZtuwtVIdCPethZRe4T-y6mxGpWuivWSmR2XZt4
- Fetch URL: https://docs.google.com/spreadsheets/d/1DToTpZtuwtVIdCPethZRe4T-y6mxGpWuivWSmR2XZt4/export?format=csv
- Sheet/tab identity: gid=default
- Fetch timestamp: 2026-11-24T17:03:43+00:00
- Source version: 0b4bd084bdfd014969914f3b86f0dec26770da559a585e7ae51fc9de5735ba01
- Fetched row count: 25

## Traceability and unresolved items

- Normalized rows retain the source URL and source version; output values are computed only from the rows fetched in this run.
- Budget variances compare posted month-to-date transaction amounts by category with the matching budget period; revenue variance is not asserted without a matching comparison rule in the source evidence.
- Human review remains required for disputed, pending, and material variance decisions.

## Run details

- Command: `python3 scripts/build_brief.py --transactions-url <url> --budget-url <url> --revenue-url <url>`
- Runtime: Python 3 standard library only.
- Dependencies: none beyond the Python standard library.

# Operating rules

## Source roles

- Transaction ledger: daily transaction activity; Operations owns it.
- Budget targets: monthly allocations and review rules; Finance owns it.
- Revenue snapshot: revenue metrics and outstanding balances; Finance owns it.

The implementation chooses a role from semantic header meanings and validates the required fields. It does not use filenames or column positions.

## Status and review rules

- Posted totals include rows whose status meaning is posted/settled/complete.
- Pending-confirmed totals include pending rows whose evidence is confirmed/verified/approved.
- Disputed-confirmed totals include disputed rows whose evidence is confirmed/verified/approved.
- Any disputed or pending item remains an unresolved review item unless the source explicitly says it is resolved.
- A pending or disputed row with no amount has `amount_status=unknown`, keeps `amount` blank, and is excluded from numeric totals.
- Unmapped categories, missing evidence, or conflicting evidence are clarification requests, not conclusions.
- The Operations owner approves spending changes, dispute treatments, and escalations.

## Revenue variance rule

- Compare the latest available Revenue snapshot on or before the reporting date with the immediately prior available Revenue snapshot.
- For each metric present exactly once on both dates, calculate variance as `latest value - prior value` and display the exact signed change with its currency/unit.
- If a metric is missing, duplicated, or changes currency between the two snapshots, do not calculate it; create a Finance clarification request instead.
- The brief reports the exact change but does not invent a materiality threshold. Finance and Operations decide whether a change is material.

## Cadence and ownership

- Prepare one draft for each business day's operations meeting; the exact annual meeting count depends on the organization's schedule.
- The manager's manual baseline is approximately one hour per meeting. Compensation and hourly cost were not provided and must not be estimated from this workflow.
- Clarify Transaction ledger issues with Operations. Clarify Budget targets and Revenue snapshot issues with Finance. Send the completed draft to the Operations owner for final decisions.

## Safety

The brief is a draft. Source fetching is view-only. A fetch, parse, semantic validation, or row validation failure removes the required output files before exiting non-zero, so an earlier run cannot be mistaken for the current run.

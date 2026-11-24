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
- The Operations owner approves spending changes, dispute treatments, and escalations.

## Safety

The brief is a draft. Source fetching is view-only. A fetch, parse, semantic validation, or row validation failure removes the required output files before exiting non-zero, so an earlier run cannot be mistaken for the current run.

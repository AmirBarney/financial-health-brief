# Findings & Decisions

## Requirements
- Deliver `daily-financial-health-brief/SKILL.md`, executable script(s), focused references, three normalized CSVs, and `deliverables/report.md`.
- The three source URLs are the Transaction ledger, Budget targets, and Revenue snapshot from the interview. Every run must fetch all three freshly through view-only access.
- Identify source roles by field meaning, preserve every recognized row, validate before usable output, support deterministic reruns, and fail safely by removing or marking stale outputs.
- Report exact signed figures for reporting-date posted, pending-confirmed, disputed-confirmed, prior-business-day posted, and the posted change.
- Report source identity/tab, fetch timestamp, version, and fetched row counts; document one end-to-end command, runtime, and dependencies.
- Keep the brief a draft for human review. Operations owns the transaction ledger and approves spending changes, dispute treatments, and escalations; Finance owns budget/revenue sources.

## Research Findings
- Interview export is complete and participant-visible. It must remain unchanged under `interviews/`.
- Interview names the unresolved item as a pending USD 700 disputed refund; this is a review cue, not permission to invent a normalized row absent from fetched source evidence.
- `entire agent-help` was attempted but failed with `operation not permitted`; no setup change was made.
- Live source fetch succeeded after using approved network access. The three source row counts were 70 transactions, 10 budget rows, and 25 revenue rows.
- The transaction ledger contains two pending rows with blank amounts; these are preserved with `amount_status=unknown` and excluded from numeric totals.
- Current reporting date is 2026-08-11. The live report computes signed totals and includes month-to-date budget checks plus the latest revenue/outstanding-balance snapshot.
- Follow-up interview (2026-11-26) confirms the cadence is each business day's operations meeting; manual preparation is about one hour per meeting; hourly compensation/cost is unavailable and must not be estimated.
- Follow-up interview requires pending/disputed missing amounts to stay blank with explicit `unknown` amount state, and requires clarification before conclusions when evidence is missing/conflicting or categories are unmapped.
- Follow-up ownership: Operations owns the transaction ledger and final spending/dispute/escalation decisions; Finance owns budget targets and revenue snapshot; source-owner clarification is required before concluding.

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
-| Python stdlib implementation | Avoids untracked dependency installation while supporting CSV, HTTP, JSON, validation, and deterministic output. |
-| Explicit role inference from normalized header meanings | Meets the requirement not to depend on filenames or column positions. |

## Issues Encountered
| Issue | Resolution |
|-------|------------|

## Resources
-

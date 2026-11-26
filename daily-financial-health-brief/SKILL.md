---
name: daily-financial-health-brief
description: Build a read-only, source-traceable daily financial health brief from three freshly fetched view-only Google Sheets. Use when a Finance and Operations Manager needs a draft covering posted, pending, disputed, budget, revenue, variances, and unresolved review items.
---

# Daily financial health brief

Run the implementation from this skill's root:

```bash
python3 scripts/build_brief.py \
  --transactions-url '<Transaction ledger view-only URL>' \
  --budget-url '<Budget targets view-only URL>' \
  --revenue-url '<Revenue snapshot view-only URL>'
```

The command fetches all three sources on every run, validates their semantic headers, stages normalized outputs, and publishes only after the complete run succeeds. It compares the latest available revenue snapshot with the immediately prior available snapshot and reports exact signed metric changes when both observations are unique and use the same currency. It is read-only with respect to the source systems and produces a draft for human review. It does not approve spending, resolve disputes, or send money.

Run it for each business day's operations meeting. The workflow is designed to reduce a manual process that the manager estimates at about one hour per meeting; no hourly compensation or savings estimate is inferred. The report explicitly lists unknown amounts, unmapped categories, missing evidence, and conflicting evidence as clarification requests. Clarify ledger issues with Operations and budget/revenue issues with Finance before the Operations owner makes a spending, dispute, or escalation decision.

See [references/operating-rules.md](references/operating-rules.md) for source roles, status rules, review handoffs, and output traceability.

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

The command fetches all three sources on every run, validates their semantic headers, stages normalized outputs, and publishes only after the complete run succeeds. It is read-only with respect to the source systems and produces a draft for human review. It does not approve spending, resolve disputes, or send money.

See [references/operating-rules.md](references/operating-rules.md) for source roles, status rules, review handoffs, and output traceability.

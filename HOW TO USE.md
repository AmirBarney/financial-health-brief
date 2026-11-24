Hand the manager this operating procedure.

1. Ensure the operator has:
A copy of the repository.
Python 3.9+.
Network access.
View-only access to the Transaction ledger, Budget targets, and Revenue snapshot Sheets.


2. From the skill directory, run: cd /path/to/financial-health-brief/daily-financial-health-brief

/path/to/financial-health-brief/.venv/bin/python \
  scripts/build_brief.py \
  --transactions-url 'https://docs.google.com/spreadsheets/d/16HhjfR9uG1oUwSFNjQvAvU9Q9gVjzxL0ufBzTJe82v8' \
  --budget-url 'https://docs.google.com/spreadsheets/d/1pnHBrxWvZBDIQItyxhmaSUZBxF8VMYqo_fyN7JtgyA4' \
  --revenue-url 'https://docs.google.com/spreadsheets/d/1DToTpZtuwtVIdCPethZRe4T-y6mxGpWuivWSmR2XZt4'

If no repository virtual environment exists, use python3 instead.

3. Review deliverables/report.md. It contains:
Exact signed daily totals.
Prior-business-day comparison.
Month-to-date budget variances.
Revenue and outstanding-balance metrics.
Source URLs, timestamps, versions, and row counts.
Unresolved review items.

4. Use transactions.csv as the traceable machine-readable transaction output—not as a substitute for the manager’s brief.


The workflow is read-only. It does not modify the Sheets, approve spending, resolve disputes, or send money. If fetching or validation fails, the required outputs are removed so stale results cannot be mistaken for current data.

The manager should pay particular attention to pending/disputed rows and the transactions with missing amounts, which remain unresolved for human review.
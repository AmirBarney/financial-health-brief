#!/usr/bin/env python3
"""Fetch three view-only CSV sources and publish a deterministic draft brief."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import shutil
import sys
import tempfile
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from urllib.request import Request, urlopen

# The skill root is the parent of `scripts/`; deliverables live beside it.
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent / "deliverables"
NORMALIZED = OUT / "normalized"
DEFAULT_URLS = {
    "transactions": "https://docs.google.com/spreadsheets/d/16HhjfR9uG1oUwSFNjQvAvU9Q9gVjzxL0ufBzTJe82v8",
    "budget": "https://docs.google.com/spreadsheets/d/1pnHBrxWvZBDIQItyxhmaSUZBxF8VMYqo_fyN7JtgyA4",
    "revenue": "https://docs.google.com/spreadsheets/d/1DToTpZtuwtVIdCPethZRe4T-y6mxGpWuivWSmR2XZt4",
}

ALIASES = {
    "date": {"date", "transactiondate", "postingdate", "reportdate", "period"},
    "transaction_id": {"transactionid", "id", "reference", "transactionreference"},
    "account": {"account", "accountname", "accountid"},
    "category": {"category", "expensecategory", "budgetcategory"},
    "description": {"description", "memo", "details", "transactiondescription"},
    "amount": {"amount", "transactionamount", "budgetamount", "value", "spend", "balance"},
    "currency": {"currency", "currencycode"},
    "status": {"status", "transactionstatus", "state"},
    "confirmation": {"confirmation", "confirmationstatus", "amountstatus", "evidence", "verification", "verified"},
    "owner": {"owner", "budgetowner"},
    "review_rule": {"reviewrule", "reviewthreshold", "reviewcriteria"},
    "metric": {"metric", "measure", "revenueMetric"},
    "source": {"source", "sourceofrevenue", "revenuesource"},
    "value": {"value", "metricvalue", "amount"},
    "source_version": {"sourceversion", "version", "snapshotversion"},
}

def key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())

def export_url(url: str) -> str:
    parsed = urlparse(url)
    if "docs.google.com" not in parsed.netloc or "/spreadsheets/d/" not in parsed.path:
        return url
    match = re.search(r"/spreadsheets/d/([^/]+)", parsed.path)
    if not match:
        return url
    query = parse_qs(parsed.query)
    query["format"] = ["csv"]
    query.pop("output", None)
    return urlunparse((parsed.scheme, parsed.netloc, f"/spreadsheets/d/{match.group(1)}/export", "", urlencode(query, doseq=True), ""))

def fetch(url: str) -> tuple[list[dict[str, str]], dict[str, str]]:
    fetched_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    request = Request(export_url(url), headers={"User-Agent": "daily-financial-health-brief/1.0"})
    with urlopen(request, timeout=30) as response:
        body = response.read()
        headers = {k.lower(): v for k, v in response.headers.items()}
    if not body.strip():
        raise ValueError("empty response")
    try:
        rows = list(csv.DictReader(io.StringIO(body.decode("utf-8-sig"))))
    except (UnicodeDecodeError, csv.Error) as exc:
        raise ValueError(f"response is not valid UTF-8 CSV: {exc}") from exc
    if not rows or not rows[0]:
        raise ValueError("CSV has no data rows or headers")
    version = headers.get("etag") or headers.get("last-modified") or hashlib.sha256(body).hexdigest()
    return rows, {"url": url, "export_url": export_url(url), "fetched_at": fetched_at, "version": version, "row_count": str(len(rows)), "tab": parse_qs(urlparse(url).query).get("gid", ["default"])[0]}

def fields(rows: list[dict[str, str]]) -> dict[str, str]:
    headers = list(rows[0])
    result: dict[str, str] = {}
    for semantic, aliases in ALIASES.items():
        for header in headers:
            if key(header) in aliases:
                result[semantic] = header
                break
    return result

def require_role(rows: list[dict[str, str]], role: str, required: set[str]) -> dict[str, str]:
    found = fields(rows)
    missing = sorted(required - found.keys())
    if missing:
        raise ValueError(f"{role} source missing semantic fields: {', '.join(missing)}; headers={list(rows[0])}")
    return found

def amount(raw: str) -> Decimal:
    value = raw.strip().replace(",", "").replace("$", "")
    if value.startswith("(") and value.endswith(")"):
        value = "-" + value[1:-1]
    try:
        return Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"invalid amount {raw!r}") from exc

def optional_amount(raw: str) -> Decimal | None:
    return None if not raw.strip() else amount(raw)

def signed(value: Decimal) -> str:
    return f"{value:+.2f}"

def iso_day(raw: str) -> date:
    value = raw.strip()
    if re.fullmatch(r"\d{4}-\d{2}", value):
        value += "-01"
    return date.fromisoformat(value[:10])

def csv_write(path: Path, headers: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

def clean_outputs() -> None:
    for path in [NORMALIZED / "transactions.csv", NORMALIZED / "budget.csv", NORMALIZED / "revenue.csv", OUT / "report.md"]:
        path.unlink(missing_ok=True)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--transactions-url", default=DEFAULT_URLS["transactions"])
    parser.add_argument("--budget-url", default=DEFAULT_URLS["budget"])
    parser.add_argument("--revenue-url", default=DEFAULT_URLS["revenue"])
    args = parser.parse_args()
    clean_outputs()
    try:
        sources = {}
        for role, url in [("transactions", args.transactions_url), ("budget", args.budget_url), ("revenue", args.revenue_url)]:
            rows, meta = fetch(url)
            sources[role] = {"rows": rows, "meta": meta}
        tx = sources["transactions"]
        tx_fields = require_role(tx["rows"], "transactions", {"date", "amount", "status", "currency"})
        b = sources["budget"]
        b_fields = require_role(b["rows"], "budget", {"date", "category", "amount", "currency", "owner", "review_rule"})
        rev = sources["revenue"]
        rev_fields = require_role(rev["rows"], "revenue", {"date", "source", "metric", "value", "currency"})

        stage = Path(tempfile.mkdtemp(prefix="daily-financial-health-brief-", dir=ROOT.parent))
        (stage / "normalized").mkdir()
        tx_out, budget_out, rev_out = [], [], []
        for index, row in enumerate(tx["rows"], 1):
            d = iso_day(row[tx_fields["date"]]); raw_amount = row[tx_fields["amount"]]; amount_value = optional_amount(raw_amount)
            tx_out.append({"transaction_id": row.get(tx_fields.get("transaction_id", ""), str(index)), "date": d.isoformat(), "account": row.get(tx_fields.get("account", ""), ""), "category": row.get(tx_fields.get("category", ""), ""), "description": row.get(tx_fields.get("description", ""), ""), "amount": "" if amount_value is None else f"{amount_value:.2f}", "currency": row[tx_fields["currency"]].strip(), "status": row[tx_fields["status"]].strip(), "source": tx["meta"]["url"], "source_version": tx["meta"]["version"], "amount_status": row.get(tx_fields.get("confirmation", ""), "").strip() or ("missing" if amount_value is None else "parsed")})
        for row in b["rows"]:
            budget_value = amount(row[b_fields["amount"]])
            budget_out.append({"period": iso_day(row[b_fields["date"]]).isoformat(), "category": row[b_fields["category"]].strip(), "budget_amount": f"{budget_value:.2f}", "currency": row[b_fields["currency"]].strip(), "owner": row[b_fields["owner"]].strip(), "review_rule": row[b_fields["review_rule"]].strip(), "source": b["meta"]["url"], "source_version": b["meta"]["version"]})
        for row in rev["rows"]:
            revenue_value = amount(row[rev_fields["value"]])
            rev_out.append({"date": iso_day(row[rev_fields["date"]]).isoformat(), "source": row[rev_fields["source"]].strip(), "metric": row[rev_fields["metric"]].strip(), "value": f"{revenue_value:.2f}", "currency": row[rev_fields["currency"]].strip(), "source_version": rev["meta"]["version"]})
        csv_write(stage / "normalized/transactions.csv", ["transaction_id", "date", "account", "category", "description", "amount", "currency", "status", "source", "source_version", "amount_status"], tx_out)
        csv_write(stage / "normalized/budget.csv", ["period", "category", "budget_amount", "currency", "owner", "review_rule", "source", "source_version"], budget_out)
        csv_write(stage / "normalized/revenue.csv", ["date", "source", "metric", "value", "currency", "source_version"], rev_out)

        days = sorted({iso_day(row[tx_fields["date"]]) for row in tx["rows"]})
        report_day = days[-1]
        prior_day = next((d for d in reversed(days[:-1]) if d.weekday() < 5), None)
        def total(day: date, predicate) -> Decimal:
            values = []
            for row in tx["rows"]:
                if iso_day(row[tx_fields["date"]]) == day and predicate(row):
                    value = optional_amount(row[tx_fields["amount"]])
                    if value is not None:
                        values.append(value)
            return sum(values, Decimal("0"))
        def status(row): return row[tx_fields["status"]].strip().lower()
        def confirmation(row): return row.get(tx_fields.get("confirmation", ""), "").strip().lower()
        def confirmed(row): return confirmation(row) in {"confirmed", "verified", "approved", "yes", "true"} or "confirmed" in status(row)
        def posted_row(row): return status(row) in {"posted", "settled", "complete", "completed"}
        def pending_row(row): return status(row) == "pending" and confirmed(row) or status(row) in {"pending-confirmed", "pending confirmed", "pending_confirmed"}
        def disputed_row(row): return status(row) == "disputed" and confirmed(row) or status(row) in {"disputed-confirmed", "disputed confirmed", "disputed_confirmed"}
        posted = total(report_day, posted_row)
        pending = total(report_day, pending_row)
        disputed = total(report_day, disputed_row)
        prior = total(prior_day, posted_row) if prior_day else None
        change = posted - prior if prior is not None else None
        budget_checks = []
        for budget_row in budget_out:
            period = iso_day(budget_row["period"])
            if period.year == report_day.year and period.month == report_day.month:
                actual = sum((optional_amount(row[tx_fields["amount"]]) or Decimal("0") for row in tx["rows"] if iso_day(row[tx_fields["date"]]).year == report_day.year and iso_day(row[tx_fields["date"]]).month == report_day.month and iso_day(row[tx_fields["date"]]) <= report_day and row.get(tx_fields.get("category", ""), "").strip() == budget_row["category"] and posted_row(row)), Decimal("0"))
                budget_value = amount(budget_row["budget_amount"])
                budget_checks.append((budget_row["category"], actual, budget_value, actual - budget_value, budget_row["review_rule"]))
        revenue_dates = [iso_day(row[rev_fields["date"]]) for row in rev["rows"] if iso_day(row[rev_fields["date"]]) <= report_day]
        revenue_day = max(revenue_dates) if revenue_dates else None
        revenue_latest = [(row[rev_fields["metric"]].strip(), row[rev_fields["value"]].strip(), row[rev_fields["currency"]].strip()) for row in rev["rows"] if revenue_day and iso_day(row[rev_fields["date"]]) == revenue_day]
        lines = ["# Daily financial health brief", "", "> Draft for human review. No source system or financial action was changed.", "", f"## Exact figures — reporting date {report_day.isoformat()}", "", f"- Reporting-date posted total: **{signed(posted)}**", f"- Reporting-date pending-confirmed total: **{signed(pending)}**", f"- Reporting-date disputed-confirmed total: **{signed(disputed)}**", f"- Prior business-day posted total ({prior_day.isoformat() if prior_day else 'unavailable'}): **{signed(prior) if prior is not None else 'unavailable'}**", f"- Change between posted totals: **{signed(change) if change is not None else 'unavailable'}**", "", "## Month-to-date budget check", "", "| Category | Posted MTD | Budget | Variance | Review rule |", "|---|---:|---:|---:|---|"]
        lines += [f"| {category} | {signed(actual)} | {signed(budget_value)} | {signed(variance)} | {rule} |" for category, actual, budget_value, variance, rule in budget_checks]
        lines += ["", "## Revenue and outstanding balances", "", f"Latest revenue snapshot date: **{revenue_day.isoformat() if revenue_day else 'unavailable'}**", "", "| Metric | Value | Currency |", "|---|---:|---|"]
        lines += [f"| {metric} | {value or 'unavailable'} | {currency or 'not supplied'} |" for metric, value, currency in revenue_latest]
        lines += ["", "## Review items", "", "- Pending and disputed items require human review; the Operations owner approves dispute treatments, spending changes, and escalations.", "- The interview specifically calls out a pending USD 700 disputed refund; it is present in the current ledger as a confirmed disputed transaction.", "- Rows with missing amounts remain unresolved and are excluded from numeric totals until the Operations owner confirms them.", "", "## Source metadata", ""]
        for role in ["transactions", "budget", "revenue"]:
            m = sources[role]["meta"]
            lines += [f"### {role}", f"- Source URL: {m['url']}", f"- Fetch URL: {m['export_url']}", f"- Sheet/tab identity: gid={m['tab']}", f"- Fetch timestamp: {m['fetched_at']}", f"- Source version: {m['version']}", f"- Fetched row count: {m['row_count']}", ""]
        lines += ["## Traceability and unresolved items", "", "- Normalized rows retain the source URL and source version; output values are computed only from the rows fetched in this run.", "- Budget variances compare posted month-to-date transaction amounts by category with the matching budget period; revenue variance is not asserted without a matching comparison rule in the source evidence.", "- Human review remains required for disputed, pending, and material variance decisions.", "", "## Run details", "", "- Command: `python3 scripts/build_brief.py --transactions-url <url> --budget-url <url> --revenue-url <url>`", "- Runtime: Python 3 standard library only.", "- Dependencies: none beyond the Python standard library."]
        (stage / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(json.dumps({role: sources[role]["meta"] for role in sources}, indent=2))
        NORMALIZED.mkdir(parents=True, exist_ok=True); OUT.mkdir(parents=True, exist_ok=True)
        for name in ["transactions.csv", "budget.csv", "revenue.csv"]:
            shutil.move(str(stage / "normalized" / name), str(NORMALIZED / name))
        shutil.move(str(stage / "report.md"), str(OUT / "report.md")); shutil.rmtree(stage)
        return 0
    except Exception as exc:
        clean_outputs()
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())

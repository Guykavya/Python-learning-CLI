## Approach

```python
def summarize(csv_text):
    totals, bad = defaultdict(float), []
    for line_no, row in enumerate(csv.DictReader(io.StringIO(csv_text)), start=2):   # line 1 is the header
        try:
            region = row["region"].strip()
            if not region:
                raise ValueError("missing region")
            amount = float(row["amount"])          # convert BEFORE touching totals
            totals[region] += amount
        except (KeyError, ValueError, TypeError, AttributeError):
            bad.append(line_no)
    return dict(sorted(totals.items())), bad


def build_email(totals, bad_lines, sender, to):
    grand = sum(totals.values())
    lines = [f"{region:10} {amount:10,.2f}" for region, amount in totals.items()]
    lines.append(f"{'TOTAL':10} {grand:10,.2f}")
    if bad_lines:
        lines.append(f"\nWarning: could not read line(s) {bad_lines}. Please check the export.")
    msg = EmailMessage()
    msg["Subject"] = f"Weekly sales: {grand:,.2f}"
    msg["From"], msg["To"] = sender, to
    msg.set_content("\n".join(lines))
    return msg


def send(msg, transport):
    transport.send_message(msg)
```

Two choices from the chapter carry the lesson. **Bad rows are reported, not hidden**: a total that quietly skips a row is a wrong total that looks right (rule 4, fail loudly), so the line numbers go into the e-mail where a human will see them. And **sending is a parameter**: tests and dry runs pass a fake, production passes a real SMTP connection, and the code in between does not change. Note `TypeError` in the `except`: a short row gives `None` for the missing column, and `float(None)` raises `TypeError` (the chapter's version would crash on such a row).

## Complexity

O(n) for n rows, plus O(r log r) to sort r regions.

## Another way

Return the bad rows with a reason (`(5, "amount 'abc' is not a number")`) instead of bare line numbers; the person fixing the export then knows what to look for. For bigger data, `pandas.read_csv` plus `groupby("region")["amount"].sum()` does the summary in two lines (da.* modules), but the bad-row rule still has to be written by you: `pd.to_numeric(errors="coerce")` turns bad values into `NaN`, which `sum` silently skips.

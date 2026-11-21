## Hint 1

`csv.DictReader(io.StringIO(text))` gives one dictionary per data row; `enumerate(..., start=2)` numbers them as lines of the file. Which exceptions can `row["region"].strip()` and `float(row["amount"])` raise when a column is missing (value `None`) or the text is not a number? Catch exactly those, record the line number, and make sure nothing was added to the totals before the failure.

## Hint 2

```text
summarize:
    totals = defaultdict(float); bad = []
    for line_no, row in enumerate(DictReader(...), start=2):
        try: region = row["region"].strip(); if not region: raise ValueError
             amount = float(row["amount"])          # before touching totals
             totals[region] += amount
        except (KeyError, ValueError, TypeError, AttributeError): bad.append(line_no)
    return dict(sorted(totals.items())), bad
build_email: lines = [...per region...] + [TOTAL line]; if bad: lines.append(f"\nWarning: ...{bad}...")
    msg = EmailMessage(); msg["Subject"], msg["From"], msg["To"] = ...; msg.set_content("\n".join(lines))
send: transport.send_message(msg)
```

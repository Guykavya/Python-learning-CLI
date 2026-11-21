# From a CSV to a weekly e-mail

Chapter section 9 (data automation: from a CSV to a weekly e-mail) and "Try it: test the bad-row rule". A very common weekly job: take an export, summarize it, mail the summary. Split it into three jobs so each can be tested: **summarize** (pure), **build the message** (pure), **send** (a side effect behind a replaceable transport). No e-mail ever leaves your machine in this problem: the tests pass a `FakeTransport`.

## What to write

```python
def summarize(csv_text) -> tuple[dict[str, float], list[int]]: ...
def build_email(totals, bad_lines, sender, to) -> EmailMessage: ...
def send(msg, transport) -> None: ...
```

`summarize(csv_text)` reads a CSV with a header `region,amount`:
- returns `(totals, bad_lines)`: `totals` maps each region (spaces stripped) to the sum of its amounts as `float`, **sorted by region**; `bad_lines` lists the **line numbers** (the header is line 1) of rows that could not be used;
- a row is bad if the region is empty, the amount is not a number, or a column is missing (a short row gives `None` for the missing column);
- a bad row must leave **no trace** in the totals (convert the amount *before* adding anything).

`build_email(totals, bad_lines, sender, to)` returns an `email.message.EmailMessage` with:
- `Subject`: `Weekly sales: <grand total>` formatted with `:,.2f` (for example `Weekly sales: 2,540.25`), `From`, `To`;
- a body (set with `set_content`) of one line per region, `f"{region:10} {amount:10,.2f}"`, then a line `f"{'TOTAL':10} {total:10,.2f}"`, and, **only if there are bad lines**, an empty line and `Warning: could not read line(s) [5, 7]. Please check the export.`

`send(msg, transport)` hands the message to `transport.send_message(msg)`. (A real transport would be `smtplib.SMTP_SSL`, which has the same method.)

## Example

```python
export = "region,amount\nnorth,1200.50\nsouth,830\nnorth,99.50\neast,abc\nwest,410.25\n,12\n"
totals, bad = summarize(export)
# ({'north': 1300.0, 'south': 830.0, 'west': 410.25}, [5, 7])
msg = build_email(totals, bad, "reports@example.com", "boss@example.com")
msg["Subject"]             # 'Weekly sales: 2,540.25'
print(msg.get_content())
# north        1,300.00
# south          830.00
# west           410.25
# TOTAL        2,540.25
#
# Warning: could not read line(s) [5, 7]. Please check the export.
```

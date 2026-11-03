## Hint 1

Split the work in two: deciding about **one** record (good row, or a reason why not), and
the loop over the batch that collects good rows and quarantine entries. For the decision,
which three checks come in which order? Which exception class covers `KeyError`,
`ValueError` and `decimal.InvalidOperation`, but not `KeyboardInterrupt`?

## Hint 2

```
for record in records:
    if not isinstance(record, dict): reason = "not an object"
    elif errors := check(record):     reason = "; ".join(errors)
    else:
        try: good.append(transform(record)); continue
        except Exception as e: reason = f"{type(e).__name__}: {e}"
    bad.append({"run_id": run_id, "reason": reason, "record": record})

if bad:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for entry in bad: f.write(json.dumps(entry) + "\n")
```

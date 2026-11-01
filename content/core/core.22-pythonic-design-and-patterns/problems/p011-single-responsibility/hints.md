## Hint 1

Read the old function and underline every "and": it reads text **and** checks it **and**
adds up **and** prints. If each underlined part were its own function, what would go in and
what would come out? Which of the four is the only one that talks to the outside world?

## Hint 2

```
parse_order(text):   rows = []; for each stripped non-blank line: rows.append(split and strip)
validate_order(rows): errors = []; for n, fields in enumerate(rows, start=1): one message or none
price_order(rows):    round(sum(int(qty) * float(price) ...), 2)
process_order(text):  rows = parse ; errors = validate ; if errors: join lines + INVALID ; else OK line
```
A small private helper that returns the message for one row keeps `validate_order` short.
(Extra helpers are allowed; only the four names above are required.)

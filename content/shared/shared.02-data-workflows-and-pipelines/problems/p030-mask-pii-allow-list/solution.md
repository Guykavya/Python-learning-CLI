## Approach

`rpartition("@")` splits at the last `@` and returns `(local, "@", domain)`, or
`("", "", whole)` when there is no `@`. Checking that all three parts are non-empty catches every
malformed case at once. The mask has a fixed shape (first letter, three stars, domain) so it
reveals as little as possible: not the length, not the rest of the name.

The allow-list is a loop over the **allowed** names. Because the result is built from the
allow-list, a new column in the source can never appear in the export unless someone decides to
add it. Building new dicts leaves the input rows intact for the rest of the pipeline.

## Code

```python
def mask_email(email):
    if email is None:
        return None
    local, at, domain = email.strip().lower().rpartition("@")
    if not at or not local or not domain:
        return "***"
    return f"{local[0]}***@{domain}"


def select_columns(row, allowed):
    return {name: row[name] for name in allowed if name in row}


def prepare_export(rows, allowed):
    out = []
    for row in rows:
        kept = select_columns(row, allowed)
        if "email" in kept:
            kept["email"] = mask_email(kept["email"])
        out.append(kept)
    return out
```

## Complexity

O(rows x allowed columns). Each email is masked in O(length of the address).

## Another way

A regular expression, `re.fullmatch(r"(.+)@([^@]+)", email)`, gives the same split: the greedy
`(.+)` takes everything up to the last `@`. In a real pipeline you would keep the allow-list per
consumer in configuration (`support: [id, status, city, email]`, `finance: [id, amount, ...]`) and
review changes to it like code. Remember that masking is for **display**: `a***@example.com` is
the same for `asha@` and `anil@`, so it cannot be used to join or count customers. For that you
need a pseudonym (next problem).

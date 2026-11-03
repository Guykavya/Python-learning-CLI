## Hint 1

Which method splits a string at its **last** separator and always returns three parts, even when
the separator is missing? (`str.rpartition`.) What do the three parts look like for
`"asha@example.com"`, for `"broken"` and for `"@example.com"`? Which of them must become `"***"`?

## Hint 2

For the allow-list, loop over `allowed`, not over the row. Then a column the row has but
`allowed` does not mention can never sneak in.

```
mask_email(email):
    if email is None: return None
    local, at, domain = email.strip().lower().rpartition("@")
    if at, local or domain is empty: return "***"
    return local[0] + "***@" + domain

select_columns(row, allowed):
    return {name: row[name] for name in allowed if name in row}

prepare_export(rows, allowed):
    for each row: kept = select_columns(row, allowed)
                  if "email" in kept: kept["email"] = mask_email(kept["email"])
    return the list of kept dicts
```

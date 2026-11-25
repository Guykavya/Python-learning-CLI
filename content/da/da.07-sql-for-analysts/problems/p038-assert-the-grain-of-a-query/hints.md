## Hint 1

Which pandas method marks rows whose key columns repeat, and how do you keep **all** the rows of a repeated key? Which method tells you whether any value of the key columns is missing? In which order should the two checks run, and what is the type of what you return?

## Hint 2

```text
df = con.execute(sql).df()
if df[key].isna().any().any(): raise AssertionError("... NULL ...")
dup = df[df.duplicated(subset=key, keep=False)]
if len(dup): examples = first 3 distinct key values of dup -> raise AssertionError("... duplicate ...")
return df
```

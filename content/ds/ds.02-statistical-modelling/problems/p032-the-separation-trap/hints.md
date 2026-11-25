## Hint 1

What do you have to do to catch a *warning* as well as an exception? Look at `warnings.catch_warnings(record=True)` and `warnings.simplefilter('always')`.

## Hint 2

```text
with catch_warnings(record=True) as caught:
    simplefilter("always")
    try: res = Logit(y, X).fit(disp=0)
    except LinAlgError: return None, "singular ..."
    except Exception as e: if 'separation' in name/message: return None, "perfect separation"; else raise
if any warning mentions separation: return None, ...
if max |params| > 15: return None, "separation suspected"
return res, "ok"
```

## Hint 1

Which codes have fixed texts? Put them in a dictionary and look them up first. What is left over, and how do you recover the signal number from a code in the 129 to 192 range?

## Hint 2

```text
if not 0 <= code <= 255: raise ValueError
if code in FIXED: return FIXED[code]
if 129 <= code <= 192:
    n = code - 128
    text = f"{code}: killed by signal {n} ({SIGNALS.get(n, 'unknown name')})"
    add the extra sentence for 137 and for 143
    return text
return f"{code}: application-specific error code"
```

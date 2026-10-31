## Hint 1

You need one pattern that matches any of the words, only as whole words, in any case. How do
you join several words into one pattern? What must surround the whole alternation so `\b`
applies to every word, not just the first and last?

## Hint 2

The replacement depends on the match (its length), so the replacement must be a **function**
that receives the `Match`. And `subn` instead of `sub` gives you the count.

```
if words is empty: return (text, 0)
alts = "|".join(re.escape(w) for each w in words)
pattern = compile(r"\b(?:" + alts + r")\b", IGNORECASE)
return pattern.subn(lambda m: "*" * len(m.group()), text)
```

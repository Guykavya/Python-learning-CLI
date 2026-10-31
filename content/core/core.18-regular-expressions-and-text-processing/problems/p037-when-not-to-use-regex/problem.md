# Explain: when not to use a regex

Once you know regex, every text problem starts to look like one. Some are not. A teammate
proposes these five regexes:

| # | Task | Proposed regex |
|---|---|---|
| a | Get every link from an HTML page | `<a href="(.*?)">` |
| b | Read the `"price"` from a JSON API response | `"price":\s*(\d+)` |
| c | Check that brackets in a formula are balanced: `((a+b)*(c-d))` | `^\(.*\)$` |
| d | Split a line like `alice,bob,carol` | `re.split(r",", line)` |
| e | Check a filename ends with `.csv` | `re.search(r"\.csv$", name)` |

In `answer.md` (about 250 to 400 words):

1. For **each** of a to e, say what goes wrong (or what is simply unnecessary), give one concrete
   input that breaks it or shows the problem, and name what to use instead.
2. Explain in your own words **why** regular expressions cannot check balanced brackets in
   general (what would the pattern need to "remember"?).
3. Give a short rule of thumb: when *is* regex the right tool?

**Example** of the level of detail expected for one part:

> d. Nothing breaks, but `line.split(",")` does the same thing, is faster and every reader
> understands it. Use regex only when the separator is a *pattern* (for example "comma or
> semicolon with any spaces").

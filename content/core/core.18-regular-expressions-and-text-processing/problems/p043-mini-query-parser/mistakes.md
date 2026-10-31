- `q.split()` first: it cuts `"Jane Doe"` into two terms before any regex can see the quotes.
- Putting `\S+` before the quoted alternative: `\S+` matches `"Jane` and the phrase is lost.
- Making the value optional (`(?:...)?`): then `tag:` becomes a filter with an empty value
  instead of a free word.
- `if m.group("quoted"):` instead of `is not None`: the empty quoted value `""` falls into the
  `word` branch, which is `None`.
- Forgetting `.lower()` on keys, or lower-casing the values too.
- Returning a `defaultdict`: it compares equal to a dict, but a later `result["missing"]` silently
  adds a key. Return a plain `dict`.
- Expecting `time:10:30` to split at the second colon: `\w+` stops at the first colon, and the
  value `\S+` takes the rest.

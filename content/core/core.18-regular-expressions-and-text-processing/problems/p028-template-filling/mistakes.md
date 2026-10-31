- Using `values[name]` without a check: a missing name raises `KeyError`.
- Returning `""` or `None` for a missing name instead of `m.group(0)`. The placeholder must stay.
- Building a replacement string per value, like `re.sub(pattern, values["p"], text)`. Backslashes
  in the value are processed.
- Looping "replace until nothing changes". A value that contains a placeholder would be
  expanded, and a value containing its own placeholder would loop forever.
- Using `\w+` for the name: then `{{ 1x }}` is accepted.
- Using `.*` for the name: `{{ a }} and {{ b }}` becomes one giant placeholder (greedy `.*`
  runs to the last `}}`).
- Forgetting `str()`: returning an `int` from the function raises `TypeError`.

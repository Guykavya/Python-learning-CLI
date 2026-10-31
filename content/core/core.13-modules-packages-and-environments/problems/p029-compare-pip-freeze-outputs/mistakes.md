- Comparing versions as strings. `"3.10" < "3.9"` is `True` as text, so 3.10 would look older. Text order
  is right only by accident. Use tuples of ints.
- Comparing names without normalising, so `Flask` -> `flask` looks like "removed + added".
- Replacing each separator on its own: `charset--normalizer` would keep two dashes. A *run* of
  separators becomes **one** dash.
- Treating `3.7` -> `3.7.0` as an upgrade. They are equal; drop trailing zeros first.
- Splitting `name @ url` on `@` alone. A url can contain `@` too (`git+https://...@abc123`); split on
  `" @ "` once with `partition`.
- Crashing on `-e ...` lines or comments instead of skipping them.

- A greedy value `(?P<value>.*)\s*`. The `.*` keeps the trailing spaces and `\s*` matches nothing.
  Use `.*?` (lazy) or strip afterwards.
- Using `re.search` or `re.match` instead of `re.fullmatch`. `re.search` finds `key = 1` inside
  `my key = 1` and accepts a key with a space.
- Writing `(?P<value>.+)`. Then `debug =` (an empty value) is rejected.
- Writing a literal space around `=` instead of `\s*`. `port=8080` then fails.
- Returning `m.groups()`, a tuple, instead of `m.groupdict()`.
- Using `\w+` for the key. `\w` includes digits, so `1st` would be accepted.

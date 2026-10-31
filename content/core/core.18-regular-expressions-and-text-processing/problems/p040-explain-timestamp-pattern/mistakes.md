- Saying `\d{2}` would be "the same" as `0[1-9]|1[0-2]`: it also accepts `00` and `13` to `99`.
- Thinking the `-` and `:` in the pattern need spaces in the input. In verbose mode the spaces in
  the pattern are ignored.
- Claiming `2025-02-31...` is rejected. The pattern has no idea which month has 31 days.
- Missing why `09:15.5` fails: the fraction lives inside the optional seconds block, so it
  cannot appear without `:ss`.
- Saying `^...$` would behave the same. `$` also matches just before a final newline; `\Z` does not.
- Forgetting that `None` means "this optional group did not take part", not an empty string.

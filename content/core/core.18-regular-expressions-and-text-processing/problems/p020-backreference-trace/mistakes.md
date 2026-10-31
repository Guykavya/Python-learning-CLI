- Thinking `\1` repeats the group's *pattern*. It repeats the matched *text*: `(['"])...\1`
  needs the same quote, not any quote.
- Ending the `"it's"` match at the apostrophe. Group 1 is `"`, so only a `"` can close it.
- Printing `'"'` with quotes. `print` shows the characters of the string, not its repr.
- Guessing the tag match is `<b>bold</i>`. The closing tag must repeat group 1 (`b`).
- Assuming `"(a)\1"` and `r"(a)\1"` are the same pattern. Without `r`, `\1` is an escape for
  the character with code 1.
- Forgetting that IGNORECASE applies to backreferences too.

- Expecting `^` to match at every line without `re.M`. Without it, `^` is the start of the
  whole string only.
- Expecting `$` without `re.M` to give the last word of each line. It gives only the last word
  of the string.
- Thinking `re.M` changes `.`. It does not: only DOTALL (`re.S`) lets `.` match `\n`. People
  mix up "multi-line" with "dot matches newline".
- Forgetting that `\w` is Unicode-aware by default, so `café` is one word. `re.ASCII` changes that.
- Writing `re.I + re.M`. It happens to work, but `|` is the right operator for flags: adding the
  same flag twice gives a different flag.

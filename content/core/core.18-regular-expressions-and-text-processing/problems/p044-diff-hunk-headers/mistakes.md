- Forgetting `re.MULTILINE`: `^` then matches only at the start of the whole text, and only a
  header on the very first line is found.
- Leaving out `^`: removed lines like `-@@ -1 +1 @@` are taken for headers.
- Writing `+(\d+)` without the backslash: `+` is a quantifier, and the pattern fails to compile
  or means something else.
- Writing `,?(\d*)`: the group is then `""` (not `None`) when missing, and `int("")` raises
  `ValueError`.
- Treating a length of `0` as missing. `@@ -0,0 +1,3 @@` (a new file) has a real old length 0.
- Returning the strings from `m.groups()` without converting to `int`.

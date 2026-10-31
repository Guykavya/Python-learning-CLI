- `text.split("=")` without the limit: `url = a=b` splits into three parts and the unpacking fails.
- Checking `line.startswith("#")` before stripping: an indented comment is then treated as a setting.
- Counting line numbers only for useful lines. The number must match the line in the file,
  so blank and comment lines count too.
- Building a list and returning it: the function is then not lazy.
- Forgetting to strip the value, so `"Kavya"` comes back as `" Kavya"`.

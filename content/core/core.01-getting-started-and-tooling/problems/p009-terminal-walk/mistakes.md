- Writing output for `echo "..." > hello.py`. With `>` the text goes into the
  file, not to the screen.
- Writing `"print('hi')"` with the outer double quotes. Bash removes them before
  `echo` sees the text.
- Answering `5` for `wc -c`. `echo` ends its output with a newline character,
  and `wc -c` counts it.

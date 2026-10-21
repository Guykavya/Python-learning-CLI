- Expecting the first line to print before the crash. Syntax errors are found
  at compile time, before any line runs.
- Fixing only the first error and assuming the program is done. Run again; the
  next error was hidden behind the first.
- Mixing quote types: `'text"` never closes.
- Looking only at the reported line. For an unclosed bracket, Python sometimes
  reports a later line; check the line above too.

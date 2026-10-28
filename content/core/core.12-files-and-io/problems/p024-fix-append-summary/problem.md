# Fix: the error summary appender

`append_summary(src, dst)` should read the log file `src`, count the lines that contain the word `ERROR`
(anywhere in the line), and **append** one line `errors=N` to the file `dst`. It returns `N`.
Earlier lines in `dst` must stay.

**This code has bugs. Find and fix them.** The program runs, but the tests fail: the summary file loses
its old lines, the lines glue together, some errors are missed, and Python warns about files that were
never closed. Write the corrected function in `solution.py`.

**Example**

```text
# app.log                       # report.txt before
10:01 INFO start                errors=0
10:02 ERROR disk full
10:03 WARN slow
10:04 ERROR timeout
```

```python
append_summary("app.log", "report.txt")    # returns 2
# report.txt now: "errors=0\nerrors=2\n"
```

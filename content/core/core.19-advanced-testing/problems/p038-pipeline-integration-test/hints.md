## Hint 1

Write the input file as one multi-line string with every awkward row you can think of: `Food` and ` food ` (same category), a blank
amount, the text `abc`, a negative amount, two categories with the same total. What should the report look like? Work it out by hand
**before** you run anything.

## Hint 2

Then compare the **whole** output with one list of lines (`dst.read_text().splitlines() == [...]`). A test that only checks
`run(...) == 3` cannot see a wrong total or a wrong order. Add the boundary files: header only, every row invalid, input file missing.

```
def make(tmp_path, body): src = tmp_path/"in.csv"; src.write_text("date,category,amount\n" + body); return src, tmp_path/"out.csv"
test_messy:   run -> returns number of REPORT lines; lines == [header, rent..., food..., fun..., games...]
test_empty:   body "" -> run == 0 and lines == [header]
test_all_bad: body "d,Food,\nd,Food,-1\n" -> run == 0
test_missing: with pytest.raises(FileNotFoundError): run(tmp_path/"nope.csv", ...)
```

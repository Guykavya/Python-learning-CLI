## Hint 1

List what the tool promises: the default and the effect of each option, how words are cleaned (case, punctuation), the order of
the ranking and of ties, the JSON shape, the error case. Write one small text file for each promise. Work out the expected output by hand.

## Hint 2

Ties are easy to forget: make a file where two words have the same count and appear in **non-alphabetical** order. For the exit code, think about what
`main()` returns versus what the shell sees: they only meet in the last two lines, and only a real process runs them.

```
def test_x(tmp_path, capsys):
    f = tmp_path/"t.txt"; f.write_text("...")
    assert wordstat.main([str(f), "--top", "2"]) == 0
    assert capsys.readouterr().out.splitlines() == [...]
errors: code == 2, captured.out == "", "nope.txt" in captured.err
def test_script(...): r = subprocess.run([sys.executable, wordstat.__file__, str(missing)], capture_output=True, text=True, timeout=30)
    assert r.returncode == 2
```

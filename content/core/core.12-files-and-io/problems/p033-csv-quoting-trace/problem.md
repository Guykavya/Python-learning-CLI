# Trace: how csv quotes cells

The `csv` module adds quotes only when a cell needs them. It can also put a newline **inside** one cell,
so lines and rows are not the same thing. Predict every line.

```python
import csv
import io

buf = io.StringIO()
writer = csv.writer(buf, lineterminator="\n")
writer.writerow(["id", "note"])
writer.writerow([1, "plain"])
writer.writerow([2, "has, comma"])
writer.writerow([3, 'say "hi"'])
writer.writerow([4, "two\nlines"])
writer.writerow([5, ""])
writer.writerow([6, None])
text = buf.getvalue()

print(text.count("\n"))
lines = text.splitlines()
print(len(lines))
print(lines[3])
print(lines[4])
print(lines[5])

rows = list(csv.reader(io.StringIO(text)))
print(len(rows))
print(rows[3])
print(rows[4])
print(rows[5], rows[6])
print(rows[1][0] + rows[2][0])
```

Write exactly what the program prints to **standard output**, one line for each printed line, in `answer.txt`.
The program never ends with a traceback. Lines sent to `sys.stderr` do not count.

`print` shows a list with `repr`, so a newline inside a cell is shown as `\n` there.

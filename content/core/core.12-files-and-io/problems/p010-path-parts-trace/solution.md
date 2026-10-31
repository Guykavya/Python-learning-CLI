## Approach

The name is `sales.2024.csv`, the stem is `sales.2024` (only the last suffix is removed) and the suffix is `.csv`. `suffixes` lists all of them: `['.2024', '.csv']`. The parent is `data/reports` and its name is `reports`. `with_suffix` swaps `.csv` for `.json`; `with_name` replaces the whole last part; `with_stem` keeps the suffix and swaps the stem. `parts` gives `('data', 'reports', 'sales.2024.csv')`. Joining uses `/`; if the right side is absolute, it replaces everything on the left, so we get `/etc`. `x.tar.gz` has the suffix `.gz` only. A name without a dot has the suffix `''`, so the test prints `True`. `..` stays as a part. A path starting with `/` is absolute.

## Output

```text
sales.2024.csv
sales.2024
.csv
['.2024', '.csv']
data/reports
reports
data/reports/sales.2024.json
data/reports/totals.txt
data/reports/q1.csv
('data', 'reports', 'sales.2024.csv')
a/b/c.txt
/etc
.gz
True
('a', '..', 'b')
True
```

## Complexity

O(1).

## Another way

Try the same with `Path` on your own system and a real folder. `Path("a/b") / "/etc"` is `/etc` on Linux too. Change the example name to `.bashrc` and print `stem` and `suffix`: the stem is the whole name and the suffix is empty.

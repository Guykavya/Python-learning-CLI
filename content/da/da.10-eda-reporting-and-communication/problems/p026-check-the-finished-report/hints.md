## Hint 1

Write each check as a few lines and keep the order. Which regular expression captures the file inside `![alt](file)`? Which captures the date after `Data to: `? Dates in `YYYY-MM-DD` form compare correctly as strings.

## Hint 2

```text
refs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", md_text)
for f in refs: if not (Path(figures_dir) / f).exists(): ...
for p in sorted(Path(figures_dir).glob("*.png")): if p.name not in refs: ...
m = re.search(r"^Data to: (\d{4}-\d{2}-\d{2})", md_text, re.M)
```

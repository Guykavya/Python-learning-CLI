## Approach

Each problem a reader could find (a wrong number, a broken image, a leftover TODO, an old date) becomes one mechanical check. Running them on every build turns "I hope it's right" into a list of what is wrong.

## Code

```python
import re
from pathlib import Path


def check_report(md_text, numbers, figures_dir, data_to):
    problems = []
    for name, text in numbers.items():
        if text not in md_text:
            problems.append(f"{name} = {text} does not appear in the text")
    if "{" in md_text or "}" in md_text or "TODO" in md_text:
        problems.append("unfilled template placeholder or TODO left in the text")
    folder = Path(figures_dir)
    refs = re.findall(r"!\[[^\]]*\]\(([^)]+)\)", md_text)
    for f in refs:
        if not (folder / f).exists():
            problems.append(f"figure file missing: {f}")
    for p in sorted(folder.glob("*.png")):
        if p.name not in refs:
            problems.append(f"figure not used in the text: {p.name}")
    m = re.search(r"^Data to: (\d{4}-\d{2}-\d{2})", md_text, re.M)
    if not m:
        problems.append("no 'Data to:' line")
    elif m.group(1) < data_to:
        problems.append(f"stale date: text says {m.group(1)}, data run to {data_to}")
    return problems
```

## Complexity

O(length of the text + number of files).

## Another way

Run the checks inside the test suite of the analysis (`pytest`), so that a broken report fails the build like broken code.

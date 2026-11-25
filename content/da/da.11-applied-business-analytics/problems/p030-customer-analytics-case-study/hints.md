## Hint 1

Do it in the order of the statement and print each number as you go: first the four analyses (each is a few lines using the given helpers), then the strings, then the finding, then the page. Run `lint_finding` early and fix what it says.

## Hint 2

```text
ab_text, fun_text, repeat lines, segment lines are made ONCE and used both in the finding/page and in results["expected"]
page = finding.render_markdown() + sections
results["decimals"] = sorted(set(re.findall(DEC, page)))
check: expected strings missing -> "missing: ..."; decimals in the page not in results["decimals"] -> "number not in the results: ..."
```

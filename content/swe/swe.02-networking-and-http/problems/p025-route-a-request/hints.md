## Hint 1

Turn each pattern into something you can test a path against. What does `{id}` stand for in a regular expression? What must `/notes/{id}` not match?

## Hint 2

Three outcomes, in this order of thought: is there any pattern for this path at all (if not, 404)? Is there a handler for this method among them (200)? Otherwise 405 and the list of methods that exist.

## Hint 3

```text
group the routes by pattern: pattern -> {method: handler}
for each pattern: regex = escape the fixed parts, replace {name} by (?P<name>[^/]+), anchor with ^ $
matches = patterns whose regex matches the path, sorted by number of parameters
for each match: if method (or GET for HEAD) is there: return 200, handler, groupdict
if matches: 405 with Allow = sorted union of methods; else 404
```

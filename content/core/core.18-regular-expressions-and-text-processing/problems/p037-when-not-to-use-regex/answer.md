**1. The five proposals.**

- **a. HTML links.** HTML is not one fixed shape. `<a class="x" href="/a">`, `<a href='/a'>`
  (single quotes), `<A HREF="/a">`, an `href` split across two lines, or `<!-- <a href="old"> -->`
  inside a comment all break `<a href="(.*?)">`. Use a real parser: `html.parser.HTMLParser` from
  the standard library (override `handle_starttag` and read the `href` attribute), or a library
  such as BeautifulSoup.
- **b. JSON price.** `{"price": 12.50}` loses the `.50`, `{"price": -3}` or `{"price": "12"}` is
  missed, and `{"old": {"price": 9}, "price": 12}` returns the wrong one (the nested key comes
  first). Use `json.loads(text)["price"]`: it understands numbers, strings, escapes and nesting.
- **c. Balanced brackets.** `^\(.*\)$` only checks the first and last characters: `(a))(b` → no,
  but `())((()` → **yes**, though it is unbalanced. Use a counter loop: add 1 for `(`, subtract 1
  for `)`, fail if the count ever goes below 0, and require 0 at the end. With several kinds of
  brackets, use a stack (a list).
- **d. Simple split.** Nothing breaks: but `line.split(",")` is clearer and faster. Regex only
  pays off when the separator is a pattern, such as `r"[,;]\s*"`.
- **e. File extension.** It works, but `name.endswith(".csv")` says the same with no escaping to
  get wrong (forget the `\` and `xcsv` matches). For case-insensitive checks:
  `name.lower().endswith(".csv")` or `pathlib.Path(name).suffix.lower() == ".csv"`.

**2. Why regex cannot count nesting.** A regular expression is matched by a machine with a
fixed, finite amount of memory: it can remember "where am I in the pattern", but not an
unlimited number. To check `(((...)))` it would need to remember how many brackets are still
open, and that number can grow without limit. Any fixed pattern can be beaten by nesting one level
deeper than it handles. A counter or a stack has that unlimited memory; a regex does not. (Some
engines add recursion extensions, but Python's `re` does not, and such patterns are unreadable.)

**3. Rule of thumb.** Use regex for **flat, local patterns in text**: find or validate tokens
(dates, ids, phone numbers), pull fields out of lines with a known shape (log lines), and
substitutions. Do not use it when:
- a plain string method does the job (`split`, `startswith`, `endswith`, `in`, `strip`);
- the data has a real format with a parser (`json`, `csv`, `html.parser`, `xml`, `tomllib`);
- the structure nests (brackets, tags, quoted strings inside quoted strings).
If the regex needs a long comment to be understood and still has edge cases, it is a sign to
switch tools.

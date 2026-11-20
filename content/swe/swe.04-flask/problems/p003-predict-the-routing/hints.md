## Hint 1

Take the requests one at a time. For each one, ask: is there a rule with this path? Is the method allowed? Does a converter reject the value?

## Hint 2

Rule `"/about/"` (with a slash) answers `/about` with a redirect to the slash version. Rule `"/contact"` (without) does **not** accept `/contact/`. Look at section 3.5 for how the `Location` of that redirect is written. `url_for("new")` inside `redirect` builds a **path** only.

## Hint 3

```text
1  /about        rule has a slash   -> 308 + Location (full URL, see the chapter)
2  /about/       matches            -> 200 about
3  /contact/     rule has no slash  -> 404
4  /old          redirect() default -> 302 /new
5  /moved        code=301           -> 301 /new
6  /item/x       int converter      -> 404
7  GET /submit   path exists, wrong method -> 405
8  POST /submit  -> 200 saved
```

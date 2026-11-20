## Approach

Evaluate each template from left to right and keep the result of each filter.

```text
1: [none]
2: [HELLO W…]
3: [2026-03-09]
4: [3 items]
5: []
6: [&lt;b&gt;hi&lt;/b&gt; <b>hi</b>]
```

- **1.** `default` fires for every false value, and `0` is false. The text is `none`, not `0`. To replace only `None`, use `default_if_none`.
- **2.** `upper` gives `HELLO WORLD` (11 characters). `truncatechars:8` keeps 7 characters, `HELLO W`, and adds the one-character ellipsis: 8 in total.
- **3.** The `date` filter formats a `datetime.date`: `2026-03-09`.
- **4.** `length` of a list with three items is 3; the text around the expression is copied unchanged.
- **5.** A missing variable renders as an empty string, so only the brackets remain.
- **6.** Auto-escaping turns `<` into `&lt;` and `>` into `&gt;`. `|safe` switches that off for this one use, so the raw tag comes out. Never use `|safe` on text a user typed (section 5.2).

Real output of the program, run with Django 6.1.3.

## Complexity

Not applicable; this is a reading exercise.

## Another way

Render a template one filter at a time (`{{ title|upper }}`, then `{{ title|upper|truncatechars:8 }}`) to see where each step changes the text. This is how you debug a long chain in real projects.

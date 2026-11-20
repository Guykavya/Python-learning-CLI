## Approach

Apply the section 3.1 rule to each parameter, then ask whether the text in the URL converts to the declared type.

```text
1: 200 {'user_id': -3, 'limit': 10, 'draft': False, 'tag': None}
2: 200 {'user_id': 7, 'limit': 3, 'draft': True, 'tag': None}
3: 200 {'user_id': 7, 'limit': 10, 'draft': False, 'tag': 'py'}
4: 422 query.limit
5: 422 path.user_id query.draft
6: 404
7: 200 {'user_id': 7, 'limit': 10, 'draft': False, 'tag': 'go'}
8: 422 query.limit
```

- **1.** `user_id` is in the path; `"-3"` is a valid integer. The type says "int", nothing more, so negative ids pass. The others take their defaults.
- **2.** `"3"` becomes `3`; `draft=yes` becomes `True` (query booleans accept `true/1/yes/on` and `false/0/no/off`).
- **3.** `draft=0` is `False`; `tag` is an optional `str`.
- **4.** `"abc"` cannot be an int: one error at `["query", "limit"]`.
- **5.** Two problems, two entries, **all collected in one response**: `["path", "user_id"]` and `["query", "draft"]` (`maybe` is not a known boolean word).
- **6.** `/users//posts` has an empty segment where `{user_id}` should be, so the **router** finds no route: 404. Routing (step 1 of the lifecycle in section 6.1) happens before any parameter is read.
- **7.** A plain `str` parameter receives **one** value; with a repeated key FastAPI keeps the last one, `"go"`. To get both, declare `tag: Annotated[list[str] | None, Query()] = None`.
- **8.** `"2.5"` is not a whole number; the query is text, and the text `"2.5"` does not parse as an int. No rounding happens.

Real output of the program, run with FastAPI 0.162.0 and Pydantic 2.14.3.

## Complexity

Not applicable; this is a reading exercise.

## Another way

Open `/docs` (section 19) or print `app.openapi()["paths"]["/users/{user_id}/posts"]["get"]["parameters"]`: it lists each parameter with `"in": "path"` or `"in": "query"`, whether it is required, and its type. That table is exactly the section 3.1 rule applied to your signature.

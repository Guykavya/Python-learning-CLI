## Approach

Follow the lifecycle of section 6.1: routing, then reading the raw pieces (including **parsing the JSON body**), then validating every parameter and the body, collecting all errors.

```text
1: 422 path.project_id int_parsing
2: 422 body.priority missing
3: 422 body.tags.1 string_type
4: 422 query.notify bool_parsing
4: 422 body.title string_too_short
4: 422 body.priority greater_than_equal
5: 422 body.24 json_invalid
```

- **1.** Only the path is wrong. The body is fine, so there is one error, at `path.project_id`.
- **2.** `priority` has no default, so it is required: `missing`. `title` and `tags` are fine (`tags` has the default `[]`).
- **3.** `tags` is a list; its item at index **1** (the second item, `5`) is not a string. The `loc` is a path into the structure: `body.tags.1` (section 5.8). Note `5` is **not** converted to `"5"`: Pydantic does not turn numbers into strings.
- **4.** Three problems, three entries, one response: the query parameter first, then the body fields in the order the model declares them (`title`, then `priority`). `priority: 0` breaks `ge=1`: `greater_than_equal`.
- **5.** The body text `{"title": "write tests",` is cut off. In step 2 of the lifecycle FastAPI must parse the JSON before it can validate anything, and parsing fails, so it answers at once with **one** error, `json_invalid`. The path `abc` and `notify=maybe` are **never checked**. The last part of the `loc` is the character position where the parser stopped: the text is 24 characters long and ended in the middle of an object, so the position is 24.

Real output of the program, run with FastAPI 0.162.0 and Pydantic 2.14.3.

## Complexity

Not applicable; this is a reading exercise.

## Another way

A client program reads a 422 like this, never by `msg`:

```python
for error in response.json()["detail"]:
    source, *path = error["loc"]
    if source == "body" and path[:1] == ["title"] and error["type"] == "string_too_short":
        show_under_field("title", "Please use at least 3 characters")
```

Section 8.2 shows how a server can reshape these errors into its own envelope while keeping `loc` and `type`.

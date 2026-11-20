## Hint 1

Count the body parameters of each endpoint. With exactly **one** model and nothing else, the JSON object **is** the model. With **two or more** body parameters, what does section 4.2 say the JSON looks like?

## Hint 2

`Body(embed=True)` asks for the "several parts" shape even when there is only one model: the model goes under a key named like the parameter. `Annotated[int, Body()]` makes a plain int a body part too, so `/d` has two body parts. A missing part gives a `missing` error at `body.<parameter name>`, and every missing part is reported.

## Hint 3

```text
/a  expects {"name": ...}                                  (the model itself)
/b  expects {"item": {"name": ...}, "user": {"username": ...}}
/c  expects {"item": {"name": ...}}                        (embed=True)
/d  expects {"item": {"name": ...}, "count": <int>}
Compare each request with its expected shape; each missing key -> body.<key>:missing
```

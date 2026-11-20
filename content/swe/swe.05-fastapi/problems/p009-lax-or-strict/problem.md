# Lax or strict?

Chapter section 5.4 (lax versus strict mode). Pydantic converts some values and refuses others, and strict mode refuses much more. Here are two models and seven input values. For every value the program validates each field **on its own** (the other field keeps its default) and prints the stored value with `repr`, or `error`.

```python
from pydantic import BaseModel, ConfigDict, ValidationError


class Lax(BaseModel):
    n: int = 0
    ok: bool = False


class Strict(BaseModel):
    model_config = ConfigDict(strict=True)
    n: int = 0
    ok: bool = False


def result(model, field, value):
    try:
        obj = model.model_validate({field: value})
    except ValidationError:
        return "error"
    return repr(getattr(obj, field))


inputs = ["5", 5.0, 5.5, "true", "yes", 1, True]
for number, value in enumerate(inputs, 1):
    print(
        f"{number}: lax n={result(Lax, 'n', value)} ok={result(Lax, 'ok', value)}"
        f" | strict n={result(Strict, 'n', value)} ok={result(Strict, 'ok', value)}"
    )
```

Write your answer in `answer.txt`: seven lines, `1: ...` to `7: ...`, exactly in the format of the `print` (for example `8: lax n=3 ok=error | strict n=error ok=False`). Remember that `repr` of a stored int is `5` and of a bool is `True`. Do not run it.

## After you answer

1. Which inputs does lax `int` accept, and what do they have in common? Why is `5.5` refused while `5.0` is accepted?
2. Line 7: lax mode turned `True` into an int. Is that what you want for a field like `quantity`? Which setting stops it?
3. When would you choose strict mode for a model in a real project (section 5.4's rule of thumb)?

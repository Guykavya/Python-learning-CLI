## Approach

Pandas converts a column of digits to numbers unless told otherwise, and a number has no leading zeros. The argument `dtype={"column": "str"}` makes the reader keep the raw text. Naming only the two identifier columns lets `qty` stay a normal integer column.

## Code

```python
import pandas as pd


def read_with_codes(path):
    return pd.read_csv(path, dtype={"pin": "str", "product_code": "str"})
```

## Complexity

O(size of the file).

## Another way

`dtype="str"` reads **every** column as text; convert the numeric ones afterwards (Ch. 18 `load_sales` does exactly that). For a file you do not know yet, text first is the safest start.

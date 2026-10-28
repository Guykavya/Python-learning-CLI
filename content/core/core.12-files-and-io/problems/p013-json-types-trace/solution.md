## Approach

`dumps` writes keys as strings (the int key `2` becomes `"2"`), `True` as `true`, `None` as `null`, the tuple as an array, and `9.5` as `9.5`. After `loads`, the dict has string keys and `pair` is a **list** `[1, 2]`, so the comparison with a tuple prints `False`. `back.get(2)` is `None` (there is no int key now), and `back["2"]` is `two`. By default non-ASCII text is escaped: `"caf\u00e9"`; with `ensure_ascii=False` the `é` stays. With `sort_keys=True` and `indent=1` the keys come out sorted, one element per line, with 1 space of indent. A set cannot be written, so `TypeError` is caught. Last, `1`, `2.0`, `"3"`, `null`, `true` come back as `1`, `2.0`, `'3'`, `None`, `True`.

## Output

```text
{"id": 1, "2": "two", "ok": true, "none": null, "pair": [1, 2], "price": 9.5}
{'id': 1, '2': 'two', 'ok': True, 'none': None, 'pair': [1, 2], 'price': 9.5}
False
None two
"caf\u00e9"
"café"
{
 "a": [
  1,
  {
   "z": 0
  }
 ],
 "b": 1
}
set is not serialisable
[1, 2.0, '3', None, True]
```

## Complexity

O(1).

## Another way

Write the text to a file, read it back and compare with `==`. Your data does not survive unless it only uses dicts with string keys, lists, strings, numbers, booleans and `None`. For other types, convert them first or use `default=`.

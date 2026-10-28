# Trace: what JSON does to Python values

`json.dumps` turns Python data into text, and `json.loads` turns it back. Not everything survives the trip. Predict each line.

```python
import json

data = {"id": 1, 2: "two", "ok": True, "none": None, "pair": (1, 2), "price": 9.50}
text = json.dumps(data)
print(text)
back = json.loads(text)
print(back)
print(back["pair"] == (1, 2))
print(back.get(2), back["2"])
print(json.dumps("café"))
print(json.dumps("café", ensure_ascii=False))
print(json.dumps({"b": 1, "a": [1, {"z": 0}]}, sort_keys=True, indent=1))

try:
    json.dumps({1, 2})
except TypeError:
    print("set is not serialisable")

print(json.loads('[1, 2.0, "3", null, true]'))
```

Write exactly what the program prints, one line for each printed line, in `answer.txt`. A print of an empty string is an empty line. The program never stops with an error, so you never need to write a traceback.

## Hint 1

Which functions work on files: `json.dump`/`json.load` or `json.dumps`/`json.loads`? Which options make the output readable, sorted and Unicode friendly?

## Hint 2

```
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, sort_keys=True, ensure_ascii=False)
    f.write("\n")
with open(path, encoding="utf-8") as f:
    return json.load(f)
```

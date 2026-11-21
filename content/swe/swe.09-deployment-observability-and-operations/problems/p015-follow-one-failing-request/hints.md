## Hint 1

Do it in the same order as the tutorial: first keep only the lines that belong to the request (what must you do with lines that are not JSON, or JSON that is not an object?), then put them in time order, then answer the two questions "where did it fail first?" and "which services did it pass?".

## Hint 2

```text
events = []
for line in lines:
    try: data = json.loads(line) except (TypeError, ValueError): continue
    if not a dict or data.get("request_id") != request_id: continue
    events.append({"ts": data.get("ts", ""), "service": data.get("service", "unknown"), "level": data.get("level", ""), "msg": data.get("msg", "")})
events.sort(key=lambda e: e["ts"])
first_error = first event with level in ("ERROR", "CRITICAL") or None
services = distinct services in order of appearance
```

## Approach

```python
def trace_request(lines, request_id):
    events = []
    for line in lines:
        try:
            data = json.loads(line)
        except (TypeError, ValueError):
            continue
        if not isinstance(data, dict) or data.get("request_id") != request_id:
            continue
        events.append({"ts": data.get("ts", ""), "service": data.get("service", "unknown"),
                       "level": data.get("level", ""), "msg": data.get("msg", "")})
    events.sort(key=lambda event: event["ts"])
    first_error = next((event for event in events if event["level"] in ERROR_LEVELS), None)
    services = []
    for event in events:
        if event["service"] not in services:
            services.append(event["service"])
    return {"events": events, "first_error": first_error, "services": services}
```

This is the investigation pattern of chapter 8.4 as code: get the id, collect everything with that id from **every** service (8.5), read it in time order, find the first thing that went wrong. In the test data the first error in time is the **worker's** failure, not the web app's `unhandled error` that the customer saw: the cause is upstream of the symptom, which is why you follow the id instead of reading one service's log.

## Complexity

O(n) to filter and O(k log k) to sort the k matching events. For gigabytes of logs you let the log system (Loki, OpenSearch) filter by `request_id` and only post-process the result.

## Another way

The shell version: `cat web.log worker.log | jq -c --arg id "$ID" 'select(.request_id == $id)' | jq -s -c 'sort_by(.ts)'`. Distributed tracing tools (OpenTelemetry, Jaeger) add timing per step and draw the chain, but they start from the same idea: one id across all services.

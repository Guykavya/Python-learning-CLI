## Hint 1

Build a normal Python dict first, in the order you want, and call `json.dumps` once at the end. Which `json.dumps` arguments give compact output and make unknown objects printable? What does `json.dumps` do with a newline inside a string?

## Hint 2

```text
entry = {"ts": strftime(gmtime(record.created)) + f".{int(record.msecs):03d}Z",
         "level": ..., "logger": ..., "msg": record.getMessage(), "request_id": request_id_var.get()}
for key, value in getattr(record, "fields", {}).items():
    if key not in entry: entry[key] = value          # the fixed keys win
if record.exc_info: entry["exception"] = self.formatException(record.exc_info)
return json.dumps(entry, separators=(",", ":"), default=str)

configure_logging: handler = StreamHandler(stream or sys.stdout); handler.setFormatter(JsonFormatter())
                   root.handlers[:] = [handler]; root.setLevel(level)
```

## Approach

```python
class JsonFormatter(logging.Formatter):
    def format(self, record):
        entry = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)) + f".{int(record.msecs):03d}Z",
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": request_id_var.get(),
        }
        for key, value in (getattr(record, "fields", None) or {}).items():
            if key not in entry:
                entry[key] = value
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, separators=(",", ":"), default=str)


def configure_logging(level="INFO", stream=None):
    handler = logging.StreamHandler(stream or sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level)
```

Three choices worth noticing: the request id comes from a **context variable**, so any code anywhere can log it without passing it around (chapter 8.2); the traceback is **one string field**, never several log lines (otherwise `jq select(.request_id == $id)` would lose most of it); and `json.dumps` escapes every line break, so a malicious value cannot start a fake second record (log injection, swe.07 15.6).

## Complexity

O(size of the record) per line.

## Another way

The `python-json-logger` package (not installed here) provides the same formatter. The standard library alone is enough: `logging.Formatter` is designed to be subclassed. For the highest throughput services use a logger that writes JSON natively (for example `structlog`).

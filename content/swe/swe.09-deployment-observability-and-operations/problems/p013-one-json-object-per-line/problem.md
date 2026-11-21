# One JSON object per line

Chapter sections 5.1 (`logs.py`), 8.1 (from text to events) and 8.2 (the request ID). A log that a machine can search is **one JSON object per line**, with fixed field names, the **request id** on every line, and extra facts as fields (not formatted into the message). Write the formatter and the function that installs it.

## What to write

```python
request_id_var: ContextVar[str]          # default "-" (given in the starter)

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str: ...

def configure_logging(level: str = "INFO", stream=None) -> None: ...
```

`format(record)` returns **one line** of compact JSON (`separators=(",", ":")`) with these keys, in this order:

| Key | Value |
|---|---|
| `ts` | the time of the record in **UTC**: `YYYY-MM-DDTHH:MM:SS.mmmZ`, from `record.created` (seconds) and `record.msecs` (milliseconds, zero-padded to 3 digits) |
| `level` | `record.levelname` |
| `logger` | `record.name` |
| `msg` | `record.getMessage()` (the message with its `%s` arguments filled in) |
| `request_id` | `request_id_var.get()` |

Then, in this order:

- the **extra fields**: callers write `log.info("order created", extra={"fields": {"order_id": 7}})`, so the record has an attribute `fields` (a dict). Its items are added after the five keys above. A field whose name is one of the five fixed keys is **ignored** (a caller must not be able to forge `level` or `request_id`).
- if the record has exception information, an `exception` key with the formatted traceback as **one string** (use `self.formatException(record.exc_info)`; the newlines inside it are escaped by JSON, so the record is still one line). The `exception` key is added last.
- values that JSON cannot write (a `Path`, a `datetime`, an exception object) are written with `str()` (use `json.dumps(..., default=str)`).

`configure_logging(level, stream)` replaces the handlers of the **root logger** by one `StreamHandler(stream)` (`sys.stdout` when `stream` is `None`) that uses `JsonFormatter`, and sets the root level to `level`.

## Example

```python
request_id_var.set("demo-req-0001")
log.info("order created", extra={"fields": {"order_id": 7}})
# {"ts":"2026-11-09T07:13:20.115Z","level":"INFO","logger":"pagebound","msg":"order created","request_id":"demo-req-0001","order_id":7}
```

## Hint 1

`struct.pack(fmt, v1, v2, ...)` needs one value per code in the format (the `4s` and `8s` codes take
**bytes**). `struct.unpack(fmt, data)` needs exactly `struct.calcsize(fmt)` bytes and returns a tuple.
What happens to a 9-byte name with `8s`? Try it.

## Hint 2

For the name: `raw = name.encode("utf-8")`, check `len(raw) > 8`, pack `raw`. To unpack:
`raw.rstrip(b"\x00").decode("utf-8")`. For the file: read all bytes, unpack the header from the first
20, then check `len(body) == count * 20` before `struct.iter_unpack(RECORD, body)`.

## Hint 3

```
pack_header  -> struct.pack(HEADER, MAGIC, version, flags, count, timestamp)
unpack_header(data):
    if len(data) < 20: ValueError
    magic, version, flags, count, ts = struct.unpack(HEADER, data[:20])
    if magic != MAGIC: ValueError
    return dict(...)
write_file: open "wb"; write header with len(records); write pack_record for each
read_file:  open "rb"; data = read(); header = unpack_header(data); body = data[20:]
            check length; records = [decode(*t) for t in struct.iter_unpack(RECORD, body)]
```

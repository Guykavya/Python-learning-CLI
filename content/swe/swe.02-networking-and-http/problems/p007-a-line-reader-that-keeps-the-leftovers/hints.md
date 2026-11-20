## Hint 1

What state must the object remember between two calls? Where do the bytes of an unfinished line go?

## Hint 2

Keep a `bytes` buffer. Append each chunk, then take lines off the front as long as the buffer contains `b"\n"`. Decode a line only when it is complete, so a split UTF-8 character is whole by then.

## Hint 3

```text
buffer += chunk
while b"\n" in buffer:
    line, buffer = split at the first newline
    drop a trailing b"\r"
    result.append(line.decode("utf-8"))
if len(buffer) > 65536: raise ValueError
return result
```

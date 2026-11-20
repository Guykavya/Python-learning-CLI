# Split host and port

A client receives text like `example.com:8080` and must decide where to connect. Write

```python
split_hostport(text, scheme="http")   # -> (host, port)
```

Rules:

- `"example.com:8080"` gives `("example.com", 8080)`.
- Without a port, use the default of the scheme: `http` is 80, `https` is 443. Any other scheme with no port raises `ValueError`.
- An **IPv6** address must be in square brackets: `"[::1]:443"` gives `("::1", 443)` and `"[::1]"` gives `("::1", default)`. The brackets are removed from the host.
- Text with more than one colon and no brackets (`"::1"`, `"a:b:c"`) is ambiguous: `ValueError`.
- The port must be digits only and in `1..65535`: `"host:0"`, `"host:70000"`, `"host:http"`, `"host:"` raise `ValueError`.
- An empty host (`""`, `":80"`, `"[]:80"`) raises `ValueError`.
- Return the port as an `int`.

## Example

```python
split_hostport("localhost")                  # ("localhost", 80)
split_hostport("localhost", "https")         # ("localhost", 443)
split_hostport("example.com:8080")           # ("example.com", 8080)
split_hostport("[2001:db8::1]:9000")         # ("2001:db8::1", 9000)
```

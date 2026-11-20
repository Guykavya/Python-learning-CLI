# Path traversal and SSRF guards

Chapter sections 14.5 and 14.6, with "Try it: why resolve before checking?". Two features turn a text from the client into something your server **touches**: a file name (`GET /files?name=...`) and a URL (`POST /webhooks/test` with `{"url": ...}`). Both texts are untrusted. Write two guards in `solution.py`.

## 1. `safe_join(base, user_path)`

`base` is the upload folder (a `str` or `Path`), `user_path` is the client's text. Return a `Path` to the file the client asked for **only if it is inside `base`**; otherwise raise `PermissionError`.

- Join, then **resolve** (`Path.resolve()`: it removes `..` and follows symlinks), then compare with the resolved `base` using `is_relative_to`. Check the thing you will really open, not the text you were given.
- `..` segments that stay inside (`a/../b.txt`) are fine. `..` that leave the folder, absolute paths (`/etc/passwd`), and **symlinks inside `base` that point outside** are not.
- A sibling folder whose name starts like the base (`uploads-evil` next to `uploads`) is **outside**: a text `startswith` test would wrongly accept it.
- A name containing a NUL character (`"a\0b"`) raises `PermissionError`.
- The file does not have to exist (the caller reports 404 later). No file is opened or created.

## 2. `check_url(url, resolve)`

`resolve(host)` is a function **given to you** that returns the list of IP address texts for a host name (in production it wraps DNS; in the tests it is a fake, so nothing touches the network). `check_url` returns the **list of IP addresses it approved** (the ones the caller should connect to), or raises `UnsafeURL` (a subclass of `ValueError`, in the starter).

1. The scheme must be `http` or `https`. Anything else (`file`, `ftp`, `gopher`, `javascript`) raises `UnsafeURL` **without calling `resolve`**.
2. The URL needs a host name (`url.hostname` from `urllib.parse.urlparse`). The host in `user@host` is the part after the `@`, which `urlparse` already handles.
3. If the host is already an IP address text (`ipaddress.ip_address(host)` works, IPv6 in brackets included), use it as the only address and do not call `resolve`. Otherwise call `resolve(host)` **once**. If it raises `OSError` or returns an empty list, raise `UnsafeURL`.
4. **Every** address must be public: `ipaddress.ip_address(a).is_global`. An IPv4 address hidden in IPv6 (`::ffff:127.0.0.1`) is unwrapped with `.ipv4_mapped` first. One bad address in the list rejects the whole URL (DNS may return several).
5. Return the list of address texts exactly as they were given.

Resolve first, then check: host texts like `2130706433` or `0x7f000001` or a name such as `localtest.example` do not *look* dangerous, but the resolver turns them into `127.0.0.1`.

## Example

```text
safe_join("/srv/up", "docs/a.txt")        -> Path("/srv/up/docs/a.txt")
safe_join("/srv/up", "../secret.txt")      -> PermissionError
safe_join("/srv/up", "/etc/passwd")        -> PermissionError
check_url("https://hooks.example.com/pay", lambda h: ["93.184.216.34"])  -> ["93.184.216.34"]
check_url("https://hooks.example.com/pay", lambda h: ["10.0.0.5"])       -> raises UnsafeURL
check_url("file:///etc/passwd", resolve)   -> raises UnsafeURL   (resolve is never called)
```

The tests import `safe_join`, `check_url` and `UnsafeURL`.

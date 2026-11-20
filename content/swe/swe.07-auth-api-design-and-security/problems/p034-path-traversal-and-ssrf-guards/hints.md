## Hint 1

For the path: what is the *final* path that `open()` would use after `..` and symlinks are applied? Which `pathlib` method computes it? For the URL: what does the server finally connect to, a text or an address, and where does that address come from?

## Hint 2

`(Path(base) / user_path).resolve()` gives the final path, and `.is_relative_to(Path(base).resolve())` compares it with the folder. Why does `Path("/srv/up") / "/etc/passwd"` give `/etc/passwd`? For the URL: write the checks in the order of the statement (scheme, host, addresses) and ask for each step what would go wrong if you moved it later.

## Hint 3

```text
safe_join:
    if "\0" in user_path: raise PermissionError
    root = Path(base).resolve();  target = (root / user_path).resolve()
    if not target.is_relative_to(root): raise PermissionError
    return target

check_url:
    parts = urlparse(url); scheme in (http, https) else UnsafeURL; host = parts.hostname or raise
    try ip_address(host): addresses = [host]
    except ValueError: addresses = resolve(host)  (OSError or empty -> UnsafeURL)
    for each address: ip = ip_address(a); unwrap ipv4_mapped; if not ip.is_global: raise UnsafeURL
    return addresses
```

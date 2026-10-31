- Creating the client inside `__init__` (`self.client = HttpClient()`). That removes the seam.
- Asking the client twice (once to check, once to print). A fake that counts calls shows it; a real
  service may charge for it.
- Using `<`/`>` instead of `<=`/`>=` at the borders 5 and 30.
- Printing `21.5` as `22C` by rounding: the spec says "as the client gave it".
- Catching every exception (`except Exception`) and hiding real bugs as "no data". Catch `KeyError` only.

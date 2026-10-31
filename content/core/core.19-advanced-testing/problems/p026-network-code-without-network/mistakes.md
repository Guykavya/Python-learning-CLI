- `def fetch_title(url, http_get=default_get)`: the default is frozen when the function is defined, so
  `monkeypatch.setattr(solution, "default_get", fake)` has no effect on it.
- `from urllib.request import urlopen`: the module keeps its own reference, so patching
  `urllib.request.urlopen` does not reach it.
- Calling `http_get` twice (once for the status, once for the body).
- Letting `HTTPError` escape from `default_get`: a 404 is data for the caller, not a crash.
- Catching `Exception` around `json.loads`: only `ValueError` means bad JSON.
- A test that "works" because the real network happens to be reachable. The guard exists so that such
  a test fails everywhere, always.

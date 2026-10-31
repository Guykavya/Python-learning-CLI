# side_effect: test a retry loop

A mock can do more than return one value. Setting `side_effect` to a **list** makes each call
return the next item, and an item that is an exception **class or instance** is raised instead of
returned. That lets you script "fail, fail, succeed" without a real network.

```python
def fetch_with_retry(client, url, attempts=3):
    """Call client.get(url). Retry on ConnectionError: at most `attempts` calls in total.
    Other exceptions are not retried. After the last failure raise the last ConnectionError.
    attempts < 1 raises ValueError."""
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    last = None
    for _ in range(attempts):
        try:
            return client.get(url)
        except ConnectionError as error:
            last = error
    raise last
```

Write tests (`from target import fetch_with_retry`) using `Mock` and `side_effect` that check:
success at once; success on the last allowed attempt; all attempts fail (which error is raised,
how many calls); an error that is not a `ConnectionError` is raised at once; the `attempts` value is
honoured; `attempts=0` raises `ValueError`. Write at least 5 test functions. Eight buggy versions
are tried.

**Example**

```python
def test_recovers_on_second_try():
    client = Mock()
    client.get.side_effect = [ConnectionError("down"), "page"]
    assert fetch_with_retry(client, "http://x") == "page"
    assert client.get.call_count == 2
```

**How this is checked.** Your `solution.py` is a file of pytest tests. The checker copies it next
to the code above (saved as `target.py`) and runs real pytest, first on the **correct** code (all
your tests must pass), then on several **buggy copies** (at least one of your tests must fail on
each; the report names any bug that survives). To try your tests yourself, save the code as
`target.py` in your folder and run `python -m pytest solution.py -p no:cacheprovider`.

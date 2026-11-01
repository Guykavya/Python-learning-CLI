## Hint 1

`as_completed` gives you back **futures**, in finishing order. How will you know which URL a
finished future belongs to? Where does an exception raised in a worker show up again in your
code, and what should you do there?

## Hint 2

```
results = {}
with ThreadPoolExecutor(max_workers=workers) as ex:
    future_to_url = {ex.submit(fetch, url): url for url in urls}   # submit ALL first
    for fut in as_completed(future_to_url):
        url = future_to_url[fut]
        try:
            results[url] = fut.result()
        except Exception as exc:
            results[url] = exc
return results
```

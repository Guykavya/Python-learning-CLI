## Hint 1

Which numbers must the registry remember? Make a list: how many requests per `(method, route, status)`, and for each `(method, route)` the sum, the count and one counter per bucket. Which Python container makes "add one to a key that may not exist yet" easy?

## Hint 2

```text
observe: lock; requests[(method, route, str(status))] += 1
         key = (method, route); sums[key] += seconds; counts[key] += 1
         for each bucket i with seconds <= BUCKETS[i]: bucket_counts[key][i] += 1     # cumulative!
observe_request: route = getattr(scope.get("route"), "path", "unmatched"); observe(scope["method"], route, ...)
render: HELP/TYPE lines, then sorted counter lines, then for each (method, route): the buckets, +Inf, _sum (:.6f), _count, then the gauge
```

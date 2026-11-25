## Approach

Separate the numbers (`describe`) from the words (`report`): the report calls `describe` and only formats. That is the design of the chapter's project: a function that returns a dict is easy to test, and the text is a thin layer on top.

## Code

```python
import statistics


def _quartiles(data):
    if len(data) == 1:
        return data[0], data[0]
    q1, _, q3 = statistics.quantiles(data, n=4, method="inclusive")
    return q1, q3


def describe(values):
    data = [v for v in values if v is not None]
    missing = len(values) - len(data)
    if not data:
        raise ValueError("no values to describe")
    n = len(data)
    mean = statistics.fmean(data)
    median = statistics.median(data)
    q1, q3 = _quartiles(data)
    spread = statistics.pstdev(data)
    return {
        "n": n,
        "missing": missing,
        "mean": mean,
        "median": median,
        "sd": statistics.stdev(data) if n > 1 else None,
        "min": min(data),
        "q1": q1,
        "q3": q3,
        "max": max(data),
        "iqr": q3 - q1,
        "skew_hint": (mean - median) / spread if spread else 0.0,
    }


def report(name, values, unit=""):
    s = describe(values)
    u = f" {unit}" if unit else ""
    sd_text = "n/a" if s["sd"] is None else f"{s['sd']:.1f}"
    if abs(s["mean"] - s["median"]) > 0.10 * abs(s["median"]):
        advice = "report the median (the mean and the median differ by more than 10%)"
    else:
        advice = "either centre is fine"
    lines = [
        f"{name}  (n = {s['n']}, missing = {s['missing']})",
        "-" * 40,
        f"centre : mean {s['mean']:.1f}{u}   median {s['median']:.1f}{u}",
        f"spread : sd {sd_text}   IQR {s['iqr']:.1f}",
        f"range  : {s['min']:.1f} to {s['max']:.1f}",
        f"advice : {advice}",
    ]
    return "\n".join(lines)

```

## Complexity

O(n log n) (sorting inside `median` and `quantiles`).

## Another way

pandas' `Series.describe()` gives a similar table (da.03), but it silently drops missing values and uses the exclusive-style linear percentiles by a different default; writing your own makes the choices visible.

# Back-of-the-envelope estimates

Chapter sections 13.2 (requirements), 13.3 (back-of-the-envelope estimates), 13.4 (numbers worth remembering) and "Try it: size a small product". Before you draw any boxes you need the order of magnitude of the load: how many requests per second, and how much data. You do not need three decimals; you need to know whether the answer is "one small server" or "a cluster". A few facts make it fast: a day has 86,400 seconds, traffic is not flat (**peak is typically 2 to 5 times the average**), and the read-to-write ratio comes from the product (a feed is read 100 times for each post written).

## What to write

```python
def estimate(dau, writes_per_user, reads_per_write, bytes_per_item, years, peak_factor) -> dict: ...
```

- `dau`: daily active users. `writes_per_user`: how many items (writes) one active user creates **per day**. `reads_per_write`: how many reads the product serves for each write. `bytes_per_item`: the size of one stored item. `years`: how long data is kept. `peak_factor`: peak load divided by average load.
- Return a dict with exactly these keys:

| Key | Meaning | Formula | Rounded to |
|---|---|---|---|
| `avg_write_qps` | average writes per second | `dau * writes_per_user / 86_400` | 2 decimals |
| `peak_write_qps` | peak writes per second | `avg_write_qps * peak_factor` (use the **unrounded** average) | 2 decimals |
| `avg_read_qps` | average reads per second | `avg_write_qps * reads_per_write` (unrounded) | 2 decimals |
| `peak_read_qps` | peak reads per second | `avg_read_qps * peak_factor` (unrounded) | 2 decimals |
| `storage_gb` | data after `years` | `dau * writes_per_user * 365 * years * bytes_per_item / 1e9` | 1 decimal |

Round **only at the end**, so the rounding of one number never feeds another. Raise `ValueError` for a negative number, for `years <= 0`, or for `peak_factor < 1` (the peak cannot be below the average).

## Example

Taskboard as a small team product: 20,000 daily users, 4 writes each per day, 9 reads for every write, 1,000 bytes per item, kept 3 years, peak 3 times the average:

```python
estimate(20_000, 4, 9, 1_000, 3, 3)
# {'avg_write_qps': 0.93, 'peak_write_qps': 2.78, 'avg_read_qps': 8.33, 'peak_read_qps': 25.0, 'storage_gb': 87.6}
```

Read it as a decision (chapter 13.3): a few dozen requests per second at peak and under 100 GB means **one database server and two app servers are plenty**; anything fancier is waste.

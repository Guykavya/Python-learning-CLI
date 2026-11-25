# Birthday problem: formula and simulation

Chapter section 9.3. In a group of `k` people, what is the chance that **at least two share a birthday** (365 equally likely days, ignore leap years)? Count the opposite: the chance that all `k` birthdays differ is `(365/365) (364/365) ... ((365 - k + 1)/365)`.

Write two functions:

- `p_shared_birthday(k)`: the exact probability (for `k > 365` it is `1.0`);
- `simulate_birthday(k, trials, seed)`: estimate it by simulation. Create `rng = np.random.default_rng(seed)`, draw `trials` groups of `k` random birthdays and return the share of groups that contain a repeated day.

## Example

```text
p_shared_birthday(23)  ->  0.5073      (more than half, with only 23 people)
```

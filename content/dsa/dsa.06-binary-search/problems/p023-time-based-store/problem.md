# Time-based key-value store

Implement a store that remembers values over time. Commands come one per line:

- `set key value time`: store `value` for `key` at that time. For one key the times of `set` commands are **strictly increasing** in the input.
- `get key time`: print the value that `key` had at that time: the value of the `set` with the **largest time `<= time`**. Print `NONE` if the key has no such `set`.

Keys and values are words without spaces. Per key keep a list of times and a list of values; a `get` is an upper bound search on the times.
`bisect` is not allowed (write the search yourself).

## Input

- Line 1: `q`, the number of commands. Then `q` lines, each a `set` or a `get`.

## Output

One line for every `get`, in order.

## Constraints

- `1 <= q <= 200000`, times between `1` and `10^9`

## Example

Input:

```
7
set love high 10
set love low 20
get love 5
get love 10
get love 15
get love 25
get fun 3
```

Output:

```
NONE
high
high
low
NONE
```

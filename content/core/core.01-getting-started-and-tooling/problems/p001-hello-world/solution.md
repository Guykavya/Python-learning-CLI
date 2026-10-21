## Approach

Each `print` call writes its text and then a newline. Two lines of output need
two calls. Text values (strings) must be inside quotes.

## Code

```python
print("Hello, World!")
print("I am learning Python.")
```

## Why it works

Without quotes, Python would read `Hello` as a variable name and stop with a
`NameError`. The quotes make it a string literal. `print` adds `"\n"` at the end
by default, so the second call starts on a new line.

## Another way

One call with an explicit newline character: `print("Hello, World!\nI am learning Python.")`.
It works, but two calls are easier to read.

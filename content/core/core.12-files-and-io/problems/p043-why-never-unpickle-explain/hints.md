## Hint 1

When you call `pickle.load`, does Python only copy values out of the file, or does it execute something?
What kind of instruction could "rebuild an object" need? Think: "call this class or function with these arguments".

## Hint 2

Four parts: (1) a pickle is a list of instructions, `load` runs them; (2) the file can name any importable
callable, example `print`, a real attacker would pick a harmful one; (3) json has only plain data types, so it
cannot call anything, but it also cannot keep tuples, sets or bytes; (4) use json for outside data, or check an
`hmac` signature before loading.

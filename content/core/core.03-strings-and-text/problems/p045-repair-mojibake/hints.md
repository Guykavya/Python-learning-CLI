## Hint 1

How was the garbled text made? Write the two steps that turned `café` into `cafÃ©`.

## Hint 2

It was `"café".encode("utf-8").decode("latin-1")`. To undo it, do the opposite steps in reverse order.

## Hint 3

```
garbled = input()
fixed = garbled.encode("latin-1").decode("utf-8")
print("Fixed:", fixed)
print("Shorter by:", len(garbled) - len(fixed))
```

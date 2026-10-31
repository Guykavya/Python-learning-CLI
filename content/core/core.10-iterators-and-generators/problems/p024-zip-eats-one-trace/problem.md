# Trace: zip and the lost item

`zip` stops when its shortest input is finished. But **how** does it find out that an input is
finished, and what happens to the other inputs at that moment?

Predict the exact output. The only difference between the two halves is the **order** of the
arguments to `zip`.

```python
def numbers():
    for n in [1, 2, 3, 4, 5]:
        print("give", n)
        yield n


letters = ["a", "b"]

it = numbers()
for pair in zip(it, letters):
    print(pair)
print("left:", list(it))

print("---")
it = numbers()
for pair in zip(letters, it):
    print(pair)
print("left:", list(it))
```

Write exactly what the program prints, one line for each printed line, in `answer.txt`.
The program never stops with an error, so you never need to write a traceback.

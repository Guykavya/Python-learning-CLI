# The order of except, else and finally

Predict **exactly** what this program prints. Use the diagram in chapter section 8: for each
call, decide whether the `try` block finishes normally, raises a handled exception, or raises an
unhandled one.

```python
def convert(text):
    print("start", repr(text))
    try:
        number = int(text)
    except ValueError:
        print("  except")
        number = 0
    else:
        print("  else", number)
    finally:
        print("  finally")
    print("  end", number)
    return number

total = 0
for t in ["4", "x", "-2"]:
    total += convert(t)
print("total", total)

try:
    convert(None)
except TypeError:
    print("TypeError reached the caller")
```

Write your answer in `answer.txt`, one line per printed line. Keep the leading spaces that some lines print.

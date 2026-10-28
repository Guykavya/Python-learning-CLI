# Duck-typed speakers

"If it walks like a duck and quacks like a duck, it is a duck." Python code usually does not ask
"what class are you?". It just tries to use the object. Anything with a `speak()` method can speak,
whatever its class.

Write `make_noise(things)` in `solution.py`:

- `things` is a list of any objects.
- For each object that **has** a `speak` attribute, call `speak()` and collect the result.
- Skip objects that have **no** `speak` attribute.
- Return the list of results, in the original order.
- Use the **EAFP** style ("easier to ask forgiveness than permission"): try to get `thing.speak`, and
  catch `AttributeError` if it is missing.
- Careful: if `speak()` itself crashes with an `AttributeError` (a bug **inside** that method), that
  error must **not** be hidden. Only catch the error from *looking up* `speak`, not from calling it.

**Example**

```python
class Duck:
    def speak(self):
        return "Quack"

class Robot:
    def speak(self):
        return "Beep"

class Rock:
    pass

print(make_noise([Duck(), Rock(), Robot(), "text", Duck()]))
# ['Quack', 'Beep', 'Quack']
```

# Explain: why you must never unpickle unknown data

Your teammate Anil stores the state of a program with `pickle`:

```python
import pickle

with open("state.pkl", "wb") as f:
    pickle.dump({"user": "anil", "scores": (3, 5)}, f)

with open("state.pkl", "rb") as f:
    state = pickle.load(f)
```

He wants to let users upload their own `state.pkl` files and read them with `pickle.load`.
You tell him not to.

In `answer.md` (about 150 to 300 words), explain:

1. What a pickle file really contains: is it only data, or more than that? Say what `pickle.load` does while
   it reads the file.
2. Why an attacker who controls the file controls your program. Describe, in words (no real attack code), what
   the file can ask Python to call. Give a **harmless** example of such a call.
3. Why `json` does not have this problem, and one thing `pickle` can keep that `json` cannot.
4. Two safe ways to handle the upload (for example a different format, or a signature).

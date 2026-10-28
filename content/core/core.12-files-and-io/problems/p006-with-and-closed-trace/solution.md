## Approach

A freshly opened file is not closed (`False`). After `close()` it is `True`. Writing to a closed file raises `ValueError`, which the program catches and reports. Inside the first `with`, `g.closed` is `False`; after it, `True`, and `first` holds `hello`. In the second `with`, the error is raised, but `with` closes the file on the way out, so the `except` prints `caught boom` and afterwards `h.closed` is `True`. The `name` attribute stays: `demo.txt`.

## Output

```text
False
True
ValueError: file is closed
False
True
hello
caught boom
True
demo.txt
```

## Complexity

O(1).

## Another way

Remove the `with` and the `close()` from the first lines and call `print(f.closed)` again at the end. It stays `False` until you close it, or until Python collects the object. With `with`, you never have to remember.

# Simplify a Unix path

Write `simplify_path(path)`. `path` is an **absolute** Unix path (it starts with `/`). Return its simplest form (chapter section 7, "Simplify a file path"):

- `.` means "this directory": drop it;
- `..` means "the parent directory": go up one level, but going up from the root `/` stays at the root;
- several slashes in a row count as one;
- any other name, including `...` or `.hidden`, is an ordinary directory name;
- the result starts with exactly one `/`, has single slashes between names, and no trailing slash (except the root itself, `/`).

## Example

```python
>>> simplify_path("/a/./b/../../c/")
'/c'
>>> simplify_path("/home//kavya/")
'/home/kavya'
>>> simplify_path("/../")
'/'
>>> simplify_path("/.../a/../b")
'/.../b'
```

`/a/./b/../../c/`: enter `a`, stay, enter `b`, go up (back in `a`), go up (back in `/`), enter `c`.

## Constraints

- `1 <= len(path) <= 3000`; names contain letters, digits, `.` and `_`.

## Think about

What does `"/a//b/".split("/")` return? Which of its pieces can you simply skip?

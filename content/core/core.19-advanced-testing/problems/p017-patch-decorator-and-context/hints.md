## Hint 1

`backup` looks up `os` and `shutil` inside the module `target`. So where must you patch: `os.path.exists`
or `target.os.path.exists`? (Both reach the same function here, but think about which name the code
under test uses.) What does `exists` have to return for the "happy path" and for the missing file?

## Hint 2

For the happy path set `exists` to return `True` (`return_value=True`) and check the call on the copy
mock. For the missing file set it to `False`, expect `FileNotFoundError`, and assert `copy_mock.assert_not_called()`.

## Hint 3

```
@patch("target.shutil.copy")                # decorator form
@patch("target.os.path.exists", return_value=True)
def test_happy(exists_mock, copy_mock): result = backup(P); copy_mock.assert_called_once_with(P, P + ".bak"); result == P + ".bak"

def test_missing():                          # context manager form
    with patch("target.os.path.exists", return_value=False), patch("target.shutil.copy") as copy_mock:
        with pytest.raises(FileNotFoundError): backup(P)
        copy_mock.assert_not_called()
```

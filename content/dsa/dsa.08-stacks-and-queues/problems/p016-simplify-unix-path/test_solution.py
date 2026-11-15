import pytest

from solution import simplify_path


@pytest.mark.parametrize("path, want, why", [
    ("/a/./b/../../c/", "/c", "the example"),
    ("/home/", "/home", "no trailing slash"),
    ("/home//kavya/", "/home/kavya", "several slashes count as one"),
    ("/../", "/", "going up from the root stays at the root: do not pop an empty stack"),
    ("/", "/", "the root itself"),
    ("///", "/", "only slashes"),
    ("/.", "/", "a single dot is the current directory"),
    ("/...", "/...", "three dots is an ordinary name"),
    ("/.../a/../b", "/.../b", "... is a name, .. goes up"),
    ("/.hidden/./x", "/.hidden/x", "a name may start with a dot"),
    ("/a/../../b/../c//.//", "/c", "several ups, one too many"),
    ("/a/b/c/../../..", "/", "going all the way back up"),
    ("/a/b/c/../..", "/a", "up twice"),
    ("/x_1/y.z/..", "/x_1", "names with _ and ."),
])
def test_cases(path, want, why):
    try:
        got = simplify_path(path)
    except IndexError:
        raise AssertionError(f"simplify_path({path!r}) crashed: check that the stack is not empty before popping on '..'.") from None
    assert got == want, f"simplify_path({path!r}) should be {want!r}, got {got!r}: {why}."


def test_long_path():
    path = "/" + "/".join(f"d{i}" for i in range(500)) + "/.." * 499
    assert simplify_path(path) == "/d0", "500 directories and 499 times '..' leave only /d0."

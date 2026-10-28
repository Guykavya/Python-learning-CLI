from solution import strip_result


def read_name(raw):
    """Return the part after the colon."""
    return raw.split(":")[1]


def test_still_strips():
    f = strip_result(read_name)
    assert f("id: Ann  ") == "Ann", "The wrapper must still strip the result. Keep `.strip()` on the returned text."


def test_name_kept():
    f = strip_result(read_name)
    assert f.__name__ == "read_name", "__name__ is 'wrapper'. Put @functools.wraps(func) on the line above `def wrapper`."


def test_doc_kept():
    f = strip_result(read_name)
    assert f.__doc__ == "Return the part after the colon.", "The docstring was lost. functools.wraps(func) copies __doc__ to the wrapper."


def test_wrapped_points_to_original():
    f = strip_result(read_name)
    assert getattr(f, "__wrapped__", None) is read_name, "f.__wrapped__ should be the original function. wraps sets it; did you pass func to wraps?"


def test_still_a_new_function():
    f = strip_result(read_name)
    assert f is not read_name, "Return the wrapper, not func itself. wraps copies the metadata; it does not replace the wrapper."


def test_keywords_pass_through():
    @strip_result
    def pad(text, width=6):
        """Pad text."""
        return text.center(width)

    assert pad("ab", width=10) == "ab", "Keyword arguments must reach the original function."
    assert pad.__qualname__.endswith("pad"), "__qualname__ is copied by wraps too."

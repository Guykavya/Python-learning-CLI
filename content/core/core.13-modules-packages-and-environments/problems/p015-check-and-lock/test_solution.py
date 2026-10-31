from solution import make_lock

REQS = [
    ("requests", ">=2.31,<3"),
    ("flask", ""),
    ("numpy", ">=1.26"),
    ("numpy", "<2"),
    ("rich", ""),
]
INSTALLED = {"Flask": "3.0.2", "requests": "2.32.3", "numpy": "2.1.0", "Typing_Extensions": "4.12.2"}


def test_example():
    lock, problems = make_lock(REQS, INSTALLED)
    assert lock == ["flask==3.0.2", "requests==2.32.3"], (
        "Lock each required name whose requirements all pass, sorted by name. numpy fails '<2', rich is missing."
    )
    assert problems == ["numpy: 2.1.0 does not satisfy <2", "rich: not installed"], (
        "One problem per failing requirement, in requirement order, in the exact text format."
    )


def test_returns_tuple_of_lists():
    result = make_lock([], {})
    assert isinstance(result, tuple) and len(result) == 2, "Return a tuple (lock, problems)."
    assert result == ([], []), "No requirements give an empty lock and no problems."


def test_installed_names_are_normalised():
    lock, problems = make_lock([("typing-extensions", ">=4"), ("zope-interface", "")],
                               {"Typing_Extensions": "4.12.2", "zope.interface": "6.4"})
    assert problems == [], "pip freeze may print 'Typing_Extensions' or 'zope.interface'. Normalise installed names before looking up."
    assert lock == ["typing-extensions==4.12.2", "zope-interface==6.4"], "Use the normalised name in the lock line."


def test_numeric_comparison():
    lock, problems = make_lock([("django", ">=4.9")], {"django": "4.10.1"})
    assert lock == ["django==4.10.1"], "4.10.1 is newer than 4.9. Compare versions as tuples of ints, not as strings."
    assert problems == [], "4.10.1 satisfies >=4.9."


def test_not_installed():
    lock, problems = make_lock([("rich", ">=13")], {"Rich-Click": "1.8"})
    assert problems == ["rich: not installed"], "rich-click is a different package. Use 'name: not installed'."
    assert lock == [], "A missing package cannot be locked."


def test_failing_version_message():
    lock, problems = make_lock([("requests", ">=2.31,<3")], {"requests": "3.0.0"})
    assert problems == ["requests: 3.0.0 does not satisfy >=2.31,<3"], (
        "Message format: '<name>: <version> does not satisfy <specifier>' with the whole specifier."
    )
    assert lock == [], "A package with a problem is not locked."


def test_duplicate_name_needs_all_to_pass():
    lock, problems = make_lock([("numpy", "<2"), ("numpy", ">=1.26")], {"numpy": "1.26.4"})
    assert lock == ["numpy==1.26.4"], "Both numpy lines pass, so numpy is locked once, not twice."
    lock, problems = make_lock([("numpy", "<2"), ("numpy", ">=1.26")], {"numpy": "1.20.0"})
    assert lock == [], "If any line for a name fails, that name is not locked, even if an earlier line passed."
    assert problems == ["numpy: 1.20.0 does not satisfy >=1.26"], "Only the failing line becomes a problem."


def test_extra_installed_packages_ignored():
    lock, problems = make_lock([("flask", "")], {"flask": "3.0.2", "pip": "24.0", "setuptools": "70.0"})
    assert lock == ["flask==3.0.2"], "Only required packages go into the lock. Ignore everything else that is installed."


def test_lock_sorted_by_name():
    reqs = [("zstd", ""), ("attrs", ""), ("mypy", "")]
    lock, _ = make_lock(reqs, {"zstd": "1.5", "attrs": "23.2", "mypy": "1.10"})
    assert lock == ["attrs==23.2", "mypy==1.10", "zstd==1.5"], "Sort the lock lines by name."


def test_inputs_not_changed():
    reqs = [("flask", "")]
    installed = {"Flask": "3.0.2"}
    make_lock(reqs, installed)
    assert installed == {"Flask": "3.0.2"} and reqs == [("flask", "")], "Do not change the caller's list or dict. Build new ones."

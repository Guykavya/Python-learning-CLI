import pytest

from solution import CHECKS


def test_there_are_enough_checks():
    assert isinstance(CHECKS, list) and len(CHECKS) >= 4, f"Write at least 4 checks and list them in CHECKS; found {len(CHECKS)}"
    assert all(callable(check) for check in CHECKS), "Every item of CHECKS must be a function taking a repository."
    names = [check.__name__ for check in CHECKS]
    assert len(set(names)) == len(names), "Give every check its own name (and do not list one twice)."


def run(check, factory):
    """Run one check on a fresh repository. Return None if it passed, or the AssertionError message."""
    try:
        check(factory())
    except AssertionError as exc:
        return str(exc) or "(no message)"
    return None


def test_every_check_passes_on_the_honest_repositories(honest_repos):
    for name, factory in honest_repos.items():
        for check in CHECKS:
            failure = run(check, factory)
            assert failure is None, \
                f"{check.__name__} FAILED on the honest {name} ({failure}). A contract check must pass on every honest implementation: is the rule you check really part of the interface?"


def test_checks_use_only_the_interface_and_fail_with_assertions(lying_repos, honest_repos):
    for check in CHECKS:
        for factories in (honest_repos, lying_repos):
            for name, factory in factories.items():
                try:
                    check(factory())
                except AssertionError:
                    pass
                except Exception as exc:
                    pytest.fail(f"{check.__name__} raised {type(exc).__name__} on the {name}: {exc}. A check must only raise AssertionError (use add_member, is_member, members and assert).")


@pytest.mark.parametrize("liar, rule", [
    ("duplicating fake", "adding the same member twice must be the same as adding it once"),
    ("case-sensitive fake", "handles must be compared (and stored) without regard to case"),
    ("project-blind fake", "membership must be per project"),
])
def test_each_lying_fake_is_caught(lying_repos, liar, rule):
    factory = lying_repos[liar]
    catching = [check.__name__ for check in CHECKS if run(check, factory) is not None]
    assert catching, f"No check caught the {liar}. Write a check that fails when {rule}."


def test_failures_have_messages(lying_repos):
    for liar, factory in lying_repos.items():
        for check in CHECKS:
            failure = run(check, factory)
            assert failure != "(no message)", f"{check.__name__} fails on the {liar} without a message: every assert must say which rule was broken."

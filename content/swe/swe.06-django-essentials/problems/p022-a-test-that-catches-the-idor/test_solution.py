import pytest
from django.contrib.auth.models import User
from django.test import Client

from solution import Note, check_owner_only


def test_the_given_views_are_unchanged():
    from solution import urlpatterns
    assert len(urlpatterns) == 3, "Do not change the given urlpatterns or views: only write check_owner_only."


def test_check_passes_on_the_safe_view():
    try:
        check_owner_only(Client(), "/safe")
    except AssertionError as error:
        pytest.fail(f"Your check failed on the CORRECT view (/safe), so the check itself is wrong: {error}. "
                    "The owner must get 200 and see the text; the other user must get 404.")


def test_the_check_used_two_users_and_a_note():
    check_owner_only(Client(), "/safe")
    assert User.objects.count() >= 2, "A security rule needs two actors: create the owner AND another user."
    assert Note.objects.count() >= 1, "Create a Note owned by the first user, then ask for it as the other one."


def test_check_catches_the_idor():
    with pytest.raises(AssertionError):
        check_owner_only(Client(), "/leaky")
    # (pytest.raises fails with "DID NOT RAISE" if your check never asserts that the OTHER user is refused)


def test_check_also_catches_a_view_that_is_too_strict():
    with pytest.raises(AssertionError):
        check_owner_only(Client(), "/closed")
    # (if this fails: your check must also prove that the OWNER gets 200 with the note's text)


def test_the_failure_is_an_assertion_not_another_error():
    try:
        check_owner_only(Client(), "/leaky")
    except AssertionError as error:
        assert str(error) != "", "Give your assert a message that says what went wrong (who got which status)."
    except Exception as error:
        pytest.fail(f"The check must fail with an AssertionError (an assert), not {type(error).__name__}: {error}")

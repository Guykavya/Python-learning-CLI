import pytest

from solution import worth_retrying


@pytest.mark.parametrize("method", ["GET", "HEAD", "OPTIONS", "PUT", "DELETE", "get", "Put"])
@pytest.mark.parametrize("status", [408, 429, 500, 502, 503, 504, None])
def test_idempotent_methods_retry_transient_failures(method, status):
    assert worth_retrying(method, status) is True, f"{method} {status}: safe to repeat and transient: retry."


@pytest.mark.parametrize("status", [408, 429, 500, 502, 503, 504, None])
def test_post_and_patch_are_not_retried_without_a_key(status):
    assert worth_retrying("POST", status) is False, "POST may already have been processed: do not repeat it blindly."
    assert worth_retrying("patch", status) is False


@pytest.mark.parametrize("status", [408, 429, 500, 503, None])
def test_post_with_an_idempotency_key_is_retried(status):
    assert worth_retrying("POST", status, has_idempotency_key=True) is True
    assert worth_retrying("POST", status, True) is True


@pytest.mark.parametrize("status", [200, 201, 204, 301, 302, 304, 400, 401, 403, 404, 405, 409, 422, 501])
def test_other_statuses_are_never_retried(status):
    for method in ("GET", "PUT", "POST", "DELETE"):
        assert worth_retrying(method, status) is False, f"{method} {status} is not transient: do not retry."
        assert worth_retrying(method, status, True) is False

import os

import pytest

from solution import current_version, deploy


def ok(release_dir):
    return True


def bad(release_dir):
    return False


def test_a_healthy_deploy_goes_live(tmp_path):
    assert deploy(tmp_path, "1.0.0", {"app.txt": "v1", "app/main.py": "print(1)"}, ok) is True
    assert current_version(tmp_path) == "1.0.0"
    assert (tmp_path / "releases" / "1.0.0" / "app" / "main.py").read_text(encoding="utf-8") == "print(1)"


def test_the_previous_release_survives_a_healthy_deploy(tmp_path):
    deploy(tmp_path, "1.0.0", {"app.txt": "v1"}, ok)
    assert deploy(tmp_path, "1.1.0", {"app.txt": "v2"}, ok) is True
    assert current_version(tmp_path) == "1.1.0"
    assert (tmp_path / "releases" / "1.0.0" / "app.txt").read_text(encoding="utf-8") == "v1", \
        "The old release must NOT be deleted by a deploy: it is what a rollback goes back to (and it may be needed hours later)."


def test_failed_check_leaves_the_old_version_live_and_untouched(tmp_path):
    deploy(tmp_path, "1.0.0", {"app.txt": "v1"}, ok)
    assert deploy(tmp_path, "2.0.0", {"app.txt": "v2"}, bad) is False, "A failed health check: deploy returns False."
    assert current_version(tmp_path) == "1.0.0", "A failed health check must put the pointer back on the old version (users must not keep the broken release)."
    assert (tmp_path / "releases" / "1.0.0" / "app.txt").read_text(encoding="utf-8") == "v1", "The old release is intact and still there."


def test_a_check_that_raises_is_a_failure_too(tmp_path):
    deploy(tmp_path, "1.0.0", {"app.txt": "v1"}, ok)

    def boom(release_dir):
        raise ConnectionError("no answer")

    assert deploy(tmp_path, "1.1.0", {"app.txt": "v2"}, boom) is False, "An exception from the check is a failed check: return False, do not crash."
    assert current_version(tmp_path) == "1.0.0"


def test_first_deploy_failing_leaves_no_pointer(tmp_path):
    assert deploy(tmp_path, "1.0.0", {"app.txt": "v1"}, bad) is False
    assert current_version(tmp_path) is None and not (tmp_path / "current").exists(), \
        "With no previous version, a failed deploy must not leave the pointer naming the broken release."


def test_a_write_error_never_leaves_the_pointer_on_a_half_written_release(tmp_path):
    deploy(tmp_path, "1.0.0", {"app.txt": "v1"}, ok)
    with pytest.raises(OSError):
        deploy(tmp_path, "2.0.0", {"first": "a file", "first/second": "needs a folder"}, ok)
    assert current_version(tmp_path) == "1.0.0", "The release could not be written: the pointer must not have moved (write the release BEFORE switching)."
    assert not (tmp_path / "releases" / "2.0.0").exists(), "No half-written release folder may be left under its final name."
    assert [p.name for p in (tmp_path / "releases").iterdir()] == ["1.0.0"], "No temporary folder may remain either."


def test_the_old_release_survives_a_write_error(tmp_path):
    deploy(tmp_path, "1.0.0", {"app.txt": "v1"}, ok)
    with pytest.raises(OSError):
        deploy(tmp_path, "2.0.0", {"first": "x", "first/second": "y"}, ok)
    assert (tmp_path / "releases" / "1.0.0" / "app.txt").read_text(encoding="utf-8") == "v1"


def test_pointer_and_release_are_published_with_os_replace(tmp_path, monkeypatch):
    destinations = []
    real = os.replace
    monkeypatch.setattr(os, "replace", lambda a, b: (destinations.append(os.path.basename(str(b))), real(a, b))[1])
    deploy(tmp_path, "1.0.0", {"app.txt": "v1"}, ok)
    assert "1.0.0" in destinations, "Publish the release folder with os.replace from a temporary folder."
    assert "current" in destinations, "Switch the pointer with a temporary file and os.replace."


def test_the_check_sees_the_new_version_live(tmp_path):
    deploy(tmp_path, "1.0.0", {"app.txt": "v1"}, ok)
    seen = []
    deploy(tmp_path, "1.1.0", {"app.txt": "v2"}, lambda d: seen.append((current_version(tmp_path), d.name)) or True)
    assert seen == [("1.1.0", "1.1.0")], "The health check runs after the switch, with the release folder."


def test_two_failures_in_a_row_still_serve_the_last_good_version(tmp_path):
    deploy(tmp_path, "1.0.0", {"app.txt": "v1"}, ok)
    deploy(tmp_path, "1.1.0", {"app.txt": "v2"}, bad)
    deploy(tmp_path, "1.2.0", {"app.txt": "v3"}, bad)
    assert current_version(tmp_path) == "1.0.0"
    assert (tmp_path / "releases" / "1.0.0" / "app.txt").read_text(encoding="utf-8") == "v1"

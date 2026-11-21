import os

import pytest

from solution import current_version, deploy


def ok(release_dir):
    return True


def bad(release_dir):
    return False


def releases(root):
    folder = root / "releases"
    return sorted(p.name for p in folder.iterdir()) if folder.exists() else []


def test_first_deploy(tmp_path):
    result = deploy(tmp_path, "1.0.0", {"app.txt": "v1", "app/main.py": "print(1)"}, ok)
    assert result == {"version": "1.0.0", "status": "live", "live": "1.0.0", "error": None}, f"A healthy deploy is live; got {result}"
    assert current_version(tmp_path) == "1.0.0", "The pointer file 'current' names the live version."
    assert (tmp_path / "releases" / "1.0.0" / "app" / "main.py").read_text(encoding="utf-8") == "print(1)", "Nested files are written under the release folder."
    assert (tmp_path / "history.txt").read_text(encoding="utf-8").split() == ["1.0.0"]


def test_current_version_without_pointer(tmp_path):
    assert current_version(tmp_path) is None, "No pointer file yet: None."


def test_second_deploy_keeps_the_first_release(tmp_path):
    deploy(tmp_path, "1.0.0", {"app.txt": "v1"}, ok)
    result = deploy(tmp_path, "1.1.0", {"app.txt": "v2"}, ok)
    assert result["live"] == "1.1.0" and current_version(tmp_path) == "1.1.0"
    assert releases(tmp_path) == ["1.0.0", "1.1.0"], "The previous release stays, ready for a rollback (immutable images, chapter 12.1)."
    assert (tmp_path / "releases" / "1.0.0" / "app.txt").read_text(encoding="utf-8") == "v1"


def test_the_pointer_is_switched_before_the_health_check(tmp_path):
    deploy(tmp_path, "1.0.0", {"a": "1"}, ok)
    seen = []

    def check(release_dir):
        seen.append((current_version(tmp_path), release_dir))
        return True

    deploy(tmp_path, "1.1.0", {"a": "2"}, check)
    assert seen == [("1.1.0", tmp_path / "releases" / "1.1.0")], \
        f"The health check runs AFTER the switch (like the chapter's script, which checks the running service) and receives the release folder; got {seen}"


def test_failed_check_rolls_back_and_keeps_the_evidence(tmp_path):
    deploy(tmp_path, "1.0.0", {"app.txt": "v1"}, ok)
    result = deploy(tmp_path, "2.0.0", {"app.txt": "v2"}, bad)
    assert result == {"version": "2.0.0", "status": "rolled_back", "live": "1.0.0", "error": "health check failed"}, f"Got {result}"
    assert current_version(tmp_path) == "1.0.0", "The old version is live again."
    assert (tmp_path / "releases" / "1.0.0" / "app.txt").read_text(encoding="utf-8") == "v1", "The old release is untouched."
    assert (tmp_path / "releases" / "2.0.0" / "app.txt").read_text(encoding="utf-8") == "v2", "The failed release folder stays for inspection."


def test_a_health_check_that_raises_is_a_failure(tmp_path):
    deploy(tmp_path, "1.0.0", {"a": "1"}, ok)

    def boom(release_dir):
        raise ConnectionError("service did not answer")

    result = deploy(tmp_path, "1.1.0", {"a": "2"}, boom)
    assert result["status"] == "rolled_back" and result["live"] == "1.0.0", "An exception in the check is a failed check, not a crash of the deploy."
    assert result["error"] == "ConnectionError: service did not answer", f"error is 'ExceptionName: message'; got {result['error']!r}"
    assert current_version(tmp_path) == "1.0.0"


def test_first_deploy_that_fails_has_nothing_to_go_back_to(tmp_path):
    result = deploy(tmp_path, "1.0.0", {"a": "1"}, bad)
    assert result == {"version": "1.0.0", "status": "failed", "live": None, "error": "health check failed"}
    assert current_version(tmp_path) is None and not (tmp_path / "current").exists(), "No previous version: the pointer is removed, it must not name a broken release."
    assert releases(tmp_path) == ["1.0.0"], "The failed release stays for inspection."


def test_two_failures_in_a_row_leave_the_last_good_version_live(tmp_path):
    deploy(tmp_path, "1.0.0", {"a": "1"}, ok)
    deploy(tmp_path, "1.1.0", {"a": "2"}, bad)
    result = deploy(tmp_path, "1.2.0", {"a": "3"}, bad)
    assert result["live"] == "1.0.0" and current_version(tmp_path) == "1.0.0", \
        "The second failure must roll back to the last GOOD version (1.0.0), not to the failed 1.1.0."
    assert releases(tmp_path) == ["1.0.0", "1.1.0", "1.2.0"]


def test_recovery_after_a_failure(tmp_path):
    deploy(tmp_path, "1.0.0", {"a": "1"}, ok)
    deploy(tmp_path, "1.1.0", {"a": "2"}, bad)
    assert deploy(tmp_path, "1.1.1", {"a": "3"}, ok)["live"] == "1.1.1", "After a failure the next good version goes live as usual."


def test_pruning_keeps_the_newest_releases(tmp_path):
    for n in range(1, 9):
        deploy(tmp_path, f"1.{n}.0", {"a": str(n)}, ok, keep=5)
    assert releases(tmp_path) == [f"1.{n}.0" for n in range(4, 9)], "Keep the 5 newest release folders; delete the oldest by deploy order (1.10 would sort before 1.9 by name)."


def test_pruning_never_deletes_the_live_release(tmp_path):
    deploy(tmp_path, "1.0.0", {"a": "1"}, ok, keep=3)
    for n in range(1, 7):
        deploy(tmp_path, f"2.{n}.0", {"a": str(n)}, bad, keep=3)
    assert current_version(tmp_path) == "1.0.0" and "1.0.0" in releases(tmp_path), \
        "The live release is the OLDEST folder here, but it must never be pruned: six failed deploys pushed it out of the 'newest 3'."
    assert len(releases(tmp_path)) == 3, f"keep=3 means three folders in total, including the live one; got {releases(tmp_path)}"


def test_pruning_orders_by_deploy_time_not_by_name(tmp_path):
    for version in ("1.9.0", "1.10.0", "1.11.0", "1.12.0"):
        deploy(tmp_path, version, {"a": "x"}, ok, keep=3)
    assert releases(tmp_path) == ["1.10.0", "1.11.0", "1.12.0"], \
        "1.9.0 was deployed first, so it is the oldest and must be pruned, although '1.9.0' sorts AFTER '1.10.0' as text. Use the order of history.txt."


def test_releases_are_immutable(tmp_path):
    deploy(tmp_path, "1.0.0", {"a": "original"}, ok)
    with pytest.raises(ValueError):
        deploy(tmp_path, "1.0.0", {"a": "changed"}, ok)
    assert (tmp_path / "releases" / "1.0.0" / "a").read_text(encoding="utf-8") == "original", "Deploying an existing version must not touch it."


@pytest.mark.parametrize("version", ["", "../x", "a/b", ".hidden", "v 1", "1.0.0/..", "a\\b"])
def test_bad_versions_are_refused_before_anything_is_written(tmp_path, version):
    with pytest.raises(ValueError):
        deploy(tmp_path, version, {"a": "1"}, ok)
    assert releases(tmp_path) == [] and current_version(tmp_path) is None, "Validation comes first: nothing may be created."


@pytest.mark.parametrize("path", ["/etc/passwd", "../outside.txt", "a/../../b", "", "\\windows\\x"])
def test_bad_file_paths_are_refused(tmp_path, path):
    with pytest.raises(ValueError):
        deploy(tmp_path, "1.0.0", {"ok.txt": "1", path: "x"}, ok)
    assert releases(tmp_path) == [], "A path that could escape the release folder is refused before any file is written."
    assert not (tmp_path.parent / "outside.txt").exists()


def test_a_write_error_leaves_nothing_half_written(tmp_path):
    deploy(tmp_path, "1.0.0", {"a": "1"}, ok)
    with pytest.raises(OSError):
        deploy(tmp_path, "2.0.0", {"conflict": "a file", "conflict/inside": "needs a folder"}, ok)
    assert releases(tmp_path) == ["1.0.0"], "No release folder and no .tmp folder may remain after a write error."
    assert current_version(tmp_path) == "1.0.0", "The pointer never moved."


def test_pointer_is_written_atomically(tmp_path, monkeypatch):
    calls = []
    real = os.replace
    monkeypatch.setattr(os, "replace", lambda a, b: (calls.append(os.path.basename(str(b))), real(a, b))[1])
    deploy(tmp_path, "1.0.0", {"a": "1"}, ok)
    assert "current" in calls, "Switch the pointer with a temporary file and os.replace, so a reader never sees a half-written pointer."
    assert "1.0.0" in calls, "Publish the release folder with os.replace too."


def test_a_release_can_have_no_files(tmp_path):
    assert deploy(tmp_path, "1.0.0", {}, ok)["status"] == "live" and (tmp_path / "releases" / "1.0.0").is_dir()

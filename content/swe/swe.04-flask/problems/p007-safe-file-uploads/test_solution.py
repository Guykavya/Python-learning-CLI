import io

import pytest

from solution import create_app


@pytest.fixture
def app(tmp_path):
    folder = tmp_path / "uploads"
    return create_app({"TESTING": True, "UPLOAD_FOLDER": str(folder), "MAX_CONTENT_LENGTH": 1000})


@pytest.fixture
def client(app):
    return app.test_client()


def send(client, name, content=b"data"):
    return client.post("/upload", data={"file": (io.BytesIO(content), name)}, content_type="multipart/form-data")


def files_in(app):
    from pathlib import Path
    folder = Path(app.config["UPLOAD_FOLDER"])
    return sorted(p.name for p in folder.iterdir()) if folder.exists() else []


def test_normal_upload(client, app):
    r = send(client, "notes.txt", b"hello")
    assert r.status_code == 201, f"A good upload must give 201, got {r.status_code}: {r.get_data(as_text=True)[:80]}"
    assert r.get_json() == {"saved_as": "notes.txt"}
    from pathlib import Path
    assert (Path(app.config["UPLOAD_FOLDER"]) / "notes.txt").read_bytes() == b"hello", "The file must be saved in UPLOAD_FOLDER (create the folder if needed)."


def test_too_large_is_413(client, app):
    r = send(client, "big.txt", b"x" * 5000)
    assert r.status_code == 413, f"A body above MAX_CONTENT_LENGTH must give 413, got {r.status_code}. Is MAX_CONTENT_LENGTH set in the config?"
    assert files_in(app) == [], "Nothing may be saved when the upload is too large."


def test_default_limit_is_one_mebibyte():
    app = create_app({"TESTING": True})
    assert app.config["MAX_CONTENT_LENGTH"] == 1024 * 1024, "The factory default for MAX_CONTENT_LENGTH is 1024 * 1024."


def test_path_traversal_is_neutralised(client, app, tmp_path):
    r = send(client, "../../evil.txt")
    assert r.status_code == 201
    assert r.get_json() == {"saved_as": "evil.txt"}, f"secure_filename removes the directories, got {r.get_json()}"
    assert files_in(app) == ["evil.txt"]
    assert not (tmp_path.parent / "evil.txt").exists() and not (tmp_path / "evil.txt").exists(), "The file escaped the upload folder!"


def test_disallowed_extension(client, app):
    for name in ("run.py", "page.html", "README", "../../evil.py", "archive.txt.exe"):
        r = send(client, name)
        assert r.status_code == 400, f"{name!r} is not an allowed type; expected 400, got {r.status_code}."
        assert "error" in r.get_json()
    assert files_in(app) == [], "Rejected files must not be written."


def test_extension_check_ignores_case_and_the_name_is_cleaned(client):
    r = send(client, "my file (1).PDF")
    assert r.status_code == 201
    assert r.get_json() == {"saved_as": "my_file_1.PDF"}, f"got {r.get_json()}; use secure_filename for the final name."


def test_names_that_clean_to_nothing(client):
    r = send(client, "???")
    assert r.status_code == 400, "A name that secure_filename turns into '' must be refused."


def test_no_overwrite(client, app):
    from pathlib import Path
    assert send(client, "a.txt", b"one").get_json() == {"saved_as": "a.txt"}
    assert send(client, "a.txt", b"two").get_json() == {"saved_as": "a-1.txt"}
    assert send(client, "a.txt", b"three").get_json() == {"saved_as": "a-2.txt"}
    folder = Path(app.config["UPLOAD_FOLDER"])
    assert (folder / "a.txt").read_bytes() == b"one", "The first file was overwritten!"
    assert (folder / "a-1.txt").read_bytes() == b"two" and (folder / "a-2.txt").read_bytes() == b"three"


def test_missing_field_and_empty_filename(client):
    assert client.post("/upload", data={}, content_type="multipart/form-data").status_code == 400, "No 'file' field: 400, not a KeyError/500."
    r = client.post("/upload", data={"file": (io.BytesIO(b"x"), "")}, content_type="multipart/form-data")
    assert r.status_code == 400, "An empty filename (the browser sends it when no file is chosen) is a 400."

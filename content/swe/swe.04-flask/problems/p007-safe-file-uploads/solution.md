## Approach

Never use what the user sends as it is: bound the size, clean the name, check the type with an allow-list, and choose the final path yourself.

```python
from pathlib import Path

from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename

ALLOWED = {"png", "jpg", "txt", "pdf"}


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(MAX_CONTENT_LENGTH=1024 * 1024, UPLOAD_FOLDER="uploads")
    app.config.update(test_config or {})

    @app.post("/upload")
    def upload():
        file = request.files.get("file")
        if file is None or not file.filename:
            return jsonify(error="no file was sent"), 400
        name = secure_filename(file.filename)
        extension = name.rsplit(".", 1)[-1].lower() if "." in name else ""
        if not name or extension not in ALLOWED:
            return jsonify(error="file type not allowed"), 400
        folder = Path(app.config["UPLOAD_FOLDER"])
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / name
        stem, suffix = target.stem, target.suffix
        number = 1
        while target.exists():
            target = folder / f"{stem}-{number}{suffix}"
            number += 1
        file.save(target)
        return jsonify(saved_as=target.name), 201

    return app
```

Example: `../../evil.txt` becomes `evil.txt`, so the file lands in `UPLOAD_FOLDER` and not two directories above it. `archive.txt.exe` has the extension `exe` (the part after the **last** dot), so it is refused even though it contains `.txt`.

The size limit works because Flask reads the body lazily: once you access `request.files` (or `form`), Werkzeug stops at `MAX_CONTENT_LENGTH` and the request fails with 413.

## Complexity

`O(size of the file)` for saving; `O(k)` for `k` existing numbered copies of the same name (use a random prefix or a database id if that matters).

## Another way

Store files under a **generated name** (`uuid4().hex + ".png"`) and keep the original name only in the database. That avoids collisions and name tricks at once. Also check the real content (a PNG starts with a fixed byte signature); the extension is only a hint.

## Not covered

An extension check does not prove the content. A file named `x.png` could be a script. Never serve uploads from a folder that the server executes, and send `Content-Disposition: attachment` for types you do not display.

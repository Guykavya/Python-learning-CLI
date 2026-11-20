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
        file = request.files.get("file")          # reading request.files enforces MAX_CONTENT_LENGTH
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

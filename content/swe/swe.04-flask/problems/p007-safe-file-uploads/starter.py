import os

from flask import Flask, jsonify, request


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(UPLOAD_FOLDER="uploads")      # TODO: also MAX_CONTENT_LENGTH
    app.config.update(test_config or {})

    @app.post("/upload")
    def upload():
        file = request.files["file"]
        path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)   # TODO: dangerous
        file.save(path)
        return jsonify(saved_as=file.filename), 201

    return app

from flask import Flask, jsonify, request, url_for


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(test_config or {})
    notes = []

    @app.post("/api/notes")
    def create_note():
        if not request.is_json:
            return jsonify(error="Content-Type must be application/json"), 415
        data = request.get_json(silent=True)
        if data is None:
            return jsonify(error="Body is not valid JSON"), 400
        if not isinstance(data, dict):
            return jsonify(error="JSON body must be an object"), 400
        fields = {}
        title = data.get("title")
        if not isinstance(title, str) or not title.strip():
            fields["title"] = "is required and must be a non-empty string"
        elif len(title.strip()) > 100:
            fields["title"] = "must be at most 100 characters"
        body = data.get("body", "")
        if not isinstance(body, str):
            fields["body"] = "must be a string"
        if fields:
            return jsonify(error="validation failed", fields=fields), 422
        note = {"id": len(notes) + 1, "title": title.strip(), "body": body}
        notes.append(note)
        response = jsonify(note)
        response.status_code = 201
        response.headers["Location"] = url_for("get_note", note_id=note["id"])
        return response

    @app.get("/api/notes/<int:note_id>")
    def get_note(note_id):
        for note in notes:
            if note["id"] == note_id:
                return jsonify(note)
        return jsonify(error="not found"), 404

    return app

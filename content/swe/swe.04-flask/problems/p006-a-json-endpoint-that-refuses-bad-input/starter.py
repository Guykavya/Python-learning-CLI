from flask import Flask, jsonify, request


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(test_config or {})
    notes = []

    @app.post("/api/notes")
    def create_note():
        data = request.get_json()             # TODO: this answers with HTML pages when the input is bad
        note = {"id": len(notes) + 1, "title": data["title"], "body": data.get("body", "")}
        notes.append(note)
        return jsonify(note), 201

    @app.get("/api/notes/<int:note_id>")
    def get_note(note_id):
        for note in notes:
            if note["id"] == note_id:
                return jsonify(note)
        return jsonify(error="not found"), 404

    return app

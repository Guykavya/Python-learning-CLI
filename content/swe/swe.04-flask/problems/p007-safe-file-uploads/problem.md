# Safe file uploads

Chapter section 4.4. An upload is **user-controlled data on your disk**. In `solution.py` write `create_app(test_config=None)` with `POST /upload` (multipart form, field `file`). Defaults in the factory: `MAX_CONTENT_LENGTH = 1024 * 1024` and `UPLOAD_FOLDER = "uploads"`; `test_config` overrides them (the tests point the folder at a temporary directory and shrink the limit).

Rules:

1. A request whose body is larger than `MAX_CONTENT_LENGTH` gets **413** (Flask does this for you once the config is set and `request.files` is read).
2. No `file` field, or an empty filename: **400** `{"error": "..."}`.
3. The name is cleaned with `werkzeug.utils.secure_filename`. If nothing is left, or the extension is not in the allow-list `png, jpg, txt, pdf` (case-insensitive): **400**. Nothing is written.
4. The file is saved **inside** `UPLOAD_FOLDER` (create the folder if it does not exist), under the cleaned name. An upload named `../../evil.txt` becomes `evil.txt` in the folder.
5. A file is **never overwritten**: if `a.txt` exists, save `a-1.txt`, then `a-2.txt`, and so on (the number goes before the extension).
6. Success: **201** `{"saved_as": "<final name>"}`.

## Example

```text
file "notes.txt"        -> 201 {"saved_as": "notes.txt"}
file "notes.txt" again  -> 201 {"saved_as": "notes-1.txt"}
file "../../evil.txt"   -> 201 {"saved_as": "evil.txt"}     (inside UPLOAD_FOLDER)
file "run.py"           -> 400
file "my file (1).PDF"  -> 201 {"saved_as": "my_file_1.PDF"}
```

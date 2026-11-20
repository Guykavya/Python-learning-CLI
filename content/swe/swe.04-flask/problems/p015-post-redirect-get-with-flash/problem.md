# Post/Redirect/Get with flash

Chapter sections 8.1 to 8.3. If a POST answers with a page, pressing **F5** sends the form again (a double order, a double comment). The cure is **Post/Redirect/Get**: after a successful POST, redirect to a GET page. In `solution.py` write `create_app(test_config=None)` for a feedback form (the `SECRET_KEY` is set for you in the starter, flash needs it):

- `GET /feedback` shows the form: inputs `name` and `message`.
- `POST /feedback` with `name` and `message` (both stripped):
  - `name` empty → error `Name is required`; `message` shorter than 10 characters → error `Message must have at least 10 characters`.
  - **Invalid:** answer **200** with the form again, every error shown in a `<p class="error">`, and the typed values still in the fields (escaped).
  - **Valid:** append `{"name":..., "message":...}` to the list `app.extensions["feedback"]` (the tests read it), `flash(f"Thanks, {name}!")` and **redirect** (`302`) to `/thanks`.
- `GET /thanks` shows each flashed message in `<p class="flash">`, and `Nothing to see` when there are none. A flash message is shown **once**: after the first visit it is gone.

The two templates are strings in the starter (`render_template_string`).

## Example

```text
POST /feedback name=Asha message="Great course, thank you"  -> 302 Location: /thanks
GET  /thanks                                                -> <p class="flash">Thanks, Asha!</p>
GET  /thanks (again)                                        -> Nothing to see
```

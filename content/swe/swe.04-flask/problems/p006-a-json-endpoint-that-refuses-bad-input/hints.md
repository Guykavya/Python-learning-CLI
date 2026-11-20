## Hint 1

Which attribute of `request` tells you the content type is JSON? And what does `request.get_json(silent=True)` return when the text cannot be parsed, instead of raising?

## Hint 2

Check from the outside in: content type, then parse, then shape (dict), then fields. Collect field problems in a dict instead of returning at the first one. For `Location`, build the response object first (`response = jsonify(note)`), then set `status_code` and `headers`.

## Hint 3

```text
if not request.is_json: return error, 415
data = request.get_json(silent=True)
if data is None: return error, 400
if not isinstance(data, dict): return error, 400
fields = {}
validate title (str, non-blank, <= 100) and body (str if present)
if fields: return {"error": "validation failed", "fields": fields}, 422
store; response 201 with Location = url_for("get_note", note_id=id)
```

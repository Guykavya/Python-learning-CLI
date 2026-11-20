## Hint 1

Which three things does the user control in an upload? The **size**, the **name** and the **type**. Which line of the starter trusts each of them?

## Hint 2

`MAX_CONTENT_LENGTH` goes into `app.config`; Flask checks it when you touch `request.files`. `secure_filename("../../evil.txt")` returns `"evil.txt"`. For the extension, take what comes after the last dot of the **cleaned** name and compare it, lower-cased, with a set. `Path.exists()` helps with the numbering.

## Hint 3

```text
file = request.files.get("file"); if missing or no filename -> 400
name = secure_filename(file.filename)
extension = text after the last "." in name, lower-case ("" when no dot)
if name == "" or extension not in ALLOWED -> 400
target = folder / name
while target.exists(): target = folder / f"{stem}-{n}{suffix}"; n += 1
file.save(target); return 201
```

## Hint 1

What are the two actors in the story? What must be true for each of them when they ask for the same note? Write the two expectations (status code and content) in plain words before writing code. A test that only looks at the second actor would pass on a view that refuses everybody: what does the first actor prove?

## Hint 2

Create `alice` and `bob` with `User.objects.create_user(name, password=...)` and `Note.objects.create(owner=alice, text="...")`. Build the URL from the note's `pk`. Then `client.force_login(alice)`, `client.get(url)`, `assert response.status_code == 200`; then `client.force_login(bob)` and ask again. Put a message on every assert that says who got which status.

## Hint 3

```text
alice, bob = two users; note = Note(owner=alice, text="alice-secret-...")
url = base + "/notes/" + pk + "/"
login as alice -> GET url -> assert 200 and the secret text in the page
login as bob   -> GET url -> assert 404 and the secret text NOT in the page
```

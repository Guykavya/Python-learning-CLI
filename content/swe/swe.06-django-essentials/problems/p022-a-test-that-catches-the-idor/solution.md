## Approach

A test for an authorisation rule needs two actors and two expectations: the owner may, the other user may not.

```python
def check_owner_only(client, base):
    alice = User.objects.create_user("alice", password="alice-pass-123")
    bob = User.objects.create_user("bob", password="bob-pass-123")
    note = Note.objects.create(owner=alice, text="alice-secret-9431")
    url = f"{base}/notes/{note.pk}/"

    client.force_login(alice)
    response = client.get(url)
    assert response.status_code == 200, f"the owner got {response.status_code} for {url}, expected 200"
    assert "alice-secret-9431" in response.content.decode(), "the owner's page must show the note text"

    client.force_login(bob)
    response = client.get(url)
    assert response.status_code == 404, f"another user got {response.status_code} for {url}, expected 404"
    assert "alice-secret-9431" not in response.content.decode(), "the note text leaked to another user"
```

- On `/safe`, alice gets 200 and bob gets 404 (the queryset filter makes the note "not exist" for him): the check passes.
- On `/leaky`, bob gets 200 and the text: the second block fails with a message. This is the IDOR.
- On `/closed`, alice already gets 404: the first block fails. Without the owner's request this wrong view would look "secure".

The test file calls the same function with the three prefixes: a good check is one that **passes** the right code and **fails** every wrong version (this idea is called mutation testing: change the code on purpose and see whether the tests notice).

## Complexity

Each run creates two users and one note and makes two requests: a handful of queries.

## Another way

In a project, put this in a `TestCase` with `setUp` creating the two users and use `self.client.force_login(...)`. Also test the list page: `response.context["object_list"]` for bob must not contain alice's note. For many rules, loop over a table of `(user, url, expected status)` rows so that a new rule is one more row.

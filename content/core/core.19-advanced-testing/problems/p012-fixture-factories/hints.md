## Hint 1

What does the test receive when it asks for `make_user`: a user, or something that makes
users? Inside the fixture, where do you keep the list of names created so far, and who adds
to it?

## Hint 2

The fixture needs `yield`: what you yield is the factory, and the lines after `yield` are the
cleanup. A test that already deleted its user makes a second `delete_user` raise. How can the
cleanup check first whether the name is still there?

```
@pytest.fixture
def make_user():
    created = []
    def make(name, admin=False): user = create_user(...); created.append(name); return user
    yield make
    for name in created:
        if name in all_users(): delete_user(name)
```

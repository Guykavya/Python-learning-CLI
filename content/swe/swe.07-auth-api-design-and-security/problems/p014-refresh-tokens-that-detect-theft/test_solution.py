import pytest

from solution import InvalidToken, RefreshStore, TokenReuse


class Clock:
    def __init__(self, t=0):
        self.t = t

    def __call__(self):
        return self.t


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def store(clock):
    return RefreshStore(clock, ttl=100)


def test_issue_gives_a_long_random_unique_token(store):
    tokens = {store.issue("asha") for _ in range(200)}
    assert len(tokens) == 200, "Two tokens were equal: build them with secrets.token_urlsafe(32), not from the time or a counter."
    assert all(len(t) >= 32 for t in tokens), "A refresh token needs at least 32 characters (about 256 bits)."


def test_rotate_returns_the_user_and_a_different_token(store):
    t1 = store.issue("asha")
    user, t2 = store.rotate(t1)
    assert user == "asha", f"rotate must return (user, new_token); the user was {user!r}."
    assert isinstance(t2, str) and t2 != t1, "rotate must return a NEW token, not the old one."


def test_the_new_token_works_again_and_chains(store):
    t = store.issue("asha")
    for _ in range(5):
        user, t = store.rotate(t)
        assert user == "asha"


def test_unknown_token_is_invalid(store):
    with pytest.raises(InvalidToken):
        store.rotate("never-issued")


def test_the_store_keeps_only_a_hash(store):
    t = store.issue("asha")
    text = repr(vars(store))
    assert t not in text, "The raw token is stored. Keep sha256(token) as the key, like a password hash: a stolen database must not contain usable tokens."


def test_expiry_boundary(clock, store):
    t = store.issue("asha")                    # expires at 100
    clock.t = 100
    user, _ = store.rotate(t)                  # exactly at the expiry second: still valid
    assert user == "asha", "At now == expires the token is still valid (it is refused only when expires < now)."
    t2 = store.issue("ravi")                   # issued at 100, expires at 200
    clock.t = 201
    with pytest.raises(InvalidToken):
        store.rotate(t2)


def test_rotated_token_gets_a_fresh_lifetime(clock, store):
    t = store.issue("asha")                    # expires 100
    clock.t = 90
    _, t2 = store.rotate(t)                    # new token expires 190
    clock.t = 150
    user, _ = store.rotate(t2)
    assert user == "asha", "The new token must live a full ttl from the moment of rotation (now + ttl)."


def test_reusing_a_retired_token_raises_token_reuse(store):
    t1 = store.issue("asha")
    store.rotate(t1)
    with pytest.raises(TokenReuse):
        store.rotate(t1)


def test_reuse_revokes_the_whole_family(store):
    t1 = store.issue("asha")
    _, t2 = store.rotate(t1)
    _, t3 = store.rotate(t2)
    with pytest.raises(TokenReuse):
        store.rotate(t1)                       # the thief replays the oldest token
    with pytest.raises(InvalidToken):
        store.rotate(t3)                       # the honest user's newest token is dead too
    with pytest.raises((InvalidToken, TokenReuse)):
        store.rotate(t2)


def test_reuse_does_not_touch_other_logins(store):
    phone = store.issue("asha")
    laptop = store.issue("asha")               # a second login of the same user = a second family
    _, phone2 = store.rotate(phone)
    with pytest.raises(TokenReuse):
        store.rotate(phone)
    user, _ = store.rotate(laptop)
    assert user == "asha", "Only the family of the reused token may be revoked. The other login of the same user must keep working."


def test_rotation_keeps_the_family(store):
    t1 = store.issue("asha")
    _, t2 = store.rotate(t1)
    fam = {row["family"] for row in store.rows.values()}
    assert len(fam) == 1, f"Tokens of one login must share one family id (found {len(fam)} families after one rotation)."
    t_other = store.issue("asha")
    fam2 = {row["family"] for row in store.rows.values()}
    assert len(fam2) == 2, "A new login must start a new family."

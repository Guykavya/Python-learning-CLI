import pytest

from solution import CURRENT as DEFAULT_CURRENT
from solution import hash_password, needs_rehash, verify_and_upgrade, verify_password

CUR = (2**10, 8, 1)            # the "current" cost of these tests: small, so they run fast


def make(pw="old-password", n=2**10, r=8, p=1):
    return hash_password(pw, n=n, r=r, p=p)


def test_default_current_is_a_cost_tuple():
    assert len(DEFAULT_CURRENT) == 3 and DEFAULT_CURRENT[0] >= 2**14, "CURRENT is given in the starter (n, r, p); do not change it."


def test_needs_rehash_false_for_current_cost():
    assert needs_rehash(make(), CUR) is False, "A hash made with exactly the current n, r, p is up to date: False."


def test_needs_rehash_true_when_n_is_lower():
    assert needs_rehash(make(n=2**8), CUR) is True, "n=2**8 is lower than the current 2**10: True."


@pytest.mark.parametrize("n,r,p", [(2**10, 4, 1), (2**10, 8, 1)])
def test_needs_rehash_each_parameter(n, r, p):
    expected = (r, p) < (8, 1)
    assert needs_rehash(make(n=n, r=r, p=p), CUR) is expected, f"n={n}, r={r}, p={p} against {CUR}: expected {expected}. Compare each of n, r, p."


def test_needs_rehash_true_when_p_is_lower():
    assert needs_rehash(make(n=2**10, r=8, p=1), (2**10, 8, 2)) is True, "p=1 is lower than the current p=2: True."


def test_stronger_hash_is_left_alone():
    assert needs_rehash(make(n=2**11), CUR) is False, "A hash that is already stronger than current must NOT be rehashed (never downgrade). Compare with 'lower than', not '!='."


@pytest.mark.parametrize("bad", ["", "garbage", "scrypt$1$2", "bcrypt$1024$8$1$AAAA$AAAA", "scrypt$x$8$1$AAAA$AAAA"])
def test_unreadable_strings_need_rehash(bad):
    try:
        result = needs_rehash(bad, CUR)
    except Exception as exc:
        pytest.fail(f"needs_rehash raised {type(exc).__name__} for {bad!r}; return True for any string you cannot read.")
    assert result is True, f"{bad!r} cannot be used as a hash: needs_rehash must be True."


def test_wrong_password_never_upgrades():
    legacy = make(n=2**8)
    assert verify_and_upgrade("nope", legacy, CUR) == (False, None), \
        "A wrong password gives (False, None): never create a new hash after a failed login."


def test_unreadable_hash_gives_false_none():
    assert verify_and_upgrade("pw", "garbage", CUR) == (False, None), "An unreadable stored hash cannot verify: (False, None)."


def test_up_to_date_hash_is_not_replaced():
    stored = make()
    assert verify_and_upgrade("old-password", stored, CUR) == (True, None), \
        "Right password and a hash that is up to date: (True, None). Do not hash again for nothing."


def test_legacy_hash_is_upgraded():
    legacy = make(n=2**8)
    ok, new = verify_and_upgrade("old-password", legacy, CUR)
    assert ok is True, "The right password must log in."
    assert isinstance(new, str), "Right password + old cost: return the new hash string as the second item."
    assert new.split("$")[1:4] == ["1024", "8", "1"], f"The new hash must use the current cost {CUR}; got {new.split('$')[1:4]}"
    assert new != legacy, "The new hash must be a new string."
    assert verify_password("old-password", new) is True, "The new hash must verify with the same password."
    assert verify_password("other", new) is False, "The new hash must not verify other passwords."


def test_after_upgrade_nothing_more_to_do():
    legacy = make(n=2**8)
    _, new = verify_and_upgrade("old-password", legacy, CUR)
    assert verify_and_upgrade("old-password", new, CUR) == (True, None), "After the upgrade, the next login needs no upgrade."


def test_upgrade_uses_a_fresh_salt():
    legacy = make(n=2**8)
    _, new = verify_and_upgrade("old-password", legacy, CUR)
    assert new.split("$")[4] != legacy.split("$")[4], "The new hash needs a NEW salt: call hash_password again, do not copy the old salt."

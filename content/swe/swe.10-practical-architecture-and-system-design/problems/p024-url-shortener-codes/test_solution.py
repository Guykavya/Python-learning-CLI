import pytest

from solution import ALPHABET, AliasTaken, InvalidAlias, Shortener, decode, encode


# ----------------------------------------------------------------------------- base62
@pytest.mark.parametrize("n, code", [(0, "0"), (9, "9"), (10, "A"), (35, "Z"), (36, "a"), (61, "z"), (62, "10"), (3_843, "zz"),
                                     (125_000_000, "8SUD2"), (6_000_000_000, "6Y3O5Y")])
def test_encode_known_values(n, code):
    assert encode(n) == code, f"encode({n}) should be {code!r} (digits 0-9, A-Z, a-z; most significant first)"


def test_round_trip():
    assert all(decode(encode(n)) == n for n in range(0, 20_000)), "decode(encode(n)) must give n back"
    assert decode(encode(10 ** 15)) == 10 ** 15


def test_decode_known_values():
    assert decode("10") == 62 and decode("zz") == 3_843 and decode("0") == 0 and decode("000010") == 62, "Leading zeros do not change the value."


@pytest.mark.parametrize("bad", ["", "a-b", "ab c", "é", "1.5"])
def test_decode_rejects_bad_codes(bad):
    with pytest.raises(ValueError):
        decode(bad)


def test_encode_rejects_negative_numbers():
    with pytest.raises(ValueError):
        encode(-1)


def test_the_alphabet_is_the_chapters():
    assert ALPHABET == "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" and len(set(ALPHABET)) == 62


# ----------------------------------------------------------------------------- generated codes
def test_generated_codes_are_seven_characters_from_a_counter():
    s = Shortener()
    assert [s.create(f"https://example.com/{i}") for i in range(3)] == ["0000001", "0000002", "0000003"], \
        "The counter starts at 1; each code is encode(n) padded with zeros to 7 characters."


def test_the_same_url_gets_different_codes():
    s = Shortener()
    a, b = s.create("https://example.com/same"), s.create("https://example.com/same")
    assert a != b, "Two users shortening the same page get two codes."
    assert s.resolve(a) == s.resolve(b) == "https://example.com/same"


def test_resolve():
    s = Shortener()
    code = s.create("https://example.com/long/path")
    assert s.resolve(code) == "https://example.com/long/path"
    assert s.resolve("nothing") is None, "An unknown code resolves to None (the web layer answers 404)."


def test_the_counter_crosses_a_base62_boundary():
    s = Shortener()
    s.counter = 61
    assert [s.create("u") for _ in range(3)] == ["000000z", "0000010", "0000011"], "61 -> 'z', 62 -> '10', 63 -> '11'"


# ----------------------------------------------------------------------------- aliases
def test_a_valid_alias_is_the_code():
    s = Shortener()
    assert s.create("https://example.com/sale", alias="spring-sale") == "spring-sale"
    assert s.resolve("spring-sale") == "https://example.com/sale"


@pytest.mark.parametrize("alias", ["ab", "a" * 33, "has space", "slash/inside", "dot.dot", "émile", "", "semi;colon"])
def test_invalid_aliases(alias):
    with pytest.raises(InvalidAlias):
        Shortener().create("u", alias=alias)


def test_alias_length_limits_are_inclusive():
    s = Shortener()
    assert s.create("u", alias="abc") == "abc"
    assert s.create("u", alias="a" * 32) == "a" * 32


@pytest.mark.parametrize("alias", ["admin", "Admin", "API", "login", "static", "health"])
def test_reserved_words(alias):
    with pytest.raises(InvalidAlias, match="reserved"):
        Shortener().create("u", alias=alias)


def test_a_custom_reserved_list():
    s = Shortener(reserved=("secret",))
    with pytest.raises(InvalidAlias):
        s.create("u", alias="SECRET")
    assert s.create("u", alias="admin") == "admin", "Only the words of THIS shortener's list are reserved."


def test_a_taken_alias_is_refused_without_regard_to_case():
    s = Shortener()
    s.create("https://example.com/1", alias="Spring-Sale")
    for again in ("Spring-Sale", "spring-sale", "SPRING-SALE"):
        with pytest.raises(AliasTaken):
            s.create("https://example.com/2", alias=again)
    assert s.resolve("spring-sale") == "https://example.com/1", "The first owner keeps it."


def test_the_code_keeps_the_case_the_user_typed():
    s = Shortener()
    assert s.create("u", alias="MyLink") == "MyLink"
    assert s.resolve("mylink") == s.resolve("MYLINK") == s.resolve("MyLink") == "u"


# ----------------------------------------------------------------------------- aliases against generated codes (the chapter's "Try it")
def test_an_alias_that_looks_like_a_generated_code_is_skipped_by_the_counter():
    s = Shortener()
    assert s.create("a") == "0000001"
    assert s.create("b", alias="0000002") == "0000002"
    assert s.create("c") == "0000003", "The next generated code would have been 0000002: it is taken, so the counter skips it."
    assert s.resolve("0000002") == "b", "...and the alias still resolves to its owner, not to the new link."


def test_an_alias_equal_to_an_existing_generated_code_is_taken():
    s = Shortener()
    code = s.create("a")
    with pytest.raises(AliasTaken):
        s.create("b", alias=code)


def test_a_skipped_counter_value_is_never_reused():
    s = Shortener()
    s.create("x", alias="0000001")
    assert s.create("a") == "0000002"
    assert s.create("b") == "0000003"


def test_a_failed_create_does_not_consume_a_counter_value():
    s = Shortener()
    for bad in ("x", "admin"):
        with pytest.raises(InvalidAlias):
            s.create("u", alias=bad)
    s.create("seed", alias="taken-one")
    with pytest.raises(AliasTaken):
        s.create("u", alias="taken-one")
    assert s.create("first real one") == "0000001", "Failed requests must not burn counter values."


def test_many_codes_are_unique():
    s = Shortener()
    codes = [s.create(f"u{i}") for i in range(2_000)]
    assert len(set(codes)) == 2_000 and all(len(c) == 7 for c in codes)

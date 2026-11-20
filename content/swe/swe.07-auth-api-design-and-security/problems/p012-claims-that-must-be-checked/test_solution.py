import pytest

from solution import InvalidClaim, check_claims

ISS, AUD = "pagebound-auth", "payments"
GOOD = {"sub": "42", "iss": ISS, "aud": AUD, "exp": 1000}


def call(claims, now=900, **kw):
    return check_claims(claims, now, ISS, AUD, **kw)


def reason_of(claims, now=900, **kw):
    try:
        call(claims, now, **kw)
    except InvalidClaim as exc:
        return exc.reason
    except Exception as exc:
        pytest.fail(f"Raised {type(exc).__name__} instead of InvalidClaim for {claims!r}. Check types before you use a value.")
    return None


def test_good_claims_are_returned():
    assert call(GOOD) == GOOD, "When every rule passes, return the claims."


def test_exception_carries_the_reason_and_text():
    with pytest.raises(InvalidClaim) as info:
        call({**GOOD, "iss": "evil"})
    assert info.value.reason == "wrong_issuer", "InvalidClaim.reason must name the failed rule."
    assert "wrong_issuer" in str(info.value), "str(exception) should contain the reason too."


@pytest.mark.parametrize("sub", [None, "", 42, ["42"]])
def test_sub_must_be_a_non_empty_string(sub):
    assert reason_of({**GOOD, "sub": sub}) == "missing_sub", f"sub={sub!r} is not a non-empty string: 'missing_sub' (the id is a string, chapter 4.2)."


def test_sub_missing_entirely():
    claims = {k: v for k, v in GOOD.items() if k != "sub"}
    assert reason_of(claims) == "missing_sub", "No sub at all: 'missing_sub'."


def test_exp_is_required():
    claims = {k: v for k, v in GOOD.items() if k != "exp"}
    assert reason_of(claims) == "missing_exp", "A token without exp lives for ever: refuse it with 'missing_exp'."


@pytest.mark.parametrize("exp", ["1000", None, True, [1000]])
def test_exp_must_be_a_number(exp):
    assert reason_of({**GOOD, "exp": exp}) == "missing_exp", f"exp={exp!r} is not a number (a bool is not a number here): 'missing_exp'."


def test_expiry_boundary_with_default_leeway():
    assert reason_of(GOOD, now=1029) is None, "29 s after exp, with 30 s leeway: still accepted."
    assert reason_of(GOOD, now=1029.9) is None, "29.9 s after exp: still accepted."
    assert reason_of(GOOD, now=1030) == "expired", "Exactly exp + leeway is expired: the rule is now - leeway >= exp."


def test_expiry_without_leeway():
    assert reason_of(GOOD, now=999, leeway=0) is None, "One second before exp with leeway 0: valid."
    assert reason_of(GOOD, now=1000, leeway=0) == "expired", "At now == exp with leeway 0 the token is expired."


def test_nbf_is_optional():
    assert reason_of(GOOD) is None, "A token with no nbf is fine."


def test_nbf_boundary():
    claims = {**GOOD, "nbf": 1000, "exp": 5000}
    assert reason_of(claims, now=969) == "not_yet_valid", "nbf=1000, now=969, leeway 30: 1000 > 999 so the token is not yet valid."
    assert reason_of(claims, now=970) is None, "nbf=1000, now=970: 1000 > 1000 is False, so it is valid (the rule is nbf > now + leeway)."
    assert reason_of(claims, now=1000) is None


@pytest.mark.parametrize("nbf", ["900", None, True])
def test_nbf_bad_type(nbf):
    assert reason_of({**GOOD, "nbf": nbf}) == "bad_nbf", f"nbf={nbf!r} is present but not a number: 'bad_nbf'."


def test_issuer():
    assert reason_of({**GOOD, "iss": "someone-else"}) == "wrong_issuer", "A different issuer is refused."
    assert reason_of({**GOOD, "iss": ISS.upper()}) == "wrong_issuer", "The issuer must match exactly, including capitals."
    claims = {k: v for k, v in GOOD.items() if k != "iss"}
    assert reason_of(claims) == "wrong_issuer", "A missing iss is a wrong issuer."


def test_audience_string():
    assert reason_of({**GOOD, "aud": "reports"}) == "wrong_audience", "A token for another service must be refused (chapter 4.2)."
    assert reason_of({**GOOD, "aud": "payments-admin"}) == "wrong_audience", \
        "'payments' in 'payments-admin' is True for strings, but the audience must EQUAL the string. Use == for a string aud."
    assert reason_of({**GOOD, "aud": ""}) == "wrong_audience", "An empty audience is not ours."


def test_audience_list():
    assert reason_of({**GOOD, "aud": ["reports", "payments"]}) is None, "A list that contains our audience is accepted."
    assert reason_of({**GOOD, "aud": ["reports", "billing"]}) == "wrong_audience", "A list without our audience is refused."
    assert reason_of({**GOOD, "aud": []}) == "wrong_audience", "An empty list contains nothing."
    assert reason_of({**GOOD, "aud": ["payments-admin"]}) == "wrong_audience", "Whole-element match only."


def test_audience_missing_or_odd():
    claims = {k: v for k, v in GOOD.items() if k != "aud"}
    assert reason_of(claims) == "wrong_audience", "No aud: refused."
    assert reason_of({**GOOD, "aud": 5}) == "wrong_audience", "aud of a bad type: refused, not a crash."
    assert reason_of({**GOOD, "aud": None}) == "wrong_audience", "aud=None: refused, not a crash."


def test_order_of_the_checks():
    assert reason_of({"exp": 1}, now=999999) == "missing_sub", "sub is checked first."
    assert reason_of({**GOOD, "exp": 1, "aud": "x", "iss": "x"}, now=999999) == "expired", "expired comes before issuer and audience."
    assert reason_of({**GOOD, "nbf": 99999, "iss": "x", "aud": "x"}) == "not_yet_valid", "nbf comes before issuer and audience."
    assert reason_of({**GOOD, "iss": "x", "aud": "x"}) == "wrong_issuer", "issuer comes before audience."


def test_float_times():
    assert reason_of({**GOOD, "exp": 1000.5}, now=1030.4) is None, "Floats work as times."
    assert reason_of({**GOOD, "exp": 1000.5}, now=1030.5) == "expired"

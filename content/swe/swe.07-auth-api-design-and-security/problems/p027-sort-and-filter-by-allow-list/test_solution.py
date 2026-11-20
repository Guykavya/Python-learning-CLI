import pytest

from solution import ListingError, parse_listing


def test_defaults():
    assert parse_listing({}) == {"sort": "-created", "status": None, "limit": 20}, (
        "With no parameters: sort '-created', status None, limit 20 (an int).")


@pytest.mark.parametrize("sort", ["created", "-created", "total"])
def test_allowed_sorts(sort):
    assert parse_listing({"sort": sort})["sort"] == sort


@pytest.mark.parametrize("status", ["pending", "paid", "cancelled"])
def test_allowed_statuses(status):
    assert parse_listing({"status": status})["status"] == status


@pytest.mark.parametrize("raw,value", [("1", 1), ("20", 20), ("100", 100), ("007", 7)])
def test_allowed_limits_become_ints(raw, value):
    got = parse_listing({"limit": raw})["limit"]
    assert got == value and type(got) is int, f"limit {raw!r} must become the int {value}, got {got!r}."


def test_all_parameters_together():
    assert parse_listing({"sort": "total", "status": "paid", "limit": "5"}) == {"sort": "total", "status": "paid", "limit": 5}


@pytest.mark.parametrize("sort", [
    "id; DROP TABLE orders", "secret_note", "password_hash", "(SELECT 1)", "total DESC", "-total", "Created", "CREATED",
    "", " created", "created ", "--created", "+created", "created,total",
])
def test_bad_sort_is_refused_and_names_the_allowed_values(sort):
    with pytest.raises(ListingError) as info:
        parse_listing({"sort": sort})
    message = str(info.value)
    assert info.value.status == 400, "A bad parameter is a 400 error."
    assert "sort" in message, f"The message should name the parameter: {message!r}"
    for allowed in ("created", "-created", "total"):
        assert allowed in message, f"The message must list the allowed values; {allowed!r} is missing from {message!r}."


@pytest.mark.parametrize("status", ["PAID", "Paid", "refunded", "", "paid OR 1=1", "paid ", "pending,paid"])
def test_bad_status_is_refused_and_names_the_allowed_values(status):
    with pytest.raises(ListingError) as info:
        parse_listing({"status": status})
    message = str(info.value)
    assert "status" in message
    for allowed in ("pending", "paid", "cancelled"):
        assert allowed in message, f"The message must list the allowed statuses; {allowed!r} is missing."


@pytest.mark.parametrize("limit", ["0", "101", "1000", "-1", "-0", "abc", "", "1.5", "5 ", " 5", "+5", "1e2", "٣", "²", "99999999999999999999"])
def test_bad_limit_is_refused(limit):
    with pytest.raises(ListingError) as info:
        parse_listing({"limit": limit})
    assert "limit" in str(info.value), f"The message should name the parameter 'limit': {str(info.value)!r}"
    assert "100" in str(info.value), "Say what is allowed: a whole number from 1 to 100."


@pytest.mark.parametrize("name", ["owner_id", "offset", "Sort", "secret_note", "password_hash__startswith"])
def test_unknown_parameters_are_refused(name):
    with pytest.raises(ListingError) as info:
        parse_listing({name: "2"})
    message = str(info.value)
    assert name in message, f"Name the unknown parameter {name!r} in the message."
    for allowed in ("sort", "status", "limit"):
        assert allowed in message, f"List the allowed parameters; {allowed!r} is missing."


def test_one_bad_parameter_spoils_the_request_even_if_others_are_fine():
    with pytest.raises(ListingError):
        parse_listing({"sort": "total", "status": "paid", "limit": "500"})


def test_the_input_dict_is_not_changed():
    params = {"sort": "total", "limit": "5"}
    parse_listing(params)
    assert params == {"sort": "total", "limit": "5"}


def test_listing_error_has_status_400_on_the_class():
    assert ListingError.status == 400

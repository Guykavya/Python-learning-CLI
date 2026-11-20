from solution import CookieJar

SHOP = "https://shop.test"


def test_example_of_the_statement():
    jar = CookieJar()
    jar.store(SHOP + "/login", "sid=abc; Path=/; HttpOnly; Secure", now=0)
    jar.store(SHOP + "/login", "theme=dark; Max-Age=60", now=0)
    assert jar.header_for(SHOP + "/cart", now=10) == "sid=abc; theme=dark"
    assert jar.header_for("http://shop.test/cart", now=10) == "theme=dark", "A Secure cookie is not sent over plain http."
    assert jar.header_for(SHOP + "/cart", now=60) == "sid=abc", "Max-Age=60 set at 0: expired at 60."


def test_empty_jar_and_other_hosts():
    jar = CookieJar()
    assert jar.header_for(SHOP + "/", now=0) == ""
    jar.store(SHOP + "/", "a=1", now=0)
    assert jar.header_for("https://other.test/", now=0) == "", "Cookies belong to the host that set them."
    assert jar.header_for("https://sub.shop.test/", now=0) == "", "Host-only: sub-domains do not get it."
    assert jar.header_for("https://shop.test:8443/", now=0) == "a=1", "Ports are ignored."


def test_domain_attribute_is_ignored():
    jar = CookieJar()
    jar.store(SHOP + "/", "a=1; Domain=test", now=0)
    assert jar.header_for("https://other.test/", now=0) == "", "Every cookie is host-only here, whatever Domain says."
    assert jar.header_for(SHOP + "/", now=0) == "a=1"


def test_path_matches_whole_segments():
    jar = CookieJar()
    jar.store(SHOP + "/", "c=1; Path=/shop", now=0)
    for ok in ("/shop", "/shop/", "/shop/cart", "/shop/a/b"):
        assert jar.header_for(SHOP + ok, now=0) == "c=1", f"The path {ok} is under /shop."
    for no in ("/", "/shopping", "/sho", "/other"):
        assert jar.header_for(SHOP + no, now=0) == "", f"The path {no} is NOT under /shop (compare whole segments)."


def test_path_ending_with_a_slash():
    jar = CookieJar()
    jar.store(SHOP + "/", "c=1; Path=/a/", now=0)
    assert jar.header_for(SHOP + "/a/b", now=0) == "c=1"
    assert jar.header_for(SHOP + "/a", now=0) == ""


def test_default_path_is_the_directory_of_the_request():
    jar = CookieJar()
    jar.store(SHOP + "/a/b", "x=1", now=0)       # default path /a
    jar.store(SHOP + "/top", "y=1", now=0)       # default path /
    jar.store(SHOP, "z=1", now=0)                # no path: /
    assert jar.header_for(SHOP + "/a/c", now=0) == "x=1; y=1; z=1"
    assert jar.header_for(SHOP + "/b", now=0) == "y=1; z=1"
    assert [c["path"] for c in jar.all(0)] == ["/a", "/", "/"]


def test_longer_paths_first_then_creation_order():
    jar = CookieJar()
    jar.store(SHOP + "/", "root1=1; Path=/", now=0)
    jar.store(SHOP + "/", "deep=1; Path=/a/b", now=0)
    jar.store(SHOP + "/", "root2=1; Path=/", now=0)
    jar.store(SHOP + "/", "mid=1; Path=/a", now=0)
    assert jar.header_for(SHOP + "/a/b/c", now=0) == "deep=1; mid=1; root1=1; root2=1"


def test_secure_only_over_https_and_not_set_over_http():
    jar = CookieJar()
    jar.store("http://shop.test/", "s=1; Secure", now=0)
    assert jar.all(0) == [], "A Secure cookie set over plain http is ignored."
    jar.store(SHOP + "/", "s=1; Secure", now=0)
    assert jar.header_for("http://shop.test/", now=0) == ""
    assert jar.header_for(SHOP + "/", now=0) == "s=1"


def test_max_age_expiry_and_deletion():
    jar = CookieJar()
    jar.store(SHOP + "/", "t=1; Max-Age=10", now=100)
    assert jar.header_for(SHOP + "/", now=109.9) == "t=1"
    assert jar.header_for(SHOP + "/", now=110) == "", "At now == expires the cookie is gone."
    jar.store(SHOP + "/", "k=1", now=0)
    jar.store(SHOP + "/", "k=; Max-Age=0", now=1)
    assert jar.header_for(SHOP + "/", now=2) == "", "Max-Age=0 deletes the cookie."
    jar.store(SHOP + "/", "n=1; Max-Age=-5", now=0)
    assert jar.all(0) == [], "A cookie with Max-Age <= 0 is not stored."


def test_same_name_replaces_and_keeps_its_place():
    jar = CookieJar()
    jar.store(SHOP + "/", "a=1", now=0)
    jar.store(SHOP + "/", "b=1", now=0)
    jar.store(SHOP + "/", "a=2", now=0)
    assert jar.header_for(SHOP + "/", now=0) == "a=2; b=1", "Replacing keeps the original creation order."
    jar.store(SHOP + "/", "a=3; Path=/x", now=0)
    assert jar.header_for(SHOP + "/x", now=0) == "a=3; a=2; b=1", "Another path is another cookie, even with the same name."


def test_http_only_is_kept():
    jar = CookieJar()
    jar.store(SHOP + "/", "sid=1; HttpOnly", now=0)
    jar.store(SHOP + "/", "pref=2", now=0)
    got = {c["name"]: c for c in jar.all(0)}
    assert got["sid"]["http_only"] is True and got["pref"]["http_only"] is False
    assert jar.header_for(SHOP + "/", now=0) == "sid=1; pref=2", "HttpOnly does not change what we send."


def test_all_has_the_documented_keys():
    jar = CookieJar()
    jar.store(SHOP + "/x/y", "n=v; Max-Age=30", now=5)
    assert jar.all(5) == [{"name": "n", "value": "v", "host": "shop.test", "path": "/x", "secure": False,
                           "http_only": False, "expires": 35}]
    assert jar.all(40) == [], "all() shows live cookies only."


def test_values_with_equals_and_spaces_and_bad_headers():
    jar = CookieJar()
    jar.store(SHOP + "/", "token=abc==; Path=/", now=0)
    jar.store(SHOP + "/", "  spaced = v  ;  path = /  ", now=0)
    jar.store(SHOP + "/", "novalue", now=0)
    jar.store(SHOP + "/", "=orphan", now=0)
    jar.store(SHOP + "/", "", now=0)
    assert jar.header_for(SHOP + "/", now=0) == "token=abc==; spaced=v", "A '=' inside the value stays; bad headers are ignored."


def test_attribute_names_ignore_case():
    jar = CookieJar()
    jar.store(SHOP + "/", "a=1; SECURE; httponly; MAX-AGE=5; PATH=/p", now=0)
    c = jar.all(0)[0]
    assert (c["secure"], c["http_only"], c["expires"], c["path"]) == (True, True, 5, "/p")

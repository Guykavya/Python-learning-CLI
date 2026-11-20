from pathlib import Path

import pytest

from solution import UnsafeURL, check_url, safe_join

# ---------------------------------------------------------------- safe_join


@pytest.fixture
def folders(tmp_path):
    base = tmp_path / "uploads"
    (base / "docs").mkdir(parents=True)
    (base / "docs" / "a.txt").write_text("a", encoding="utf-8")
    (base / "b.txt").write_text("b", encoding="utf-8")
    (tmp_path / "secret.txt").write_text("TOP SECRET", encoding="utf-8")
    (tmp_path / "uploads-evil").mkdir()
    (tmp_path / "uploads-evil" / "x.txt").write_text("evil", encoding="utf-8")
    return tmp_path, base


@pytest.mark.parametrize("name", ["b.txt", "docs/a.txt", "docs/../b.txt", "./docs/./a.txt", "new/not/yet/there.txt", "docs/../docs/a.txt"])
def test_paths_inside_are_returned_resolved(folders, name):
    root, base = folders
    got = safe_join(base, name)
    assert isinstance(got, Path), f"Return a Path; got {type(got).__name__}"
    assert got == (base / name).resolve(), f"{name!r}: expected the resolved path {(base / name).resolve()}, got {got}"
    assert got.is_absolute(), "Return the resolved (absolute) path"


def test_str_and_path_base_both_work(folders):
    root, base = folders
    assert safe_join(str(base), "b.txt") == safe_join(base, "b.txt") == (base / "b.txt").resolve(), "base may be a str or a Path"


@pytest.mark.parametrize("name", [
    "../secret.txt", "../../etc/passwd", "docs/../../secret.txt", "a/../../secret.txt", "../uploads-evil/x.txt",
    "../uploads/../secret.txt", "..",
])
def test_dot_dot_that_leaves_the_folder_is_refused(folders, name):
    root, base = folders
    with pytest.raises(PermissionError):
        safe_join(base, name)
        pytest.fail(f"{name!r} leaves the base folder and must raise PermissionError")


def test_absolute_paths_are_refused(folders):
    root, base = folders
    outside = str((root / "secret.txt").resolve())
    for name in (outside, "/etc/passwd", "/"):
        with pytest.raises(PermissionError):
            safe_join(base, name)
            pytest.fail(f"The absolute path {name!r} replaces the base when joined: resolve, then check is_relative_to")


def test_sibling_folder_with_the_same_prefix_is_outside(folders):
    root, base = folders
    with pytest.raises(PermissionError):
        safe_join(base, "../uploads-evil/x.txt")
        pytest.fail("'uploads-evil' starts with 'uploads' but it is another folder: use is_relative_to, not startswith")


def test_nul_character_is_refused(folders):
    root, base = folders
    with pytest.raises(PermissionError):
        safe_join(base, "b.txt\0.png")
        pytest.fail("A NUL character in a path must raise PermissionError (not ValueError)")


def test_symlink_pointing_outside_is_refused(folders):
    root, base = folders
    try:
        (base / "link").symlink_to(root, target_is_directory=True)
        (base / "filelink").symlink_to(root / "secret.txt")
    except (OSError, NotImplementedError):
        pytest.skip("this system does not allow symlinks for this user")
    for name in ("link/secret.txt", "filelink", "link/../secret.txt"):
        with pytest.raises(PermissionError):
            safe_join(base, name)
            pytest.fail(f"{name!r} goes through a symlink to a place outside the folder: resolve() follows symlinks, then check")


def test_symlink_staying_inside_is_allowed(folders):
    root, base = folders
    try:
        (base / "shortcut").symlink_to(base / "docs", target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("this system does not allow symlinks for this user")
    got = safe_join(base, "shortcut/a.txt")
    assert got == (base / "docs" / "a.txt").resolve(), "A symlink that stays inside the folder is fine; return the resolved target"


def test_a_base_behind_a_symlink_still_works(folders):
    root, base = folders
    try:
        (root / "alias").symlink_to(base, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("this system does not allow symlinks for this user")
    assert safe_join(root / "alias", "b.txt") == (base / "b.txt").resolve(), (
        "Resolve base too: otherwise the resolved target never looks 'inside' the unresolved base")
    with pytest.raises(PermissionError):
        safe_join(root / "alias", "../secret.txt")
        pytest.fail("Leaving through '..' from a symlinked base must still be refused")


def test_no_file_is_created(folders):
    root, base = folders
    before = sorted(p.name for p in base.rglob("*"))
    safe_join(base, "never/created.txt")
    assert sorted(p.name for p in base.rglob("*")) == before, "safe_join only computes a path; it must not create anything"


# ---------------------------------------------------------------- check_url

PUBLIC = "93.184.216.34"


class Resolver:
    """A fake DNS: a dict host -> list of addresses; records every lookup."""

    def __init__(self, table=None):
        self.table = table or {}
        self.calls = []

    def __call__(self, host):
        self.calls.append(host)
        if host not in self.table:
            raise OSError(f"no such host {host}")
        return list(self.table[host])


def test_a_public_host_is_approved_and_the_addresses_are_returned():
    r = Resolver({"hooks.example.com": [PUBLIC, "8.8.8.8"]})
    got = check_url("https://hooks.example.com/pay?x=1", r)
    assert got == [PUBLIC, "8.8.8.8"], f"Return the approved addresses exactly as the resolver gave them; got {got!r}"
    assert r.calls == ["hooks.example.com"], f"Call resolve once with the host name; calls: {r.calls}"


def test_http_is_allowed_too():
    assert check_url("http://hooks.example.com/", Resolver({"hooks.example.com": [PUBLIC]})) == [PUBLIC]


@pytest.mark.parametrize("url", [
    "file:///etc/passwd", "ftp://hooks.example.com/x", "gopher://hooks.example.com/", "javascript:alert(1)",
    "//hooks.example.com/x", "hooks.example.com/x", "data:text/plain,hi", "",
])
def test_other_schemes_are_refused_before_any_lookup(url):
    r = Resolver({"hooks.example.com": [PUBLIC]})
    with pytest.raises(UnsafeURL):
        check_url(url, r)
        pytest.fail(f"{url!r} is not an http(s) URL and must raise UnsafeURL")
    assert r.calls == [], f"{url!r}: refuse a bad scheme without resolving anything; calls: {r.calls}"


@pytest.mark.parametrize("url", [
    "https://127.0.0.1/admin", "https://10.0.0.5:6379/", "https://192.168.1.10/", "https://172.16.0.1/",
    "https://169.254.169.254/latest/meta-data/", "https://0.0.0.0/", "https://100.64.0.1/",
    "https://[::1]/", "https://[::ffff:127.0.0.1]/", "https://[fe80::1]/", "https://[fd00::1]/",
    "https://93.184.216.34@127.0.0.1/", "http://[::ffff:169.254.169.254]/",
])
def test_non_public_ip_literals_are_refused(url):
    r = Resolver()
    with pytest.raises(UnsafeURL):
        check_url(url, r)
        pytest.fail(f"{url!r} points to a loopback, private, link-local or otherwise non-public address and must be refused")
    assert r.calls == [], f"{url!r}: an IP literal needs no lookup; calls: {r.calls}"


@pytest.mark.parametrize("url, expected", [
    ("https://93.184.216.34/hook", ["93.184.216.34"]),
    ("https://8.8.8.8:8443/x", ["8.8.8.8"]),
    ("https://[2606:4700:4700::1111]/", ["2606:4700:4700::1111"]),
])
def test_public_ip_literals_are_approved(url, expected):
    r = Resolver()
    assert check_url(url, r) == expected, f"{url!r} is a public address and must be approved as {expected}"
    assert r.calls == [], "An IP literal is not resolved"


@pytest.mark.parametrize("host, address", [
    ("localtest.example", "127.0.0.1"),
    ("2130706433", "127.0.0.1"),
    ("0x7f000001", "127.0.0.1"),
    ("internal.corp.example", "10.1.2.3"),
    ("metadata.example", "169.254.169.254"),
    ("v6.example", "::1"),
    ("mapped.example", "::ffff:10.0.0.1"),
])
def test_names_that_resolve_to_private_addresses_are_refused(host, address):
    r = Resolver({host: [address]})
    with pytest.raises(UnsafeURL):
        check_url(f"https://{host}/x", r)
        pytest.fail(f"{host!r} looks harmless but resolves to {address}: resolve first, then check the ADDRESS")


def test_one_bad_address_among_good_ones_rejects_the_url():
    r = Resolver({"mixed.example": [PUBLIC, "10.0.0.7", "8.8.8.8"]})
    with pytest.raises(UnsafeURL):
        check_url("https://mixed.example/", r)
        pytest.fail("A DNS answer with one private address among public ones must be refused: check EVERY address")


def test_unresolvable_or_empty_answers_are_refused():
    with pytest.raises(UnsafeURL):
        check_url("https://nowhere.example/", Resolver())
        pytest.fail("A resolver error (OSError) must become UnsafeURL")
    with pytest.raises(UnsafeURL):
        check_url("https://empty.example/", Resolver({"empty.example": []}))
        pytest.fail("An empty address list means 'cannot connect': UnsafeURL, never 'approved with no checks'")


def test_userinfo_does_not_hide_the_real_host():
    r = Resolver({"evil.example": ["127.0.0.1"], "good.example": [PUBLIC]})
    with pytest.raises(UnsafeURL):
        check_url("https://good.example@evil.example/", r)
        pytest.fail("In user@host the host is the part after '@' (evil.example), which resolves to 127.0.0.1")
    assert r.calls == ["evil.example"], f"Resolve the real host name only; calls: {r.calls}"
    assert check_url("https://evil.example@good.example/", r) == [PUBLIC], "The user part is ignored; the host is good.example"


def test_host_case_does_not_matter():
    r = Resolver({"hooks.example.com": [PUBLIC]})
    assert check_url("HTTPS://Hooks.Example.COM/x", r) == [PUBLIC], "urlparse lower-cases scheme and hostname: use parts.hostname"


def test_unsafe_url_is_a_value_error():
    assert issubclass(UnsafeURL, ValueError)

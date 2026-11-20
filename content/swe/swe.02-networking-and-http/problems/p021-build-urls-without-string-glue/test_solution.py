from urllib.parse import parse_qs, unquote, urlsplit

from solution import build_url


def test_the_example():
    assert build_url("https://api.example.com/v1/", ["users", "a/b"], {"q": "x y", "tag": ["a", "b"]}) == (
        "https://api.example.com/v1/users/a%2Fb?q=x+y&tag=a&tag=b")
    assert build_url("http://h", ["files", "../etc"]) == "http://h/files/..%2Fetc"


def test_plain_segments():
    assert build_url("https://x.test", ["a", "b", "c"]) == "https://x.test/a/b/c"
    assert build_url("https://x.test/", []) == "https://x.test", "No segments: just the base (without a trailing slash)."
    assert build_url("https://x.test/v1", ["users", 42]) == "https://x.test/v1/users/42", "Numbers are turned into text."


def test_special_characters_in_a_segment_stay_in_that_segment():
    out = build_url("https://x.test", ["a b&c#d?e%f/g"])
    assert out == "https://x.test/a%20b%26c%23d%3Fe%25f%2Fg", (
        "Every special character, including '/', must be percent-encoded inside a segment (quote(..., safe='')).")
    assert urlsplit(out).fragment == "" and urlsplit(out).query == "", "'#' and '?' in a value must not start a fragment or a query."


def test_non_english_text_is_utf8():
    out = build_url("https://x.test", ["नमस्ते", "ça va"])
    assert out == "https://x.test/%E0%A4%A8%E0%A4%AE%E0%A4%B8%E0%A5%8D%E0%A4%A4%E0%A5%87/%C3%A7a%20va"
    assert unquote(urlsplit(out).path) == "/नमस्ते/ça va"


def test_query_values_and_lists():
    out = build_url("https://x.test", ["s"], {"q": "a&b=c", "n": 3, "tag": ["x", "y z"]})
    assert parse_qs(urlsplit(out).query) == {"q": ["a&b=c"], "n": ["3"], "tag": ["x", "y z"]}, (
        "Use urlencode(..., doseq=True): lists give one pair per item.")
    assert "q=a%26b%3Dc" in out


def test_none_values_and_empty_query_leave_no_question_mark():
    assert build_url("https://x.test", ["s"], {}) == "https://x.test/s"
    assert build_url("https://x.test", ["s"], None) == "https://x.test/s"
    assert build_url("https://x.test", ["s"], {"a": None}) == "https://x.test/s", "No pair left: no '?' at all."
    assert build_url("https://x.test", ["s"], {"a": None, "b": "1"}) == "https://x.test/s?b=1"
    assert build_url("https://x.test", ["s"], {"a": []}) == "https://x.test/s", "An empty list gives no pair."


def test_round_trip_of_hostile_input():
    evil = "../../admin?role=root#frag&x=1"
    out = build_url("https://x.test/api", ["users", evil], {"v": evil})
    parts = urlsplit(out)
    assert parts.path.count("/") == 3, "The hostile value must remain ONE path segment."
    assert unquote(parts.path.split("/")[-1]) == evil
    assert parse_qs(parts.query) == {"v": [evil]}

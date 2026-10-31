from solution import extract_emails


def test_one_address_in_a_sentence():
    assert extract_emails("Mail kavya@example.com today") == ["kavya@example.com"], "The domain part '.+' is greedy and runs to the end of the line. A domain is labels of [A-Za-z0-9-] and dots, never spaces."


def test_two_addresses_on_one_line():
    text = "Mail kavya@example.com or ravi@club.co.in, thanks"
    assert extract_emails(text) == ["kavya@example.com", "ravi@club.co.in"], "Expected two complete addresses. A greedy '.+' merges them into one; a domain pattern with only one label cuts 'club.co.in' short."


def test_domain_needs_a_dot():
    assert extract_emails("admin@localhost") == [], "An unescaped '.' matches ANY character, so 'localhost' passes as 'localhos' + 't'. Escape it: \\."
    assert extract_emails("write to test@site now") == [], "No dot in the domain: not an email."


def test_capital_letters():
    assert extract_emails("RAVI@GMAIL.COM") == ["RAVI@GMAIL.COM"], "[a-z] knows only small letters. Allow A-Z too (or use re.IGNORECASE)."
    assert extract_emails("Bob@Site.Com") == ["Bob@Site.Com"], "Mixed case must be returned as written, not lower-cased."


def test_full_stop_after_address():
    assert extract_emails("Write to x@y.com.") == ["x@y.com"], "The final '.' ends the sentence. The top-level part is letters only, so it cannot end with a dot."
    assert extract_emails("Contact: <RAVI@GMAIL.COM>. Bye") == ["RAVI@GMAIL.COM"], "Brackets and the full stop are not part of the address."


def test_percent_in_local_part():
    assert extract_emails("kavya%club@college.edu") == ["kavya%club@college.edu"], "'%' is allowed in the local part. If it is missing from the class, the match silently starts after it."


def test_top_level_part_needs_two_letters():
    assert extract_emails("x@y.z") == [], "The top-level part needs 2 or more letters: [A-Za-z]{2,}."
    assert extract_emails("bob@site.com2") == [], "The top-level part must not run into digits or letters: end with \\b."


def test_valid_shapes():
    assert extract_emails("a.b-c+d_e@my-site.in") == ["a.b-c+d_e@my-site.in"], "Dots, hyphens, plus and underscore are allowed in the local part; hyphens in a domain label."
    assert extract_emails("r@mail.co.uk") == ["r@mail.co.uk"], "Several labels: (?:[A-Za-z0-9-]+\\.)+ then the top-level part."


def test_order_duplicates_and_empty():
    text = "a@b.com, c@d.org\na@b.com"
    assert extract_emails(text) == ["a@b.com", "c@d.org", "a@b.com"], "Keep the order and keep duplicates."
    assert extract_emails("") == [], "No text, no emails."
    assert extract_emails("no at-sign here") == [], "No '@', no emails."

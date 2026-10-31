from solution import render


def test_basic():
    assert render("Hello {{ name }}!", {"name": "Kavya"}) == "Hello Kavya!", "Replace {{ name }} by values['name']."


def test_spacing_variants():
    values = {"x": "1"}
    assert render("{{x}}", values) == "1", "No spaces inside the braces is allowed: \\s*, not a required space."
    assert render("{{   x   }}", values) == "1", "Several spaces are allowed too."
    assert render("{{\tx\t}}", values) == "1", "Any whitespace (\\s*), including tabs."


def test_non_string_values():
    assert render("You owe ₹{{amount}}.", {"amount": 250}) == "You owe ₹250.", "Values can be ints: convert with str(...). re.sub needs the function to return a string."
    assert render("{{ ok }}", {"ok": True}) == "True", "Any value is turned into text with str()."


def test_missing_key_left_as_written():
    assert render("Dear {{ title }} {{ name }}", {"name": "Rao"}) == "Dear {{ title }} Rao", "A missing name stays exactly as written: return m.group(0). values[name] would raise KeyError."
    assert render("{{title}}", {}) == "{{title}}", "Keep the original spacing of a missing placeholder."


def test_same_name_twice():
    assert render("{{ a }}-{{a}}", {"a": "x"}) == "x-x", "Every occurrence is filled, not only the first."


def test_invalid_placeholders_are_text():
    values = {"name": "N", "first": "F", "x": "X"}
    assert render("{ name }", values) == "{ name }", "Single braces are not a placeholder."
    assert render("{{ first name }}", values) == "{{ first name }}", "A name has no spaces inside."
    assert render("{{ 1x }}", values) == "{{ 1x }}", "A name cannot start with a digit: [A-Za-z_]\\w*."
    assert render("{{ user.name }}", values) == "{{ user.name }}", "A dot is not allowed in a name."


def test_values_are_not_processed_again():
    assert render("{{ a }}", {"a": "{{ b }}", "b": "NO"}) == "{{ b }}", "A value is inserted once. re.sub does a single pass, do not loop until nothing changes."


def test_backslashes_inserted_as_they_are():
    assert render("Path: {{ p }}", {"p": "C:\\new\\1"}) == "Path: C:\\new\\1", "A value with backslashes must be inserted as it is. As a replacement STRING, '\\n' and '\\1' are processed: use a replacement FUNCTION."


def test_no_placeholders_and_empty():
    assert render("plain text", {"x": 1}) == "plain text", "Text without placeholders is unchanged."
    assert render("", {}) == "", "Empty template gives empty output."

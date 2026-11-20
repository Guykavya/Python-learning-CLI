from solution import lint_message


def test_perfect_messages():
    assert lint_message("Fix crash when cart is empty") == []
    assert lint_message("Fix crash when cart is empty\n") == [], "A final newline is normal; ignore it."
    body = "Round once, at the end, so intermediate values keep their precision."
    assert lint_message("Round totals to two decimals\n\n" + body + "\n") == []


def test_empty():
    assert lint_message("") == ["empty"]
    assert lint_message("  \n\n") == ["empty"], "Only whitespace is empty too, and returns only 'empty'."


def test_subject_length_limit_is_50():
    assert lint_message("a" * 50) == [], "Exactly 50 characters is allowed."
    assert lint_message("a" * 51) == ["subject-too-long"], "51 characters is too long."


def test_subject_period():
    assert lint_message("Fix crash.") == ["subject-ends-with-period"]
    assert lint_message("Fix crash.\n\nBody ends with a period.") == ["subject-ends-with-period"], (
        "Only the subject may not end with a period; the body may.")


def test_blank_line_after_subject():
    assert lint_message("Add helper\nIt applies a percent.") == ["no-blank-line"], (
        "A body must start after one blank line.")
    assert lint_message("Add helper\n\nFirst paragraph.\n\nSecond paragraph.") == [], (
        "Blank lines inside the body are fine.")


def test_body_line_limit_is_72():
    assert lint_message("Add helper\n\n" + "b" * 72) == [], "72 characters is allowed in the body."
    assert lint_message("Add helper\n\n" + "b" * 73) == ["body-line-too-long"]
    assert lint_message("Add helper\n\nshort\n" + "b" * 80) == ["body-line-too-long"], "Check every body line."


def test_several_problems_in_the_fixed_order():
    msg = "x" * 60 + ".\n" + "y" * 80
    assert lint_message(msg) == [
        "subject-too-long", "subject-ends-with-period", "no-blank-line", "body-line-too-long"], (
        "Return the codes in the order of the table, each once.")

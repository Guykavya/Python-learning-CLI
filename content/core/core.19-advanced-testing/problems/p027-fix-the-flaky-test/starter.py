from target import events, greeting, record, roll_dice, unique_tags


def test_events_are_kept_in_order():
    record("x")
    record("y")
    assert events() == ["x", "y"]


def test_next_record_number():
    assert record("z") == 3


def test_morning_greeting():
    assert greeting() == "Good morning"


def test_unique_tags():
    assert unique_tags(["python", "testing", "python"]) == ["python", "testing"]


def test_six_appears():
    assert 6 in roll_dice(6)

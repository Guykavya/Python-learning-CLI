import pytest

from solution import make_noise


class Duck:
    def speak(self):
        return "Quack"


class Robot:
    def speak(self):
        return "Beep"


class Rock:
    pass


class Parrot:
    def __init__(self, word):
        self.word = word

    def speak(self):
        return self.word * 2


class BrokenSpeaker:
    def speak(self):
        return self.volume  # bug: there is no volume attribute


def test_example():
    assert make_noise([Duck(), Rock(), Robot(), "text", Duck()]) == ["Quack", "Beep", "Quack"], (
        "Call speak() on objects that have it, skip the others, keep the order."
    )


def test_unrelated_classes_work():
    assert make_noise([Parrot("hi"), Robot()]) == ["hihi", "Beep"], (
        "Any object with speak() works, whatever its class. Do not check isinstance."
    )


def test_empty_and_all_skipped():
    assert make_noise([]) == [], "No things, no noise: return []."
    assert make_noise([Rock(), 5, None, [1, 2]]) == [], "Objects without speak are skipped, not an error."


def test_speak_is_called_not_collected():
    result = make_noise([Duck()])
    assert result == ["Quack"], "Collect the RESULT of speak(), not the method itself. Did you forget the brackets?"


def test_bug_inside_speak_is_not_hidden():
    try:
        make_noise([Duck(), BrokenSpeaker()])
    except AttributeError:
        pass
    else:
        pytest.fail(
            "BrokenSpeaker.speak() has a bug that raises AttributeError. make_noise must not hide it. "
            "Put only the lookup (thing.speak) inside the try, and call speak() after it."
        )


def test_other_errors_inside_speak_propagate():
    class Angry:
        def speak(self):
            raise ValueError("no")

    with pytest.raises(ValueError):
        make_noise([Angry()])


def test_speak_called_once_per_object():
    class Counting:
        calls = 0

        def speak(self):
            Counting.calls += 1
            return "one"

    make_noise([Counting(), Counting()])
    assert Counting.calls == 2, "Call speak() exactly once for each object."

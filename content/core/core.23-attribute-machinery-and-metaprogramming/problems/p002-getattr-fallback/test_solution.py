import copy
import pickle

import pytest

from solution import Settings


def make():
    return Settings({"host": "db.local", "debug": True}, {"host": "localhost", "port": 5432, "debug": False})


def test_values_win_over_defaults():
    s = make()
    assert s.host == "db.local", "A name given in values must win over the same name in defaults."
    assert s.debug is True, "values['debug'] is True; do not return the default False."


def test_missing_names_come_from_defaults():
    s = make()
    assert s.port == 5432, "'port' is not in values, so __getattr__ must return defaults['port']."


def test_defaults_are_optional():
    s = Settings({"a": 1})
    assert s.a == 1, "Settings(values) with no defaults must still expose the values."
    with pytest.raises(AttributeError):
        s.b


def test_unknown_name_raises_attribute_error_naming_it():
    s = make()
    with pytest.raises(AttributeError) as info:
        s.timeout
    assert "timeout" in str(info.value), "The AttributeError message must name the missing attribute ('timeout')."


def test_unknown_name_is_not_a_key_error():
    s = make()
    try:
        s.timeout
    except KeyError:
        pytest.fail("Unknown names must raise AttributeError, not KeyError. Catch the KeyError and raise AttributeError.")
    except AttributeError:
        pass


def test_getattr_default_and_hasattr_work():
    s = make()
    assert getattr(s, "timeout", 30) == 30, (
        "getattr(obj, name, default) only uses the default when AttributeError is raised."
    )
    assert hasattr(s, "port") is True, "hasattr must be True for a name found in defaults."
    assert hasattr(s, "timeout") is False, "hasattr must be False for an unknown name (raise AttributeError)."


def test_dunder_and_private_names_are_not_invented():
    s = Settings({}, {"x": 1})
    assert not hasattr(s, "__deepcopy__"), (
        "Names starting with '_' must raise AttributeError at once. Otherwise copy and pickle think you provide __deepcopy__ etc."
    )
    assert not hasattr(s, "_cache"), "A private name that was never set must raise AttributeError."


def test_assignment_later_wins():
    s = make()
    s.port = 6000
    assert s.port == 6000, "After s.port = 6000 the instance attribute exists, so the default must no longer be used."


def test_instances_do_not_share_values():
    a = Settings({"host": "a"}, {"port": 1})
    b = Settings({"host": "b"}, {"port": 2})
    assert (a.host, a.port, b.host, b.port) == ("a", 1, "b", 2), (
        "Each Settings object keeps its own values and defaults. Do not store them on the class."
    )


def test_copy_and_deepcopy_work():
    s = make()
    try:
        c = copy.copy(s)
        d = copy.deepcopy(s)
    except RecursionError:
        pytest.fail(
            "copy created the object WITHOUT running __init__, then looked up '__setstate__'/'__deepcopy__'. "
            "Your __getattr__ read self._something, which is missing, so it called itself forever. "
            "Raise AttributeError for names that start with '_' before touching self."
        )
    assert (c.host, c.port, d.host, d.port) == ("db.local", 5432, "db.local", 5432), "Copies must keep values and defaults."


def test_pickle_round_trip():
    s = make()
    try:
        back = pickle.loads(pickle.dumps(s))
    except RecursionError:
        pytest.fail("Unpickling looks up '__setstate__' before __init__ runs. Guard names starting with '_'.")
    assert (back.host, back.port) == ("db.local", 5432), "A pickled and unpickled Settings must keep its data."

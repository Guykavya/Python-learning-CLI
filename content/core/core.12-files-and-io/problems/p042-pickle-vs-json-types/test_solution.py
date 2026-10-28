from solution import json_loses, load_pickle, save_pickle


def test_pickle_round_trip(tmp_path):
    obj = {"t": (1, 2), "s": {3, 4}, "b": b"\x00\xff", 7: "int key", "nested": [{"x": None}, 1.5]}
    path = tmp_path / "state.pkl"
    save_pickle(obj, path)
    back = load_pickle(path)
    assert back == obj, "load_pickle must give back an object equal to the saved one."
    assert type(back["t"]) is tuple, "pickle keeps tuples as tuples."
    assert type(back["s"]) is set, "pickle keeps sets as sets."
    assert 7 in back, "pickle keeps int keys as int keys."


def test_pickle_file_is_binary(tmp_path):
    path = tmp_path / "x.pkl"
    save_pickle([1, 2], path)
    data = path.read_bytes()
    assert data[:1] == b"\x80", "A pickle file is binary and starts with the byte 0x80. Open the file with 'wb'."


def test_pickle_of_simple_values(tmp_path):
    for value in [0, "text", None, [1, [2]], 3.25]:
        path = tmp_path / "v.pkl"
        save_pickle(value, path)
        assert load_pickle(path) == value, f"The value {value!r} must survive a pickle round trip."


def test_json_safe_values():
    assert json_loses({"a": [1, 2, 3], "b": "x", "c": None, "d": 1.5, "e": True}) is False, "These values all survive json unchanged."
    assert json_loses([]) is False, "An empty list survives."
    assert json_loses("text") is False, "A string survives."


def test_tuple_is_lost():
    assert json_loses({"point": (1, 2)}) is True, "json turns a tuple into a list, so the object is not equal after the trip."


def test_deep_tuple_is_lost():
    assert json_loses([[1, [2, (3,)]]]) is True, "A tuple deep inside a list is also lost. Compare the whole round trip."


def test_int_keys_are_lost():
    assert json_loses({1: "one"}) is True, "json turns the key 1 into the text '1'."


def test_set_and_bytes_raise_type_error():
    assert json_loses({"tags": {"x"}}) is True, "json.dumps raises TypeError for a set. Catch it and return True."
    assert json_loses(b"abc") is True, "json.dumps raises TypeError for bytes. Catch it and return True."

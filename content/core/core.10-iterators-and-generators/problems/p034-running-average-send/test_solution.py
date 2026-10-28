from solution import averager


def started():
    g = averager()
    first = next(g)
    assert first is None, "The priming next(g) must return None: there is no average yet."
    return g


def test_priming_returns_none():
    started()


def test_running_average():
    g = started()
    assert g.send(10) == 10.0, "After one number the average is that number."
    assert g.send(20) == 15.0, "(10 + 20) / 2 = 15.0. Keep a total and a count, not only the last value."
    assert g.send(30) == 20.0, "(10 + 20 + 30) / 3 = 20.0."


def test_result_is_float():
    g = started()
    result = g.send(3)
    assert isinstance(result, float), "Return a float: use / not //."
    assert g.send(4) == 3.5, "(3 + 4) / 2 = 3.5. Did you use integer division //?"


def test_reset_with_next():
    g = started()
    g.send(100)
    g.send(200)
    assert next(g) is None, "next(g) sends None, which must reset and return None."
    assert g.send(4) == 4.0, "After a reset the old numbers must be forgotten: reset both total and count."
    assert g.send(6) == 5.0, "After the reset: (4 + 6) / 2 = 5.0."


def test_reset_with_send_none():
    g = started()
    g.send(1)
    assert g.send(None) is None, "send(None) is a reset and must return None."
    assert g.send(9) == 9.0, "The reset must clear the count too, not only the total."


def test_zero_is_a_number_not_a_reset():
    g = started()
    g.send(10)
    assert g.send(0) == 5.0, "0 is a real number: (10 + 0) / 2 = 5.0. Test 'is None', not truthiness ('if not x')."


def test_never_ends():
    g = started()
    for i in range(1000):
        g.send(i)
    assert g.send(1000) == 500.0, "The generator must keep going for ever: use while True."


def test_independent_generators():
    a = started()
    b = started()
    a.send(10)
    b.send(1)
    assert a.send(20) == 15.0, "Each generator keeps its own data. Do not use global variables."
    assert b.send(3) == 2.0, "Each generator keeps its own data. Do not use global variables."

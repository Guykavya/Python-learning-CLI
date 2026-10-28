import pytest

from solution import AlreadyParkedError, LotFullError, NotParkedError, ParkingError, ParkingLot


def test_exception_hierarchy():
    for cls in (LotFullError, AlreadyParkedError, NotParkedError):
        assert issubclass(cls, ParkingError), f"{cls.__name__} must inherit from ParkingError."
    assert issubclass(ParkingError, Exception), "ParkingError must inherit from Exception."


def test_exception_data_and_messages():
    e = LotFullError("large")
    assert e.size == "large" and str(e) == "no free spot for a large car", "LotFullError stores size; check the message."
    e = AlreadyParkedError("KA02", "S2")
    assert (e.plate, e.spot) == ("KA02", "S2"), "AlreadyParkedError stores plate and spot."
    assert str(e) == "KA02 is already parked at S2", "Pass the message to super().__init__."
    e = NotParkedError("ZZ99")
    assert e.plate == "ZZ99" and str(e) == "ZZ99 is not parked here", "NotParkedError stores plate; check the message."


def test_bad_lot_sizes():
    for args in ((-1, 2), (2, -1), (1.5, 2), ("2", 1)):
        with pytest.raises(ValueError):
            ParkingLot(*args)
    assert ParkingLot(0, 0).report() == [], "A lot with no spots is allowed."


def test_small_cars_fill_small_then_large():
    lot = ParkingLot(small=2, large=1)
    assert lot.park("ka01", "small") == "S1", "The first small car takes S1."
    assert lot.park("KA02", "small") == "S2", "The next free small spot is S2."
    assert lot.park("ka03", "small") == "L1", "Small spots are full, so a small car takes a large spot."


def test_large_car_never_takes_small_spot():
    lot = ParkingLot(small=3, large=0)
    try:
        spot = lot.park("BUS1", "large")
    except LotFullError as e:
        assert e.size == "large", "LotFullError(size) records the size that did not fit."
    else:
        pytest.fail(f"A large car was parked at {spot}. A large car needs a large spot; with none free, raise LotFullError.")
    assert lot.free("small") == 3, "A refused car must not take any spot."


def test_full_lot():
    lot = ParkingLot(small=1, large=1)
    lot.park("A", "small")
    lot.park("B", "small")
    with pytest.raises(LotFullError, match="small"):
        lot.park("C", "small")


def test_already_parked():
    lot = ParkingLot(small=2, large=1)
    lot.park("ka02", "small")
    with pytest.raises(AlreadyParkedError) as info:
        lot.park(" ka02 ", "large")
    assert (info.value.plate, info.value.spot) == ("KA02", "S1"), (
        "Compare plates after strip().upper(); the error carries the clean plate and its current spot."
    )


def test_bad_size():
    lot = ParkingLot(1, 1)
    with pytest.raises(ValueError):
        lot.park("A", "medium")
    assert lot.where("A") is None, "A car with a bad size is not parked."


def test_leave_and_reuse_lowest_spot():
    lot = ParkingLot(small=3, large=1)
    for plate in ("A", "B", "C"):
        lot.park(plate, "small")
    assert lot.leave("b") == "S2", "leave returns the freed spot. Plates are compared after upper()."
    assert lot.leave("a") == "S1", "A leaves S1."
    assert lot.park("D", "small") == "S1", "Take the free spot with the LOWEST number (S1, not S2)."
    assert lot.park("E", "small") == "S2", "Then S2."


def test_leave_frees_large_spot_used_by_small_car():
    lot = ParkingLot(small=1, large=1)
    lot.park("A", "small")
    lot.park("B", "small")
    assert lot.where("B") == "L1", "B had to use the large spot."
    assert lot.leave("B") == "L1", "Leaving frees the large spot."
    assert lot.park("TRUCK", "large") == "L1", "Now a large car fits in L1."


def test_leave_unknown():
    lot = ParkingLot(1, 1)
    with pytest.raises(NotParkedError, match="ZZ99"):
        lot.leave("zz99")
    lot.park("A", "small")
    lot.leave("A")
    with pytest.raises(NotParkedError):
        lot.leave("A")


def test_where():
    lot = ParkingLot(1, 1)
    lot.park("ka01", "large")
    assert lot.where(" KA01") == "L1", "where uses the clean plate too."
    assert lot.where("nobody") is None, "A car that is not parked: None."


def test_free_counts_spots():
    lot = ParkingLot(small=2, large=2)
    lot.park("A", "small")
    lot.park("B", "large")
    assert (lot.free("small"), lot.free("large")) == (1, 1), "free(kind) counts free spots of that kind."
    lot.park("C", "small")
    lot.park("D", "small")
    assert (lot.free("small"), lot.free("large")) == (0, 0), "D (small) took the last large spot."


def test_full_walkthrough():
    lot = ParkingLot(small=2, large=1)
    assert lot.park("ka01", "small") == "S1"
    assert lot.park("KA02", "small") == "S2"
    assert lot.park("ka03", "small") == "L1"
    with pytest.raises(LotFullError):
        lot.park("ka04", "large")
    assert lot.leave("ka01") == "S1"
    assert lot.free("small") == 1, "S1 is free again."
    assert lot.report() == ["S2 KA02", "L1 KA03"], "report lists taken spots only, small first, with clean plates."
    assert lot.park("ka04", "small") == "S1", "The free small spot S1 is used before anything else."
    with pytest.raises(LotFullError):
        lot.park("ka05", "small")
    assert lot.leave("ka03") == "L1"
    assert lot.park("ka06", "large") == "L1"
    assert lot.report() == ["S1 KA04", "S2 KA02", "L1 KA06"], "Spot order, not parking order."


def test_report_number_order():
    lot = ParkingLot(small=11, large=0)
    for i in range(11):
        lot.park(f"C{i}", "small")
    for i in range(1, 10):
        lot.leave(f"C{i}")
    assert lot.report() == ["S1 C0", "S11 C10"], "Spots in number order: S1 ... S11."
    lot.park("X", "small")
    assert lot.report() == ["S1 C0", "S2 X", "S11 C10"], "S2 comes before S11 (numbers, not text order)."


def test_catch_base_class():
    lot = ParkingLot(0, 0)
    try:
        lot.park("A", "small")
    except ParkingError as e:
        assert isinstance(e, LotFullError), "A full lot raises LotFullError, which `except ParkingError` also catches."

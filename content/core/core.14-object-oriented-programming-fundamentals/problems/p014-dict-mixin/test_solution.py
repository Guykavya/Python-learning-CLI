from solution import Product, Student, ToDictMixin


def test_classes_use_the_mixin():
    assert issubclass(Student, ToDictMixin), "Student must list ToDictMixin as a base: class Student(ToDictMixin):"
    assert issubclass(Product, ToDictMixin), "Product must list ToDictMixin as a base."
    assert "to_dict" not in vars(Student) and "to_dict" not in vars(Product), (
        "Do not write to_dict in Student or Product. Write it once, in the mixin."
    )


def test_mixin_has_no_init():
    assert "__init__" not in vars(ToDictMixin), "A mixin adds behaviour only; it should not define __init__."


def test_student_to_dict():
    s = Student("Kavya", 17)
    assert s.to_dict() == {"name": "Kavya", "roll": 17}, "Student.to_dict() should hold name and roll, but not _notes."


def test_product_to_dict():
    p = Product("PEN-01", 20)
    assert p.to_dict() == {"sku": "PEN-01", "price": 20}, "Product.to_dict() should hold sku and price, but not _discount."


def test_internal_attributes_still_exist():
    s = Student("Kavya", 17)
    p = Product("PEN-01", 20)
    assert s._notes == [] and p._discount == 0, "Store the internal attributes too: self._notes = [] and self._discount = 0."


def test_attributes_added_later_appear():
    s = Student("Kavya", 17)
    s.city = "Pune"
    s._secret = "x"
    assert s.to_dict() == {"name": "Kavya", "roll": 17, "city": "Pune"}, (
        "to_dict() must read vars(self) each time, so new public attributes appear and new _ ones do not."
    )


def test_underscore_inside_a_name_is_public():
    s = Student("Kavya", 17)
    s.first_name = "K"
    assert s.to_dict() == {"name": "Kavya", "roll": 17, "first_name": "K"}, (
        "Only names that START with '_' are internal. first_name is public: use name.startswith('_')."
    )


def test_returns_a_new_dict():
    s = Student("Kavya", 17)
    d = s.to_dict()
    d["name"] = "changed"
    d["extra"] = 1
    assert s.name == "Kavya", "Changing the returned dict must not change the object. Build a new dict."
    assert not hasattr(s, "extra"), "Adding to the returned dict must not add attributes to the object."


def test_mixin_works_for_any_class():
    class Base:
        def __init__(self):
            self.kind = "base"

    class Thing(Base, ToDictMixin):
        def __init__(self, size):
            super().__init__()
            self.size = size
            self.__hidden = 1

    assert Thing(3).to_dict() == {"kind": "base", "size": 3}, (
        "to_dict() must only use self and vars(self), so it works in any class. "
        "A mangled name like _Thing__hidden starts with '_' too."
    )


def test_mixin_on_its_own():
    class Empty(ToDictMixin):
        pass

    assert Empty().to_dict() == {}, "An object with no attributes gives an empty dict."

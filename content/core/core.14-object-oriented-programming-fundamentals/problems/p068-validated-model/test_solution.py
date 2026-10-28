import pytest

from solution import Field, FieldError, IntField, Model, StrField


class User(Model):
    name = StrField(min_length=1, max_length=20)
    age = IntField(min_value=0, max_value=150)
    role = StrField(choices=["admin", "user"], required=False, default="user")


class Admin(User):
    role = StrField(choices=["admin"], required=False, default="admin")
    level = IntField(min_value=1)


class Note(Model):
    text = StrField(required=False)


def messages(eg):
    return [str(e) for e in eg.exceptions]


# ------------------------------------------------------------ fields on their own

def test_field_error():
    e = FieldError("age", "must be an int")
    assert (e.field, e.message, str(e)) == ("age", "must be an int", "age: must be an int"), "FieldError(field, message), str is 'field: message'."


def test_base_field_missing_values():
    assert Field().check("x", 5) == 5, "A present value is returned unchanged."
    with pytest.raises(FieldError, match="x: is required"):
        Field().check("x", None)
    assert Field(required=False).check("x", None) is None, "Not required and no default: None is fine."
    assert Field(default=7).check("x", None) == 7, "A default fills in a missing value."


@pytest.mark.parametrize("value, message", [
    ("5", "n: must be an int"), (5.0, "n: must be an int"), (True, "n: must be an int"),
    (-1, "n: must be >= 0"), (11, "n: must be <= 10"),
])
def test_int_field_errors(value, message):
    with pytest.raises(FieldError) as info:
        IntField(min_value=0, max_value=10).check("n", value)
    assert str(info.value) == message, f"IntField.check('n', {value!r}) should fail with {message!r}, got {str(info.value)!r}."


def test_int_field_ok_and_limits_optional():
    f = IntField(min_value=0, max_value=10)
    assert f.check("n", 0) == 0 and f.check("n", 10) == 10, "Limits are inclusive."
    assert IntField().check("n", -10 ** 9) == -10 ** 9, "No limits given: any int is fine."


def test_int_field_passes_kwargs_to_field():
    f = IntField(min_value=1, required=False, default=3)
    assert (f.required, f.default) == (False, 3), "IntField passes required/default on to Field.__init__ with **kwargs."
    assert f.check("n", None) == 3, "For None, IntField uses super().check(), which returns the default."
    with pytest.raises(FieldError, match="n: is required"):
        IntField().check("n", None)


@pytest.mark.parametrize("value, message", [
    (5, "s: must be a str"),
    ("", "s: length must be >= 1"),
    ("abcdef", "s: length must be <= 5"),
    ("abc", "s: must be one of: ab, abcd"),
])
def test_str_field_errors(value, message):
    with pytest.raises(FieldError) as info:
        StrField(min_length=1, max_length=5, choices=["ab", "abcd"]).check("s", value)
    assert str(info.value) == message, f"StrField.check('s', {value!r}) should fail with {message!r}, got {str(info.value)!r}."


def test_str_field_check_order():
    with pytest.raises(FieldError, match="length must be <= 2"):
        StrField(max_length=2, choices=["a"]).check("s", "abc")  # length before choices


def test_str_field_ok():
    assert StrField().check("s", "") == "", "Default min_length is 0: the empty string is fine."
    assert StrField(choices=["x", "y"]).check("s", "y") == "y", "A value from choices is fine."


# ------------------------------------------------------------ Model

def test_fields_in_order():
    fields = User.fields()
    assert list(fields) == ["name", "age", "role"], f"fields() lists the Field class attributes in definition order. Got {list(fields)}."
    assert fields["age"] is vars(User)["age"], "Return the Field objects themselves."


def test_fields_inherited_and_overridden():
    fields = Admin.fields()
    assert list(fields) == ["name", "age", "role", "level"], (
        f"Got {list(fields)}. Base fields first; a redefined field keeps its original position. "
        "Walk reversed(cls.__mro__)."
    )
    assert fields["role"] is vars(Admin)["role"], "The subclass's role Field wins."
    assert fields["name"] is vars(User)["name"], "name is inherited from User."


def test_fields_ignores_other_attributes():
    class WithExtras(Model):
        title = StrField()
        LIMIT = 5

        def helper(self):
            return 1

    assert list(WithExtras.fields()) == ["title"], "Only Field objects count, not other class attributes or methods."


def test_init_sets_values_and_none():
    u = User(name="Kavya")
    assert (u.name, u.age, u.role) == ("Kavya", None, None), "Every field becomes an instance attribute: given value or None."
    assert isinstance(type(u).age, IntField), "The instance attribute must not replace the Field on the class."


def test_init_unknown_field():
    with pytest.raises(TypeError, match="unknown field 'nmae'"):
        User(nmae="x")


def test_validate_ok_fills_defaults():
    u = User(name="Kavya", age=21)
    assert u.validate() is u, "validate returns self when everything is fine."
    assert u.to_dict() == {"name": "Kavya", "age": 21, "role": "user"}, "Cleaned values are stored back: the default role fills in."


def test_validate_collects_all_errors():
    bad = User(name="", age=200, role="boss")
    with pytest.raises(ExceptionGroup) as info:
        bad.validate()
    eg = info.value
    assert eg.message == "User has 3 invalid field(s)", f"Group message: f'{{ClassName}} has {{n}} invalid field(s)'. Got {eg.message!r}."
    assert messages(eg) == ["name: length must be >= 1", "age: must be <= 150", "role: must be one of: admin, user"], (
        f"One FieldError per bad field, in fields() order. Got {messages(eg)}."
    )
    assert all(isinstance(e, FieldError) for e in eg.exceptions), "The group contains FieldError objects."


def test_failed_validate_changes_nothing():
    u = User(name="Kavya", age=-5)
    with pytest.raises(ExceptionGroup):
        u.validate()
    assert u.role is None, "When validation fails, do not store any cleaned values (role stays None)."


def test_required_missing():
    with pytest.raises(ExceptionGroup) as info:
        User().validate()
    assert messages(info.value) == ["name: is required", "age: is required"], "Missing required fields are errors; role has a default."


def test_subclass_model():
    a = Admin(name="Asha", age=30, level=2)
    assert a.validate().to_dict() == {"name": "Asha", "age": 30, "role": "admin", "level": 2}, "Admin uses its own role default."
    with pytest.raises(ExceptionGroup) as info:
        Admin(name="Asha", age=30, role="user", level=0).validate()
    assert info.value.message == "Admin has 2 invalid field(s)", "Use type(self).__name__ in the message."
    assert messages(info.value) == ["role: must be one of: admin", "level: must be >= 1"], "Admin's role field allows only 'admin'."


def test_optional_field_without_default():
    n = Note()
    assert n.validate().to_dict() == {"text": None}, "required=False without default: None is valid."


def test_models_do_not_share_values():
    a = User(name="A", age=1)
    b = User(name="B", age=2)
    assert (a.name, b.name) == ("A", "B"), "Values live on each instance, not on the class."

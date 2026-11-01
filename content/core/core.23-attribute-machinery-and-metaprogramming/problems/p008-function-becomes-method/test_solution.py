import types

from solution import bind, method_parts, rebind


class Account:
    def __init__(self, owner, balance):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        return self.balance


class Slotted:
    __slots__ = ("x",)

    def __init__(self, x):
        self.x = x


def describe(self, prefix="obj"):
    return f"{prefix}:{type(self).__name__}"


def test_bind_returns_a_bound_method():
    acc = Account("ada", 10)
    m = bind(describe, acc)
    assert isinstance(m, types.MethodType), (
        "bind must return a real bound method (types.MethodType). Use func.__get__(obj, type(obj)); "
        "a lambda or functools.partial is not a method."
    )
    assert m() == "obj:Account", "Calling the bound method must pass obj as the first argument (self)."
    assert m(prefix="x") == "x:Account", "Extra arguments must be passed through after self."


def test_bind_remembers_object_and_function():
    acc = Account("ada", 10)
    m = bind(describe, acc)
    assert m.__self__ is acc, "A bound method remembers its instance in __self__."
    assert m.__func__ is describe, "A bound method remembers the plain function in __func__."


def test_bind_does_not_modify_the_object_or_class():
    acc = Account("ada", 10)
    before = dict(vars(acc))
    bind(describe, acc)
    assert vars(acc) == before, "bind must not set any attribute on the object."
    assert "describe" not in vars(Account), "bind must not add the function to the class."


def test_bind_works_without_instance_dict():
    s = Slotted(5)
    m = bind(describe, s)
    assert m() == "obj:Slotted", (
        "bind must work for objects with __slots__ (no __dict__). Do not do setattr(obj, ...); bind with __get__."
    )


def test_bind_works_with_lambda():
    acc = Account("ada", 10)
    m = bind(lambda self, n: self.balance * n, acc)
    assert m(3) == 30, "Every function, including a lambda, has __get__ and can be bound."


def test_method_parts():
    acc = Account("ada", 10)
    func, obj = method_parts(acc.deposit)
    assert func is Account.deposit, (
        "The function behind acc.deposit is the plain function stored on the class, Account.deposit (__func__)."
    )
    assert obj is acc, "The second part is the instance (__self__)."
    assert func(obj, 5) == 15, "Calling the function with the instance by hand is exactly what the bound method does."


def test_rebind_to_other_object():
    a = Account("ada", 10)
    b = Account("bob", 100)
    m = rebind(a.deposit, b)
    assert m.__self__ is b, "rebind must return a method bound to the OTHER object."
    assert m(1) == 101 and a.balance == 10, "Calling the rebound method changes b, not a."
    assert m.__func__ is Account.deposit, "rebind keeps the same underlying function."


def test_rebind_does_not_change_original():
    a = Account("ada", 10)
    b = Account("bob", 100)
    original = a.deposit
    rebind(original, b)
    assert original.__self__ is a, "Bound methods cannot be re-pointed: rebind must create a NEW method object."

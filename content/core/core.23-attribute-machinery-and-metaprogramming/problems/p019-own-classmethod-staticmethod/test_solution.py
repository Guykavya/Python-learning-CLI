import ast
from pathlib import Path

import solution
from solution import ClassMethod, StaticMethod


def make_classes():
    class Temperature:
        def __init__(self, celsius):
            self.celsius = celsius

        @ClassMethod
        def from_fahrenheit(cls, f):
            return cls((f - 32) * 5 / 9)

        @ClassMethod
        def describe(cls, suffix=""):
            return cls.__name__ + suffix

        @StaticMethod
        def c_to_f(c):
            return c * 9 / 5 + 32

    class Lab(Temperature):
        pass

    return Temperature, Lab


def test_classmethod_called_on_the_class():
    Temperature, _ = make_classes()
    t = Temperature.from_fahrenheit(212)
    assert type(t) is Temperature and t.celsius == 100, "Temperature.from_fahrenheit(212) must call func(Temperature, 212)."


def test_classmethod_called_on_an_instance_gets_the_class():
    Temperature, _ = make_classes()
    t = Temperature(5).from_fahrenheit(32)
    assert type(t) is Temperature and t.celsius == 0, (
        "Called on an instance, a class method still receives the CLASS. Bind to owner, not to instance."
    )
    assert Temperature(5).describe() == "Temperature"


def test_classmethod_passes_the_subclass():
    _, Lab = make_classes()
    assert type(Lab.from_fahrenheit(212)) is Lab, (
        "Lab.from_fahrenheit must build a Lab: the owner passed to __get__ is the class the attribute was "
        "looked up on (Lab), not the class where it was defined."
    )
    assert Lab(1).describe() == "Lab", "On a Lab instance, cls is Lab."


def test_classmethod_returns_a_real_bound_method():
    Temperature, Lab = make_classes()
    method = Lab.describe
    raw = Temperature.__dict__["describe"]
    assert method.__self__ is Lab, (
        "The result must be a bound method with __self__ = the class. Use types.MethodType(func, cls) "
        "(a lambda or closure has no __self__)."
    )
    assert method.__func__ is raw.__func__, "The bound method's __func__ must be the original function."
    assert method("!") == "Lab!", "Extra arguments are passed after cls."


def test_classmethod_get_without_owner():
    Temperature, Lab = make_classes()
    raw = Temperature.__dict__["describe"]
    bound = raw.__get__(Lab(0))
    assert bound() == "Lab", (
        "desc.__get__(obj) may be called with no owner. Then use type(instance) as the class."
    )


def test_keyword_arguments_pass_through():
    Temperature, _ = make_classes()
    assert Temperature.from_fahrenheit(f=212).celsius == 100, "Keyword arguments must reach the function."
    assert Temperature.c_to_f(c=0) == 32


def test_staticmethod_on_class_and_instance():
    Temperature, _ = make_classes()
    assert Temperature.c_to_f(100) == 212, "A static method gets exactly the arguments you pass."
    assert Temperature(3).c_to_f(0) == 32, (
        "Called on an instance, a static method must NOT receive the instance. Return the plain function from __get__."
    )


def test_staticmethod_returns_the_function_itself():
    Temperature, Lab = make_classes()
    raw = Temperature.__dict__["c_to_f"]
    assert Temperature.c_to_f is raw.__func__, "Class access must return the original function object itself (no wrapper)."
    assert Lab(1).c_to_f is raw.__func__, "Instance access too: no binding at all."


def test_staticmethod_object_is_callable():
    Temperature, _ = make_classes()
    raw = Temperature.__dict__["c_to_f"]
    assert raw(100) == 212, "The StaticMethod object itself must be callable (define __call__), like staticmethod in 3.10+."


def test_descriptors_are_the_learners_own():
    Temperature, _ = make_classes()
    assert type(Temperature.__dict__["describe"]) is ClassMethod
    assert type(Temperature.__dict__["c_to_f"]) is StaticMethod
    assert not issubclass(ClassMethod, classmethod) and not issubclass(StaticMethod, staticmethod), (
        "Write the descriptors yourself; do not subclass the built-ins."
    )
    tree = ast.parse(Path(solution.__file__).read_text())
    used = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    assert not used & {"classmethod", "staticmethod"}, "Do not use the built-in classmethod/staticmethod in solution.py."

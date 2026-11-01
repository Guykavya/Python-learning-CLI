import pytest

from solution import InterfaceMeta


def make_shape():
    class Shape(metaclass=InterfaceMeta, abstract=True):
        required = ("area", "perimeter")

        def describe(self):
            return f"{type(self).__name__} with area {self.area()}"

    return Shape


def test_concrete_class_that_implements_everything():
    Shape = make_shape()

    class Square(Shape):
        def __init__(self, side):
            self.side = side

        def area(self):
            return self.side ** 2

        def perimeter(self):
            return 4 * self.side

    sq = Square(3)
    assert sq.area() == 9 and sq.side == 3, "Concrete classes must be created and instantiated normally (with __init__)."
    assert sq.describe() == "Square with area 9", "Inherited methods of the abstract base still work."
    assert isinstance(Square, InterfaceMeta), "Subclasses get the metaclass of their base automatically."


def test_missing_names_raise_at_class_creation():
    Shape = make_shape()
    with pytest.raises(TypeError) as info:
        class Circle(Shape):
            pass
    assert str(info.value) == "Circle must implement: area, perimeter", (
        "The class statement itself must fail, with the class name and the missing names sorted, joined by ', '."
    )

    with pytest.raises(TypeError) as info:
        class Half(Shape):
            def perimeter(self):
                return 0
    assert str(info.value) == "Half must implement: area", "Only the names that are really missing are listed."


def test_message_names_are_sorted():
    class Base(metaclass=InterfaceMeta, abstract=True):
        required = ("zeta", "alpha", "mid")

    with pytest.raises(TypeError) as info:
        class Bad(Base):
            pass
    assert str(info.value) == "Bad must implement: alpha, mid, zeta", "Sort the missing names alphabetically."


def test_abstract_keyword_is_consumed_and_not_inherited():
    Shape = make_shape()
    assert Shape.is_abstract is True, "A class created with abstract=True is abstract."
    with pytest.raises(TypeError):
        class Forgot(Shape):           # no abstract=True: concrete, so checked
            def area(self):
                return 1

    class Polygon(Shape, abstract=True):
        def area(self):
            return 0

    assert Polygon.is_abstract is True, "abstract=True works on subclasses too."

    class Triangle(Polygon):
        def perimeter(self):
            return 3

    assert Triangle.is_abstract is False, (
        "The abstract flag must not be inherited: store it per class and read it from vars(cls), "
        "not with a plain class attribute lookup that finds the parent's value."
    )
    assert Triangle().area() == 0, "An implementation inherited from an abstract parent counts."


def test_other_class_keywords_reach_init_subclass():
    seen = []

    class Plugin(metaclass=InterfaceMeta, abstract=True):
        required = ("run",)

        def __init_subclass__(cls, /, tag=None, **kwargs):
            super().__init_subclass__(**kwargs)
            seen.append((cls.__name__, tag))

    class Fast(Plugin, tag="fast"):
        def run(self):
            return "go"

    class Slow(Plugin, abstract=True, tag="slow"):
        pass

    assert seen == [("Fast", "fast"), ("Slow", "slow")], (
        "Pop 'abstract' in the metaclass but pass every other keyword on to type.__new__, "
        "which hands them to __init_subclass__."
    )


def test_requirements_are_collected_from_the_whole_mro():
    Shape = make_shape()

    class Named(Shape, abstract=True):
        required = ("name",)

    assert Named.requirements == ("area", "name", "perimeter"), (
        "requirements is the sorted union of every 'required' tuple in the MRO, not just the nearest one."
    )
    with pytest.raises(TypeError) as info:
        class Blob(Named):
            def name(self):
                return "blob"
    assert str(info.value) == "Blob must implement: area, perimeter", (
        "A subclass that defines its own 'required' still has to implement the parent's requirements."
    )


def test_inherited_and_mixin_implementations_count():
    Shape = make_shape()

    class AreaMixin:
        def area(self):
            return 42

    class Thing(AreaMixin, Shape):
        def perimeter(self):
            return 1

    assert Thing().area() == 42, "A method from a plain mixin class in the MRO counts as implemented."


def test_none_means_not_implemented():
    Shape = make_shape()

    class Base(Shape):
        def area(self):
            return 1

        def perimeter(self):
            return 2

    with pytest.raises(TypeError) as info:
        class NoArea(Base):
            area = None
    assert str(info.value) == "NoArea must implement: area", (
        "area = None in the class shadows the parent's method (lookup finds None first), so it is not implemented."
    )


def test_abstract_class_cannot_be_instantiated():
    Shape = make_shape()
    with pytest.raises(TypeError) as info:
        Shape()
    assert str(info.value) == "Shape is abstract", (
        "Override __call__ on the metaclass: Shape() calls type(Shape).__call__(Shape)."
    )


def test_metaclass_properties_are_not_visible_on_instances():
    Shape = make_shape()

    class Square(Shape):
        def area(self):
            return 1

        def perimeter(self):
            return 4

    assert Square.is_abstract is False and Square.requirements == ("area", "perimeter"), (
        "is_abstract and requirements are properties on the metaclass, read through the class."
    )
    with pytest.raises(AttributeError):
        Square().is_abstract
    with pytest.raises(AttributeError):
        Square().requirements
    assert "is_abstract" not in vars(Square) and "requirements" not in vars(Square), (
        "Define is_abstract and requirements on the metaclass, not as attributes copied into every class."
    )

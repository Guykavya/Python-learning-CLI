import pytest

from solution import TypedList


def test_subscription_returns_a_real_subclass():
    IntList = TypedList[int]
    assert isinstance(IntList, type), (
        "TypedList[int] must be a class. Without your own __class_getitem__, list's version returns a "
        "types.GenericAlias, which checks nothing."
    )
    assert issubclass(IntList, TypedList) and issubclass(IntList, list), "TypedList[int] must subclass TypedList (and so list)."
    assert IntList.item_type is int, "The new class must remember its element type in item_type."


def test_subclass_name():
    assert TypedList[int].__name__ == "TypedList[int]", "Name the new class 'TypedList[<type name>]'."
    assert TypedList[str].__name__ == "TypedList[str]"


def test_same_parameter_gives_the_same_class():
    assert TypedList[int] is TypedList[int], (
        "TypedList[int] must return the SAME class every time (cache it in a dict). "
        "Otherwise isinstance(x, TypedList[int]) fails for lists made earlier."
    )
    assert TypedList[int] is not TypedList[str], "Different element types need different classes."


def test_append_checks_type():
    nums = TypedList[int]()
    nums.append(1)
    nums.append(2)
    assert nums == [1, 2], "Correctly typed items are appended normally."
    with pytest.raises(TypeError) as info:
        nums.append("3")
    msg = str(info.value)
    assert "int" in msg and "str" in msg, "The TypeError message must name the expected type (int) and the type it got (str)."
    assert nums == [1, 2], "A rejected item must not be added."


def test_constructor_checks_items():
    nums = TypedList[int]([1, 2, 3])
    assert nums == [1, 2, 3] and isinstance(nums, TypedList[int]), "TypedList[int]([1, 2, 3]) builds a checked list."
    with pytest.raises(TypeError):
        TypedList[int]([1, "two", 3])


def test_constructor_reads_a_generator_once():
    nums = TypedList[int](n * n for n in range(4))
    assert nums == [0, 1, 4, 9], (
        "A generator can be read only once. If you loop over it to check and then pass it to list.__init__, "
        "the list ends up empty. Turn it into a list first."
    )


def test_isinstance_works_with_subclasses_of_item_type():
    class Animal:
        pass

    class Dog(Animal):
        pass

    pets = TypedList[Animal]()
    pets.append(Dog())
    assert len(pets) == 1, "Use isinstance, so a Dog is accepted where an Animal is expected."


def test_plain_typedlist_accepts_anything():
    anything = TypedList([1, "a", None])
    anything.append(3.5)
    assert anything == [1, "a", None, 3.5], "TypedList without [T] has item_type object and accepts every value."


def test_parameter_must_be_a_class():
    with pytest.raises(TypeError):
        TypedList[3]

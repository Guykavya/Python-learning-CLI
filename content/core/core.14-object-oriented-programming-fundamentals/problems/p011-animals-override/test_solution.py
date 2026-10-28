from solution import Animal, Cat, Cow, Dog


def test_base_animal():
    a = Animal("Blob")
    assert a.name == "Blob", "Animal stores its name."
    assert a.sound() == "...", "A plain Animal's sound is '...'."
    assert a.describe() == "Blob says ...", "describe() should return '<name> says <sound>'."


def test_subclasses_inherit_from_animal():
    for cls in (Dog, Cat, Cow):
        assert issubclass(cls, Animal), f"{cls.__name__} must inherit from Animal: class {cls.__name__}(Animal):"


def test_sounds():
    assert Dog("Rex").sound() == "Woof", "Dog.sound() should return 'Woof'."
    assert Cat("Tom").sound() == "Meow", "Cat.sound() should return 'Meow'."
    assert Cow("Gauri").sound() == "Moo", "Cow.sound() should return 'Moo'."


def test_describe_uses_the_overridden_sound():
    assert Dog("Rex").describe() == "Rex says Woof", "describe() must call self.sound(), so a Dog says Woof."
    assert Cat("Tom").describe() == "Tom says Meow", "describe() must call self.sound(), so a Cat says Meow."
    assert Cow("Gauri").describe() == "Gauri says Moo", "describe() must call self.sound(), so a Cow says Moo."


def test_subclasses_override_only_sound():
    for cls in (Dog, Cat, Cow):
        own = vars(cls)
        assert "sound" in own, f"{cls.__name__} should override sound()."
        assert "describe" not in own, f"{cls.__name__} should not repeat describe(); inherit it from Animal."
        assert "__init__" not in own, f"{cls.__name__} does not need its own __init__; Animal's is inherited."


def test_describe_works_for_a_new_subclass():
    class Duck(Animal):
        def sound(self):
            return "Quack"

    assert Duck("Donald").describe() == "Donald says Quack", (
        "describe() must not check the type (if isinstance(self, Dog) ...). Just call self.sound()."
    )


def test_fetch_only_on_dogs():
    assert Dog("Rex").fetch() == "Rex fetches the ball", "Dog.fetch() should return '<name> fetches the ball'."
    assert not hasattr(Cat("Tom"), "fetch"), "Only dogs fetch. Put fetch() in Dog, not in Animal."


def test_isinstance():
    d = Dog("Rex")
    assert isinstance(d, Dog) and isinstance(d, Animal), "A Dog is also an Animal."
    assert not isinstance(d, Cat), "A Dog is not a Cat."

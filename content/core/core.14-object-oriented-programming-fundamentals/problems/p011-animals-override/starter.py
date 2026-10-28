class Animal:
    def __init__(self, name):
        self.name = name

    def sound(self):
        return "..."

    def describe(self):
        # TODO: "<name> says <sound>", using self.sound()
        raise NotImplementedError


# TODO: Dog, Cat and Cow inherit from Animal and override sound()
# TODO: Dog also has fetch()

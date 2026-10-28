class Person:
    def __init__(self, name, age):
        # TODO: check age, store name and age
        pass

    def describe(self):
        raise NotImplementedError


class Employee(Person):
    def __init__(self, name, age, employee_id, salary):
        # TODO: let Person set name and age, then add employee_id and salary
        pass

    def describe(self):
        raise NotImplementedError


class Manager(Employee):
    def __init__(self, name, age, employee_id, salary):
        # TODO: let Employee do its part, then start an empty reports list
        pass

    def add_report(self, employee):
        raise NotImplementedError

    def describe(self):
        raise NotImplementedError

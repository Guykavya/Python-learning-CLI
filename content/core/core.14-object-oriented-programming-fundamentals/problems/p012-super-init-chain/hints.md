## Hint 1

If `Employee.__init__` sets only `employee_id` and `salary`, who sets `name` and `age`? And if it
sets `self.name` and `self.age` itself, who checks that the age is not negative? Which one line lets
`Person` do its own job?

## Hint 2

Each `describe` can ask its parent for the text so far and add one piece:
`return super().describe() + ", id " + self.employee_id`. Then `Manager` only adds the reports part,
and a change to `Person.describe` shows up everywhere.

## Hint 3

```
class Person:
    __init__: check age, store name and age
    describe: f"{self.name} ({self.age})"

class Employee(Person):
    __init__(self, name, age, employee_id, salary):
        super().__init__(name, age)
        check salary, store employee_id and salary
    describe: super().describe() + f", id {self.employee_id}"

class Manager(Employee):
    __init__(self, name, age, employee_id, salary):
        super().__init__(name, age, employee_id, salary)
        self.reports = []           # a NEW list for each manager
    add_report(self, employee):
        if not isinstance(employee, Employee): raise TypeError(...)
        if employee is self: raise ValueError(...)
        self.reports.append(employee)
    describe: super().describe() + f", {len(self.reports)} reports"
```

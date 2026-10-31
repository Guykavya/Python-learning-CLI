## Approach

Each class does **its own** part and leaves the rest to its parent (chapter section 11):

- `Person` checks and stores `name` and `age`.
- `Employee` asks `Person` to do that with `super().__init__(name, age)`, then checks and stores its
  two extra fields.
- `Manager` asks `Employee` (which asks `Person`), then creates its own empty `reports` list.

Because every subclass goes through `super().__init__`, the age check written once in `Person`
protects all three classes. If a subclass set `self.age = age` itself, the check would be skipped.

`describe` works the same way: each version asks the parent for the text so far and adds one part.
`reports` is created in `__init__`, so every manager gets a new list (section 5's shared-list trap).

## Code

```python
class Person:
    def __init__(self, name, age):
        if age < 0:
            raise ValueError("age cannot be negative")
        self.name = name
        self.age = age

    def describe(self):
        return f"{self.name} ({self.age})"


class Employee(Person):
    def __init__(self, name, age, employee_id, salary):
        super().__init__(name, age)
        if salary < 0:
            raise ValueError("salary cannot be negative")
        self.employee_id = employee_id
        self.salary = salary

    def describe(self):
        return super().describe() + f", id {self.employee_id}"


class Manager(Employee):
    def __init__(self, name, age, employee_id, salary):
        super().__init__(name, age, employee_id, salary)
        self.reports = []

    def add_report(self, employee):
        if not isinstance(employee, Employee):
            raise TypeError("reports must be employees")
        if employee is self:
            raise ValueError("a manager cannot report to themselves")
        self.reports.append(employee)

    def describe(self):
        return super().describe() + f", {len(self.reports)} reports"
```

## Complexity

O(1) for every method; `describe` walks a chain of three classes.

## Another way

`Person.__init__(self, name, age)` (naming the parent directly) also works in single inheritance, but
it hard-codes the parent's name, and it breaks the cooperative chain you will need with multiple
inheritance (section 12). Prefer `super()`. If `Manager` needed no extra fields at all, it could skip
`__init__` entirely and inherit `Employee`'s.

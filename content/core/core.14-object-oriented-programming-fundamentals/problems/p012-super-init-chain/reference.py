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

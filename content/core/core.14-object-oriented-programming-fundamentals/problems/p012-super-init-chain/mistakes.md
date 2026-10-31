- Forgetting `super().__init__(...)`. The object then has no `name` or `age`, and you get
  `AttributeError` later, far from the real mistake.
- Setting `self.name = name; self.age = age` again in `Employee`. It works until someone passes a
  negative age: `Person`'s check never runs.
- Writing `super().__init__(self, name, age)`. `super()` already passes `self`; the extra `self` shifts
  every argument by one.
- Using `def __init__(..., reports=[])` or a class attribute `reports = []`. All managers share one list.
- Copying `f"{self.name} ({self.age})"` into every `describe`. Build on `super().describe()`.
- Checking `type(employee) == Employee` in `add_report`. A `Manager` is an `Employee` too; use `isinstance`.

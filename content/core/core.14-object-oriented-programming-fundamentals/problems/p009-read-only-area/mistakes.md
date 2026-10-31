- Saving `self.area = ...` in `__init__`. With a property named `area` it raises `AttributeError`;
  without one, the value is stale after the radius changes.
- Adding a setter that silently ignores the value (`pass`). The caller thinks it worked. Leave the
  setter out so Python raises `AttributeError`.
- Using `value < 0` for the check. A circle of radius 0 is not a circle; the rule says zero or negative.
- Writing `self._radius = radius` in `__init__`. The constructor then skips the check.
- Writing `math.pi * self.radius * 2`. That is the circumference, not the area.

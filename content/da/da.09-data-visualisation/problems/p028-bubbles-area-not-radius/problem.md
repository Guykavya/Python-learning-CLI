# Bubbles: area, not radius

Chapter section 6.3. In a bubble chart a third number is shown as the **size** of each dot. The eye reads the **area** of a circle, so the area, not the radius, must
be proportional to the value: a value twice as large gets a circle with twice the area (a radius only 1.41 times larger). If you make the radius proportional, the big bubbles look
much bigger than the data say.

In matplotlib, the `s` argument of `ax.scatter` is the marker **area** (in points squared). Write two functions:

- `bubble_sizes(values, max_area)` returns a NumPy array of areas: `max_area * value / max(value)`, so the largest value gets exactly `max_area`.
  A value of 0 gets area 0; a **negative** value raises `ValueError("negative value")`; if all values are 0, return all zeros (no division by zero).
- `bubble_chart(x, y, values, max_area=400)` draws a scatter of `y` against `x` with those areas and returns the Figure.

## Example

`bubble_sizes([10, 20, 40], 400)` is `[100., 200., 400.]`.

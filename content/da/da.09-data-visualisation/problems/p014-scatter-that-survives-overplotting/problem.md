# Scatter that survives overplotting

Chapter section 4.4. With thousands of points a scatter becomes a solid blob: the dots hide each other. Make each dot **small** and
**see-through** so that dense areas look darker.

Write `overplot_scatter(df, xlabel, ylabel)`. `df` has columns `x` and `y`. Draw one scatter and return the Figure.

- **every** point is drawn (one marker per row);
- if `len(df) > 2000`: `alpha <= 0.3` and the marker area `s <= 10`;
- otherwise (a small sample): `alpha >= 0.5` (or no alpha at all) and `s >= 20`, so single points stay visible;
- the axes carry the given labels (they must contain the units).

## Example

2,500 points drawn with `alpha=0.2, s=6`; 100 points drawn with `alpha=0.8, s=30`.

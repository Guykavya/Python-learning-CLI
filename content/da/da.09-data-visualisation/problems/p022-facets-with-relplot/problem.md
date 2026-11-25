# Facets with relplot

Chapter section 5.5. Figure-level seaborn functions (`relplot`, `catplot`, `displot`) create their own figure and can split the data into **small multiples**.
They return a `FacetGrid`, a wrapper around the figure.

Write `store_lines(df)`. `df` has the columns `week`, `store` and `revenue` (one row per store and week). Return a `FacetGrid` made by `sns.relplot` that shows:

- a **line** of revenue against week (`kind="line"`, no interval: `errorbar=None`);
- **one panel per store** (`col="store"`, three panels per row at most: `col_wrap=3`);
- panel titles that are **just the store name**, not `store = Airport` (`g.set_titles("{col_name}")`);
- **one shared y axis**, so the panels can be compared (`facet_kws={"sharey": True}`).

## Example

Data for stores A, B, C gives a `FacetGrid` with three panels titled `A`, `B`, `C` that all use the same y scale.

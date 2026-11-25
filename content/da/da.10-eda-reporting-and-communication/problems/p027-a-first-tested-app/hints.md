## Hint 1

Which function draws each element? A multiselect **returns** the current selection; on the next interaction the whole file runs again with the new value. What should happen when the list is empty?

## Hint 2

```text
df = DATA if df is None else df
st.title("Revenue by city")
cities = sorted(df["city"].unique())
chosen = st.multiselect("City", cities, default=cities)
if not chosen: st.info(...); return
st.metric("Revenue", f"{total:,.0f}")
```

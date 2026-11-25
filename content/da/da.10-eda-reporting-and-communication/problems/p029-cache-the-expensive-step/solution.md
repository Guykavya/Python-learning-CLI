## Approach

The cache key is the argument `n`. The first call for each value runs the body (and increments the counter); every later call with the same value returns the stored DataFrame without running it.

## Code

```python
import pandas as pd
import streamlit as st


@st.cache_data
def load_data(n):
    st.session_state["load_calls"] = st.session_state.get("load_calls", 0) + 1     # counts real calls (for the test)
    return pd.DataFrame({"x": range(n)})


def main():
    n = st.selectbox("Rows", [10, 100, 1000])
    df = load_data(n)
    st.metric("Rows loaded", f"{len(df):,}")


if __name__ == "__main__":
    main()
```

## Complexity

One real load per distinct argument; every rerun after that is a dictionary lookup.

## Another way

`@st.cache_resource` caches objects that should be **shared** and not copied (a database connection, a model). `cache_data` returns a copy of the stored data on each call, so one rerun cannot change another's data.

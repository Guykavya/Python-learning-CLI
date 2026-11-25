# Cache the expensive step

Chapter section 8.4. Every click reruns the whole script. If loading the data takes ten seconds, every click takes ten seconds, unless the result is **cached**: `@st.cache_data` stores the result
of a function **by its arguments** and returns the stored result when the same arguments come again.

`solution.py` is an app whose `load_data(n)` is "expensive". The starter counts its real calls in `st.session_state["load_calls"]` (keep that line: it is how the test sees the calls).
Right now the counter goes up on **every** rerun. Change the app so that:

- `load_data` is cached with `@st.cache_data`, so it really runs **once per distinct `n`**;
- the app still shows a selectbox `Rows` with the options `10`, `100`, `1000` and a metric `Rows loaded` with the number of rows (`f"{len(df):,}"`).

## Example

Start (n = 10), rerun twice, choose 100, choose 10 again: the app ran five times, `load_data` really ran **twice** (once for 10, once for 100).

## Hint 1

What does the decorator use as the key of the cache? What happens on a rerun where the selectbox still says 10?

## Hint 2

Put `@st.cache_data` on the line above `def load_data(n):`. Nothing else needs to change. Note that a cached function's body only runs on a cache **miss**: that is why the counter inside it counts real calls.

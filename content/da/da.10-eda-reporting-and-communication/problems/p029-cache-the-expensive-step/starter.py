import pandas as pd
import streamlit as st


def load_data(n):
    st.session_state["load_calls"] = st.session_state.get("load_calls", 0) + 1     # counts real calls (keep this line)
    return pd.DataFrame({"x": range(n)})


def main():
    n = st.selectbox("Rows", [10, 100, 1000])
    df = load_data(n)
    st.metric("Rows loaded", f"{len(df):,}")


if __name__ == "__main__":
    main()

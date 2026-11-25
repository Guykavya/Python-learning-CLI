import pandas as pd
import streamlit as st

DATA = pd.DataFrame({"city": ["Metro", "Metro", "Large", "Small"], "revenue": [1200.0, 800.0, 950.0, 400.0]})


def main(df=None):
    df = DATA if df is None else df
    st.title("Revenue by city")
    cities = sorted(df["city"].unique())
    chosen = st.multiselect("City", cities, default=cities)
    if not chosen:
        st.info("Select at least one city.")
        return
    total = df.loc[df["city"].isin(chosen), "revenue"].sum()
    st.metric("Revenue", f"{total:,.0f}")


if __name__ == "__main__":
    main()

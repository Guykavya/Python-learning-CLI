import pandas as pd
import streamlit as st

DATA = pd.DataFrame({"city": ["Metro", "Metro", "Large", "Small"], "revenue": [1200.0, 800.0, 950.0, 400.0]})


def main(df=None):
    """Title, a City multiselect (all selected), and a Revenue metric; an info message when nothing is selected."""
    raise NotImplementedError


if __name__ == "__main__":
    main()

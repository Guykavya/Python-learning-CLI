# A first tested app

Chapter sections 8.1 to 8.3. A Streamlit app is a Python file that is run **from top to bottom on every interaction**. We test it without a browser with `AppTest`.

`solution.py` is the app. Write `main(df=None)`:

- `df` defaults to the small table `DATA` (already in the starter); a test can pass its own table;
- a title `Revenue by city` (`st.title`);
- a multiselect labelled `City` with the sorted city names as options, **all selected** by default;
- if nothing is selected: `st.info("Select at least one city.")` and nothing else below it;
- otherwise one `st.metric` labelled `Revenue` whose value is the total revenue of the selected cities, written like `3,350` (thousands separator, no decimals).

Keep the last two lines of the starter: `if __name__ == "__main__": main()`. They make `streamlit run solution.py` (and the test) start the app.

Run it yourself with `streamlit run solution.py` and click around; the test does the same in memory.

## Example

By default the metric shows `3,350`; with only `Metro` selected it shows `2,000`.

## Hint 1

Copy the logic you already wrote (problems 6 and 28) and test each function on a tiny table before touching Streamlit. The app then calls them in order: filter, KPIs, baseline, display.

## Hint 2

```text
with st.sidebar: channels = st.multiselect("Channel", sorted(...), default=sorted(...)); ...
sel = filter_data(...); if sel is None: st.warning(...); return
kpis = monthly_kpis(*sel); base = baseline(kpis); last = kpis.index[-1]
tab_find, tab_explore = st.tabs(["Findings", "Explore"])
with tab_find: st.markdown(finding_text(kpis, base))
with tab_explore: c1, c2, c3 = st.columns(3); c1.metric(...); ...; st.line_chart(...)
```

def yoy_change(series):
    last_year = series.copy()
    last_year.index = last_year.index + 12
    out = series - last_year.reindex(series.index)
    out.name = series.name
    return out

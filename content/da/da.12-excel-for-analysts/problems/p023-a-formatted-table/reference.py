import pandas as pd
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter


def _plain(v):
    if v is None or (not isinstance(v, str) and pd.isna(v)):
        return None
    if isinstance(v, pd.Timestamp):
        return v.to_pydatetime()
    return v.item() if hasattr(v, "item") else v


def write_df(ws, df, formats=None):
    formats = formats or {}
    ws.append(list(df.columns))
    for c in ws[1]:
        c.font = Font(bold=True)
    for row in df.itertuples(index=False):
        ws.append([_plain(v) for v in row])
    for j, name in enumerate(df.columns, 1):
        letter = get_column_letter(j)
        fmt = formats.get(name)
        is_date = pd.api.types.is_datetime64_any_dtype(df[name])
        if fmt is None and is_date:
            fmt = "yyyy-mm-dd"
        if fmt:
            for r in range(2, len(df) + 2):
                ws.cell(r, j).number_format = fmt
        longest = max([len(str(name))] + [len(str(ws.cell(r, j).value)) for r in range(2, len(df) + 2) if ws.cell(r, j).value is not None])
        ws.column_dimensions[letter].width = min(longest + 2, 40)
    ws.freeze_panes = "A2"

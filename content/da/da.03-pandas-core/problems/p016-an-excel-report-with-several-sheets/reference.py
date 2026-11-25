import pandas as pd


def write_report(path, sheets):
    """Write each frame of `sheets` to its own sheet of the workbook at `path`, without the index."""
    with pd.ExcelWriter(path) as writer:
        for name, frame in sheets.items():
            frame.to_excel(writer, sheet_name=name, index=False)

import pandas as pd
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter


def write_df(ws, df, formats=None):
    """Header in bold in row 1, plain Python values from row 2, number formats by column, frozen header, column widths."""
    raise NotImplementedError

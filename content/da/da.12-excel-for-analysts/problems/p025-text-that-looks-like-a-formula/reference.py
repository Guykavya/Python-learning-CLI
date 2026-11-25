def write_safe(ws, row, col, value):
    cell = ws.cell(row, col, value)
    if isinstance(value, str) and value[:1] in ("=", "+", "-", "@"):
        cell.data_type = "s"
    return cell

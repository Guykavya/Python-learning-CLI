def code_cells(nb):
    result = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source = cell.get("source", "")
        result.append(source if isinstance(source, str) else "".join(source))
    return result

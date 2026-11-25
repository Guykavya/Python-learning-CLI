def run_order_problems(nb):
    largest = 0
    bad = []
    for index, cell in enumerate(nb["cells"]):
        if cell["cell_type"] != "code":
            continue
        count = cell.get("execution_count")
        if count is None or count <= largest:
            bad.append(index)
        else:
            largest = count
    return bad

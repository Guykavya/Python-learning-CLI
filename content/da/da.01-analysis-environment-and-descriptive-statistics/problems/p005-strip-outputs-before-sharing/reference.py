import copy


def strip_outputs(nb):
    clean = copy.deepcopy(nb)
    for cell in clean.get("cells", []):
        cell.get("metadata", {}).pop("execution", None)
        if cell.get("cell_type") == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
    return clean

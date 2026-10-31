import csv


def sum_column(path, column):
    total = 0.0
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cell = row[column]
            if cell.strip() != "":
                total += float(cell)
    return total

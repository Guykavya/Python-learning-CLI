from itertools import zip_longest


def csv_lines(columns, fill=""):
    for row in zip_longest(*columns, fillvalue=fill):
        yield ",".join(str(value) for value in row)

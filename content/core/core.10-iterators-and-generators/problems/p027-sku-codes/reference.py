import itertools


def sku_codes(product, sizes, colours, unavailable=()):
    for size, colour in itertools.product(sizes, colours):
        if (size, colour) in unavailable:
            continue
        yield f"{product}-{size}-{colour}".upper()

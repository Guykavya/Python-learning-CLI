RATES = {"local": 5.0, "national": 8.0, "world": 20.0}
WEIGHT_FEES = [(1, 0.0), (5, 2.5), (20, 7.5)]
HEAVY_FEE = 15.0
FLAT_EXTRAS = {"fragile": 3.0, "signature": 1.5}
INSURED_RATE = 0.03
EXPRESS_FACTOR = 1.5


def shipping_cost(weight_kg, zone, express=False, extras=[]):
    if zone not in RATES:
        raise ValueError(f"unknown zone: {zone}")
    cost = RATES[zone]
    for limit, fee in WEIGHT_FEES:
        if weight_kg < limit:
            cost += fee
            break
    else:
        cost += HEAVY_FEE
    if express:
        cost *= EXPRESS_FACTOR
    total = cost
    if weight_kg > 20:
        extras.append("insured")
    if "insured" in extras:
        total += cost * INSURED_RATE
    for name in set(extras):
        total += FLAT_EXTRAS.get(name, 0.0)
    return int(total * 100) / 100

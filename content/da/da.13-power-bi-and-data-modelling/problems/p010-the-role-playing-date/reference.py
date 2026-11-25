def ship_date_measure():
    return "CALCULATE([Revenue], USERELATIONSHIP(Sales[ShipDateKey], Date[DateKey]))"

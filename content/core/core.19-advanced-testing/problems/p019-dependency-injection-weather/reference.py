class WeatherReport:
    def __init__(self, client):
        self.client = client

    def line(self, city):
        try:
            temp = self.client.temperature(city)
        except KeyError:
            return f"{city}: no data"
        if temp >= 30:
            label = "hot"
        elif temp <= 5:
            label = "cold"
        else:
            label = "mild"
        return f"{city}: {temp}C, {label}"

    def lines(self, cities):
        return [self.line(city) for city in cities]

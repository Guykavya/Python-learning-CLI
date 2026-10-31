class WeatherReport:
    def __init__(self, client):
        self.client = client

    def line(self, city):
        return city

    def lines(self, cities):
        return [self.line(city) for city in cities]

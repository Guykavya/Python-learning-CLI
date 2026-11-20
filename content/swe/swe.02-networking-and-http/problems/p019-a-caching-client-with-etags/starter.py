class CachingClient:
    def __init__(self, client, clock):
        self.client = client
        self.clock = clock
        self.cache = {}

    def get(self, url):
        # TODO: fresh copy -> ("cache"); else request (with If-None-Match when possible); handle 304 and 200
        response = self.client.get(url)
        return response.content, "network"

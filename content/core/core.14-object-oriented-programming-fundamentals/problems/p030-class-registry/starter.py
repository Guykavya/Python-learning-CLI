import json


class Exporter:
    registry = {}

    @classmethod
    def register(cls, name):
        # TODO: return a decorator that stores the class in cls.registry
        def decorator(klass):
            return klass
        return decorator

    @classmethod
    def create(cls, name, **options):
        return None

    @classmethod
    def formats(cls):
        return []

    def export(self, rows):
        raise NotImplementedError


class CsvExporter(Exporter):
    def __init__(self, sep=","):
        self.sep = sep

    def export(self, rows):
        return ""


class JsonExporter(Exporter):
    def __init__(self, indent=None):
        self.indent = indent

    def export(self, rows):
        return ""

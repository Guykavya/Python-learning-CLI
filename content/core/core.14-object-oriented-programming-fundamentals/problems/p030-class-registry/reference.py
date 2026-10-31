import json


class Exporter:
    registry = {}

    @classmethod
    def register(cls, name):
        def decorator(klass):
            if not (isinstance(klass, type) and issubclass(klass, Exporter)):
                raise TypeError(f"{klass!r} is not an Exporter subclass")
            if name in Exporter.registry:
                raise ValueError(f"format {name!r} is already registered")
            Exporter.registry[name] = klass
            klass.format_name = name
            return klass
        return decorator

    @classmethod
    def create(cls, name, **options):
        if name not in Exporter.registry:
            known = ", ".join(sorted(Exporter.registry))
            raise KeyError(f"unknown format {name!r} (known: {known})")
        return Exporter.registry[name](**options)

    @classmethod
    def formats(cls):
        return sorted(Exporter.registry)

    def export(self, rows):
        raise NotImplementedError(f"{type(self).__name__} must define export()")


@Exporter.register("csv")
class CsvExporter(Exporter):
    def __init__(self, sep=","):
        self.sep = sep

    def export(self, rows):
        if not rows:
            return ""
        lines = [self.sep.join(rows[0])]
        for row in rows:
            lines.append(self.sep.join(str(value) for value in row.values()))
        return "\n".join(lines)


@Exporter.register("json")
class JsonExporter(Exporter):
    def __init__(self, indent=None):
        self.indent = indent

    def export(self, rows):
        return json.dumps(rows, indent=self.indent)

import copy


class User:
    def __init__(self, name: str) -> None:
        self.name = name


class Document:
    def __init__(self, title: str, lines: list[str] | None = None, tags: list[str] | None = None,
                 owner: User | None = None) -> None:
        self.title = title
        self.lines: list[str] = list(lines) if lines else []
        self.tags: list[str] = list(tags) if tags else []
        self.owner = owner
        self.links: list["Document"] = []
        self._cache: dict[str, int] = {}

    def add_line(self, text: str) -> None:
        self.lines.append(text)
        self._cache.clear()

    def word_count(self) -> int:
        if "words" not in self._cache:
            self._cache["words"] = sum(len(line.split()) for line in self.lines)
        return self._cache["words"]

    def __copy__(self) -> "Document":
        new = type(self).__new__(type(self))
        new.__dict__.update(self.__dict__)
        new.lines = list(self.lines)
        new.tags = list(self.tags)
        new._cache = {}
        return new

    def __deepcopy__(self, memo: dict[int, object]) -> "Document":
        new = type(self).__new__(type(self))
        memo[id(self)] = new
        for key, value in self.__dict__.items():
            if key == "owner":
                new.owner = value
            elif key == "_cache":
                new._cache = {}
            else:
                setattr(new, key, copy.deepcopy(value, memo))
        return new

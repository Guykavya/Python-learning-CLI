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
        """copy.copy(doc): new lines and tags lists, shared owner and links, empty cache."""
        raise NotImplementedError

    def __deepcopy__(self, memo: dict[int, object]) -> "Document":
        """copy.deepcopy(doc): everything copied except owner (shared); empty cache; cycles kept."""
        raise NotImplementedError

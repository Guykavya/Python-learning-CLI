import copy

from solution import Document, User


def make():
    owner = User("Kavya")
    doc = Document("Notes", ["hello world", "copy me"], ["draft"], owner)
    other = Document("Other", ["x"], [], owner)
    doc.links.append(other)
    doc.word_count()  # fills the cache
    return doc, other, owner


# ------------------------------------------------------------------ copy.copy
def test_copy_is_a_new_document():
    doc, _, _ = make()
    c = copy.copy(doc)
    assert c is not doc and type(c) is Document, "copy.copy must return a NEW Document."
    assert c.title == doc.title and c.lines == doc.lines and c.tags == doc.tags, "The copy has the same data."


def test_copy_has_its_own_lines_and_tags():
    doc, _, _ = make()
    c = copy.copy(doc)
    c.add_line("only in the copy")
    c.tags.append("copy")
    assert doc.lines == ["hello world", "copy me"], (
        "Adding a line to the copy changed the original: the default shallow copy shares the lines list. "
        "In __copy__ give the new document list(self.lines)."
    )
    assert doc.tags == ["draft"], "The tags list must not be shared either: list(self.tags)."
    assert doc.word_count() == 4, "The original's word count must not change when the copy changes."


def test_copy_shares_owner_and_links():
    doc, other, owner = make()
    c = copy.copy(doc)
    assert c.owner is owner, "A copy of a document has the same owner (the same User object)."
    assert c.links is doc.links and c.links[0] is other, "A shallow copy shares the links list (only lines and tags are new)."


def test_copy_cache_is_fresh():
    doc, _, _ = make()
    c = copy.copy(doc)
    assert c._cache == {} and c._cache is not doc._cache, (
        "The cache is derived data: a copy starts with a new EMPTY cache, never the original's dict."
    )
    assert c.word_count() == 4, "The copy can still compute its word count."


# ------------------------------------------------------------------ copy.deepcopy
def test_deepcopy_copies_data_but_shares_owner():
    doc, other, owner = make()
    d = copy.deepcopy(doc)
    assert d is not doc and type(d) is Document, "deepcopy returns a new Document."
    assert d.owner is owner, (
        "deepcopy must NOT clone the owner: copying a document does not create a new person. "
        "The default deepcopy copies every attribute, so write __deepcopy__ and keep self.owner as it is."
    )
    assert d.lines == doc.lines and d.lines is not doc.lines, "Lines are copied."
    assert d.tags is not doc.tags, "Tags are copied."
    assert d.links is not doc.links and d.links[0] is not other, "Linked documents are deep-copied too."
    assert d.links[0].title == "Other" and d.links[0].owner is owner, "A linked copy also keeps its (shared) owner."
    assert d._cache == {} and d._cache is not doc._cache, "deepcopy also starts with an empty cache."


def test_deepcopy_handles_cycles():
    owner = User("Kavya")
    a = Document("A", owner=owner)
    b = Document("B", owner=owner)
    a.links.append(b)
    b.links.append(a)
    a2 = copy.deepcopy(a)
    assert a2.links[0].links[0] is a2, (
        "A links to B and B links back to A. In the copy, B's link must point to the NEW A. Register the new "
        "object with memo[id(self)] = new BEFORE copying the attributes, and pass memo to copy.deepcopy."
    )
    assert a2.links[0] is not b, "B was copied too."


def test_deepcopy_keeps_shared_documents_shared():
    doc, _, _ = make()
    pair = [doc, doc]
    copied = copy.deepcopy(pair)
    assert copied[0] is copied[1], "The same document twice in a list becomes the same copy twice (memo)."
    assert copied[0] is not doc, "...and that copy is new."


# ------------------------------------------------------------------ subclasses
class Draft(Document):
    def __init__(self, title, version=1):
        super().__init__(title, ["v" + str(version)])
        self.version = version


def test_copies_keep_the_subclass_and_extra_attributes():
    d = Draft("Plan", version=3)
    c = copy.copy(d)
    dc = copy.deepcopy(d)
    assert type(c) is Draft and type(dc) is Draft, (
        "Create the copy with type(self).__new__(type(self)), not Document(...), so a subclass is copied as itself."
    )
    assert c.version == 3 and dc.version == 3, (
        "Attributes added by a subclass must be copied too: copy self.__dict__ instead of listing attributes by hand."
    )
